from decimal import Decimal

from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.models.audit_entry import AuditAction
from app.models.employee import Employee
from app.models.evaluation import Evaluation, EvaluationStatus
from app.models.review_cycle import ReviewCycle, ReviewCycleStatus
from app.models.role import RoleName
from app.models.user import User
from app.schemas.audit import AuditEntryResponse
from app.schemas.evaluation import (
    EvaluationCreateRequest,
    EvaluationResponse,
    EvaluationUpdateRequest,
)
from app.services.audit_service import AuditService
from app.services.access_service import AccessService
from app.services.errors import AuthorizationError, NotFoundError, ValidationError
from app.services.nine_box_service import NineBoxService


class EvaluationService:
    def __init__(
        self,
        access_service: AccessService | None = None,
        nine_box_service: NineBoxService | None = None,
        audit_service: AuditService | None = None,
    ) -> None:
        self.access_service = access_service or AccessService()
        self.nine_box_service = nine_box_service or NineBoxService()
        self.audit_service = audit_service or AuditService(self.access_service)

    def list_evaluations(
        self,
        session: Session,
        current_user: User,
        employee_id: int | None = None,
        review_cycle_id: int | None = None,
    ) -> list[EvaluationResponse]:
        if not self.access_service.can_view_evaluations(current_user):
            raise AuthorizationError("You do not have permission to view evaluations.")

        statement = (
            select(Evaluation)
            .options(
                selectinload(Evaluation.employee).selectinload(Employee.manager),
                selectinload(Evaluation.review_cycle),
            )
            .where(Evaluation.status != EvaluationStatus.ARCHIVED.value)
            .order_by(Evaluation.updated_at.desc(), Evaluation.id.desc())
        )

        if review_cycle_id is not None:
            statement = statement.where(Evaluation.review_cycle_id == review_cycle_id)

        if RoleName.HR_ADMIN.value in current_user.role_names or RoleName.EXECUTIVE.value in current_user.role_names:
            if employee_id is not None:
                statement = statement.where(Evaluation.employee_id == employee_id)
        else:
            visible_ids = self.access_service.get_visible_employee_ids(session, current_user)
            if employee_id is not None and employee_id not in visible_ids:
                raise AuthorizationError(
                    "You do not have permission to view evaluations for this employee."
                )
            target_ids = {employee_id} if employee_id is not None else visible_ids
            statement = statement.where(Evaluation.employee_id.in_(target_ids))

        evaluations = session.scalars(statement).all()
        return [
            self._build_evaluation_response(session, current_user, evaluation)
            for evaluation in evaluations
        ]

    def get_evaluation(
        self,
        session: Session,
        current_user: User,
        evaluation_id: int,
    ) -> EvaluationResponse:
        evaluation = self._get_evaluation(session, evaluation_id)
        self.access_service.assert_can_view_evaluation_employee(
            session,
            current_user,
            evaluation.employee,
        )
        return self._build_evaluation_response(session, current_user, evaluation)

    def create_evaluation(
        self,
        session: Session,
        current_user: User,
        payload: EvaluationCreateRequest,
    ) -> EvaluationResponse:
        employee = self._get_employee(session, payload.employee_id)
        review_cycle = self._get_review_cycle(session, payload.review_cycle_id)
        self.access_service.assert_can_manage_evaluation_employee(
            session,
            current_user,
            employee,
        )
        self._ensure_employee_is_active(employee)
        self._ensure_review_cycle_is_available(review_cycle)
        self._ensure_evaluation_does_not_exist(
            session,
            employee.id,
            review_cycle.id,
        )

        status = self._validate_evaluation_status(payload.status, allow_archived=False)
        summary_comment = self._normalize_optional_text(payload.summary_comment)
        manager_rationale = self._normalize_optional_text(payload.manager_rationale)
        promotion_recommendation = self._normalize_promotion_recommendation(
            payload.promotion_recommendation
        )
        promotion_rationale = self._normalize_optional_text(payload.promotion_rationale)

        evaluation = Evaluation(
            employee_id=employee.id,
            review_cycle_id=review_cycle.id,
            author_user_id=current_user.id,
            updated_by_user_id=current_user.id,
            performance_rating=self._normalize_rating(payload.performance_rating),
            potential_rating=payload.potential_rating,
            performance_tier="",
            potential_tier="",
            nine_box_code="",
            nine_box_label="",
            summary_comment=summary_comment,
            manager_rationale=manager_rationale,
            promotion_recommendation=promotion_recommendation,
            promotion_rationale=promotion_rationale,
            status=status,
        )
        self._apply_nine_box_snapshot(evaluation)
        session.add(evaluation)
        session.flush()
        self.audit_service.record_evaluation_change(
            session,
            current_user,
            evaluation,
            action=AuditAction.CREATED,
            before_state=None,
        )
        session.commit()
        evaluation = self._get_evaluation(session, evaluation.id)
        return self._build_evaluation_response(session, current_user, evaluation)

    def update_evaluation(
        self,
        session: Session,
        current_user: User,
        evaluation_id: int,
        payload: EvaluationUpdateRequest,
    ) -> EvaluationResponse:
        evaluation = self._get_evaluation(session, evaluation_id)
        self.access_service.assert_can_manage_evaluation_employee(
            session,
            current_user,
            evaluation.employee,
        )

        if evaluation.status == EvaluationStatus.ARCHIVED.value:
            raise ValidationError("Archived evaluations cannot be updated.")

        before_state = self.audit_service.capture_evaluation_state(evaluation)
        updates = payload.model_dump(exclude_unset=True)

        if "performance_rating" in updates:
            evaluation.performance_rating = self._normalize_rating(
                updates["performance_rating"]
            )

        if "potential_rating" in updates:
            evaluation.potential_rating = updates["potential_rating"]

        if "performance_rating" in updates or "potential_rating" in updates:
            self._apply_nine_box_snapshot(evaluation)

        if "summary_comment" in updates:
            evaluation.summary_comment = self._normalize_optional_text(
                updates["summary_comment"]
            )

        if "manager_rationale" in updates:
            evaluation.manager_rationale = self._normalize_optional_text(
                updates["manager_rationale"]
            )

        if "promotion_recommendation" in updates:
            evaluation.promotion_recommendation = self._normalize_promotion_recommendation(
                updates["promotion_recommendation"]
            )

        if "promotion_rationale" in updates:
            evaluation.promotion_rationale = self._normalize_optional_text(
                updates["promotion_rationale"]
            )

        if "status" in updates:
            evaluation.status = self._validate_evaluation_status(
                updates["status"],
                allow_archived=False,
            )

        evaluation.updated_by_user_id = current_user.id
        session.add(evaluation)
        self.audit_service.record_evaluation_change(
            session,
            current_user,
            evaluation,
            action=AuditAction.UPDATED,
            before_state=before_state,
        )
        session.commit()
        evaluation = self._get_evaluation(session, evaluation.id)
        return self._build_evaluation_response(session, current_user, evaluation)

    def archive_evaluation(
        self,
        session: Session,
        current_user: User,
        evaluation_id: int,
    ) -> EvaluationResponse:
        evaluation = self._get_evaluation(session, evaluation_id)
        self.access_service.assert_can_manage_evaluation_employee(
            session,
            current_user,
            evaluation.employee,
        )
        before_state = self.audit_service.capture_evaluation_state(evaluation)
        evaluation.status = EvaluationStatus.ARCHIVED.value
        evaluation.updated_by_user_id = current_user.id
        session.add(evaluation)
        self.audit_service.record_evaluation_change(
            session,
            current_user,
            evaluation,
            action=AuditAction.ARCHIVED,
            before_state=before_state,
        )
        session.commit()
        evaluation = self._get_evaluation(session, evaluation.id)
        return self._build_evaluation_response(session, current_user, evaluation)

    def list_evaluation_audit_entries(
        self,
        session: Session,
        current_user: User,
        evaluation_id: int,
    ) -> list[AuditEntryResponse]:
        evaluation = self._get_evaluation(session, evaluation_id)
        return self.audit_service.list_evaluation_audit_entries(
            session,
            current_user,
            evaluation,
        )

    def _get_evaluation(self, session: Session, evaluation_id: int) -> Evaluation:
        statement = (
            select(Evaluation)
            .options(
                selectinload(Evaluation.employee).selectinload(Employee.manager),
                selectinload(Evaluation.review_cycle),
            )
            .where(Evaluation.id == evaluation_id)
        )
        evaluation = session.scalar(statement)
        if evaluation is None:
            raise NotFoundError("Evaluation not found.")
        return evaluation

    def _get_employee(self, session: Session, employee_id: int) -> Employee:
        employee = session.get(Employee, employee_id)
        if employee is None:
            raise NotFoundError("Employee not found.")
        return employee

    def _get_review_cycle(self, session: Session, review_cycle_id: int) -> ReviewCycle:
        review_cycle = session.get(ReviewCycle, review_cycle_id)
        if review_cycle is None:
            raise NotFoundError("Review cycle not found.")
        return review_cycle

    def _ensure_evaluation_does_not_exist(
        self,
        session: Session,
        employee_id: int,
        review_cycle_id: int,
    ) -> None:
        statement = select(Evaluation).where(
            Evaluation.employee_id == employee_id,
            Evaluation.review_cycle_id == review_cycle_id,
        )
        if session.scalar(statement) is not None:
            raise ValidationError(
                "An evaluation already exists for this employee in the selected review cycle."
            )

    def _ensure_employee_is_active(self, employee: Employee) -> None:
        if not employee.is_active:
            raise ValidationError("Archived employees cannot receive new evaluations.")

    def _ensure_review_cycle_is_available(self, review_cycle: ReviewCycle) -> None:
        if review_cycle.status == ReviewCycleStatus.ARCHIVED.value:
            raise ValidationError("Archived review cycles cannot receive new evaluations.")

    def _normalize_rating(self, value: Decimal) -> Decimal:
        return value.quantize(Decimal("0.01"))

    def _normalize_optional_text(self, value: str | None) -> str | None:
        if value is None:
            return None

        normalized = value.strip()
        return normalized or None

    def _normalize_promotion_recommendation(self, value: str | None) -> str | None:
        if value is None:
            return None

        normalized = value.strip().lower()
        if not normalized:
            return None

        allowed_values = {
            "not_recommended",
            "future_consideration",
            "recommended_now",
        }
        if normalized not in allowed_values:
            raise ValidationError("Promotion recommendation is invalid.")

        return normalized

    def _validate_evaluation_status(self, status: str, allow_archived: bool) -> str:
        normalized = status.strip().lower()
        allowed_statuses = {evaluation_status.value for evaluation_status in EvaluationStatus}
        if not allow_archived:
            allowed_statuses.discard(EvaluationStatus.ARCHIVED.value)

        if normalized not in allowed_statuses:
            raise ValidationError("Evaluation status is invalid.")

        return normalized

    def _apply_nine_box_snapshot(self, evaluation: Evaluation) -> None:
        snapshot = self.nine_box_service.build_snapshot(
            evaluation.performance_rating,
            evaluation.potential_rating,
        )
        evaluation.performance_tier = snapshot.performance_tier
        evaluation.potential_tier = snapshot.potential_tier
        evaluation.nine_box_code = snapshot.nine_box_code
        evaluation.nine_box_label = snapshot.nine_box_label

    def _build_evaluation_response(
        self,
        session: Session,
        current_user: User,
        evaluation: Evaluation,
    ) -> EvaluationResponse:
        include_sensitive_fields = False
        if self.access_service.can_view_evaluation_sensitive_fields(current_user):
            try:
                self.access_service.assert_can_view_evaluation_sensitive_fields(
                    session,
                    current_user,
                    evaluation.employee,
                )
            except AuthorizationError:
                include_sensitive_fields = False
            else:
                include_sensitive_fields = True

        return EvaluationResponse.from_evaluation(
            evaluation,
            include_sensitive_fields=include_sensitive_fields,
        )

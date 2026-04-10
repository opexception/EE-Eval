from decimal import Decimal

from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.models.employee import Employee
from app.models.evaluation import Evaluation, EvaluationStatus
from app.models.review_cycle import ReviewCycle, ReviewCycleStatus
from app.models.role import RoleName
from app.models.user import User
from app.schemas.evaluation import (
    EvaluationCreateRequest,
    EvaluationResponse,
    EvaluationUpdateRequest,
)
from app.services.access_service import AccessService
from app.services.errors import AuthorizationError, NotFoundError, ValidationError


class EvaluationService:
    def __init__(self, access_service: AccessService | None = None) -> None:
        self.access_service = access_service or AccessService()

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
            EvaluationResponse.from_evaluation(evaluation)
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
        return EvaluationResponse.from_evaluation(evaluation)

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

        evaluation = Evaluation(
            employee_id=employee.id,
            review_cycle_id=review_cycle.id,
            author_user_id=current_user.id,
            updated_by_user_id=current_user.id,
            performance_rating=self._normalize_rating(payload.performance_rating),
            potential_rating=payload.potential_rating,
            summary_comment=summary_comment,
            status=status,
        )
        session.add(evaluation)
        session.commit()
        evaluation = self._get_evaluation(session, evaluation.id)
        return EvaluationResponse.from_evaluation(evaluation)

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

        updates = payload.model_dump(exclude_unset=True)

        if "performance_rating" in updates:
            evaluation.performance_rating = self._normalize_rating(
                updates["performance_rating"]
            )

        if "potential_rating" in updates:
            evaluation.potential_rating = updates["potential_rating"]

        if "summary_comment" in updates:
            evaluation.summary_comment = self._normalize_optional_text(
                updates["summary_comment"]
            )

        if "status" in updates:
            evaluation.status = self._validate_evaluation_status(
                updates["status"],
                allow_archived=False,
            )

        evaluation.updated_by_user_id = current_user.id
        session.add(evaluation)
        session.commit()
        evaluation = self._get_evaluation(session, evaluation.id)
        return EvaluationResponse.from_evaluation(evaluation)

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
        evaluation.status = EvaluationStatus.ARCHIVED.value
        evaluation.updated_by_user_id = current_user.id
        session.add(evaluation)
        session.commit()
        evaluation = self._get_evaluation(session, evaluation.id)
        return EvaluationResponse.from_evaluation(evaluation)

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

    def _validate_evaluation_status(self, status: str, allow_archived: bool) -> str:
        normalized = status.strip().lower()
        allowed_statuses = {evaluation_status.value for evaluation_status in EvaluationStatus}
        if not allow_archived:
            allowed_statuses.discard(EvaluationStatus.ARCHIVED.value)

        if normalized not in allowed_statuses:
            raise ValidationError("Evaluation status is invalid.")

        return normalized

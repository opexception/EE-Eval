from app.models.review_cycle import ReviewCycle, ReviewCycleStatus, ReviewCycleType
from app.models.user import User
from app.schemas.review_cycle import (
    ReviewCycleCreateRequest,
    ReviewCycleResponse,
    ReviewCycleUpdateRequest,
)
from app.services.access_service import AccessService
from app.services.errors import NotFoundError, ValidationError
from sqlalchemy import select
from sqlalchemy.orm import Session


class ReviewCycleService:
    def __init__(self, access_service: AccessService | None = None) -> None:
        self.access_service = access_service or AccessService()

    def list_review_cycles(
        self,
        session: Session,
        current_user: User,
    ) -> list[ReviewCycleResponse]:
        del current_user
        statement = (
            select(ReviewCycle)
            .where(ReviewCycle.status != ReviewCycleStatus.ARCHIVED.value)
            .order_by(ReviewCycle.start_date.desc(), ReviewCycle.name)
        )
        review_cycles = session.scalars(statement).all()
        return [
            ReviewCycleResponse.from_review_cycle(review_cycle)
            for review_cycle in review_cycles
        ]

    def get_review_cycle(
        self,
        session: Session,
        current_user: User,
        review_cycle_id: int,
    ) -> ReviewCycleResponse:
        del current_user
        review_cycle = self._get_review_cycle(session, review_cycle_id)
        return ReviewCycleResponse.from_review_cycle(review_cycle)

    def create_review_cycle(
        self,
        session: Session,
        current_user: User,
        payload: ReviewCycleCreateRequest,
    ) -> ReviewCycleResponse:
        self.access_service.assert_can_manage_review_cycles(current_user)

        name = self._normalize_required_text(payload.name, "Review cycle name is required.")
        cycle_type = self._validate_cycle_type(payload.cycle_type)
        status = self._validate_cycle_status(payload.status)
        self._validate_date_range(payload.start_date, payload.end_date)
        self._ensure_review_cycle_name_is_unique(session, name)

        review_cycle = ReviewCycle(
            name=name,
            cycle_type=cycle_type,
            start_date=payload.start_date,
            end_date=payload.end_date,
            status=status,
            created_by_user_id=current_user.id,
            updated_by_user_id=current_user.id,
        )
        session.add(review_cycle)
        session.commit()
        session.refresh(review_cycle)
        return ReviewCycleResponse.from_review_cycle(review_cycle)

    def update_review_cycle(
        self,
        session: Session,
        current_user: User,
        review_cycle_id: int,
        payload: ReviewCycleUpdateRequest,
    ) -> ReviewCycleResponse:
        self.access_service.assert_can_manage_review_cycles(current_user)

        review_cycle = self._get_review_cycle(session, review_cycle_id)
        updates = payload.model_dump(exclude_unset=True)

        if "name" in updates:
            review_cycle.name = self._normalize_required_text(
                updates["name"],
                "Review cycle name is required.",
            )
            self._ensure_review_cycle_name_is_unique(
                session,
                review_cycle.name,
                exclude_review_cycle_id=review_cycle.id,
            )

        if "cycle_type" in updates:
            review_cycle.cycle_type = self._validate_cycle_type(updates["cycle_type"])

        if "start_date" in updates:
            review_cycle.start_date = updates["start_date"]

        if "end_date" in updates:
            review_cycle.end_date = updates["end_date"]

        if "status" in updates:
            review_cycle.status = self._validate_cycle_status(updates["status"])

        self._validate_date_range(review_cycle.start_date, review_cycle.end_date)
        review_cycle.updated_by_user_id = current_user.id
        session.add(review_cycle)
        session.commit()
        session.refresh(review_cycle)
        return ReviewCycleResponse.from_review_cycle(review_cycle)

    def archive_review_cycle(
        self,
        session: Session,
        current_user: User,
        review_cycle_id: int,
    ) -> ReviewCycleResponse:
        self.access_service.assert_can_manage_review_cycles(current_user)

        review_cycle = self._get_review_cycle(session, review_cycle_id)
        review_cycle.status = ReviewCycleStatus.ARCHIVED.value
        review_cycle.updated_by_user_id = current_user.id
        session.add(review_cycle)
        session.commit()
        session.refresh(review_cycle)
        return ReviewCycleResponse.from_review_cycle(review_cycle)

    def _get_review_cycle(self, session: Session, review_cycle_id: int) -> ReviewCycle:
        review_cycle = session.get(ReviewCycle, review_cycle_id)
        if review_cycle is None:
            raise NotFoundError("Review cycle not found.")
        return review_cycle

    def _ensure_review_cycle_name_is_unique(
        self,
        session: Session,
        name: str,
        exclude_review_cycle_id: int | None = None,
    ) -> None:
        statement = select(ReviewCycle).where(ReviewCycle.name == name)
        review_cycle = session.scalar(statement)
        if review_cycle is None:
            return

        if (
            exclude_review_cycle_id is not None
            and review_cycle.id == exclude_review_cycle_id
        ):
            return

        raise ValidationError("Review cycle name already exists.")

    def _validate_date_range(self, start_date, end_date) -> None:
        if end_date < start_date:
            raise ValidationError("Review cycle end date must be on or after the start date.")

    def _validate_cycle_type(self, cycle_type: str) -> str:
        normalized = cycle_type.strip().lower()
        if not normalized:
            raise ValidationError("Review cycle type is required.")
        if normalized not in {cycle.value for cycle in ReviewCycleType}:
            raise ValidationError("Review cycle type is invalid.")
        return normalized

    def _validate_cycle_status(self, status: str) -> str:
        normalized = status.strip().lower()
        if not normalized:
            raise ValidationError("Review cycle status is required.")
        if normalized not in {cycle_status.value for cycle_status in ReviewCycleStatus}:
            raise ValidationError("Review cycle status is invalid.")
        return normalized

    def _normalize_required_text(self, value: str, error_message: str) -> str:
        normalized = value.strip()
        if not normalized:
            raise ValidationError(error_message)
        return normalized

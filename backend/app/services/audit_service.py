from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.models.audit_entry import AuditAction, AuditEntry
from app.models.evaluation import Evaluation
from app.models.user import User
from app.schemas.audit import AuditEntryResponse
from app.services.access_service import AccessService


class AuditService:
    RESOURCE_TYPE_EVALUATION = "evaluation"
    SAFE_VALUE_FIELDS = {"status", "nine_box_label"}
    TRACKED_EVALUATION_FIELDS = (
        "status",
        "nine_box_label",
        "performance_rating",
        "potential_rating",
        "summary_comment",
        "manager_rationale",
        "promotion_recommendation",
        "promotion_rationale",
    )

    def __init__(self, access_service: AccessService | None = None) -> None:
        self.access_service = access_service or AccessService()

    def capture_evaluation_state(self, evaluation: Evaluation) -> dict[str, object]:
        return {
            "status": evaluation.status,
            "nine_box_label": evaluation.nine_box_label,
            "performance_rating": (
                f"{evaluation.performance_rating:.2f}"
                if evaluation.performance_rating is not None
                else None
            ),
            "potential_rating": (
                str(evaluation.potential_rating)
                if evaluation.potential_rating is not None
                else None
            ),
            "summary_comment": evaluation.summary_comment,
            "manager_rationale": evaluation.manager_rationale,
            "promotion_recommendation": evaluation.promotion_recommendation,
            "promotion_rationale": evaluation.promotion_rationale,
        }

    def record_evaluation_change(
        self,
        session: Session,
        actor: User,
        evaluation: Evaluation,
        action: AuditAction,
        before_state: dict[str, object] | None,
    ) -> None:
        after_state = self.capture_evaluation_state(evaluation)
        field_changes = self._build_field_changes(before_state, after_state)
        if action == AuditAction.UPDATED and not field_changes:
            return

        session.add(
            AuditEntry(
                resource_type=self.RESOURCE_TYPE_EVALUATION,
                resource_id=evaluation.id,
                action=action.value,
                actor_user_id=actor.id,
                field_changes=field_changes,
            )
        )

    def list_evaluation_audit_entries(
        self,
        session: Session,
        current_user: User,
        evaluation: Evaluation,
    ) -> list[AuditEntryResponse]:
        self.access_service.assert_can_view_evaluation_audit(
            session,
            current_user,
            evaluation.employee,
        )
        statement = (
            select(AuditEntry)
            .options(selectinload(AuditEntry.actor))
            .where(
                AuditEntry.resource_type == self.RESOURCE_TYPE_EVALUATION,
                AuditEntry.resource_id == evaluation.id,
            )
            .order_by(AuditEntry.created_at.desc(), AuditEntry.id.desc())
        )
        entries = session.scalars(statement).all()
        return [AuditEntryResponse.from_audit_entry(entry) for entry in entries]

    def _build_field_changes(
        self,
        before_state: dict[str, object] | None,
        after_state: dict[str, object],
    ) -> list[dict[str, object]]:
        field_changes: list[dict[str, object]] = []
        fields = self.TRACKED_EVALUATION_FIELDS

        if before_state is None:
            for field_name in fields:
                after_value = after_state[field_name]
                if after_value is None:
                    continue
                field_changes.append(
                    self._create_field_change(
                        field_name,
                        before_value=None,
                        after_value=after_value,
                    )
                )
            return field_changes

        for field_name in fields:
            before_value = before_state[field_name]
            after_value = after_state[field_name]
            if before_value == after_value:
                continue
            field_changes.append(
                self._create_field_change(
                    field_name,
                    before_value=before_value,
                    after_value=after_value,
                )
            )

        return field_changes

    def _create_field_change(
        self,
        field_name: str,
        before_value: object | None,
        after_value: object | None,
    ) -> dict[str, object]:
        is_sensitive = field_name not in self.SAFE_VALUE_FIELDS
        if before_value is None and after_value is not None:
            change_type = "set"
        elif before_value is not None and after_value is None:
            change_type = "cleared"
        else:
            change_type = "updated"

        field_change: dict[str, object] = {
            "field": field_name,
            "change_type": change_type,
            "sensitive": is_sensitive,
        }
        if not is_sensitive:
            field_change["before"] = self._stringify_value(before_value)
            field_change["after"] = self._stringify_value(after_value)

        return field_change

    def _stringify_value(self, value: object | None) -> str | None:
        if value is None:
            return None
        return str(value)

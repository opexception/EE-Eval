from datetime import datetime

from pydantic import BaseModel

from app.models.audit_entry import AuditEntry


class AuditFieldChangeResponse(BaseModel):
    field: str
    change_type: str
    sensitive: bool
    before: str | None = None
    after: str | None = None


class AuditEntryResponse(BaseModel):
    id: int
    resource_type: str
    resource_id: int
    action: str
    actor_user_id: int
    actor_username: str
    actor_full_name: str
    field_changes: list[AuditFieldChangeResponse]
    created_at: datetime

    @classmethod
    def from_audit_entry(cls, audit_entry: AuditEntry) -> "AuditEntryResponse":
        return cls(
            id=audit_entry.id,
            resource_type=audit_entry.resource_type,
            resource_id=audit_entry.resource_id,
            action=audit_entry.action,
            actor_user_id=audit_entry.actor_user_id,
            actor_username=audit_entry.actor.username,
            actor_full_name=audit_entry.actor.full_name,
            field_changes=[
                AuditFieldChangeResponse.model_validate(field_change)
                for field_change in audit_entry.field_changes
            ],
            created_at=audit_entry.created_at,
        )

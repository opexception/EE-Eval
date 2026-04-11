from decimal import Decimal

import pytest
from sqlalchemy import select

from app.models.audit_entry import AuditEntry
from app.schemas.evaluation import EvaluationCreateRequest, EvaluationUpdateRequest
from app.services.errors import AuthorizationError
from app.services.evaluation_service import EvaluationService


def test_manager_create_logs_sensitive_fields_without_storing_text_in_audit(
    db_session,
    domain_context,
) -> None:
    response = EvaluationService().create_evaluation(
        db_session,
        domain_context.manager_user,
        EvaluationCreateRequest(
            employee_id=domain_context.peer_employee.id,
            review_cycle_id=domain_context.active_review_cycle.id,
            performance_rating=Decimal("4.05"),
            potential_rating=3,
            summary_comment="Jordan is taking on more visible cross-team work.",
            manager_rationale=(
                "Jordan is handling broader design ambiguity and showing stronger influence."
            ),
            promotion_recommendation="future_consideration",
            promotion_rationale=(
                "Jordan is trending well, but one more cycle of stronger stakeholder leadership would help."
            ),
            status="draft",
        ),
    )

    assert response.sensitive_fields_visible is True
    assert response.manager_rationale is not None
    assert response.promotion_recommendation == "future_consideration"
    assert response.promotion_rationale is not None

    audit_entry = db_session.scalar(
        select(AuditEntry).where(
            AuditEntry.resource_type == "evaluation",
            AuditEntry.resource_id == response.id,
        )
    )

    assert audit_entry is not None
    assert audit_entry.actor_user_id == domain_context.manager_user.id
    assert audit_entry.action == "created"

    redacted_fields = {
        field_change["field"]: field_change
        for field_change in audit_entry.field_changes
        if field_change["sensitive"] is True
    }
    assert "manager_rationale" in redacted_fields
    assert "promotion_recommendation" in redacted_fields
    assert "promotion_rationale" in redacted_fields
    assert redacted_fields["manager_rationale"]["change_type"] == "set"
    assert "before" not in redacted_fields["manager_rationale"]
    assert "after" not in redacted_fields["manager_rationale"]


def test_upper_manager_sees_redacted_sensitive_fields(db_session, domain_context) -> None:
    response = EvaluationService().get_evaluation(
        db_session,
        domain_context.upper_manager_user,
        domain_context.employee_evaluation.id,
    )

    assert response.sensitive_fields_visible is False
    assert response.summary_comment is not None
    assert response.manager_rationale is None
    assert response.promotion_recommendation is None
    assert response.promotion_rationale is None


def test_manager_update_creates_redacted_audit_entry(db_session, domain_context) -> None:
    service = EvaluationService()

    response = service.update_evaluation(
        db_session,
        domain_context.manager_user,
        domain_context.employee_evaluation.id,
        EvaluationUpdateRequest(
            manager_rationale=(
                "Taylor is operating more independently and leading technical conversations more often."
            ),
            promotion_recommendation="recommended_now",
            promotion_rationale=(
                "Taylor is already showing next-level impact and can absorb broader ownership now."
            ),
        ),
    )

    assert response.sensitive_fields_visible is True
    assert response.promotion_recommendation == "recommended_now"

    audit_entries = service.list_evaluation_audit_entries(
        db_session,
        domain_context.manager_user,
        domain_context.employee_evaluation.id,
    )

    assert len(audit_entries) == 1
    assert audit_entries[0].action == "updated"
    assert audit_entries[0].actor_username == domain_context.manager_user.username

    changed_fields = {
        field_change.field: field_change
        for field_change in audit_entries[0].field_changes
    }
    assert changed_fields["manager_rationale"].sensitive is True
    assert changed_fields["promotion_recommendation"].sensitive is True
    assert changed_fields["promotion_rationale"].sensitive is True
    assert changed_fields["promotion_recommendation"].before is None
    assert changed_fields["promotion_recommendation"].after is None


def test_upper_manager_cannot_view_evaluation_audit_history(db_session, domain_context) -> None:
    service = EvaluationService()
    service.update_evaluation(
        db_session,
        domain_context.manager_user,
        domain_context.employee_evaluation.id,
        EvaluationUpdateRequest(
            manager_rationale="Updated manager-only rationale for audit access testing.",
        ),
    )

    with pytest.raises(AuthorizationError) as exc_info:
        service.list_evaluation_audit_entries(
            db_session,
            domain_context.upper_manager_user,
            domain_context.employee_evaluation.id,
        )

    assert str(exc_info.value) == "You do not have permission to view evaluation audit history."

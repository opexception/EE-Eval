from decimal import Decimal

import pytest

from app.schemas.evaluation import EvaluationCreateRequest, EvaluationUpdateRequest
from app.services.errors import AuthorizationError
from app.services.evaluation_service import EvaluationService


def test_manager_can_create_evaluation_for_report(db_session, domain_context) -> None:
    response = EvaluationService().create_evaluation(
        db_session,
        domain_context.manager_user,
        EvaluationCreateRequest(
            employee_id=domain_context.peer_employee.id,
            review_cycle_id=domain_context.active_review_cycle.id,
            performance_rating=Decimal("3.45"),
            potential_rating=2,
            summary_comment="Jordan is making steady progress with stakeholder communication.",
            status="draft",
        ),
    )

    assert response.employee_id == domain_context.peer_employee.id
    assert response.review_cycle_id == domain_context.active_review_cycle.id
    assert response.performance_rating == 3.45
    assert response.performance_tier == "effective"
    assert response.potential_tier == "moderate"
    assert response.nine_box_label == "Contributor"
    assert response.status == "draft"


def test_manager_cannot_create_evaluation_outside_scope(db_session, domain_context) -> None:
    with pytest.raises(AuthorizationError) as exc_info:
        EvaluationService().create_evaluation(
            db_session,
            domain_context.outsider_manager_user,
            EvaluationCreateRequest(
                employee_id=domain_context.employee_record.id,
                review_cycle_id=domain_context.active_review_cycle.id,
                performance_rating=Decimal("3.10"),
                potential_rating=2,
                summary_comment="Out-of-scope test.",
                status="draft",
            ),
        )

    assert str(exc_info.value) == "You do not have permission to manage this evaluation."


def test_executive_can_read_but_not_update_evaluation(db_session, domain_context) -> None:
    response = EvaluationService().get_evaluation(
        db_session,
        domain_context.executive_user,
        domain_context.employee_evaluation.id,
    )

    assert response.employee_id == domain_context.employee_record.id

    with pytest.raises(AuthorizationError) as exc_info:
        EvaluationService().update_evaluation(
            db_session,
            domain_context.executive_user,
            domain_context.employee_evaluation.id,
            EvaluationUpdateRequest(summary_comment="Executive edit attempt."),
        )

    assert str(exc_info.value) == "You do not have permission to manage evaluations."


def test_employee_cannot_read_evaluations_in_first_pass(db_session, domain_context) -> None:
    with pytest.raises(AuthorizationError) as exc_info:
        EvaluationService().get_evaluation(
            db_session,
            domain_context.employee_user,
            domain_context.employee_evaluation.id,
        )

    assert str(exc_info.value) == "You do not have permission to view evaluations."

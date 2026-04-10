import pytest

from app.schemas.review_cycle import ReviewCycleCreateRequest
from app.services.errors import AuthorizationError
from app.services.review_cycle_service import ReviewCycleService


def test_review_cycle_list_excludes_archived_cycles(db_session, domain_context) -> None:
    responses = ReviewCycleService().list_review_cycles(
        db_session,
        domain_context.employee_user,
    )

    assert [response.name for response in responses] == ["2026 Annual Review"]


def test_only_hr_can_create_review_cycles(db_session, domain_context) -> None:
    with pytest.raises(AuthorizationError) as exc_info:
        ReviewCycleService().create_review_cycle(
            db_session,
            domain_context.manager_user,
            ReviewCycleCreateRequest(
                name="2026 Special Review",
                cycle_type="ad_hoc",
                start_date=domain_context.active_review_cycle.start_date,
                end_date=domain_context.active_review_cycle.end_date,
                status="draft",
            ),
        )

    assert str(exc_info.value) == "You do not have permission to manage review cycles."

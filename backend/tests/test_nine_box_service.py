from decimal import Decimal

import pytest

from app.models.evaluation import Evaluation, EvaluationStatus
from app.services.errors import AuthorizationError
from app.services.nine_box_service import NineBoxService


def test_build_snapshot_maps_ratings_to_accelerator() -> None:
    snapshot = NineBoxService().build_snapshot(Decimal("3.90"), 3)

    assert snapshot.performance_tier == "high"
    assert snapshot.potential_tier == "high"
    assert snapshot.nine_box_code == "high_potential_high_performance"
    assert snapshot.nine_box_label == "Accelerator"


def test_manager_matrix_returns_report_employees_for_cycle(db_session, domain_context) -> None:
    peer_snapshot = NineBoxService().build_snapshot(Decimal("3.25"), 2)
    db_session.add(
        Evaluation(
            employee_id=domain_context.peer_employee.id,
            review_cycle_id=domain_context.active_review_cycle.id,
            author_user_id=domain_context.manager_user.id,
            updated_by_user_id=domain_context.manager_user.id,
            performance_rating=Decimal("3.25"),
            potential_rating=2,
            performance_tier=peer_snapshot.performance_tier,
            potential_tier=peer_snapshot.potential_tier,
            nine_box_code=peer_snapshot.nine_box_code,
            nine_box_label=peer_snapshot.nine_box_label,
            summary_comment="Jordan is developing steadily.",
            status=EvaluationStatus.DRAFT.value,
        )
    )
    db_session.commit()

    matrix = NineBoxService().get_matrix(
        db_session,
        domain_context.manager_user,
        review_cycle_id=domain_context.active_review_cycle.id,
    )

    assert matrix.review_cycle_id == domain_context.active_review_cycle.id
    assert matrix.total_employees == 2

    anchor_cell = next(cell for cell in matrix.cells if cell.box_label == "Anchor")
    contributor_cell = next(cell for cell in matrix.cells if cell.box_label == "Contributor")

    assert [employee.employee_name for employee in anchor_cell.employees] == ["Taylor Brooks"]
    assert [employee.employee_name for employee in contributor_cell.employees] == ["Jordan Rivera"]


def test_manager_matrix_excludes_manager_own_employee_record(db_session, domain_context) -> None:
    manager_snapshot = NineBoxService().build_snapshot(Decimal("4.10"), 3)
    db_session.add(
        Evaluation(
            employee_id=domain_context.manager_employee.id,
            review_cycle_id=domain_context.active_review_cycle.id,
            author_user_id=domain_context.upper_manager_user.id,
            updated_by_user_id=domain_context.upper_manager_user.id,
            performance_rating=Decimal("4.10"),
            potential_rating=3,
            performance_tier=manager_snapshot.performance_tier,
            potential_tier=manager_snapshot.potential_tier,
            nine_box_code=manager_snapshot.nine_box_code,
            nine_box_label=manager_snapshot.nine_box_label,
            summary_comment="Manager self record for scope testing.",
            status=EvaluationStatus.SUBMITTED.value,
        )
    )
    db_session.commit()

    matrix = NineBoxService().get_matrix(
        db_session,
        domain_context.manager_user,
        review_cycle_id=domain_context.active_review_cycle.id,
    )

    employee_names = [
        employee.employee_name
        for cell in matrix.cells
        for employee in cell.employees
    ]

    assert "Avery Jordan" not in employee_names
    assert "Taylor Brooks" in employee_names


def test_employee_cannot_view_nine_box_matrix(db_session, domain_context) -> None:
    with pytest.raises(AuthorizationError) as exc_info:
        NineBoxService().get_matrix(
            db_session,
            domain_context.employee_user,
            review_cycle_id=domain_context.active_review_cycle.id,
        )

    assert str(exc_info.value) == "You do not have permission to view 9-box placements."

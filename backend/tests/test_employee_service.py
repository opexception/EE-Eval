import pytest

from app.schemas.employee import EmployeeCreateRequest, EmployeeUpdateRequest
from app.services.employee_service import EmployeeService
from app.services.errors import AuthorizationError


def test_manager_only_sees_their_reporting_scope(db_session, domain_context) -> None:
    responses = EmployeeService().list_employees(db_session, domain_context.manager_user)

    assert {response.employee_number for response in responses} == {
        "EMP-1200",
        "EMP-1300",
        "EMP-1310",
    }


def test_reports_only_view_excludes_the_manager_profile(db_session, domain_context) -> None:
    responses = EmployeeService().list_employees(
        db_session,
        domain_context.manager_user,
        reports_only=True,
    )

    assert {response.employee_number for response in responses} == {
        "EMP-1300",
        "EMP-1310",
    }


def test_hr_can_create_employee_profiles(db_session, domain_context) -> None:
    response = EmployeeService().create_employee(
        db_session,
        domain_context.hr_user,
        EmployeeCreateRequest(
            employee_number="EMP-1400",
            first_name="Maya",
            last_name="Patel",
            job_title="HR Generalist",
            department="People Operations",
            manager_id=domain_context.hr_employee.id,
            user_id=None,
        ),
    )

    assert response.employee_number == "EMP-1400"
    assert response.manager_id == domain_context.hr_employee.id
    assert response.manager_name == "Harper Quinn"


def test_non_hr_user_cannot_update_employee_profiles(db_session, domain_context) -> None:
    with pytest.raises(AuthorizationError) as exc_info:
        EmployeeService().update_employee(
            db_session,
            domain_context.manager_user,
            domain_context.employee_record.id,
            EmployeeUpdateRequest(job_title="Principal Engineer"),
        )

    assert str(exc_info.value) == "You do not have permission to manage employee profiles."

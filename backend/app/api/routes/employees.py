from fastapi import APIRouter

from app.api.deps import DatabaseSessionDep, EmployeeServiceDep
from app.api.errors import to_http_exception
from app.auth.deps import CurrentUserDep
from app.schemas.employee import (
    EmployeeCreateRequest,
    EmployeeResponse,
    EmployeeUpdateRequest,
)
from app.services.errors import ServiceError

router = APIRouter()


@router.get("", response_model=list[EmployeeResponse], summary="List visible employees")
def list_employees(
    current_user: CurrentUserDep,
    session: DatabaseSessionDep,
    service: EmployeeServiceDep,
    reports_only: bool = False,
) -> list[EmployeeResponse]:
    try:
        return service.list_employees(
            session,
            current_user,
            reports_only=reports_only,
        )
    except ServiceError as exc:
        raise to_http_exception(exc) from exc


@router.post("", response_model=EmployeeResponse, summary="Create an employee")
def create_employee(
    payload: EmployeeCreateRequest,
    current_user: CurrentUserDep,
    session: DatabaseSessionDep,
    service: EmployeeServiceDep,
) -> EmployeeResponse:
    try:
        return service.create_employee(session, current_user, payload)
    except ServiceError as exc:
        raise to_http_exception(exc) from exc


@router.get(
    "/{employee_id}",
    response_model=EmployeeResponse,
    summary="Get an employee",
)
def get_employee(
    employee_id: int,
    current_user: CurrentUserDep,
    session: DatabaseSessionDep,
    service: EmployeeServiceDep,
) -> EmployeeResponse:
    try:
        return service.get_employee(session, current_user, employee_id)
    except ServiceError as exc:
        raise to_http_exception(exc) from exc


@router.put(
    "/{employee_id}",
    response_model=EmployeeResponse,
    summary="Update an employee",
)
def update_employee(
    employee_id: int,
    payload: EmployeeUpdateRequest,
    current_user: CurrentUserDep,
    session: DatabaseSessionDep,
    service: EmployeeServiceDep,
) -> EmployeeResponse:
    try:
        return service.update_employee(session, current_user, employee_id, payload)
    except ServiceError as exc:
        raise to_http_exception(exc) from exc


@router.delete(
    "/{employee_id}",
    response_model=EmployeeResponse,
    summary="Archive an employee",
)
def archive_employee(
    employee_id: int,
    current_user: CurrentUserDep,
    session: DatabaseSessionDep,
    service: EmployeeServiceDep,
) -> EmployeeResponse:
    try:
        return service.archive_employee(session, current_user, employee_id)
    except ServiceError as exc:
        raise to_http_exception(exc) from exc

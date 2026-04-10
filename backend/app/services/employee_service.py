from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.models.employee import Employee
from app.models.user import User
from app.schemas.employee import (
    EmployeeCreateRequest,
    EmployeeResponse,
    EmployeeUpdateRequest,
)
from app.services.access_service import AccessService
from app.services.errors import AuthorizationError, NotFoundError, ValidationError


class EmployeeService:
    def __init__(self, access_service: AccessService | None = None) -> None:
        self.access_service = access_service or AccessService()

    def list_employees(
        self,
        session: Session,
        current_user: User,
        reports_only: bool = False,
    ) -> list[EmployeeResponse]:
        if not self.access_service.can_view_employees(current_user):
            raise AuthorizationError(
                "You do not have permission to view employee profiles."
            )

        visible_ids = self.access_service.get_visible_employee_ids(session, current_user)
        if reports_only:
            linked_employee = self.access_service.get_linked_employee(session, current_user)
            if linked_employee is not None:
                visible_ids.discard(linked_employee.id)

        statement = (
            select(Employee)
            .options(selectinload(Employee.manager))
            .where(Employee.id.in_(visible_ids))
            .order_by(Employee.last_name, Employee.first_name)
        )
        employees = session.scalars(statement).all()
        return [EmployeeResponse.from_employee(employee) for employee in employees]

    def get_employee(
        self,
        session: Session,
        current_user: User,
        employee_id: int,
    ) -> EmployeeResponse:
        employee = self._get_employee(session, employee_id)
        self.access_service.assert_can_view_employee(session, current_user, employee)
        return EmployeeResponse.from_employee(employee)

    def create_employee(
        self,
        session: Session,
        current_user: User,
        payload: EmployeeCreateRequest,
    ) -> EmployeeResponse:
        self.access_service.assert_can_manage_employee_directory(current_user)

        employee_number = self._normalize_required_text(
            payload.employee_number,
            "Employee number is required.",
        )
        first_name = self._normalize_required_text(
            payload.first_name,
            "First name is required.",
        )
        last_name = self._normalize_required_text(
            payload.last_name,
            "Last name is required.",
        )
        job_title = self._normalize_required_text(
            payload.job_title,
            "Job title is required.",
        )
        department = self._normalize_required_text(
            payload.department,
            "Department is required.",
        )

        self._ensure_employee_number_is_unique(session, employee_number)
        manager = self._resolve_manager(session, payload.manager_id)
        self._resolve_user(session, payload.user_id)
        self._ensure_user_is_available(session, payload.user_id)

        employee = Employee(
            employee_number=employee_number,
            first_name=first_name,
            last_name=last_name,
            job_title=job_title,
            department=department,
            manager_id=manager.id if manager is not None else None,
            user_id=payload.user_id,
            is_active=True,
        )
        session.add(employee)
        session.commit()
        session.refresh(employee)
        session.refresh(employee, attribute_names=["manager"])
        return EmployeeResponse.from_employee(employee)

    def update_employee(
        self,
        session: Session,
        current_user: User,
        employee_id: int,
        payload: EmployeeUpdateRequest,
    ) -> EmployeeResponse:
        self.access_service.assert_can_manage_employee_directory(current_user)

        employee = self._get_employee(session, employee_id)
        updates = payload.model_dump(exclude_unset=True)

        if "employee_number" in updates:
            employee.employee_number = self._normalize_required_text(
                updates["employee_number"],
                "Employee number is required.",
            )
            self._ensure_employee_number_is_unique(
                session,
                employee.employee_number,
                exclude_employee_id=employee.id,
            )

        if "first_name" in updates:
            employee.first_name = self._normalize_required_text(
                updates["first_name"],
                "First name is required.",
            )

        if "last_name" in updates:
            employee.last_name = self._normalize_required_text(
                updates["last_name"],
                "Last name is required.",
            )

        if "job_title" in updates:
            employee.job_title = self._normalize_required_text(
                updates["job_title"],
                "Job title is required.",
            )

        if "department" in updates:
            employee.department = self._normalize_required_text(
                updates["department"],
                "Department is required.",
            )

        if "manager_id" in updates:
            manager = self._resolve_manager(session, updates["manager_id"])
            if manager is not None and manager.id == employee.id:
                raise ValidationError("An employee cannot be their own manager.")
            employee.manager_id = manager.id if manager is not None else None

        if "user_id" in updates:
            self._resolve_user(session, updates["user_id"])
            self._ensure_user_is_available(
                session,
                updates["user_id"],
                exclude_employee_id=employee.id,
            )
            employee.user_id = updates["user_id"]

        if "is_active" in updates:
            employee.is_active = updates["is_active"]

        session.add(employee)
        session.commit()
        session.refresh(employee)
        session.refresh(employee, attribute_names=["manager"])
        return EmployeeResponse.from_employee(employee)

    def archive_employee(
        self,
        session: Session,
        current_user: User,
        employee_id: int,
    ) -> EmployeeResponse:
        self.access_service.assert_can_manage_employee_directory(current_user)

        employee = self._get_employee(session, employee_id)
        employee.is_active = False
        session.add(employee)
        session.commit()
        session.refresh(employee)
        session.refresh(employee, attribute_names=["manager"])
        return EmployeeResponse.from_employee(employee)

    def _get_employee(self, session: Session, employee_id: int) -> Employee:
        statement = (
            select(Employee)
            .options(selectinload(Employee.manager))
            .where(Employee.id == employee_id)
        )
        employee = session.scalar(statement)
        if employee is None:
            raise NotFoundError("Employee not found.")
        return employee

    def _resolve_manager(self, session: Session, manager_id: int | None) -> Employee | None:
        if manager_id is None:
            return None

        manager = session.get(Employee, manager_id)
        if manager is None:
            raise ValidationError("Manager employee was not found.")
        return manager

    def _resolve_user(self, session: Session, user_id: int | None) -> User | None:
        if user_id is None:
            return None

        user = session.get(User, user_id)
        if user is None:
            raise ValidationError("Linked user was not found.")
        return user

    def _ensure_employee_number_is_unique(
        self,
        session: Session,
        employee_number: str,
        exclude_employee_id: int | None = None,
    ) -> None:
        statement = select(Employee).where(Employee.employee_number == employee_number)
        employee = session.scalar(statement)
        if employee is None:
            return

        if exclude_employee_id is not None and employee.id == exclude_employee_id:
            return

        raise ValidationError("Employee number already exists.")

    def _ensure_user_is_available(
        self,
        session: Session,
        user_id: int | None,
        exclude_employee_id: int | None = None,
    ) -> None:
        if user_id is None:
            return

        statement = select(Employee).where(Employee.user_id == user_id)
        employee = session.scalar(statement)
        if employee is None:
            return

        if exclude_employee_id is not None and employee.id == exclude_employee_id:
            return

        raise ValidationError("That user is already linked to another employee.")

    def _normalize_required_text(self, value: str, error_message: str) -> str:
        normalized = value.strip()
        if not normalized:
            raise ValidationError(error_message)
        return normalized

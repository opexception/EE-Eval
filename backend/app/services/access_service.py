from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.employee import Employee
from app.models.role import RoleName
from app.models.user import User
from app.services.errors import AuthorizationError


class AccessService:
    def can_manage_employee_directory(self, current_user: User) -> bool:
        return RoleName.HR_ADMIN.value in current_user.role_names

    def can_manage_review_cycles(self, current_user: User) -> bool:
        return RoleName.HR_ADMIN.value in current_user.role_names

    def can_view_employees(self, current_user: User) -> bool:
        if RoleName.HR_ADMIN.value in current_user.role_names:
            return True

        if RoleName.EXECUTIVE.value in current_user.role_names:
            return True

        return bool(
            current_user.role_names.intersection(
                {
                    RoleName.EMPLOYEE.value,
                    RoleName.PEOPLE_MANAGER.value,
                    RoleName.UPPER_MANAGER.value,
                }
            )
        )

    def can_view_evaluations(self, current_user: User) -> bool:
        return bool(
            current_user.role_names.intersection(
                {
                    RoleName.HR_ADMIN.value,
                    RoleName.PEOPLE_MANAGER.value,
                    RoleName.UPPER_MANAGER.value,
                    RoleName.EXECUTIVE.value,
                }
            )
        )

    def can_manage_evaluations(self, current_user: User) -> bool:
        return bool(
            current_user.role_names.intersection(
                {
                    RoleName.HR_ADMIN.value,
                    RoleName.PEOPLE_MANAGER.value,
                }
            )
        )

    def get_linked_employee(self, session: Session, current_user: User) -> Employee | None:
        statement = select(Employee).where(Employee.user_id == current_user.id)
        return session.scalar(statement)

    def get_visible_employee_ids(
        self,
        session: Session,
        current_user: User,
    ) -> set[int]:
        if RoleName.HR_ADMIN.value in current_user.role_names:
            return set(session.scalars(select(Employee.id)).all())

        if RoleName.EXECUTIVE.value in current_user.role_names:
            return set(session.scalars(select(Employee.id)).all())

        linked_employee = self.get_linked_employee(session, current_user)
        if linked_employee is None:
            raise AuthorizationError(
                "The current account is not linked to an employee profile."
            )

        visible_ids = {linked_employee.id}
        if not current_user.role_names.intersection(
            {
                RoleName.PEOPLE_MANAGER.value,
                RoleName.UPPER_MANAGER.value,
            }
        ):
            return visible_ids

        employee_rows = session.execute(select(Employee.id, Employee.manager_id)).all()
        children_by_manager: dict[int, list[int]] = {}
        for employee_id, manager_id in employee_rows:
            if manager_id is None:
                continue
            children_by_manager.setdefault(manager_id, []).append(employee_id)

        stack = [linked_employee.id]
        while stack:
            manager_id = stack.pop()
            for child_id in children_by_manager.get(manager_id, []):
                if child_id in visible_ids:
                    continue
                visible_ids.add(child_id)
                stack.append(child_id)

        return visible_ids

    def assert_can_view_employee(
        self,
        session: Session,
        current_user: User,
        employee: Employee,
    ) -> None:
        if not self.can_view_employees(current_user):
            raise AuthorizationError("You do not have permission to view employee profiles.")

        if employee.id not in self.get_visible_employee_ids(session, current_user):
            raise AuthorizationError("You do not have permission to view this employee.")

    def assert_can_manage_employee_directory(self, current_user: User) -> None:
        if not self.can_manage_employee_directory(current_user):
            raise AuthorizationError(
                "You do not have permission to manage employee profiles."
            )

    def assert_can_manage_review_cycles(self, current_user: User) -> None:
        if not self.can_manage_review_cycles(current_user):
            raise AuthorizationError(
                "You do not have permission to manage review cycles."
            )

    def assert_can_view_evaluation_employee(
        self,
        session: Session,
        current_user: User,
        employee: Employee,
    ) -> None:
        if not self.can_view_evaluations(current_user):
            raise AuthorizationError("You do not have permission to view evaluations.")

        if RoleName.HR_ADMIN.value in current_user.role_names:
            return

        if RoleName.EXECUTIVE.value in current_user.role_names:
            return

        if employee.id not in self.get_visible_employee_ids(session, current_user):
            raise AuthorizationError("You do not have permission to view this evaluation.")

    def assert_can_manage_evaluation_employee(
        self,
        session: Session,
        current_user: User,
        employee: Employee,
    ) -> None:
        if RoleName.HR_ADMIN.value in current_user.role_names:
            return

        if RoleName.PEOPLE_MANAGER.value not in current_user.role_names:
            raise AuthorizationError("You do not have permission to manage evaluations.")

        visible_ids = self.get_visible_employee_ids(session, current_user)
        linked_employee = self.get_linked_employee(session, current_user)
        if linked_employee is None:
            raise AuthorizationError(
                "The current account is not linked to an employee profile."
            )

        if employee.id == linked_employee.id or employee.id not in visible_ids:
            raise AuthorizationError("You do not have permission to manage this evaluation.")

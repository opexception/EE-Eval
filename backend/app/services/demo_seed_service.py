from dataclasses import dataclass
from datetime import date
from decimal import Decimal

from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.auth.passwords import PasswordService
from app.core.config import get_settings
from app.models.employee import Employee
from app.models.evaluation import Evaluation, EvaluationStatus
from app.models.review_cycle import ReviewCycle, ReviewCycleStatus, ReviewCycleType
from app.models.role import Role, RoleName
from app.models.user import AuthProvider, User
from app.models.user_role import UserRole


@dataclass(frozen=True)
class DemoUserSeed:
    username: str
    full_name: str
    role_names: tuple[RoleName, ...]


@dataclass(frozen=True)
class DemoEmployeeSeed:
    employee_number: str
    first_name: str
    last_name: str
    job_title: str
    department: str
    linked_username: str | None
    manager_employee_number: str | None


@dataclass(frozen=True)
class DemoReviewCycleSeed:
    name: str
    cycle_type: ReviewCycleType
    start_date: date
    end_date: date
    status: ReviewCycleStatus


@dataclass(frozen=True)
class DemoEvaluationSeed:
    employee_number: str
    review_cycle_name: str
    author_username: str
    performance_rating: Decimal
    potential_rating: int
    summary_comment: str
    status: EvaluationStatus


@dataclass(frozen=True)
class DemoSeedResult:
    users: int
    employees: int
    review_cycles: int
    evaluations: int


ROLE_DEFINITIONS: dict[RoleName, tuple[str, str]] = {
    RoleName.EMPLOYEE: (
        "Employee",
        "Basic employee access for future self-service workflows.",
    ),
    RoleName.PEOPLE_MANAGER: (
        "People Manager",
        "Manager access for direct reports and team workflows.",
    ),
    RoleName.UPPER_MANAGER: (
        "Upper Manager",
        "Second-line manager access for review and approval workflows.",
    ),
    RoleName.EXECUTIVE: (
        "Executive",
        "Senior leadership access for calibration and summary review.",
    ),
    RoleName.HR_ADMIN: (
        "HR Administrator",
        "Broad HR access for sensitive administrative workflows.",
    ),
    RoleName.SYSTEM_ADMIN: (
        "System Administrator",
        "Operational administration without implied HR content access.",
    ),
}

DEMO_USERS: tuple[DemoUserSeed, ...] = (
    DemoUserSeed("employee.taylor", "Taylor Brooks", (RoleName.EMPLOYEE,)),
    DemoUserSeed("manager.avery", "Avery Jordan", (RoleName.PEOPLE_MANAGER,)),
    DemoUserSeed("upper.lee", "Lee Sutton", (RoleName.UPPER_MANAGER,)),
    DemoUserSeed("executive.morgan", "Morgan Hale", (RoleName.EXECUTIVE,)),
    DemoUserSeed("hr.harper", "Harper Quinn", (RoleName.HR_ADMIN,)),
    DemoUserSeed("it.rowan", "Rowan Pike", (RoleName.SYSTEM_ADMIN,)),
)

DEMO_EMPLOYEES: tuple[DemoEmployeeSeed, ...] = (
    DemoEmployeeSeed(
        employee_number="EMP-1000",
        first_name="Morgan",
        last_name="Hale",
        job_title="Chief Executive Officer",
        department="Executive",
        linked_username="executive.morgan",
        manager_employee_number=None,
    ),
    DemoEmployeeSeed(
        employee_number="EMP-1100",
        first_name="Lee",
        last_name="Sutton",
        job_title="Director of Engineering",
        department="Product Engineering",
        linked_username="upper.lee",
        manager_employee_number="EMP-1000",
    ),
    DemoEmployeeSeed(
        employee_number="EMP-1200",
        first_name="Avery",
        last_name="Jordan",
        job_title="Engineering Manager",
        department="Product Engineering",
        linked_username="manager.avery",
        manager_employee_number="EMP-1100",
    ),
    DemoEmployeeSeed(
        employee_number="EMP-1300",
        first_name="Taylor",
        last_name="Brooks",
        job_title="Senior Software Engineer",
        department="Product Engineering",
        linked_username="employee.taylor",
        manager_employee_number="EMP-1200",
    ),
    DemoEmployeeSeed(
        employee_number="EMP-1310",
        first_name="Jordan",
        last_name="Rivera",
        job_title="Product Designer",
        department="Product Design",
        linked_username=None,
        manager_employee_number="EMP-1200",
    ),
    DemoEmployeeSeed(
        employee_number="EMP-9000",
        first_name="Harper",
        last_name="Quinn",
        job_title="HR Administrator",
        department="People Operations",
        linked_username="hr.harper",
        manager_employee_number=None,
    ),
    DemoEmployeeSeed(
        employee_number="EMP-9100",
        first_name="Rowan",
        last_name="Pike",
        job_title="Systems Administrator",
        department="Information Technology",
        linked_username="it.rowan",
        manager_employee_number=None,
    ),
)

DEMO_REVIEW_CYCLES: tuple[DemoReviewCycleSeed, ...] = (
    DemoReviewCycleSeed(
        name="2025 Annual Review",
        cycle_type=ReviewCycleType.ANNUAL,
        start_date=date(2025, 1, 1),
        end_date=date(2025, 12, 31),
        status=ReviewCycleStatus.CLOSED,
    ),
    DemoReviewCycleSeed(
        name="2026 Annual Review",
        cycle_type=ReviewCycleType.ANNUAL,
        start_date=date(2026, 1, 1),
        end_date=date(2026, 12, 31),
        status=ReviewCycleStatus.ACTIVE,
    ),
    DemoReviewCycleSeed(
        name="2026 Midyear Check-In",
        cycle_type=ReviewCycleType.AD_HOC,
        start_date=date(2026, 4, 1),
        end_date=date(2026, 6, 30),
        status=ReviewCycleStatus.DRAFT,
    ),
)

DEMO_EVALUATIONS: tuple[DemoEvaluationSeed, ...] = (
    DemoEvaluationSeed(
        employee_number="EMP-1200",
        review_cycle_name="2025 Annual Review",
        author_username="upper.lee",
        performance_rating=Decimal("3.85"),
        potential_rating=2,
        summary_comment=(
            "Avery maintained strong delivery leadership and helped steady team planning during a busy year."
        ),
        status=EvaluationStatus.SUBMITTED,
    ),
    DemoEvaluationSeed(
        employee_number="EMP-1300",
        review_cycle_name="2025 Annual Review",
        author_username="manager.avery",
        performance_rating=Decimal("3.65"),
        potential_rating=2,
        summary_comment=(
            "Taylor consistently delivered reliable work and showed stronger cross-team communication by year end."
        ),
        status=EvaluationStatus.SUBMITTED,
    ),
    DemoEvaluationSeed(
        employee_number="EMP-1300",
        review_cycle_name="2026 Annual Review",
        author_username="manager.avery",
        performance_rating=Decimal("3.90"),
        potential_rating=3,
        summary_comment=(
            "Taylor is tracking above expectations early in the cycle and is taking on more mentoring work."
        ),
        status=EvaluationStatus.DRAFT,
    ),
    DemoEvaluationSeed(
        employee_number="EMP-1310",
        review_cycle_name="2026 Midyear Check-In",
        author_username="manager.avery",
        performance_rating=Decimal("3.40"),
        potential_rating=2,
        summary_comment=(
            "Jordan is building confidence in stakeholder facilitation and has kept design work well organized."
        ),
        status=EvaluationStatus.DRAFT,
    ),
)


class DemoSeedService:
    def __init__(self, password_service: PasswordService | None = None) -> None:
        self.password_service = password_service or PasswordService()

    def seed(self, session: Session) -> DemoSeedResult:
        settings = get_settings()
        if settings.environment != "development" or not settings.demo_seed.enabled:
            raise RuntimeError(
                "Demo data seeding is available only in development when EE_EVAL_SEED_DEMO_USERS is enabled."
            )

        roles_by_name = self._ensure_roles(session)
        users_by_username = self._ensure_users(
            session,
            roles_by_name,
            settings.demo_seed.password,
        )
        employees_by_number = self._ensure_employees(session, users_by_username)
        review_cycles_by_name = self._ensure_review_cycles(session, users_by_username)
        self._ensure_evaluations(
            session,
            users_by_username,
            employees_by_number,
            review_cycles_by_name,
        )

        session.commit()
        return DemoSeedResult(
            users=len(DEMO_USERS),
            employees=len(DEMO_EMPLOYEES),
            review_cycles=len(DEMO_REVIEW_CYCLES),
            evaluations=len(DEMO_EVALUATIONS),
        )

    def _ensure_roles(self, session: Session) -> dict[str, Role]:
        roles_by_name: dict[str, Role] = {}
        for role_name, (display_name, description) in ROLE_DEFINITIONS.items():
            role = session.scalar(select(Role).where(Role.name == role_name.value))
            if role is None:
                role = Role(
                    name=role_name.value,
                    display_name=display_name,
                    description=description,
                )
                session.add(role)
                session.flush()

            roles_by_name[role_name.value] = role

        return roles_by_name

    def _ensure_users(
        self,
        session: Session,
        roles_by_name: dict[str, Role],
        demo_password: str,
    ) -> dict[str, User]:
        users_by_username: dict[str, User] = {}
        for demo_user in DEMO_USERS:
            statement = (
                select(User)
                .options(selectinload(User.user_roles).selectinload(UserRole.role))
                .where(User.username == demo_user.username)
            )
            user = session.scalar(statement)
            if user is None:
                user = User(
                    username=demo_user.username,
                    full_name=demo_user.full_name,
                    auth_provider=AuthProvider.LOCAL.value,
                    is_active=True,
                )
                session.add(user)
                session.flush()

            user.full_name = demo_user.full_name
            user.auth_provider = AuthProvider.LOCAL.value
            user.is_active = True
            user.password_hash = self.password_service.hash_password(demo_password)
            user.failed_login_attempts = 0
            user.locked_until = None
            user.user_roles.clear()
            user.user_roles.extend(
                UserRole(role=roles_by_name[role_name.value])
                for role_name in demo_user.role_names
            )
            session.add(user)
            session.flush()
            users_by_username[demo_user.username] = user

        return users_by_username

    def _ensure_employees(
        self,
        session: Session,
        users_by_username: dict[str, User],
    ) -> dict[str, Employee]:
        employees_by_number: dict[str, Employee] = {}

        for demo_employee in DEMO_EMPLOYEES:
            statement = select(Employee).where(
                Employee.employee_number == demo_employee.employee_number
            )
            employee = session.scalar(statement)
            linked_user = None
            if demo_employee.linked_username is not None:
                linked_user = users_by_username[demo_employee.linked_username]

            if employee is None:
                employee = Employee(
                    employee_number=demo_employee.employee_number,
                    first_name=demo_employee.first_name,
                    last_name=demo_employee.last_name,
                    job_title=demo_employee.job_title,
                    department=demo_employee.department,
                    user_id=linked_user.id if linked_user is not None else None,
                    is_active=True,
                )
                session.add(employee)
                session.flush()
                employees_by_number[demo_employee.employee_number] = employee
                continue

            employee.first_name = demo_employee.first_name
            employee.last_name = demo_employee.last_name
            employee.job_title = demo_employee.job_title
            employee.department = demo_employee.department
            employee.user_id = linked_user.id if linked_user is not None else None
            employee.is_active = True
            session.add(employee)
            session.flush()
            employees_by_number[demo_employee.employee_number] = employee

        for demo_employee in DEMO_EMPLOYEES:
            employee = employees_by_number[demo_employee.employee_number]
            if demo_employee.manager_employee_number is None:
                employee.manager_id = None
            else:
                employee.manager_id = employees_by_number[
                    demo_employee.manager_employee_number
                ].id
            session.add(employee)

        session.flush()
        return employees_by_number

    def _ensure_review_cycles(
        self,
        session: Session,
        users_by_username: dict[str, User],
    ) -> dict[str, ReviewCycle]:
        review_cycles_by_name: dict[str, ReviewCycle] = {}
        hr_user = users_by_username["hr.harper"]

        for demo_review_cycle in DEMO_REVIEW_CYCLES:
            statement = select(ReviewCycle).where(
                ReviewCycle.name == demo_review_cycle.name
            )
            review_cycle = session.scalar(statement)
            if review_cycle is None:
                review_cycle = ReviewCycle(
                    name=demo_review_cycle.name,
                    cycle_type=demo_review_cycle.cycle_type.value,
                    start_date=demo_review_cycle.start_date,
                    end_date=demo_review_cycle.end_date,
                    status=demo_review_cycle.status.value,
                    created_by_user_id=hr_user.id,
                    updated_by_user_id=hr_user.id,
                )
                session.add(review_cycle)
                session.flush()
                review_cycles_by_name[demo_review_cycle.name] = review_cycle
                continue

            review_cycle.cycle_type = demo_review_cycle.cycle_type.value
            review_cycle.start_date = demo_review_cycle.start_date
            review_cycle.end_date = demo_review_cycle.end_date
            review_cycle.status = demo_review_cycle.status.value
            review_cycle.updated_by_user_id = hr_user.id
            session.add(review_cycle)
            session.flush()
            review_cycles_by_name[demo_review_cycle.name] = review_cycle

        return review_cycles_by_name

    def _ensure_evaluations(
        self,
        session: Session,
        users_by_username: dict[str, User],
        employees_by_number: dict[str, Employee],
        review_cycles_by_name: dict[str, ReviewCycle],
    ) -> None:
        for demo_evaluation in DEMO_EVALUATIONS:
            employee = employees_by_number[demo_evaluation.employee_number]
            review_cycle = review_cycles_by_name[demo_evaluation.review_cycle_name]
            author = users_by_username[demo_evaluation.author_username]
            statement = select(Evaluation).where(
                Evaluation.employee_id == employee.id,
                Evaluation.review_cycle_id == review_cycle.id,
            )
            evaluation = session.scalar(statement)
            if evaluation is None:
                evaluation = Evaluation(
                    employee_id=employee.id,
                    review_cycle_id=review_cycle.id,
                    author_user_id=author.id,
                    updated_by_user_id=author.id,
                    performance_rating=demo_evaluation.performance_rating,
                    potential_rating=demo_evaluation.potential_rating,
                    summary_comment=demo_evaluation.summary_comment,
                    status=demo_evaluation.status.value,
                )
                session.add(evaluation)
                session.flush()
                continue

            evaluation.author_user_id = author.id
            evaluation.updated_by_user_id = author.id
            evaluation.performance_rating = demo_evaluation.performance_rating
            evaluation.potential_rating = demo_evaluation.potential_rating
            evaluation.summary_comment = demo_evaluation.summary_comment
            evaluation.status = demo_evaluation.status.value
            session.add(evaluation)

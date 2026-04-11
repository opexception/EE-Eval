from datetime import date
from dataclasses import dataclass
from pathlib import Path
import sys

import pytest
from sqlalchemy import create_engine, event
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

BACKEND_DIR = Path(__file__).resolve().parents[1]
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

from app.core.config import get_settings
from app.db.session import get_engine, get_session_factory
from app.models import Base, Role, RoleName, User, UserRole
from app.models.employee import Employee
from app.models.evaluation import Evaluation, EvaluationStatus
from app.models.review_cycle import ReviewCycle, ReviewCycleStatus, ReviewCycleType
from app.models.user import AuthProvider
from app.services.nine_box_service import NineBoxService


@pytest.fixture(autouse=True)
def clear_cached_settings() -> None:
    get_settings.cache_clear()
    get_engine.cache_clear()
    get_session_factory.cache_clear()
    yield
    get_settings.cache_clear()
    get_engine.cache_clear()
    get_session_factory.cache_clear()


@pytest.fixture()
def db_session() -> Session:
    engine = create_engine(
        "sqlite+pysqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )

    @event.listens_for(engine, "connect")
    def set_sqlite_pragma(dbapi_connection, connection_record) -> None:
        del connection_record
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()

    Base.metadata.create_all(engine)
    session_factory = sessionmaker(
        bind=engine,
        autoflush=False,
        autocommit=False,
        class_=Session,
        expire_on_commit=False,
    )

    with session_factory() as session:
        yield session

    Base.metadata.drop_all(engine)
    engine.dispose()


@dataclass
class DomainContext:
    hr_user: User
    executive_user: User
    upper_manager_user: User
    manager_user: User
    employee_user: User
    outsider_manager_user: User
    system_admin_user: User
    executive_employee: Employee
    upper_manager_employee: Employee
    manager_employee: Employee
    employee_record: Employee
    peer_employee: Employee
    hr_employee: Employee
    system_admin_employee: Employee
    outsider_manager_employee: Employee
    active_review_cycle: ReviewCycle
    archived_review_cycle: ReviewCycle
    employee_evaluation: Evaluation


@pytest.fixture()
def domain_context(db_session: Session) -> DomainContext:
    roles = {
        role_name.value: Role(
            name=role_name.value,
            display_name=role_name.value.replace("_", " ").title(),
            description=f"Test role for {role_name.value}.",
        )
        for role_name in RoleName
    }
    db_session.add_all(roles.values())
    db_session.flush()

    def create_user(username: str, full_name: str, role_names: tuple[RoleName, ...]) -> User:
        user = User(
            username=username,
            full_name=full_name,
            auth_provider=AuthProvider.LOCAL.value,
            password_hash="fake-hash",
            is_active=True,
        )
        user.user_roles.extend(UserRole(role=roles[role_name.value]) for role_name in role_names)
        db_session.add(user)
        db_session.flush()
        return user

    executive_user = create_user(
        "executive.morgan",
        "Morgan Hale",
        (RoleName.EXECUTIVE,),
    )
    upper_manager_user = create_user(
        "upper.lee",
        "Lee Sutton",
        (RoleName.UPPER_MANAGER,),
    )
    manager_user = create_user(
        "manager.avery",
        "Avery Jordan",
        (RoleName.PEOPLE_MANAGER,),
    )
    employee_user = create_user(
        "employee.taylor",
        "Taylor Brooks",
        (RoleName.EMPLOYEE,),
    )
    hr_user = create_user(
        "hr.harper",
        "Harper Quinn",
        (RoleName.HR_ADMIN,),
    )
    outsider_manager_user = create_user(
        "manager.casey",
        "Casey Monroe",
        (RoleName.PEOPLE_MANAGER,),
    )
    system_admin_user = create_user(
        "it.rowan",
        "Rowan Pike",
        (RoleName.SYSTEM_ADMIN,),
    )

    executive_employee = Employee(
        employee_number="EMP-1000",
        first_name="Morgan",
        last_name="Hale",
        job_title="Chief Executive Officer",
        department="Executive",
        user_id=executive_user.id,
        is_active=True,
    )
    upper_manager_employee = Employee(
        employee_number="EMP-1100",
        first_name="Lee",
        last_name="Sutton",
        job_title="Director of Engineering",
        department="Product Engineering",
        user_id=upper_manager_user.id,
        manager=executive_employee,
        is_active=True,
    )
    manager_employee = Employee(
        employee_number="EMP-1200",
        first_name="Avery",
        last_name="Jordan",
        job_title="Engineering Manager",
        department="Product Engineering",
        user_id=manager_user.id,
        manager=upper_manager_employee,
        is_active=True,
    )
    employee_record = Employee(
        employee_number="EMP-1300",
        first_name="Taylor",
        last_name="Brooks",
        job_title="Senior Software Engineer",
        department="Product Engineering",
        user_id=employee_user.id,
        manager=manager_employee,
        is_active=True,
    )
    peer_employee = Employee(
        employee_number="EMP-1310",
        first_name="Jordan",
        last_name="Rivera",
        job_title="Product Designer",
        department="Product Design",
        manager=manager_employee,
        is_active=True,
    )
    hr_employee = Employee(
        employee_number="EMP-9000",
        first_name="Harper",
        last_name="Quinn",
        job_title="HR Administrator",
        department="People Operations",
        user_id=hr_user.id,
        is_active=True,
    )
    system_admin_employee = Employee(
        employee_number="EMP-9100",
        first_name="Rowan",
        last_name="Pike",
        job_title="Systems Administrator",
        department="Information Technology",
        user_id=system_admin_user.id,
        is_active=True,
    )
    outsider_manager_employee = Employee(
        employee_number="EMP-9200",
        first_name="Casey",
        last_name="Monroe",
        job_title="Sales Manager",
        department="Sales",
        user_id=outsider_manager_user.id,
        is_active=True,
    )

    db_session.add_all(
        [
            executive_employee,
            upper_manager_employee,
            manager_employee,
            employee_record,
            peer_employee,
            hr_employee,
            system_admin_employee,
            outsider_manager_employee,
        ]
    )
    db_session.flush()

    active_review_cycle = ReviewCycle(
        name="2026 Annual Review",
        cycle_type=ReviewCycleType.ANNUAL.value,
        start_date=date(2026, 1, 1),
        end_date=date(2026, 12, 31),
        status=ReviewCycleStatus.ACTIVE.value,
        created_by_user_id=hr_user.id,
        updated_by_user_id=hr_user.id,
    )
    archived_review_cycle = ReviewCycle(
        name="2025 Annual Review",
        cycle_type=ReviewCycleType.ANNUAL.value,
        start_date=date(2025, 1, 1),
        end_date=date(2025, 12, 31),
        status=ReviewCycleStatus.ARCHIVED.value,
        created_by_user_id=hr_user.id,
        updated_by_user_id=hr_user.id,
    )
    db_session.add_all([active_review_cycle, archived_review_cycle])
    db_session.flush()

    placement_snapshot = NineBoxService().build_snapshot(3.70, 2)

    employee_evaluation = Evaluation(
        employee_id=employee_record.id,
        review_cycle_id=active_review_cycle.id,
        author_user_id=manager_user.id,
        updated_by_user_id=manager_user.id,
        performance_rating=3.70,
        potential_rating=2,
        performance_tier=placement_snapshot.performance_tier,
        potential_tier=placement_snapshot.potential_tier,
        nine_box_code=placement_snapshot.nine_box_code,
        nine_box_label=placement_snapshot.nine_box_label,
        summary_comment="Taylor is trending upward and taking on more mentoring work.",
        manager_rationale=(
            "Taylor has become much more dependable in ambiguous projects and is beginning to mentor newer engineers."
        ),
        promotion_recommendation="future_consideration",
        promotion_rationale=(
            "Taylor is moving toward the next level, but one more cycle of consistent cross-team leadership would help."
        ),
        status=EvaluationStatus.DRAFT.value,
    )
    db_session.add(employee_evaluation)
    db_session.commit()

    return DomainContext(
        hr_user=hr_user,
        executive_user=executive_user,
        upper_manager_user=upper_manager_user,
        manager_user=manager_user,
        employee_user=employee_user,
        outsider_manager_user=outsider_manager_user,
        system_admin_user=system_admin_user,
        executive_employee=executive_employee,
        upper_manager_employee=upper_manager_employee,
        manager_employee=manager_employee,
        employee_record=employee_record,
        peer_employee=peer_employee,
        hr_employee=hr_employee,
        system_admin_employee=system_admin_employee,
        outsider_manager_employee=outsider_manager_employee,
        active_review_cycle=active_review_cycle,
        archived_review_cycle=archived_review_cycle,
        employee_evaluation=employee_evaluation,
    )

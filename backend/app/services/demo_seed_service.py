from dataclasses import dataclass

from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.auth.passwords import PasswordService
from app.core.config import get_settings
from app.models.role import Role, RoleName
from app.models.user import AuthProvider, User
from app.models.user_role import UserRole


@dataclass(frozen=True)
class DemoUserSeed:
    username: str
    full_name: str
    role_names: tuple[RoleName, ...]


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


class DemoSeedService:
    def __init__(self, password_service: PasswordService | None = None) -> None:
        self.password_service = password_service or PasswordService()

    def seed(self, session: Session) -> int:
        settings = get_settings()
        if settings.environment != "development" or not settings.demo_seed.enabled:
            raise RuntimeError(
                "Demo user seeding is available only in development when EE_EVAL_SEED_DEMO_USERS is enabled."
            )

        roles_by_name = self._ensure_roles(session)
        for demo_user in DEMO_USERS:
            self._upsert_demo_user(
                session,
                demo_user,
                roles_by_name,
                settings.demo_seed.password,
            )

        session.commit()
        return len(DEMO_USERS)

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

    def _upsert_demo_user(
        self,
        session: Session,
        demo_user: DemoUserSeed,
        roles_by_name: dict[str, Role],
        demo_password: str,
    ) -> None:
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

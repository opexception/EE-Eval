from datetime import UTC, datetime, timedelta

from jwt import InvalidTokenError
from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.auth.passwords import PasswordService
from app.auth.tokens import TokenService
from app.core.config import get_settings
from app.models.user import AuthProvider, User
from app.models.user_role import UserRole
from app.schemas.auth import AuthTokenResponse
from app.schemas.user import CurrentUserResponse


class AuthenticationError(Exception):
    pass


class AuthService:
    def __init__(
        self,
        password_service: PasswordService | None = None,
        token_service: TokenService | None = None,
    ) -> None:
        self.password_service = password_service or PasswordService()
        self.token_service = token_service or TokenService()

    def login(
        self,
        session: Session,
        username: str,
        password: str,
    ) -> AuthTokenResponse:
        user = self._get_user_by_username(session, username)
        now = datetime.now(UTC)

        if (
            user is None
            or not user.is_active
            or user.auth_provider != AuthProvider.LOCAL.value
            or user.password_hash is None
            or user.is_locked(now)
        ):
            raise AuthenticationError("Invalid username or password.")

        if not self.password_service.verify_password(password, user.password_hash):
            self._record_failed_login(session, user, now)
            raise AuthenticationError("Invalid username or password.")

        self._record_successful_login(session, user, now)
        access_token = self.token_service.create_access_token(str(user.id))
        return AuthTokenResponse(
            access_token=access_token.value,
            expires_in_seconds=access_token.expires_in_seconds,
        )

    def get_current_user(self, session: Session, token: str) -> User:
        try:
            user_id = int(self.token_service.decode_access_token(token))
        except (InvalidTokenError, ValueError) as exc:
            raise AuthenticationError("Authentication required.") from exc

        user = self._get_user_by_id(session, user_id)
        if user is None or not user.is_active:
            raise AuthenticationError("Authentication required.")

        return user

    def build_current_user_response(self, user: User) -> CurrentUserResponse:
        return CurrentUserResponse.from_user(user)

    def _record_failed_login(
        self,
        session: Session,
        user: User,
        now: datetime,
    ) -> None:
        settings = get_settings()
        user.failed_login_attempts += 1
        if user.failed_login_attempts >= settings.auth.max_failed_login_attempts:
            user.locked_until = now + timedelta(minutes=settings.auth.lockout_minutes)
        session.add(user)
        session.commit()

    def _record_successful_login(
        self,
        session: Session,
        user: User,
        now: datetime,
    ) -> None:
        user.failed_login_attempts = 0
        user.locked_until = None
        user.last_login_at = now
        session.add(user)
        session.commit()

    def _get_user_by_id(self, session: Session, user_id: int) -> User | None:
        statement = (
            select(User)
            .options(selectinload(User.user_roles).selectinload(UserRole.role))
            .where(User.id == user_id)
        )
        return session.scalar(statement)

    def _get_user_by_username(self, session: Session, username: str) -> User | None:
        normalized_username = username.strip().lower()
        if not normalized_username:
            return None

        statement = (
            select(User)
            .options(selectinload(User.user_roles).selectinload(UserRole.role))
            .where(User.username == normalized_username)
        )
        return session.scalar(statement)

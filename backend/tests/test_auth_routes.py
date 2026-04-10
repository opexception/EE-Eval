from types import SimpleNamespace

import pytest
from fastapi import HTTPException

from app.api.routes.auth import get_current_user_profile, login
from app.schemas.auth import AuthTokenResponse, LoginRequest
from app.schemas.user import CurrentUserResponse
from app.services.auth_service import AuthenticationError


class StubAuthService:
    def __init__(self, should_fail: bool = False) -> None:
        self.should_fail = should_fail

    def login(
        self,
        session: object,
        username: str,
        password: str,
    ) -> AuthTokenResponse:
        if self.should_fail:
            raise AuthenticationError("Invalid username or password.")

        return AuthTokenResponse(
            access_token="test-token",
            expires_in_seconds=3600,
        )

    def build_current_user_response(self, user: object) -> CurrentUserResponse:
        return CurrentUserResponse(
            id=1,
            username="hr.harper",
            full_name="Harper Quinn",
            auth_provider="local",
            roles=["hr_admin"],
            is_active=True,
        )


def test_login_route_returns_access_token() -> None:
    response = login(
        credentials=LoginRequest(
            username="hr.harper",
            password="DemoPass123!ChangeMe",
        ),
        session=object(),
        service=StubAuthService(),
    )

    assert response.model_dump() == {
        "access_token": "test-token",
        "token_type": "bearer",
        "expires_in_seconds": 3600,
    }


def test_login_route_returns_401_for_invalid_credentials() -> None:
    with pytest.raises(HTTPException) as exc_info:
        login(
            credentials=LoginRequest(
                username="hr.harper",
                password="wrong-password",
            ),
            session=object(),
            service=StubAuthService(should_fail=True),
        )

    assert exc_info.value.status_code == 401
    assert exc_info.value.detail == "Invalid username or password."


def test_current_user_route_returns_authenticated_user() -> None:
    response = get_current_user_profile(
        current_user=SimpleNamespace(),
        service=StubAuthService(),
    )

    assert response.model_dump() == {
        "id": 1,
        "username": "hr.harper",
        "full_name": "Harper Quinn",
        "auth_provider": "local",
        "roles": ["hr_admin"],
        "is_active": True,
    }

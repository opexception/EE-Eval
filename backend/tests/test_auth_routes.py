from types import SimpleNamespace

from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.auth.deps import get_auth_service, get_current_user
from app.schemas.auth import AuthTokenResponse
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


def test_login_route_returns_access_token(
    app: FastAPI,
    client: TestClient,
) -> None:
    app.dependency_overrides[get_auth_service] = lambda: StubAuthService()

    response = client.post(
        "/api/auth/login",
        json={"username": "hr.harper", "password": "DemoPass123!ChangeMe"},
    )

    assert response.status_code == 200
    assert response.json() == {
        "access_token": "test-token",
        "token_type": "bearer",
        "expires_in_seconds": 3600,
    }


def test_login_route_returns_401_for_invalid_credentials(
    app: FastAPI,
    client: TestClient,
) -> None:
    app.dependency_overrides[get_auth_service] = lambda: StubAuthService(
        should_fail=True
    )

    response = client.post(
        "/api/auth/login",
        json={"username": "hr.harper", "password": "wrong-password"},
    )

    assert response.status_code == 401
    assert response.json() == {"detail": "Invalid username or password."}


def test_current_user_route_returns_authenticated_user(
    app: FastAPI,
    client: TestClient,
) -> None:
    app.dependency_overrides[get_auth_service] = lambda: StubAuthService()
    app.dependency_overrides[get_current_user] = lambda: SimpleNamespace()

    response = client.get(
        "/api/auth/me",
        headers={"Authorization": "Bearer test-token"},
    )

    assert response.status_code == 200
    assert response.json() == {
        "id": 1,
        "username": "hr.harper",
        "full_name": "Harper Quinn",
        "auth_provider": "local",
        "roles": ["hr_admin"],
        "is_active": True,
    }


def test_current_user_route_requires_authentication(client: TestClient) -> None:
    response = client.get("/api/auth/me")

    assert response.status_code == 401
    assert response.json() == {"detail": "Authentication required."}


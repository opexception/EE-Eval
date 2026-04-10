from fastapi import APIRouter, HTTPException, status

from app.auth.deps import AuthServiceDep, CurrentUserDep
from app.api.deps import DatabaseSessionDep
from app.schemas.auth import AuthTokenResponse, LoginRequest
from app.schemas.user import CurrentUserResponse
from app.services.auth_service import AuthenticationError

router = APIRouter()


@router.post("/login", response_model=AuthTokenResponse, summary="Log in locally")
def login(
    credentials: LoginRequest,
    session: DatabaseSessionDep,
    service: AuthServiceDep,
) -> AuthTokenResponse:
    try:
        return service.login(session, credentials.username, credentials.password)
    except AuthenticationError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(exc),
        ) from exc


@router.get("/me", response_model=CurrentUserResponse, summary="Current user")
def get_current_user_profile(
    current_user: CurrentUserDep,
    service: AuthServiceDep,
) -> CurrentUserResponse:
    return service.build_current_user_response(current_user)


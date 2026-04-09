from fastapi import APIRouter, Response, status

from app.api.deps import DatabaseSessionDep, HealthServiceDep
from app.schemas.health import LivenessResponse, ReadinessResponse

router = APIRouter()


@router.get("", response_model=LivenessResponse, summary="Application liveness check")
def get_liveness(service: HealthServiceDep) -> LivenessResponse:
    return service.get_liveness()


@router.get(
    "/ready",
    response_model=ReadinessResponse,
    summary="Application readiness check",
)
def get_readiness(
    response: Response,
    session: DatabaseSessionDep,
    service: HealthServiceDep,
) -> ReadinessResponse:
    readiness = service.get_readiness(session)
    if readiness.status != "ok":
        response.status_code = status.HTTP_503_SERVICE_UNAVAILABLE
    return readiness

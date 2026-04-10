from typing import Any

from fastapi import Response, status

from app.api.routes.health import get_liveness, get_readiness
from app.schemas.health import LivenessResponse, ReadinessResponse


class StubHealthService:
    def __init__(self, readiness: ReadinessResponse) -> None:
        self._readiness = readiness

    def get_liveness(self) -> LivenessResponse:
        return LivenessResponse()

    def get_readiness(self, session: Any) -> ReadinessResponse:
        return self._readiness


def test_liveness_endpoint_returns_ok() -> None:
    response = get_liveness(StubHealthService(ReadinessResponse(status="ok", database="ok")))

    assert response.model_dump() == {"status": "ok"}


def test_readiness_endpoint_returns_ok_when_service_reports_ready() -> None:
    response = Response()
    payload = get_readiness(
        response=response,
        session=object(),
        service=StubHealthService(ReadinessResponse(status="ok", database="ok")),
    )

    assert response.status_code == status.HTTP_200_OK
    assert payload.model_dump() == {"status": "ok", "database": "ok"}


def test_readiness_endpoint_returns_503_when_service_reports_not_ready() -> None:
    response = Response()
    payload = get_readiness(
        response=response,
        session=object(),
        service=StubHealthService(
            ReadinessResponse(status="error", database="unavailable")
        ),
    )

    assert response.status_code == status.HTTP_503_SERVICE_UNAVAILABLE
    assert payload.model_dump() == {"status": "error", "database": "unavailable"}

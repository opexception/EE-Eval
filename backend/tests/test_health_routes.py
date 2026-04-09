from collections.abc import Generator
from typing import Any

from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.api.deps import get_db_session, get_health_service
from app.schemas.health import LivenessResponse, ReadinessResponse


class StubHealthService:
    def __init__(self, readiness: ReadinessResponse) -> None:
        self._readiness = readiness

    def get_liveness(self) -> LivenessResponse:
        return LivenessResponse()

    def get_readiness(self, session: Any) -> ReadinessResponse:
        return self._readiness


def _override_db_session() -> Generator[object, None, None]:
    yield object()


def test_liveness_endpoint_returns_ok(client: TestClient) -> None:
    response = client.get("/api/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_readiness_endpoint_returns_ok_when_service_reports_ready(
    app: FastAPI,
    client: TestClient,
) -> None:
    app.dependency_overrides[get_db_session] = _override_db_session
    app.dependency_overrides[get_health_service] = lambda: StubHealthService(
        ReadinessResponse(status="ok", database="ok")
    )

    response = client.get("/api/health/ready")

    assert response.status_code == 200
    assert response.json() == {"status": "ok", "database": "ok"}


def test_readiness_endpoint_returns_503_when_service_reports_not_ready(
    app: FastAPI,
    client: TestClient,
) -> None:
    app.dependency_overrides[get_db_session] = _override_db_session
    app.dependency_overrides[get_health_service] = lambda: StubHealthService(
        ReadinessResponse(status="error", database="unavailable")
    )

    response = client.get("/api/health/ready")

    assert response.status_code == 503
    assert response.json() == {"status": "error", "database": "unavailable"}


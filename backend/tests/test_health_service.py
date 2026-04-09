from sqlalchemy.exc import SQLAlchemyError

from app.services.health_service import HealthService


class HealthySession:
    def execute(self, statement: object) -> int:
        return 1


class BrokenSession:
    def execute(self, statement: object) -> int:
        raise SQLAlchemyError("database unavailable")


def test_health_service_reports_database_ready_when_query_succeeds() -> None:
    service = HealthService()

    result = service.get_readiness(HealthySession())  # type: ignore[arg-type]

    assert result.status == "ok"
    assert result.database == "ok"


def test_health_service_reports_database_unavailable_when_query_fails() -> None:
    service = HealthService()

    result = service.get_readiness(BrokenSession())  # type: ignore[arg-type]

    assert result.status == "error"
    assert result.database == "unavailable"

from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.schemas.health import LivenessResponse, ReadinessResponse


class HealthService:
    def get_liveness(self) -> LivenessResponse:
        return LivenessResponse()

    def get_readiness(self, session: Session) -> ReadinessResponse:
        try:
            session.execute(text("SELECT 1"))
        except SQLAlchemyError:
            return ReadinessResponse(status="error", database="unavailable")

        return ReadinessResponse(status="ok", database="ok")


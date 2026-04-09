from typing import Annotated

from fastapi import Depends
from sqlalchemy.orm import Session

from app.db.session import get_db_session
from app.services.health_service import HealthService


def get_health_service() -> HealthService:
    return HealthService()


DatabaseSessionDep = Annotated[Session, Depends(get_db_session)]
HealthServiceDep = Annotated[HealthService, Depends(get_health_service)]

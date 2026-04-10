from typing import Annotated

from fastapi import Depends
from sqlalchemy.orm import Session

from app.db.session import get_db_session
from app.services.employee_service import EmployeeService
from app.services.evaluation_service import EvaluationService
from app.services.health_service import HealthService
from app.services.review_cycle_service import ReviewCycleService


def get_health_service() -> HealthService:
    return HealthService()


def get_employee_service() -> EmployeeService:
    return EmployeeService()


def get_review_cycle_service() -> ReviewCycleService:
    return ReviewCycleService()


def get_evaluation_service() -> EvaluationService:
    return EvaluationService()


DatabaseSessionDep = Annotated[Session, Depends(get_db_session)]
HealthServiceDep = Annotated[HealthService, Depends(get_health_service)]
EmployeeServiceDep = Annotated[EmployeeService, Depends(get_employee_service)]
ReviewCycleServiceDep = Annotated[
    ReviewCycleService,
    Depends(get_review_cycle_service),
]
EvaluationServiceDep = Annotated[
    EvaluationService,
    Depends(get_evaluation_service),
]

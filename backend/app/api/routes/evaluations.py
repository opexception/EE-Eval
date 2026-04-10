from fastapi import APIRouter

from app.api.deps import DatabaseSessionDep, EvaluationServiceDep
from app.api.errors import to_http_exception
from app.auth.deps import CurrentUserDep
from app.schemas.evaluation import (
    EvaluationCreateRequest,
    EvaluationResponse,
    EvaluationUpdateRequest,
)
from app.services.errors import ServiceError

router = APIRouter()


@router.get(
    "",
    response_model=list[EvaluationResponse],
    summary="List visible evaluations",
)
def list_evaluations(
    current_user: CurrentUserDep,
    session: DatabaseSessionDep,
    service: EvaluationServiceDep,
    employee_id: int | None = None,
    review_cycle_id: int | None = None,
) -> list[EvaluationResponse]:
    try:
        return service.list_evaluations(
            session,
            current_user,
            employee_id=employee_id,
            review_cycle_id=review_cycle_id,
        )
    except ServiceError as exc:
        raise to_http_exception(exc) from exc


@router.post(
    "",
    response_model=EvaluationResponse,
    summary="Create an evaluation",
)
def create_evaluation(
    payload: EvaluationCreateRequest,
    current_user: CurrentUserDep,
    session: DatabaseSessionDep,
    service: EvaluationServiceDep,
) -> EvaluationResponse:
    try:
        return service.create_evaluation(session, current_user, payload)
    except ServiceError as exc:
        raise to_http_exception(exc) from exc


@router.get(
    "/{evaluation_id}",
    response_model=EvaluationResponse,
    summary="Get an evaluation",
)
def get_evaluation(
    evaluation_id: int,
    current_user: CurrentUserDep,
    session: DatabaseSessionDep,
    service: EvaluationServiceDep,
) -> EvaluationResponse:
    try:
        return service.get_evaluation(session, current_user, evaluation_id)
    except ServiceError as exc:
        raise to_http_exception(exc) from exc


@router.put(
    "/{evaluation_id}",
    response_model=EvaluationResponse,
    summary="Update an evaluation",
)
def update_evaluation(
    evaluation_id: int,
    payload: EvaluationUpdateRequest,
    current_user: CurrentUserDep,
    session: DatabaseSessionDep,
    service: EvaluationServiceDep,
) -> EvaluationResponse:
    try:
        return service.update_evaluation(session, current_user, evaluation_id, payload)
    except ServiceError as exc:
        raise to_http_exception(exc) from exc


@router.delete(
    "/{evaluation_id}",
    response_model=EvaluationResponse,
    summary="Archive an evaluation",
)
def archive_evaluation(
    evaluation_id: int,
    current_user: CurrentUserDep,
    session: DatabaseSessionDep,
    service: EvaluationServiceDep,
) -> EvaluationResponse:
    try:
        return service.archive_evaluation(session, current_user, evaluation_id)
    except ServiceError as exc:
        raise to_http_exception(exc) from exc

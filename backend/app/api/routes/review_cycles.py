from fastapi import APIRouter

from app.api.deps import DatabaseSessionDep, ReviewCycleServiceDep
from app.api.errors import to_http_exception
from app.auth.deps import CurrentUserDep
from app.schemas.review_cycle import (
    ReviewCycleCreateRequest,
    ReviewCycleResponse,
    ReviewCycleUpdateRequest,
)
from app.services.errors import ServiceError

router = APIRouter()


@router.get(
    "",
    response_model=list[ReviewCycleResponse],
    summary="List review cycles",
)
def list_review_cycles(
    current_user: CurrentUserDep,
    session: DatabaseSessionDep,
    service: ReviewCycleServiceDep,
) -> list[ReviewCycleResponse]:
    try:
        return service.list_review_cycles(session, current_user)
    except ServiceError as exc:
        raise to_http_exception(exc) from exc


@router.post(
    "",
    response_model=ReviewCycleResponse,
    summary="Create a review cycle",
)
def create_review_cycle(
    payload: ReviewCycleCreateRequest,
    current_user: CurrentUserDep,
    session: DatabaseSessionDep,
    service: ReviewCycleServiceDep,
) -> ReviewCycleResponse:
    try:
        return service.create_review_cycle(session, current_user, payload)
    except ServiceError as exc:
        raise to_http_exception(exc) from exc


@router.get(
    "/{review_cycle_id}",
    response_model=ReviewCycleResponse,
    summary="Get a review cycle",
)
def get_review_cycle(
    review_cycle_id: int,
    current_user: CurrentUserDep,
    session: DatabaseSessionDep,
    service: ReviewCycleServiceDep,
) -> ReviewCycleResponse:
    try:
        return service.get_review_cycle(session, current_user, review_cycle_id)
    except ServiceError as exc:
        raise to_http_exception(exc) from exc


@router.put(
    "/{review_cycle_id}",
    response_model=ReviewCycleResponse,
    summary="Update a review cycle",
)
def update_review_cycle(
    review_cycle_id: int,
    payload: ReviewCycleUpdateRequest,
    current_user: CurrentUserDep,
    session: DatabaseSessionDep,
    service: ReviewCycleServiceDep,
) -> ReviewCycleResponse:
    try:
        return service.update_review_cycle(
            session,
            current_user,
            review_cycle_id,
            payload,
        )
    except ServiceError as exc:
        raise to_http_exception(exc) from exc


@router.delete(
    "/{review_cycle_id}",
    response_model=ReviewCycleResponse,
    summary="Archive a review cycle",
)
def archive_review_cycle(
    review_cycle_id: int,
    current_user: CurrentUserDep,
    session: DatabaseSessionDep,
    service: ReviewCycleServiceDep,
) -> ReviewCycleResponse:
    try:
        return service.archive_review_cycle(session, current_user, review_cycle_id)
    except ServiceError as exc:
        raise to_http_exception(exc) from exc

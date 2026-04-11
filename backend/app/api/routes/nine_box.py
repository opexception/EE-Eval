from fastapi import APIRouter

from app.api.deps import DatabaseSessionDep, NineBoxServiceDep
from app.api.errors import to_http_exception
from app.auth.deps import CurrentUserDep
from app.schemas.nine_box import NineBoxMatrixResponse
from app.services.errors import ServiceError

router = APIRouter()


@router.get(
    "",
    response_model=NineBoxMatrixResponse,
    summary="Get a 9-box matrix for a review cycle",
)
def get_nine_box_matrix(
    current_user: CurrentUserDep,
    session: DatabaseSessionDep,
    service: NineBoxServiceDep,
    review_cycle_id: int | None = None,
) -> NineBoxMatrixResponse:
    try:
        return service.get_matrix(
            session,
            current_user,
            review_cycle_id=review_cycle_id,
        )
    except ServiceError as exc:
        raise to_http_exception(exc) from exc

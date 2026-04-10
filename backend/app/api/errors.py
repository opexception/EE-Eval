from fastapi import HTTPException

from app.services.errors import ServiceError


def to_http_exception(error: ServiceError) -> HTTPException:
    return HTTPException(
        status_code=error.status_code,
        detail=str(error),
    )

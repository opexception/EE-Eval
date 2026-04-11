from fastapi import APIRouter

from app.api.routes.auth import router as auth_router
from app.api.routes.employees import router as employees_router
from app.api.routes.evaluations import router as evaluations_router
from app.api.routes.health import router as health_router
from app.api.routes.nine_box import router as nine_box_router
from app.api.routes.review_cycles import router as review_cycles_router

api_router = APIRouter()
api_router.include_router(auth_router, prefix="/auth", tags=["auth"])
api_router.include_router(employees_router, prefix="/employees", tags=["employees"])
api_router.include_router(
    review_cycles_router,
    prefix="/review-cycles",
    tags=["review-cycles"],
)
api_router.include_router(
    evaluations_router,
    prefix="/evaluations",
    tags=["evaluations"],
)
api_router.include_router(nine_box_router, prefix="/nine-box", tags=["nine-box"])
api_router.include_router(health_router, prefix="/health", tags=["health"])

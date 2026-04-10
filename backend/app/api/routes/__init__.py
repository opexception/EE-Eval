from app.api.routes.auth import router as auth_router
from app.api.routes.employees import router as employees_router
from app.api.routes.evaluations import router as evaluations_router
from app.api.routes.health import router as health_router
from app.api.routes.review_cycles import router as review_cycles_router

__all__ = [
    "auth_router",
    "employees_router",
    "evaluations_router",
    "health_router",
    "review_cycles_router",
]

__all__ = ["auth_router", "health_router"]

from types import SimpleNamespace

from fastapi import Depends, FastAPI
from fastapi.testclient import TestClient

from app.auth.deps import get_current_user, require_roles
from app.models.role import RoleName


def create_protected_test_app() -> FastAPI:
    app = FastAPI()

    @app.get("/protected")
    def protected_route(
        current_user: object = Depends(require_roles(RoleName.HR_ADMIN)),
    ) -> dict[str, bool]:
        return {"ok": True}

    return app


def test_role_requirement_allows_matching_role() -> None:
    app = create_protected_test_app()
    app.dependency_overrides[get_current_user] = lambda: SimpleNamespace(
        role_names={"hr_admin"}
    )

    with TestClient(app) as client:
        response = client.get("/protected", headers={"Authorization": "Bearer test"})

    assert response.status_code == 200
    assert response.json() == {"ok": True}


def test_role_requirement_rejects_missing_role() -> None:
    app = create_protected_test_app()
    app.dependency_overrides[get_current_user] = lambda: SimpleNamespace(
        role_names={"employee"}
    )

    with TestClient(app) as client:
        response = client.get("/protected", headers={"Authorization": "Bearer test"})

    assert response.status_code == 403
    assert response.json() == {
        "detail": "You do not have permission to access this resource."
    }

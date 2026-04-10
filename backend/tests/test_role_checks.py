from types import SimpleNamespace

import pytest
from fastapi import HTTPException

from app.auth.deps import require_roles
from app.models.role import RoleName


def test_role_requirement_allows_matching_role() -> None:
    dependency = require_roles(RoleName.HR_ADMIN)
    current_user = SimpleNamespace(role_names={"hr_admin"})

    assert dependency(current_user) is current_user


def test_role_requirement_rejects_missing_role() -> None:
    dependency = require_roles(RoleName.HR_ADMIN)
    current_user = SimpleNamespace(role_names={"employee"})

    with pytest.raises(HTTPException) as exc_info:
        dependency(current_user)

    assert exc_info.value.status_code == 403
    assert exc_info.value.detail == "You do not have permission to access this resource."

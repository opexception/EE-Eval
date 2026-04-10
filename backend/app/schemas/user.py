from pydantic import BaseModel

from app.models.user import User


class CurrentUserResponse(BaseModel):
    id: int
    username: str
    full_name: str
    auth_provider: str
    roles: list[str]
    is_active: bool

    @classmethod
    def from_user(cls, user: User) -> "CurrentUserResponse":
        return cls(
            id=user.id,
            username=user.username,
            full_name=user.full_name,
            auth_provider=user.auth_provider,
            roles=sorted(user.role_names),
            is_active=user.is_active,
        )


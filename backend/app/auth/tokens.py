from dataclasses import dataclass
from datetime import UTC, datetime, timedelta

import jwt
from jwt import InvalidTokenError

from app.core.config import get_settings


@dataclass(frozen=True)
class AccessToken:
    value: str
    expires_in_seconds: int


class TokenService:
    def create_access_token(self, subject: str) -> AccessToken:
        settings = get_settings()
        expires_in_seconds = settings.auth.access_token_expire_minutes * 60
        issued_at = datetime.now(UTC)
        expires_at = issued_at + timedelta(seconds=expires_in_seconds)
        payload = {
            "sub": subject,
            "type": "access",
            "iat": issued_at,
            "exp": expires_at,
        }
        token = jwt.encode(
            payload,
            settings.auth.jwt_secret,
            algorithm=settings.auth.algorithm,
        )
        return AccessToken(value=token, expires_in_seconds=expires_in_seconds)

    def decode_access_token(self, token: str) -> str:
        settings = get_settings()
        payload = jwt.decode(
            token,
            settings.auth.jwt_secret,
            algorithms=[settings.auth.algorithm],
        )
        subject = payload.get("sub")
        token_type = payload.get("type")
        if token_type != "access" or not subject:
            raise InvalidTokenError("Invalid access token.")
        return str(subject)


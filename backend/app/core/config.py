from dataclasses import dataclass
from functools import lru_cache
import os

from sqlalchemy import URL

DEFAULT_DEVELOPMENT_JWT_SECRET = "replace-with-a-local-development-secret"
DEFAULT_DEMO_PASSWORD = "DemoPass123!ChangeMe"


@dataclass(frozen=True)
class DatabaseSettings:
    host: str
    port: int
    name: str
    user: str
    password: str
    echo: bool
    pool_pre_ping: bool

    @property
    def sqlalchemy_url(self) -> str:
        return URL.create(
            drivername="postgresql+psycopg",
            username=self.user,
            password=self.password,
            host=self.host,
            port=self.port,
            database=self.name,
        ).render_as_string(hide_password=False)


@dataclass(frozen=True)
class Settings:
    app_name: str
    environment: str
    debug: bool
    api_prefix: str
    cors_origins: tuple[str, ...]
    database: DatabaseSettings
    auth: "AuthSettings"
    demo_seed: "DemoSeedSettings"


@dataclass(frozen=True)
class AuthSettings:
    jwt_secret: str
    algorithm: str
    access_token_expire_minutes: int
    max_failed_login_attempts: int
    lockout_minutes: int


@dataclass(frozen=True)
class DemoSeedSettings:
    enabled: bool
    password: str


def _read_bool(name: str, default: bool) -> bool:
    raw_value = os.getenv(name)
    if raw_value is None:
        return default
    return raw_value.strip().lower() in {"1", "true", "yes", "on"}


def _read_int(name: str, default: int) -> int:
    raw_value = os.getenv(name)
    if raw_value is None:
        return default
    return int(raw_value)


def _normalize_api_prefix(raw_value: str | None) -> str:
    if raw_value is None or not raw_value.strip():
        return "/api"

    prefix = raw_value.strip()
    if not prefix.startswith("/"):
        prefix = f"/{prefix}"

    return prefix.rstrip("/") or "/api"


def _read_csv(name: str, default: tuple[str, ...]) -> tuple[str, ...]:
    raw_value = os.getenv(name)
    if raw_value is None:
        return default

    values = tuple(
        item.strip()
        for item in raw_value.split(",")
        if item.strip()
    )
    return values or default


def _read_jwt_secret(environment: str) -> str:
    secret = os.getenv("EE_EVAL_JWT_SECRET", DEFAULT_DEVELOPMENT_JWT_SECRET)
    if environment != "development" and secret == DEFAULT_DEVELOPMENT_JWT_SECRET:
        raise ValueError(
            "EE_EVAL_JWT_SECRET must be configured outside development."
        )
    return secret


@lru_cache
def get_settings() -> Settings:
    environment = os.getenv("EE_EVAL_ENV", "development")
    return Settings(
        app_name=os.getenv("EE_EVAL_APP_NAME", "EE-Eval API"),
        environment=environment,
        debug=_read_bool("EE_EVAL_DEBUG", environment == "development"),
        api_prefix=_normalize_api_prefix(os.getenv("EE_EVAL_API_PREFIX")),
        cors_origins=_read_csv(
            "EE_EVAL_CORS_ORIGINS",
            ("http://localhost:5173",),
        ),
        database=DatabaseSettings(
            host=os.getenv("DATABASE_HOST", "postgres"),
            port=_read_int("DATABASE_PORT", 5432),
            name=os.getenv("DATABASE_NAME", "ee_eval"),
            user=os.getenv("DATABASE_USER", "ee_eval"),
            password=os.getenv("DATABASE_PASSWORD", "change-me"),
            echo=_read_bool("DATABASE_ECHO", False),
            pool_pre_ping=_read_bool("DATABASE_POOL_PRE_PING", True),
        ),
        auth=AuthSettings(
            jwt_secret=_read_jwt_secret(environment),
            algorithm="HS256",
            access_token_expire_minutes=_read_int(
                "EE_EVAL_ACCESS_TOKEN_EXPIRE_MINUTES",
                60,
            ),
            max_failed_login_attempts=_read_int(
                "EE_EVAL_MAX_FAILED_LOGIN_ATTEMPTS",
                5,
            ),
            lockout_minutes=_read_int("EE_EVAL_LOCKOUT_MINUTES", 15),
        ),
        demo_seed=DemoSeedSettings(
            enabled=_read_bool("EE_EVAL_SEED_DEMO_USERS", environment == "development"),
            password=os.getenv("EE_EVAL_DEMO_PASSWORD", DEFAULT_DEMO_PASSWORD),
        ),
    )

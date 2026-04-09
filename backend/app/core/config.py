from dataclasses import dataclass
from functools import lru_cache
import os

from sqlalchemy import URL


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
    database: DatabaseSettings


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


@lru_cache
def get_settings() -> Settings:
    environment = os.getenv("EE_EVAL_ENV", "development")
    return Settings(
        app_name=os.getenv("EE_EVAL_APP_NAME", "EE-Eval API"),
        environment=environment,
        debug=_read_bool("EE_EVAL_DEBUG", environment == "development"),
        api_prefix=_normalize_api_prefix(os.getenv("EE_EVAL_API_PREFIX")),
        database=DatabaseSettings(
            host=os.getenv("DATABASE_HOST", "postgres"),
            port=_read_int("DATABASE_PORT", 5432),
            name=os.getenv("DATABASE_NAME", "ee_eval"),
            user=os.getenv("DATABASE_USER", "ee_eval"),
            password=os.getenv("DATABASE_PASSWORD", "change-me"),
            echo=_read_bool("DATABASE_ECHO", False),
            pool_pre_ping=_read_bool("DATABASE_POOL_PRE_PING", True),
        ),
    )

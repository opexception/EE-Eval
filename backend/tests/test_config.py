from app.core.config import get_settings


def test_settings_build_database_url_from_environment(monkeypatch) -> None:
    get_settings.cache_clear()

    monkeypatch.setenv("EE_EVAL_APP_NAME", "EE-Eval Test API")
    monkeypatch.setenv("EE_EVAL_ENV", "test")
    monkeypatch.setenv("EE_EVAL_DEBUG", "false")
    monkeypatch.setenv("EE_EVAL_API_PREFIX", "api")
    monkeypatch.setenv("DATABASE_HOST", "db.internal")
    monkeypatch.setenv("DATABASE_PORT", "6543")
    monkeypatch.setenv("DATABASE_NAME", "ee_eval_test")
    monkeypatch.setenv("DATABASE_USER", "app_user")
    monkeypatch.setenv("DATABASE_PASSWORD", "safe-password")
    monkeypatch.setenv("DATABASE_ECHO", "true")
    monkeypatch.setenv("DATABASE_POOL_PRE_PING", "false")

    settings = get_settings()

    assert settings.app_name == "EE-Eval Test API"
    assert settings.environment == "test"
    assert settings.debug is False
    assert settings.api_prefix == "/api"
    assert settings.database.host == "db.internal"
    assert settings.database.port == 6543
    assert settings.database.echo is True
    assert settings.database.pool_pre_ping is False
    assert (
        settings.database.sqlalchemy_url
        == "postgresql+psycopg://app_user:safe-password@db.internal:6543/ee_eval_test"
    )

    get_settings.cache_clear()


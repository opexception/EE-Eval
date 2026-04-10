from app.core.config import get_settings


def test_settings_include_auth_and_seed_configuration(monkeypatch) -> None:
    monkeypatch.setenv("EE_EVAL_APP_NAME", "EE-Eval Test API")
    monkeypatch.setenv("EE_EVAL_ENV", "test")
    monkeypatch.setenv("EE_EVAL_DEBUG", "false")
    monkeypatch.setenv("EE_EVAL_API_PREFIX", "api")
    monkeypatch.setenv(
        "EE_EVAL_CORS_ORIGINS",
        "http://localhost:5173,http://127.0.0.1:5173",
    )
    monkeypatch.setenv("EE_EVAL_JWT_SECRET", "test-jwt-secret")
    monkeypatch.setenv("EE_EVAL_ACCESS_TOKEN_EXPIRE_MINUTES", "90")
    monkeypatch.setenv("EE_EVAL_MAX_FAILED_LOGIN_ATTEMPTS", "4")
    monkeypatch.setenv("EE_EVAL_LOCKOUT_MINUTES", "30")
    monkeypatch.setenv("EE_EVAL_SEED_DEMO_USERS", "false")
    monkeypatch.setenv("EE_EVAL_DEMO_PASSWORD", "DemoPassword123!ChangeMe")
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
    assert settings.cors_origins == (
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    )
    assert settings.auth.jwt_secret == "test-jwt-secret"
    assert settings.auth.access_token_expire_minutes == 90
    assert settings.auth.max_failed_login_attempts == 4
    assert settings.auth.lockout_minutes == 30
    assert settings.demo_seed.enabled is False
    assert settings.demo_seed.password == "DemoPassword123!ChangeMe"
    assert (
        settings.database.sqlalchemy_url
        == "postgresql+psycopg://app_user:safe-password@db.internal:6543/ee_eval_test"
    )


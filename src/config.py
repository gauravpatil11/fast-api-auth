import os
from pathlib import Path

from src.constant.app_constants import ACCESS_TOKEN_EXPIRE_MINUTES, JWT_ALGORITHM


BASE_DIR = Path(__file__).resolve().parent.parent


def _load_env_file() -> None:
    env_path = BASE_DIR / ".env"
    if not env_path.exists():
        return

    for raw_line in env_path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        os.environ.setdefault(key.strip(), value.strip())


_load_env_file()


def _get_bool(name: str, default: bool) -> bool:
    value = os.getenv(name)
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "on"}


class Settings:
    app_name: str = os.getenv("APP_NAME", "FastAPI Auth Service")
    app_env: str = os.getenv("APP_ENV", "development")
    app_debug: bool = _get_bool("APP_DEBUG", True)
    app_host: str = os.getenv("APP_HOST", "127.0.0.1")
    app_port: int = int(os.getenv("APP_PORT", "8000"))
    app_log_level: str = os.getenv("APP_LOG_LEVEL", "INFO").upper()
    auto_create_tables: bool = _get_bool("AUTO_CREATE_TABLES", True)

    mysql_user: str = os.getenv("MYSQL_USER", "root")
    mysql_password: str = os.getenv("MYSQL_PASSWORD", "")
    mysql_host: str = os.getenv("MYSQL_HOST", "localhost")
    mysql_port: int = int(os.getenv("MYSQL_PORT", "3306"))
    mysql_db: str = os.getenv("MYSQL_DB", "fastapi_auth")
    db_pool_size: int = int(os.getenv("DB_POOL_SIZE", "5"))
    db_max_overflow: int = int(os.getenv("DB_MAX_OVERFLOW", "10"))
    db_pool_timeout: int = int(os.getenv("DB_POOL_TIMEOUT", "30"))

    jwt_secret_key: str = os.getenv(
        "JWT_SECRET_KEY",
        "",
    )
    jwt_algorithm: str = os.getenv("JWT_ALGORITHM", JWT_ALGORITHM)
    access_token_expire_minutes: int = int(
        os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", str(ACCESS_TOKEN_EXPIRE_MINUTES))
    )

    server_out_log_path: Path = BASE_DIR / "server-out.log"
    server_error_log_path: Path = BASE_DIR / "server-error.log"

    @property
    def sqlalchemy_database_uri(self) -> str:
        return (
            f"mysql+pymysql://{self.mysql_user}:{self.mysql_password}"
            f"@{self.mysql_host}:{self.mysql_port}/{self.mysql_db}"
        )

    @property
    def is_production(self) -> bool:
        return self.app_env.lower() == "production"

    def validate(self) -> None:
        if not self.jwt_secret_key:
            raise RuntimeError("JWT_SECRET_KEY must be configured")
        if self.is_production and self.app_debug:
            raise RuntimeError("APP_DEBUG must be false in production")


settings = Settings()

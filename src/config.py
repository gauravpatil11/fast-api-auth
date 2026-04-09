from pathlib import Path
from urllib.parse import quote_plus

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

from src.constant.app_constants import (
    APP_ENV_PRODUCTION,
    DEFAULT_ACCESS_TOKEN_EXPIRE_MINUTES,
    DEFAULT_JWT_ALGORITHM,
    DEFAULT_RESET_OTP_LENGTH,
    DEFAULT_RESET_TOKEN_EXPIRE_MINUTES,
)


BASE_DIR = Path(__file__).resolve().parent.parent


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=BASE_DIR / ".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    app_name: str = "FastAPI Auth Service"
    app_env: str = "development"
    app_debug: bool = True
    app_host: str = "127.0.0.1"
    app_port: int = 8000
    app_log_level: str = "INFO"
    auto_create_tables: bool = True

    db_user: str = "root"
    db_password: str = ""
    db_host: str = "localhost"
    db_port: int = 3306
    db_name: str = "fastapi_auth"
    db_pool_size: int = 5
    db_max_overflow: int = 10
    db_pool_timeout: int = 30

    jwt_secret_key: str = Field(default="")
    jwt_algorithm: str = DEFAULT_JWT_ALGORITHM
    access_token_expire_minutes: int = DEFAULT_ACCESS_TOKEN_EXPIRE_MINUTES
    
    reset_token_expire_minutes: int = DEFAULT_RESET_TOKEN_EXPIRE_MINUTES
    reset_otp_length: int = DEFAULT_RESET_OTP_LENGTH
    
    frontend_url: str | None = None
    password_reset_url_base: str | None = None
    password_reset_path: str = "/reset-password"
    
    mail_host: str | None = None
    mail_port: int = 587
    mail_username: str | None = None
    mail_password: str | None = None
    mail_from_email: str | None = None
    mail_use_tls: bool = True

    server_out_log_path: Path = BASE_DIR / "server-out.log"
    server_error_log_path: Path = BASE_DIR / "server-error.log"

    @field_validator("app_env", mode="before")
    @classmethod
    def normalize_app_env(cls, value: str) -> str:
        return str(value).strip().lower()

    @field_validator("app_log_level", mode="before")
    @classmethod
    def normalize_log_level(cls, value: str) -> str:
        return str(value).strip().upper()

    @field_validator("password_reset_path", mode="before")
    @classmethod
    def normalize_password_reset_path(cls, value: str) -> str:
        path = str(value).strip()
        if not path:
            return "/reset-password"
        return path if path.startswith("/") else f"/{path}"

    @field_validator("frontend_url", "password_reset_url_base", mode="before")
    @classmethod
    def normalize_optional_urls(cls, value: str | None) -> str | None:
        if value is None:
            return None
        normalized = str(value).strip().rstrip("/")
        return normalized or None

    @property
    def sqlalchemy_database_uri(self) -> str:
        encoded_password = quote_plus(self.db_password)
        return (
            f"mysql+pymysql://{self.db_user}:{encoded_password}"
            f"@{self.db_host}:{self.db_port}/{self.db_name}"
        )

    @property
    def password_reset_url(self) -> str | None:
        if self.password_reset_url_base:
            return f"{self.password_reset_url_base}{self.password_reset_path}"
        if self.frontend_url:
            return f"{self.frontend_url}{self.password_reset_path}"
        return None

    @property
    def is_production(self) -> bool:
        return self.app_env == APP_ENV_PRODUCTION

    def validate(self) -> None:
        if not self.jwt_secret_key:
            raise RuntimeError("JWT_SECRET_KEY must be configured")
        if self.is_production and self.app_debug:
            raise RuntimeError("APP_DEBUG must be false in production")
        if self.app_port <= 0:
            raise RuntimeError("APP_PORT must be greater than 0")
        if self.db_port <= 0:
            raise RuntimeError("DB_PORT must be greater than 0")
        if self.db_pool_size <= 0:
            raise RuntimeError("DB_POOL_SIZE must be greater than 0")
        if self.db_max_overflow < 0:
            raise RuntimeError("DB_MAX_OVERFLOW must be greater than or equal to 0")
        if self.db_pool_timeout <= 0:
            raise RuntimeError("DB_POOL_TIMEOUT must be greater than 0")
        if self.access_token_expire_minutes <= 0:
            raise RuntimeError("ACCESS_TOKEN_EXPIRE_MINUTES must be greater than 0")
        if self.reset_token_expire_minutes <= 0:
            raise RuntimeError("RESET_TOKEN_EXPIRE_MINUTES must be greater than 0")
        if self.reset_otp_length <= 0:
            raise RuntimeError("RESET_OTP_LENGTH must be greater than 0")
        if self.mail_port <= 0:
            raise RuntimeError("MAIL_PORT must be greater than 0")


settings = Settings()

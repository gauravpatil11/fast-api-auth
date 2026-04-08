from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

from src.constant.app_constants import ACCESS_TOKEN_EXPIRE_MINUTES, JWT_ALGORITHM


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

    mysql_user: str = "root"
    mysql_password: str = ""
    mysql_host: str = "localhost"
    mysql_port: int = 3306
    mysql_db: str = "fastapi_auth"
    db_pool_size: int = 5
    db_max_overflow: int = 10
    db_pool_timeout: int = 30

    jwt_secret_key: str = Field(default="")
    jwt_algorithm: str = JWT_ALGORITHM
    access_token_expire_minutes: int = ACCESS_TOKEN_EXPIRE_MINUTES
    
    reset_token_expire_minutes: int = 5
    reset_otp_length: int = 6
    
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

from pydantic_settings import BaseSettings, SettingsConfigDict
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent.parent


class Settings(BaseSettings):
    """Global settings and configurations."""

    model_config = SettingsConfigDict(env_file=BASE_DIR / ".env", extra="ignore")

    DEBUG: bool = False

    # FastAPI app settings
    APP_TITLE: str = "DDash"
    APP_DESCRIPTION: str = "API for DDash"
    APP_VERSION: str = "0.1.0"

    # Database
    DATABASE_ECHO: bool = False
    DATABASE_MAX_OVERFLOW: int = 1
    DATABASE_POOL_PRE_PING: bool = True
    DATABASE_POOL_SIZE: int = 5
    DATABASE_URL: str

    # Logging
    LOGGING_CORRELATION_ID_LENGTH: int = 8
    LOGGING_FILE_BACKUP_COUNT: int = 5
    LOGGING_FILE_DIR: str = "logs/api/"
    LOGGING_FILE_LEVEL: str = "INFO"
    LOGGING_FILE_MAX_BYTES: int = 1024 * 1024  # 1 megabytes
    LOGGING_FILE_NAME: str = "log"
    LOGGING_LEVEL: str = "INFO"
    LOGGING_USE_DEFAULT_HANDLERS: bool = True

    # Authentication
    ACCESS_TOKEN_EXPIRY_SECONDS: int = 3600
    ACCESS_TOKEN_SECRET_KEY: str


settings = Settings()

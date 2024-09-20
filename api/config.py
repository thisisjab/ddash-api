from pydantic_settings import BaseSettings
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent.parent


class Settings(BaseSettings):
    """Global settings and configurations."""

    DEBUG: bool = False

    # FastAPI app settings
    APP_TITLE: str = "DDash"
    APP_DESCRIPTION: str = "API for DDash"
    APP_VERSION: str = "0.1.0"

    # Logging
    LOGGING_CORRELATION_ID_LENGTH: int = 8
    LOGGING_FILE_BACKUP_COUNT: int = 5
    LOGGING_FILE_DIR: str = "logs/api/"
    LOGGING_FILE_LEVEL: str = "INFO"
    LOGGING_FILE_MAX_BYTES: int = 1024 * 1024  # 1 megabytes
    LOGGING_FILE_NAME: str = "log"
    LOGGING_LEVEL: str = "INFO"
    LOGGING_USE_DEFAULT_HANDLERS: bool = True


settings = Settings(_env_file=BASE_DIR / ".env")

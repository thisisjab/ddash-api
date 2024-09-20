from pydantic_settings import BaseSettings
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent.parent


class Settings(BaseSettings):
    """Global settings and configurations."""
    DEBUG: bool = False 

    # FastAPI app settings
    APP_TITLE: str = 'DDash'
    APP_DESCRIPTION: str = 'API for DDash'
    APP_VERSION: str = '0.1.0'


settings = Settings(_env_file=BASE_DIR / ".env")

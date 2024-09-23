import logging
from typing import AsyncIterator

from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from api.config import settings

logger = logging.getLogger(__name__)

async_database_url_scheme = "postgresql+asyncpg://{}:{}@{}:{}/{}"
sync_database_url_scheme = "postgresql://{}:{}@{}:{}/{}"

async_engine = create_async_engine(
    echo=settings.DATABASE_ECHO,
    max_overflow=settings.DATABASE_MAX_OVERFLOW,
    pool_pre_ping=settings.DATABASE_POOL_PRE_PING,
    pool_size=settings.DATABASE_POOL_SIZE,
    url=async_database_url_scheme.format(
        settings.DATABASE_USERNAME,
        settings.DATABASE_PASSWORD,
        settings.DATABASE_HOST,
        settings.DATABASE_PORT,
        settings.DATABASE_NAME,
    ),
)

AsyncSessionLocal = async_sessionmaker(
    bind=async_engine,
    autoflush=False,
    future=True,
    expire_on_commit=False,
)


async def get_session() -> AsyncIterator[async_sessionmaker]:
    try:
        yield AsyncSessionLocal
    except SQLAlchemyError as e:
        logger.exception(e)

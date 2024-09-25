from typing import AsyncGenerator, Generator

import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy import create_engine, event, text
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from sqlalchemy.orm import Session, SessionTransaction

from api.config import settings
from api.database.registry import *  # noqa: F403
from api.database.setup import (
    async_database_url_scheme,
    get_session,
    sync_database_url_scheme,
)
from api.main import app

pass  # Trick to load `BaseDatabaseModel` the last,since all database models be imported before base model.
from api.database.models import BaseDatabaseModel  # noqa: E402


@pytest.fixture
def anyio_backend() -> str:
    return "asyncio"


@pytest.fixture
async def ac() -> AsyncGenerator:
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="https://test") as c:
        yield c


@pytest.fixture(scope="session")
def setup_db() -> Generator:
    engine = create_engine(
        sync_database_url_scheme.format(
            settings.DATABASE_USERNAME,
            settings.DATABASE_PASSWORD,
            settings.DATABASE_HOST,
            settings.DATABASE_PORT,
            "",
        )
    )
    conn = engine.connect()
    # Terminate transaction
    conn.execute(text("commit"))
    try:
        conn.execute(text("drop database test"))
    except SQLAlchemyError:
        pass
    finally:
        conn.close()

    conn = engine.connect()
    # Terminate transaction
    conn.execute(text("commit"))
    conn.execute(text("create database test"))
    conn.close()

    yield

    conn = engine.connect()
    # Terminate transaction
    conn.execute(text("commit"))
    try:
        conn.execute(text("drop database test"))
    except SQLAlchemyError:
        pass
    conn.close()
    engine.dispose()


@pytest.fixture(scope="session", autouse=True)
def setup_test_db(setup_db: Generator) -> Generator:
    engine = create_engine(
        sync_database_url_scheme.format(
            settings.DATABASE_USERNAME,
            settings.DATABASE_PASSWORD,
            settings.DATABASE_HOST,
            settings.DATABASE_PORT,
            "test",
        )
    )

    with engine.begin():
        BaseDatabaseModel.metadata.drop_all(engine)
        BaseDatabaseModel.metadata.create_all(engine)
        yield
        BaseDatabaseModel.metadata.drop_all(engine)

    engine.dispose()


@pytest.fixture
async def session() -> AsyncGenerator:
    # https://github.com/sqlalchemy/sqlalchemy/issues/5811#issuecomment-756269881
    async_engine = create_async_engine(
        async_database_url_scheme.format(
            settings.DATABASE_USERNAME,
            settings.DATABASE_PASSWORD,
            settings.DATABASE_HOST,
            settings.DATABASE_PORT,
            settings.DATABASE_NAME,
        )
    )
    async with async_engine.connect() as conn:
        await conn.begin()
        await conn.begin_nested()
        AsyncSessionLocal = async_sessionmaker(
            autocommit=False,
            autoflush=False,
            bind=conn,
            future=True,
        )

        async_session = AsyncSessionLocal()

        @event.listens_for(async_session.sync_session, "after_transaction_end")
        def end_savepoint(session: Session, transaction: SessionTransaction) -> None:
            if conn.closed:
                return
            if not conn.in_nested_transaction():
                if conn.sync_connection:
                    conn.sync_connection.begin_nested()

        def test_get_session() -> Generator:
            try:
                yield AsyncSessionLocal
            except SQLAlchemyError:
                pass

        app.dependency_overrides[get_session] = test_get_session

        yield async_session
        await async_session.close()
        await conn.rollback()

    await async_engine.dispose()

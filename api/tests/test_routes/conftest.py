import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from api.users.models import User
from api.users.services import UserService

_PASSWORD = "Something-th@t-cann0t-be-guessed"


@pytest.fixture
async def created_user(session: AsyncSession) -> User:
    user = User(
        email="user@foo.buz", password=UserService(None)._hash_password(_PASSWORD)
    )
    session.add(user)
    await session.flush()
    await session.refresh(user)
    return user


@pytest.fixture
async def created_user_access_token(ac: AsyncClient, created_user: User) -> str:
    payload = {"email": created_user.email, "password": _PASSWORD}
    response = await ac.post("/auth/token", json=payload)
    return response.json()["access"]

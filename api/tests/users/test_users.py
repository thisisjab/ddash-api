import pytest
from httpx import AsyncClient
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from api.users.models import User


@pytest.fixture
async def created_user(session: AsyncSession) -> User:
    user = User(email="user@foo.buz", password="very_secret")
    session.add(user)
    await session.flush()
    await session.refresh(user)
    return user


@pytest.mark.anyio
async def test_user_create(ac: AsyncClient, session: AsyncSession):
    payload = {"email": "foo@bar.buz", "password": "foobar"}

    response = await ac.post("/users", json=payload)
    user = (
        await session.execute(select(User).where(User.email == payload["email"]))
    ).scalar_one_or_none()

    assert user is not None
    assert str(user.id) == response.json()["id"]
    assert response.status_code == 201


@pytest.mark.anyio
async def test_duplicate_user_cannot_be_created(
    ac: AsyncClient, session: AsyncSession, created_user: User
):
    payload = {"email": created_user.email, "password": "very_secret"}
    response = await ac.post("/users", json=payload)
    assert response.status_code == 400

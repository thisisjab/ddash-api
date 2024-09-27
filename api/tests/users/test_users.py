import pytest
from httpx import AsyncClient
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from api.users.models import User


@pytest.mark.anyio
async def test_user_create(ac: AsyncClient, session: AsyncSession):
    payload = {"email": "foo@bar.buz", "password": "foobar"}

    response = await ac.post("/users", json=payload)
    user = (
        await session.execute(select(User).where(User.email == payload["email"]))
    ).scalar_one_or_none()

    assert user is not None
    assert response.status_code == 200

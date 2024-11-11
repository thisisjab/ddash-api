import pytest
from httpx import AsyncClient
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from api.tests.test_routes.conftest import _PASSWORD
from api.users.models import User


@pytest.mark.anyio
async def test_user_create(ac: AsyncClient, session: AsyncSession):
    payload = {"email": "foo@bar.buz", "password": "doesn't_matter"}

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
    payload = {"email": created_user.email, "password": "doesn't_matter"}
    response = await ac.post("/users", json=payload)
    assert response.status_code == 400


@pytest.mark.anyio
async def test_user_can_obtain_access_token(ac: AsyncClient, created_user: User):
    payload = {"email": created_user.email, "password": _PASSWORD}
    response = await ac.post("/auth/token", json=payload)
    assert response.status_code == 200

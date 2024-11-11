import pytest
from httpx import AsyncClient
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from api.orgs.models import Organization
from api.users.models import User


@pytest.mark.anyio
async def test_user_can_create_organization(
    ac: AsyncClient,
    session: AsyncSession,
    created_user: User,
    created_user_access_token: str,
):
    payload = {"name": "Something", "description": "Foo"}

    response = await ac.post(
        "/organizations",
        json=payload,
        headers={"Authorization": f"Bearer {created_user_access_token}"},
    )
    existing_organization = (
        await session.execute(select(Organization))
    ).scalar_one_or_none()

    assert response.status_code == 201
    assert existing_organization is not None
    assert response.json()["id"] == str(existing_organization.id)
    assert response.json()["name"] == existing_organization.name
    assert response.json()["description"] == existing_organization.description
    assert response.json()["manager_id"] == str(existing_organization.manager_id)


@pytest.mark.anyio
async def test_non_authenticated_users_cannot_access_create_organization_route(
    ac: AsyncClient,
):
    response = await ac.post("/organizations")
    assert response.status_code == 401

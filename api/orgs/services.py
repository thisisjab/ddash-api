from uuid import UUID

from sqlalchemy import delete, select

from api.database.dependencies import AsyncSession
from api.orgs.models import Organization
from api.orgs.schemas import (
    OrganizationCreateRequest,
    OrganizationPartialUpdateRequest,
    OrganizationResponse,
)
from api.users.models import User
from api.utils.pagination import PaginatedResponse, PaginationParams


class OrganizationService:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_users_organizations(
        self, user: User, pagination_params: PaginationParams
    ) -> PaginatedResponse[OrganizationResponse]:
        query = select(Organization).where(Organization.manager_id == user.id)
        return await PaginatedResponse().paginate(
            query, self.session, pagination_params
        )

    async def get_organization(self, organization_id: UUID) -> Organization:
        query = select(Organization).where(Organization.id == organization_id)

        async with self.session() as ac:
            instance = await ac.execute(query)
            return instance.scalars().one_or_none()

    async def create_organization_for_user(
        self, data: OrganizationCreateRequest, user: User
    ) -> Organization:
        async with self.session.begin() as ac:
            instance = Organization(**data.model_dump(), manager_id=user.id)
            ac.add(instance)
            await ac.flush()
            await ac.refresh(instance)

        return instance

    async def update_organization(
        self, organization: Organization, data: OrganizationPartialUpdateRequest
    ) -> Organization:
        for k, v in data.model_dump().items():
            setattr(organization, k, v)

        async with self.session.begin() as ac:
            ac.add(organization)
            await ac.flush()
            await ac.refresh(organization)

        return organization

    async def delete_organization(self, organization: Organization) -> None:
        query = delete(Organization).where(Organization.id == organization.id)
        async with self.session.begin() as ac:
            await ac.execute(query)
            await ac.flush()

from sqlalchemy import select

from api.database.dependencies import AsyncSession
from api.orgs.models import Organization
from api.orgs.schemas import OrganizationRequest, OrganizationResponse
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

    async def create_organization_for_user(
        self, data: OrganizationRequest, user: User
    ) -> OrganizationResponse:
        async with self.session.begin() as ac:
            instance = Organization(**data.model_dump(), manager_id=user.id)
            ac.add(instance)
            await ac.flush()
            await ac.refresh(instance)

        return OrganizationResponse.model_validate(instance)

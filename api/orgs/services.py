from typing import Annotated

from fastapi import Depends

from api.orgs.models import Organization
from api.orgs.repository import OrganizationRepository
from api.orgs.schemas import OrganizationRequest, OrganizationResponse
from api.users.models import User


class OrganizationService:
    """Crud service for organization model."""

    def __init__(
        self, repository: Annotated[OrganizationRepository, Depends()]
    ) -> None:
        self.repo = repository

    async def create_organization_for_user(
        self, data: OrganizationRequest, user: User
    ) -> OrganizationResponse:
        organization = await self.repo.create(
            Organization(**data.model_dump(), manager_id=user.id)
        )

        return OrganizationResponse.model_validate(organization)

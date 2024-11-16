from typing import Annotated

from fastapi import Depends

from api.orgs.models import Organization
from api.orgs.services import OrganizationService
from api.users.models import User


class OrganizationPermissionService:
    def __init__(
        self, organization_service: Annotated[OrganizationService, Depends()]
    ) -> None:
        self.organization_service = organization_service

    async def is_organization_manager(
        self, organization: Organization, user: User
    ) -> bool:
        if organization and user and organization.manager_id == user.id:
            return True

        return False

    async def is_organization_member(
        self, organization: Organization, user: User
    ) -> bool:
        if not (organization and user):
            return False

        membership = await self.organization_service.get_membership(
            organization_id=organization.id, user_id=user.id
        )

        if membership:
            return True

        return False

    async def is_organization_member_or_manager(
        self, organization: Organization, user: User
    ) -> bool:
        return await self.is_organization_manager(
            organization, user
        ) or await self.is_organization_member(organization, user)

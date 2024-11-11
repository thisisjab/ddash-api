from typing import Annotated
from uuid import UUID

from fastapi import Depends, HTTPException, Path, status

from api.orgs.models import Organization
from api.orgs.services import OrganizationService
from api.users.auth.dependencies import AuthenticatedUser


async def get_organization_for_modification(
    organization_id: Annotated[UUID, Path()],
    service: Annotated[OrganizationService, Depends()],
    user: AuthenticatedUser,
) -> Organization:
    organization = await service.get_organization(organization_id)

    if not organization:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN)

    if organization.manager_id == user.id:
        return organization

    raise HTTPException(status_code=status.HTTP_403_FORBIDDEN)


async def get_organization_for_view(
    organization_id: Annotated[UUID, Path()],
    service: Annotated[OrganizationService, Depends()],
    user: AuthenticatedUser,
) -> Organization:
    organization = await service.get_organization(organization_id)

    if not organization:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN)

    if organization.manager_id == user.id:
        return organization

    membership = await service.get_membership(organization.id, user.id)

    if membership is not None:
        return organization

    raise HTTPException(status_code=status.HTTP_403_FORBIDDEN)

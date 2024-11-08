from typing import Annotated
from uuid import UUID

from fastapi import Depends, HTTPException, Path, Query, status
from fastapi.routing import APIRouter

from api.orgs.schemas import OrganizationRequest, OrganizationResponse
from api.orgs.services import OrganizationService
from api.users.auth.dependencies import AuthenticatedUser
from api.utils.pagination import PaginatedResponse, PaginationParams

router = APIRouter(prefix="", tags=["organizations"])


@router.get(
    "/users/{user_id}/organizations",
    response_model=PaginatedResponse[OrganizationResponse],
)
async def get_organizations(
    user_id: Annotated[UUID, Path()],
    user: AuthenticatedUser,
    service: Annotated[OrganizationService, Depends()],
    pagination_params: Annotated[PaginationParams, Query()],
):
    if user.id == user_id:
        return await service.get_users_organizations(user, pagination_params)

    raise HTTPException(
        detail="Permissions for non-owner users have not been implemented, yet.",
        status_code=status.HTTP_403_FORBIDDEN,
    )


@router.post(
    "/organizations",
    response_model=OrganizationResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_organization(
    data: OrganizationRequest,
    user: AuthenticatedUser,
    service: Annotated[OrganizationService, Depends()],
):
    return await service.create_organization_for_user(data=data, user=user)

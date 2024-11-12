from typing import Annotated
from uuid import UUID

from fastapi import Body, Depends, HTTPException, Path, Query, status
from fastapi.routing import APIRouter

from api.orgs import permissions
from api.orgs.models import Organization
from api.orgs.schemas import (
    OrganizationCreateRequest,
    OrganizationInvitationResponse,
    OrganizationInvitationSetStatusRequest,
    OrganizationPartialUpdateRequest,
    OrganizationResponse,
    OrganizationSendInvitationRequest,
)
from api.orgs.services import OrganizationService
from api.users.auth.dependencies import AuthenticatedUser
from api.users.services import UserService
from api.utils.pagination import PaginatedResponse, PaginationParams

router = APIRouter(prefix="", tags=["organizations"])


@router.get(
    "/users/me/organizations",
    response_model=PaginatedResponse[OrganizationResponse],
    status_code=status.HTTP_200_OK,
)
async def get_organizations(
    user: AuthenticatedUser,
    service: Annotated[OrganizationService, Depends()],
    pagination_params: Annotated[PaginationParams, Query()],
):
    """Get user organizations (both owned/participated)."""
    return await service.get_users_organizations(user.id, pagination_params)


@router.post(
    "/organizations",
    response_model=OrganizationResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_organization(
    data: OrganizationCreateRequest,
    user: AuthenticatedUser,
    service: Annotated[OrganizationService, Depends()],
):
    """Create an organization with manager set to current user."""
    return await service.create_organization(
        Organization(**data.model_dump(), manager_id=user.id)
    )


@router.get(
    "/organizations/{organization_id}",
    response_model=OrganizationResponse,
    status_code=status.HTTP_200_OK,
)
async def get_organization(
    organization: Annotated[permissions.get_organization_for_view, Depends()],
):
    """Get an organization by id. Note: user must be a member of the organization or the manager."""
    return organization


@router.put(
    "/organizations/{organization_id}",
    response_model=OrganizationResponse,
    status_code=status.HTTP_200_OK,
)
async def update_organization(
    body: Annotated[OrganizationPartialUpdateRequest, Body()],
    organization: Annotated[permissions.get_organization_for_modification, Depends()],
    service: Annotated[OrganizationService, Depends()],
):
    """Update an organization by id. Note: user must be the manager."""

    # TODO: look for better solution than iterating over body
    for k, v in body.model_dump().items():
        setattr(organization, k, v)

    return await service.update_organization(organization)


@router.delete(
    "/organizations/{organization_id}", status_code=status.HTTP_204_NO_CONTENT
)
async def delete_organization(
    organization: Annotated[permissions.get_organization_for_modification, Depends()],
    service: Annotated[OrganizationService, Depends()],
):
    """Delete an organization by id. This action removes all memberships and invitations. Note: user must be the manager."""
    await service.delete_organization(organization.id)


@router.post(
    "/organizations/{organization_id}/invite/", status_code=status.HTTP_204_NO_CONTENT
)
async def invite_to_organization(
    organization_service: Annotated[OrganizationService, Depends()],
    user_service: Annotated[UserService, Depends()],
    organization: Annotated[permissions.get_organization_for_modification, Depends()],
    body: Annotated[OrganizationSendInvitationRequest, Body()],
):
    """Invite an existing user to current organization with email. Note: inviter must be the manager."""

    # TODO: prohibit inviting self
    user = await user_service.get_user_by_email(body.email)
    if not user:
        raise HTTPException(
            detail="User with given email does not exist.",
            status_code=status.HTTP_400_BAD_REQUEST,
        )

    return await organization_service.invite_user_to_organization(
        organization.id, user.id
    )


@router.get(
    "/users/me/organizations/invitations",
    status_code=status.HTTP_200_OK,
    response_model=PaginatedResponse[OrganizationInvitationResponse],
)
async def get_user_invitations(
    user: AuthenticatedUser,
    service: Annotated[OrganizationService, Depends()],
    pagination_params: Annotated[PaginationParams, Query()],
):
    """Get all pending invitations for authenticated user."""
    return await service.get_user_invitations(user.id, pagination_params)


@router.post(
    "/users/me/organizations/invitations/{organization_id}",
    status_code=status.HTTP_200_OK,
    response_model=OrganizationInvitationResponse,
)
async def set_invitation_status(
    user: AuthenticatedUser,
    organization_id: Annotated[UUID, Path()],
    body: OrganizationInvitationSetStatusRequest,
    service: Annotated[OrganizationService, Depends()],
):
    """Accept or reject invitation for the organization. This action is not reservable. Note: user must be the invited."""
    invitation = await service.get_user_pending_invitation_with_organization_id(
        user.id, organization_id
    )

    if not invitation:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)

    await service.set_invitation_status(invitation, body.accepted)
    return OrganizationInvitationResponse.model_validate(invitation)

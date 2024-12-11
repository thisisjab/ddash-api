from typing import Annotated
from uuid import UUID

from fastapi import Body, Depends, HTTPException, Path, Query, status
from fastapi.routing import APIRouter

from api.orgs.models import Organization
from api.orgs.permissions import OrganizationPermissionService
from api.orgs.schemas import (
    OrganizationCreateRequest,
    OrganizationInvitationResponse,
    OrganizationInvitationSetStatusRequest,
    OrganizationMemberResponse,
    OrganizationPartialUpdateRequest,
    OrganizationResponse,
    OrganizationSendInvitationRequest,
)
from api.orgs.services import OrganizationService
from api.users.auth.dependencies import AuthenticatedUser
from api.users.services import UserService
from api.utils.pagination import PaginatedResponse, PaginationParams
from api.utils.permissions import check_permission

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
    organization_id: Annotated[UUID, Path()],
    organization_service: Annotated[OrganizationService, Depends()],
    permission_service: Annotated[OrganizationPermissionService, Depends()],
    user: AuthenticatedUser,
):
    """Get an organization by id. Note: user must be a member of the organization or the manager."""
    organization = await organization_service.get_organization(organization_id)
    await check_permission(
        permission_service.is_organization_member_or_manager,
        organization=organization,
        user=user,
    )

    return organization


@router.put(
    "/organizations/{organization_id}",
    response_model=OrganizationResponse,
    status_code=status.HTTP_200_OK,
)
async def update_organization(
    organization_id: Annotated[UUID, Path()],
    body: Annotated[OrganizationPartialUpdateRequest, Body()],
    organization_service: Annotated[OrganizationService, Depends()],
    permission_service: Annotated[OrganizationPermissionService, Depends()],
    user: AuthenticatedUser,
):
    """Update an organization by id. Note: user must be the manager."""
    organization = await organization_service.get_organization(organization_id)
    if not organization:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)

    await check_permission(
        permission_service.is_organization_manager, organization=organization, user=user
    )

    # TODO: look for better solution than iterating over body
    for k, v in body.model_dump().items():
        setattr(organization, k, v)

    return await organization_service.update_organization(organization)


@router.delete(
    "/organizations/{organization_id}", status_code=status.HTTP_204_NO_CONTENT
)
async def delete_organization(
    organization_id: Annotated[UUID, Path()],
    service: Annotated[OrganizationService, Depends()],
    permission_service: Annotated[OrganizationPermissionService, Depends()],
    user: AuthenticatedUser,
):
    """Delete an organization by id. This action removes all memberships and invitations. Note: user must be the manager."""
    organization = await service.get_organization(organization_id)
    if not organization:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)

    await check_permission(
        permission_service.is_organization_manager, organization=organization, user=user
    )

    await service.delete_organization(organization.id)


@router.get(
    "/organizations/{organization_id}/members",
    response_model=PaginatedResponse[OrganizationMemberResponse],
    status_code=status.HTTP_200_OK,
)
async def get_organization_members(
    pagination_params: Annotated[PaginationParams, Query()],
    organization_id: Annotated[UUID, Path()],
    permission_service: Annotated[OrganizationPermissionService, Depends()],
    service: Annotated[OrganizationService, Depends()],
    user: AuthenticatedUser,
):
    organization = await service.get_organization(organization_id)
    if not organization:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)

    if permission_service.is_organization_manager(organization=organization, user=user):
        return await service.get_organization_members(
            organization.id, pagination_params
        )

    await check_permission(
        permission_service.is_organization_member, organization=organization, user=user
    )

    return await service.get_organization_members(
        organization.id, pagination_params, is_active=True
    )


@router.post(
    "/organizations/{organization_id}/members/{member_id}/activate",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def activate_organization_member(
    organization_id: Annotated[UUID, Path()],
    member_id: Annotated[UUID, Path()],
    service: Annotated[OrganizationService, Depends()],
    permission_service: Annotated[OrganizationPermissionService, Depends()],
    user: AuthenticatedUser,
):
    """Activate membership of a user."""
    membership = await service.get_membership(organization_id, member_id)
    if not membership:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)

    organization = await service.get_organization(organization_id)
    await check_permission(
        permission_service.is_organization_manager, organization=organization, user=user
    )

    await service.activate_organization_member(organization_id, member_id)


@router.post(
    "/organizations/{organization_id}/members/{member_id}/deactivate",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def deactivate_organization_member(
    organization_id: Annotated[UUID, Path()],
    member_id: Annotated[UUID, Path()],
    service: Annotated[OrganizationService, Depends()],
    permission_service: Annotated[OrganizationPermissionService, Depends()],
    user: AuthenticatedUser,
):
    """Deactivate membership of a user."""
    membership = await service.get_membership(organization_id, member_id)
    if not membership:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)

    organization = await service.get_organization(organization_id)
    await check_permission(
        permission_service.is_organization_manager, organization=organization, user=user
    )

    await service.deactivate_organization_member(organization_id, member_id)


@router.post(
    "/organizations/{organization_id}/invite/", status_code=status.HTTP_204_NO_CONTENT
)
async def invite_to_organization(
    body: Annotated[OrganizationSendInvitationRequest, Body()],
    organization_id: Annotated[UUID, Path()],
    organization_service: Annotated[OrganizationService, Depends()],
    permission_service: Annotated[OrganizationPermissionService, Depends()],
    user: AuthenticatedUser,
    user_service: Annotated[UserService, Depends()],
):
    """Invite an existing user to current organization with email. Note: inviter must be the manager."""

    user_to_invite = await user_service.get_user_by_email(body.email)
    if not user_to_invite:
        raise HTTPException(
            detail="User with given email does not exist.",
            status_code=status.HTTP_400_BAD_REQUEST,
        )

    organization = await organization_service.get_organization(organization_id)
    if not organization:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)

    await check_permission(
        permission_service.is_organization_manager, organization=organization, user=user
    )

    return await organization_service.invite_user_to_organization(
        organization.id, user_to_invite.id
    )


@router.get(
    "/users/me/organizations/invitations",
    status_code=status.HTTP_200_OK,
    response_model=PaginatedResponse[OrganizationInvitationResponse],
)
async def get_user_invitations(
    pagination_params: Annotated[PaginationParams, Query()],
    service: Annotated[OrganizationService, Depends()],
    user: AuthenticatedUser,
):
    """Get all pending invitations for authenticated user."""
    return await service.get_user_invitations(user.id, pagination_params)


@router.post(
    "/users/me/organizations/invitations/{organization_id}",
    status_code=status.HTTP_204_NO_CONTENT,
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

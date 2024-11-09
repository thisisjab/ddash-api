from typing import Annotated
from uuid import UUID

from fastapi import Body, Depends, HTTPException, Path, Query, status
from fastapi.routing import APIRouter

from api.orgs import permissions
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
    "/users/{user_id}/organizations",
    response_model=PaginatedResponse[OrganizationResponse],
    status_code=status.HTTP_200_OK,
)
async def get_organizations(
    user_id: Annotated[UUID, Path()],
    user: AuthenticatedUser,
    service: Annotated[OrganizationService, Depends()],
    pagination_params: Annotated[PaginationParams, Query()],
):
    if not permissions.can_view_user_organizations(request_user=user, owner_id=user_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
        )

    return await service.get_users_organizations(user, pagination_params)


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
    return await service.create_organization_for_user(data=data, user=user)


@router.get(
    "/organizations/{organization_id}",
    response_model=OrganizationResponse,
    status_code=status.HTTP_200_OK,
)
async def get_organization(
    user: AuthenticatedUser,
    service: Annotated[OrganizationService, Depends()],
    organization_id: Annotated[UUID, Path()],
):
    organization = await service.get_organization(organization_id)

    if not organization:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)

    if not permissions.can_access_organization(
        request_user=user, organization=organization
    ):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
        )

    return organization


@router.put(
    "/organizations/{organization_id}",
    response_model=OrganizationResponse,
    status_code=status.HTTP_200_OK,
)
async def update_organization(
    user: AuthenticatedUser,
    service: Annotated[OrganizationService, Depends()],
    organization_id: Annotated[UUID, Path()],
    body: Annotated[OrganizationPartialUpdateRequest, Body()],
):
    organization = await service.get_organization(organization_id)

    if not organization:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)

    if not permissions.can_access_organization(
        request_user=user, organization=organization
    ):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
        )

    return await service.update_organization(organization, body)


@router.delete(
    "/organizations/{organization_id}", status_code=status.HTTP_204_NO_CONTENT
)
async def delete_organization(
    user: AuthenticatedUser,
    service: Annotated[OrganizationService, Depends()],
    organization_id: Annotated[UUID, Path()],
):
    organization = await service.get_organization(organization_id)

    if not organization:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)

    if not permissions.can_access_organization(
        request_user=user, organization=organization
    ):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
        )

    await service.delete_organization(organization)


@router.post(
    "/organizations/{organization_id}/invite/", status_code=status.HTTP_204_NO_CONTENT
)
async def invite_to_organization(
    user: AuthenticatedUser,
    organization_service: Annotated[OrganizationService, Depends()],
    user_service: Annotated[UserService, Depends()],
    organization_id: Annotated[UUID, Path()],
    body: Annotated[OrganizationSendInvitationRequest, Body()],
):
    organization = await organization_service.get_organization(organization_id)
    if not organization:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)

    if not permissions.can_access_organization(
        request_user=user, organization=organization
    ):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
        )

    if body.email.lower() == user.email.lower():
        raise HTTPException(
            detail="Cannot invite yourself.", status_code=status.HTTP_400_BAD_REQUEST
        )

    user = await user_service.get_user_by_email(body.email)
    if not user:
        raise HTTPException(
            detail="User with given email does not exist.",
            status_code=status.HTTP_400_BAD_REQUEST,
        )

    return await organization_service.invite_user_to_organization(organization, user)


@router.get(
    "/users/{user_id}/organizations/invitations",
    status_code=status.HTTP_200_OK,
    response_model=PaginatedResponse[OrganizationInvitationResponse],
)
async def get_user_invitations(
    user_id: Annotated[UUID, Path()],
    user: AuthenticatedUser,
    service: Annotated[OrganizationService, Depends()],
    pagination_params: Annotated[PaginationParams, Query()],
):
    if not permissions.can_view_user_organization_invitations(
        request_user=user, user_id=user_id
    ):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
        )

    return await service.get_user_invitations(user.id, pagination_params)


@router.post(
    "/users/{user_id}/organizations/invitations/{organization_id}",
    status_code=status.HTTP_200_OK,
    response_model=OrganizationInvitationResponse,
)
async def set_invitation_status(
    user_id: Annotated[UUID, Path()],
    organization_id: Annotated[UUID, Path()],
    user: AuthenticatedUser,
    body: OrganizationInvitationSetStatusRequest,
    service: Annotated[OrganizationService, Depends()],
):
    if not permissions.can_view_user_organization_invitations(
        request_user=user, user_id=user_id
    ):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
        )

    invitation = await service.get_user_pending_invitation_with_organization_id(
        user.id, organization_id
    )

    if not invitation:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)

    await service.set_invitation_status(invitation, body.accepted)

    return OrganizationInvitationResponse.model_validate(invitation)

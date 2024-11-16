from typing import Annotated
from uuid import UUID

from fastapi import Depends, HTTPException, Path, status
from fastapi.routing import APIRouter

from api.orgs.permissions import OrganizationPermissionService
from api.orgs.services import OrganizationService
from api.projects.models import Project, ProjectParticipant
from api.projects.permissions import ProjectPermissionService
from api.projects.schemas import (
    ProjectCreateRequest,
    ProjectParticipantCreateRequest,
    ProjectParticipantResponse,
    ProjectParticipantUpdateRequest,
    ProjectResponse,
    ProjectUpdateRequest,
)
from api.projects.services import ProjectService
from api.users.auth.dependencies import AuthenticatedUser
from api.utils.pagination import PaginatedResponse, PaginationQueryParams
from api.utils.permissions import check_permission

router = APIRouter(prefix="", tags=["Projects"])


@router.get(
    "/organizations/{organization_id}/projects",
    response_model=PaginatedResponse[ProjectResponse],
    status_code=status.HTTP_200_OK,
)
async def get_projects(
    organization_id: Annotated[UUID, Path()],
    organization_service: Annotated[OrganizationService, Depends()],
    pagination_params: PaginationQueryParams,
    project_service: Annotated[ProjectService, Depends()],
    permission_service: Annotated[OrganizationPermissionService, Depends()],
    user: AuthenticatedUser,
):
    organization = await organization_service.get_organization(organization_id)
    await check_permission(
        permission_service.is_organization_member_or_manager,
        organization=organization,
        user=user,
    )

    return await project_service.get_projects_of_organization(
        organization.id, pagination_params
    )


@router.post(
    "/organizations/{organization_id}/projects",
    response_model=ProjectResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_project(
    organization_id: Annotated[UUID, Path()],
    organization_service: Annotated[OrganizationService, Depends()],
    project_service: Annotated[ProjectService, Depends()],
    permission_service: Annotated[OrganizationPermissionService, Depends()],
    user: AuthenticatedUser,
    data: ProjectCreateRequest,
):
    organization = await organization_service.get_organization(organization_id)
    await check_permission(
        permission_service.is_organization_manager, organization=organization, user=user
    )

    return await project_service.create_project(
        # TODO: fix typing error for sqlalchemy model
        Project(**data.model_dump(), organization_id=organization.id, finish_date=None)
    )


@router.get(
    "/projects/{project_id}",
    response_model=ProjectResponse,
    status_code=status.HTTP_200_OK,
)
async def get_project(
    project_id: Annotated[UUID, Path()],
    organization_service: Annotated[OrganizationService, Depends()],
    project_service: Annotated[ProjectService, Depends()],
    permission_service: Annotated[ProjectPermissionService, Depends()],
    user: AuthenticatedUser,
):
    project = await project_service.get_project(project_id)
    if not project:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)

    organization = await organization_service.get_organization(project.organization_id)
    await check_permission(
        permission_service.is_project_participant_or_organization_manager,
        project=project,
        organization=organization,
        user=user,
    )

    return project


@router.put(
    "/projects/{project_id}",
    response_model=ProjectResponse,
    status_code=status.HTTP_200_OK,
)
async def update_project(
    body: ProjectUpdateRequest,
    organization_service: Annotated[OrganizationService, Depends()],
    project_id: Annotated[UUID, Path()],
    project_service: Annotated[ProjectService, Depends()],
    permission_service: Annotated[OrganizationPermissionService, Depends()],
    user: AuthenticatedUser,
):
    project = await project_service.get_project(project_id)
    if not project:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)

    organization = await organization_service.get_organization(project.organization_id)
    await check_permission(
        permission_service.is_organization_manager,
        organization=organization,
        user=user,
    )

    for k, v in body.model_dump().items():
        setattr(project, k, v)

    return await project_service.update_project(project)


@router.delete(
    "/projects/{project_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_project(
    organization_service: Annotated[OrganizationService, Depends()],
    project_id: Annotated[UUID, Path()],
    project_service: Annotated[ProjectService, Depends()],
    permission_service: Annotated[OrganizationPermissionService, Depends()],
    user: AuthenticatedUser,
):
    project = await project_service.get_project(project_id)
    if not project:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)

    organization = await organization_service.get_organization(project.organization_id)
    await check_permission(
        permission_service.is_organization_manager,
        organization=organization,
        user=user,
    )
    await project_service.delete(project.id)


@router.get(
    "/projects/{project_id}/participants",
    response_model=PaginatedResponse[ProjectParticipantResponse],
    status_code=status.HTTP_200_OK,
)
async def get_project_participants(
    organization_service: Annotated[OrganizationService, Depends()],
    pagination_params: PaginationQueryParams,
    project_id: Annotated[UUID, Path()],
    project_service: Annotated[ProjectService, Depends()],
    permission_service: Annotated[ProjectPermissionService, Depends()],
    user: AuthenticatedUser,
):
    project = await project_service.get_project(project_id)
    if not project:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)

    organization = await organization_service.get_organization(project.organization_id)
    await check_permission(
        permission_service.is_project_participant_or_organization_manager,
        organization=organization,
        project=project,
        user=user,
    )

    return await project_service.get_participants_with_user(
        project.id, pagination_params
    )


@router.post(
    "/projects/{project_id}/participants",
    response_model=ProjectParticipantResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_project_participant(
    body: ProjectParticipantCreateRequest,
    organization_service: Annotated[OrganizationService, Depends()],
    project_id: Annotated[UUID, Path()],
    project_service: Annotated[ProjectService, Depends()],
    permission_service: Annotated[OrganizationPermissionService, Depends()],
    user: AuthenticatedUser,
):
    project = await project_service.get_project(project_id)
    if not project:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)

    organization = await organization_service.get_organization(project.organization_id)
    await check_permission(
        permission_service.is_organization_manager,
        organization=organization,
        user=user,
    )

    return await project_service.create_project_participant(
        ProjectParticipant(**body.model_dump(), project_id=project.id)
    )


@router.put(
    "/projects/{project_id}/participants/{user_id}",
    response_model=ProjectParticipantResponse,
    status_code=status.HTTP_200_OK,
)
async def update_project_participant(
    body: ProjectParticipantUpdateRequest,
    organization_service: Annotated[OrganizationService, Depends()],
    project_id: Annotated[UUID, Path()],
    project_service: Annotated[ProjectService, Depends()],
    permission_service: Annotated[OrganizationPermissionService, Depends()],
    user: AuthenticatedUser,
    user_id: Annotated[UUID, Path()],
):
    participant_and_project = await project_service.get_participant_with_project(
        project_id, user_id
    )

    if not participant_and_project:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)

    participation, project = participant_and_project

    organization = await organization_service.get_organization(project.organization_id)
    await check_permission(
        permission_service.is_organization_manager,
        organization=organization,
        user=user,
    )

    participation.participation_type = (
        body.participation_type
    )  # TODO: fix type annotation
    return await project_service.update_project_participant(participation)


@router.delete(
    "/projects/{project_id}/participants/{user_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_project_participant(
    organization_service: Annotated[OrganizationService, Depends()],
    project_id: Annotated[UUID, Path()],
    project_service: Annotated[ProjectService, Depends()],
    permission_service: Annotated[OrganizationPermissionService, Depends()],
    user: AuthenticatedUser,
    user_id: Annotated[UUID, Path()],
):
    participant_and_project = await project_service.get_participant_with_project(
        project_id, user_id
    )

    if not participant_and_project:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)

    participation, project = participant_and_project

    organization = await organization_service.get_organization(project.organization_id)
    await check_permission(
        permission_service.is_organization_manager,
        organization=organization,
        user=user,
    )

    await project_service.delete_project_participant(
        participation.project_id, participation.user_id
    )

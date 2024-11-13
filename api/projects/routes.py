from typing import Annotated
from uuid import UUID

from fastapi import Depends, HTTPException, Path, status
from fastapi.routing import APIRouter

from api.orgs.permissions import (
    has_organization_change_access,
    has_organization_view_access,
)
from api.orgs.services import OrganizationService
from api.projects.models import Project
from api.projects.permissions import has_project_view_access
from api.projects.schemas import (
    ProjectCreateRequest,
    ProjectResponse,
    ProjectUpdateRequest,
)
from api.projects.services import ProjectService
from api.users.auth.dependencies import AuthenticatedUser
from api.utils.pagination import PaginatedResponse, PaginationQueryParams

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
    user: AuthenticatedUser,
):
    organization = await organization_service.get_organization(organization_id)
    await has_organization_view_access(
        organization=organization, user=user, organization_service=organization_service
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
    user: AuthenticatedUser,
    data: ProjectCreateRequest,
):
    organization = await organization_service.get_organization(organization_id)
    await has_organization_change_access(organization=organization, user=user)

    return await project_service.create_project(
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
    user: AuthenticatedUser,
):
    project = await project_service.get_project(project_id)
    if not project:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)

    organization = await organization_service.get_organization(project.organization_id)
    await has_project_view_access(
        organization=organization,
        user=user,
        organization_service=organization_service,
        project_service=project_service,
        project=project,
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
    user: AuthenticatedUser,
):
    project = await project_service.get_project(project_id)
    if not project:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)

    organization = await organization_service.get_organization(project.organization_id)
    await has_organization_change_access(organization=organization, user=user)

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
    user: AuthenticatedUser,
):
    project = await project_service.get_project(project_id)
    if not project:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)

    organization = await organization_service.get_organization(project.organization_id)
    await has_organization_change_access(organization=organization, user=user)

    await project_service.delete(project.id)

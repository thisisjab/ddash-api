from typing import Annotated
from uuid import UUID

from fastapi import Depends, Path, status
from fastapi.routing import APIRouter

from api.orgs.permissions import (
    has_organization_view_access,
)
from api.orgs.services import OrganizationService
from api.projects.models import Project
from api.projects.schemas import ProjectCreateRequest, ProjectResponse
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
    await has_organization_view_access(
        organization=organization, user=user, organization_service=organization_service
    )

    return await project_service.create_project(
        Project(**data.model_dump(), organization_id=organization.id, finish_date=None)
    )

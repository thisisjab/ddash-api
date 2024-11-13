from typing import Annotated

from fastapi import Depends, status
from fastapi.routing import APIRouter

from api.orgs.permissions import (
    get_organization_for_modification,
    get_organization_for_view,
)
from api.projects.models import Project
from api.projects.schemas import ProjectCreateRequest, ProjectResponse
from api.projects.services import ProjectService
from api.utils.pagination import PaginatedResponse, PaginationQueryParams

router = APIRouter(prefix="", tags=["Projects"])


@router.get(
    "/organizations/{organization_id}/projects",
    response_model=PaginatedResponse[ProjectResponse],
    status_code=status.HTTP_200_OK,
)
async def get_projects(
    organization: Annotated[get_organization_for_view(), Depends()],
    pagination_params: PaginationQueryParams,
    service: Annotated[ProjectService, Depends()],
):
    return await service.get_projects_of_organization(
        organization.id, pagination_params
    )


@router.post(
    "/organizations/{organization_id}/projects",
    response_model=ProjectResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_project(
    data: ProjectCreateRequest,
    organization: Annotated[get_organization_for_modification, Depends()],
    service: Annotated[ProjectService, Depends()],
):
    return await service.create_project(
        Project(**data.model_dump(), organization_id=organization.id, finish_date=None)
    )

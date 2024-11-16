from typing import Annotated
from uuid import UUID

from fastapi import Depends, HTTPException, Path, status
from fastapi.routing import APIRouter

from api.orgs.services import OrganizationService
from api.projects.permissions import has_project_view_access
from api.projects.services import ProjectService
from api.tasks.schemas import TaskPaginationItem
from api.tasks.services import TaskService
from api.users.auth.dependencies import AuthenticatedUser
from api.utils.pagination import PaginatedResponse, PaginationQueryParams

router = APIRouter(prefix="", tags=["Tasks"])


@router.get(
    "/projects/{project_id}/tasks",
    response_model=PaginatedResponse[TaskPaginationItem],
    status_code=status.HTTP_200_OK,
)
async def get_project_tasks(
    organization_service: Annotated[OrganizationService, Depends()],
    pagination_params: PaginationQueryParams,
    project_id: Annotated[UUID, Path()],
    project_service: Annotated[ProjectService, Depends()],
    task_service: Annotated[TaskService, Depends()],
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

    return await task_service.get_tasks_for_project(project_id, pagination_params)

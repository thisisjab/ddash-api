from typing import Annotated
from uuid import UUID

from fastapi import Depends, HTTPException, Path, status
from fastapi.routing import APIRouter

from api.orgs.services import OrganizationService
from api.projects.permissions import ProjectPermissionService
from api.projects.services import ProjectService
from api.tasks.models import Task
from api.tasks.permissions import TaskPermissionService
from api.tasks.schemas import (
    TaskCreateRequest,
    TaskPaginationItem,
    TaskSingleResponse,
    TaskStateUpdateRequest,
    TaskUpdateRequest,
)
from api.tasks.services import TaskService
from api.users.auth.dependencies import AuthenticatedUser
from api.utils.pagination import PaginatedResponse, PaginationQueryParams
from api.utils.permissions import check_permission

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
    permission_service: Annotated[ProjectPermissionService, Depends()],
    task_service: Annotated[TaskService, Depends()],
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

    return await task_service.get_tasks_for_project(project_id, pagination_params)


@router.post(
    "/projects/{project_id}/tasks",
    response_model=TaskPaginationItem,
    status_code=status.HTTP_201_CREATED,
)
async def create_task(
    body: TaskCreateRequest,
    organization_service: Annotated[OrganizationService, Depends()],
    project_id: Annotated[UUID, Path()],
    project_service: Annotated[ProjectService, Depends()],
    permission_service: Annotated[ProjectPermissionService, Depends()],
    task_service: Annotated[TaskService, Depends()],
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

    created_task = await task_service.create_task(
        Task(**body.model_dump(), project_id=project.id)
    )

    setattr(created_task, "assignees", [])  # Required for pydantic serialization
    return created_task


@router.get(
    "/tasks/{task_id}",
    response_model=TaskSingleResponse,
    status_code=status.HTTP_200_OK,
)
async def get_task(
    task_id: Annotated[UUID, Path()],
    permission_service: Annotated[ProjectPermissionService, Depends()],
    task_service: Annotated[TaskService, Depends()],
    user: AuthenticatedUser,
):
    result = await task_service.get_task_with_project_and_organization_and_assignees(
        task_id
    )

    if not result:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)

    task, assignees, project, organization = result
    await check_permission(
        permission_service.is_project_participant_or_organization_manager,
        organization=organization,
        project=project,
        user=user,
    )

    setattr(task, "assignees", assignees)  # Required for pydantic serialization

    return task


@router.put(
    "/tasks/{task_id}",
    response_model=TaskSingleResponse,
    status_code=status.HTTP_200_OK,
)
async def update_task(
    task_id: Annotated[UUID, Path()],
    body: TaskUpdateRequest,
    permission_service: Annotated[ProjectPermissionService, Depends()],
    task_service: Annotated[TaskService, Depends()],
    user: AuthenticatedUser,
):
    result = await task_service.get_task_with_project_and_organization_and_assignees(
        task_id
    )

    if not result:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)

    task, assignees, project, organization = result
    await check_permission(
        permission_service.is_project_participant_or_organization_manager,
        organization=organization,
        project=project,
        user=user,
    )

    for k, v in body.model_dump().items():
        setattr(task, k, v)

    task = await task_service.update_task(task)

    setattr(task, "assignees", assignees)  # Required for pydantic serialization

    return task


@router.delete(
    "/tasks/{task_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_task(
    task_id: Annotated[UUID, Path()],
    permission_service: Annotated[ProjectPermissionService, Depends()],
    task_service: Annotated[TaskService, Depends()],
    user: AuthenticatedUser,
):
    result = await task_service.get_task_with_project_and_organization_and_assignees(
        task_id
    )

    if not result:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)

    _, _, project, organization = result
    await check_permission(
        permission_service.is_project_participant_or_organization_manager,
        organization=organization,
        project=project,
        user=user,
    )

    await task_service.delete_task_and_assignees(task_id)


@router.put(
    "/tasks/{task_id}/state",
    response_model=TaskSingleResponse,
    status_code=status.HTTP_200_OK,
)
async def set_task_state(
    body: TaskStateUpdateRequest,
    task_id: Annotated[UUID, Path()],
    permission_service: Annotated[TaskPermissionService, Depends()],
    task_service: Annotated[TaskService, Depends()],
    user: AuthenticatedUser,
):
    result = await task_service.get_task_with_project_and_organization_and_assignees(
        task_id
    )

    if not result:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)

    task, assignees, _, organization = result
    await check_permission(
        permission_service.is_task_assignee_or_organization_manager,
        organization=organization,
        task=task,
        user=user,
    )

    for k, v in body.model_dump().items():
        setattr(task, k, v)

    task = await task_service.update_task(task)

    setattr(task, "assignees", assignees)

    return task

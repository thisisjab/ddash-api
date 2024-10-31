from typing import Annotated

from fastapi import Depends, status
from fastapi.routing import APIRouter

from api.projects.schemas import ProjectRequest, ProjectResponse
from api.projects.services import ProjectService
from api.users.auth.dependencies import AuthenticatedUser

router = APIRouter(prefix="/projects", tags=["Projects"])


@router.get("", response_model=list[ProjectResponse], status_code=status.HTTP_200_OK)
async def get_projects(
    service: Annotated[ProjectService, Depends()],
    user: AuthenticatedUser,
):
    return await service.get_projects_of_user(user=user)


@router.post("", response_model=ProjectResponse, status_code=status.HTTP_201_CREATED)
async def create_project(
    data: ProjectRequest,
    service: Annotated[ProjectService, Depends()],
    user: AuthenticatedUser,
):
    return await service.create_project_for_user(data, creator=user)

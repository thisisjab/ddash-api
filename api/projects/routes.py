from typing import Annotated

from fastapi import Depends, status
from fastapi.routing import APIRouter

from api.projects.schemas import ProjectIn, ProjectOut
from api.projects.services import ProjectService
from api.users.auth.dependencies import AuthenticatedUser

router = APIRouter(prefix="/projects", tags=["Projects"])


@router.get("", response_model=list[ProjectOut], status_code=status.HTTP_200_OK)
async def get_projects(
    service: Annotated[ProjectService, Depends()],
    authenticated_user: AuthenticatedUser,
):
    return await service.get_projects_of_user(user_id=authenticated_user.id)


@router.post("", response_model=ProjectOut, status_code=status.HTTP_201_CREATED)
async def create_project(
    data: ProjectIn,
    service: Annotated[ProjectService, Depends()],
    authenticated_user: AuthenticatedUser,
):
    return await service.create_project(data, creator_id=authenticated_user.id)

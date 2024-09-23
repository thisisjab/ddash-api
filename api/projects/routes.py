from typing import Annotated

from fastapi import Depends
from fastapi.routing import APIRouter

from api.projects.schemas import ProjectIn, ProjectOut
from api.projects.services import ProjectService
from api.users.auth.dependencies import AuthenticatedUser

router = APIRouter(prefix="/projects", tags=["Projects"])


@router.post("", response_model=ProjectOut)
async def create_project(
    data: ProjectIn,
    service: Annotated[ProjectService, Depends()],
    authenticated_user: AuthenticatedUser,
):
    return await service.create_project(data, creator_id=authenticated_user.id)

from typing import Annotated
from fastapi import Depends
from fastapi.routing import APIRouter

from api.projects.schemas import ProjectIn, ProjectOut
from api.projects.services import ProjectService


router = APIRouter(prefix="/projects", tags=["Projects"])


@router.post("", response_model=ProjectOut)
async def create_project(
    data: ProjectIn, service: Annotated[ProjectService, Depends()]
):
    return await service.create_single_project(data)

from typing import Annotated

from fastapi import Depends, status
from fastapi.routing import APIRouter

from api.orgs.permissions import get_organization_for_modification
from api.projects.models import Project
from api.projects.schemas import ProjectCreateRequest, ProjectResponse
from api.projects.services import ProjectService

router = APIRouter(prefix="", tags=["Projects"])


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

from typing import Annotated
from uuid import UUID

from fastapi import Depends, HTTPException, status

from api.projects.models import Project
from api.projects.repository import ProjectRepository
from api.projects.schemas import ProjectRequest, ProjectResponse
from api.users.models import User


class ProjectService:
    def __init__(self, repository: Annotated[ProjectRepository, Depends()]) -> None:
        self.repo = repository

    async def get_projects_of_user(self, user: User) -> list[ProjectResponse]:
        return await self.repo.get_all(filter_clauses=[Project.creator_id == user.id])

    async def create_project_for_user(
        self, data: ProjectRequest, creator: User
    ) -> ProjectResponse:
        project = await self.repo.create(
            Project(
                title=data.title,
                description=data.description,
                creator_id=creator.id,
                start_date=data.start_date,
                finish_date=data.finish_date,
                deadline=data.deadline,
            )
        )

        return ProjectResponse.model_validate(project)

    async def get_project_for_user_by_id(
        self, id_: UUID, user: User
    ) -> ProjectResponse:
        project = await self.repo.get(Project.id == id_, Project.creator_id == user.id)

        if not project:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)

        return ProjectResponse.model_validate(project)

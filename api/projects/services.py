from typing import Annotated

from fastapi import Depends

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

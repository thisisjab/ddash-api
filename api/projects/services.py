from uuid import UUID

from sqlalchemy import select

from api.database.dependencies import AsyncSession
from api.projects.models import Project
from api.projects.schemas import ProjectIn, ProjectOut


class ProjectService:
    def __init__(self, session: AsyncSession) -> None:
        self.async_session = session

    async def get_projects_of_user(self, user_id: UUID) -> list[ProjectOut]:
        async with self.async_session.begin() as session:
            q = (
                select(Project)
                .where(Project.creator_id == user_id)
                .order_by(Project.created_at.desc())
            )
            result = await session.execute(q)
            return result.scalars()

    async def create_project(
        self, data: ProjectIn, creator_id: UUID | str
    ) -> ProjectOut:
        async with self.async_session.begin() as session:
            project = Project(
                title=data.title,
                description=data.title,
                creator_id=creator_id,
                start_date=data.start_date,
                finish_date=data.finish_date,
                deadline=data.deadline,
            )

            session.add(project)

            await session.flush()
            await session.refresh(project)

            return ProjectOut.model_validate(project)

from api.database.dependencies import AsyncSession
from api.projects.models import Project
from api.projects.schemas import ProjectIn, ProjectOut


class ProjectService:
    def __init__(self, session: AsyncSession) -> None:
        self.async_session = session

    async def create_single_project(self, data: ProjectIn) -> ProjectOut:
        async with self.async_session.begin() as session:
            project = Project(
                title=data.title,
                description=data.title,
                start_date=data.start_date,
                finish_date=data.finish_date,
                deadline=data.deadline,
            )

            session.add(project)

            await session.flush()
            await session.refresh(project)

            return ProjectOut.model_validate(project)

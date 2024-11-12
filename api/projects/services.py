from fastapi import HTTPException, status
from sqlalchemy import exists

from api.database.dependencies import AsyncSession
from api.orgs.models import Organization
from api.projects.models import Project


class ProjectService:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_project(self, project: Project) -> Project:
        async with self.session.begin() as ac:
            organization_exists_query = (
                exists(Organization)
                .where(Organization.id == project.organization_id)
                .select()
            )
            organization_exists_result = await ac.execute(organization_exists_query)
            organization_exists = organization_exists_result.scalar()

            if not organization_exists:
                raise HTTPException(
                    detail="Organization does not exist",
                    status_code=status.HTTP_400_BAD_REQUEST,
                )

            ac.add(project)
            await ac.flush()
            await ac.refresh(project)
            return project

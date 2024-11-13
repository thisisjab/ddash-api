from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy import exists, select

from api.database.dependencies import AsyncSession
from api.orgs.models import Organization
from api.projects.models import Project
from api.projects.schemas import ProjectResponse
from api.utils.pagination import PaginatedResponse, PaginationParams


class ProjectService:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_projects_of_organization(
        self, organization_id: UUID, pagination_params: PaginationParams
    ) -> PaginatedResponse[ProjectResponse]:
        query = (
            select(Project)
            .where(Project.organization_id == organization_id)
            .order_by(Project.modified_at)
        )
        return await PaginatedResponse().paginate(
            query, self.session, pagination_params
        )

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

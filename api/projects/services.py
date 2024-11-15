from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy import delete, exists, select

from api.database.dependencies import AsyncSession
from api.orgs.models import Organization
from api.projects.models import Project, ProjectParticipant
from api.projects.schemas import ProjectParticipantResponse, ProjectResponse
from api.users.models import User
from api.utils.pagination import PaginatedResponse, PaginationParams, paginate


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
        return await paginate(query, self.session, pagination_params)

    async def get_project(self, project_id: UUID) -> Project:
        query = select(Project).where(Project.id == project_id)

        async with self.session() as ac:
            result = await ac.execute(query)
            return result.scalars().one_or_none()

    async def get_participants_with_user(
        self, project_id: UUID, pagination_params: PaginationParams
    ) -> PaginatedResponse[ProjectParticipantResponse]:
        query = (
            select(ProjectParticipant, User)
            .select_from(ProjectParticipant)
            .join(User, User.id == ProjectParticipant.user_id)
            .where(Project.id == project_id)
        )

        paginated_result = await paginate(
            query, self.session, pagination_params, serialize_items=False
        )
        paginated_response_items = []

        for item in paginated_result["items"]:
            paginated_response_items.append(
                ProjectParticipantResponse(
                    participation_type=item[0].participation_type, user=item[1]
                )
            )

        paginated_result["items"] = paginated_response_items

        return paginated_result

    async def get_participant_with_project(
        self, project_id: UUID, user_id: UUID
    ) -> tuple[ProjectParticipant, Project]:
        query = (
            select(ProjectParticipant, Project)
            .select_from(ProjectParticipant)
            .join(Project, Project.id == ProjectParticipant.project_id)
            .where(
                ProjectParticipant.project_id == project_id,
                ProjectParticipant.user_id == user_id,
            )
        )

        async with self.session() as ac:
            result = await ac.execute(query)
            result = result.one_or_none()
            return result

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

    async def create_project_participant(
        self, participant: ProjectParticipant
    ) -> ProjectParticipantResponse:
        user_query = select(User).where(User.id == participant.user_id)
        participant_exists_query = (
            exists(ProjectParticipant)
            .where(
                ProjectParticipant.user_id == participant.user_id,
                ProjectParticipant.project_id == participant.project_id,
            )
            .select()
        )

        async with self.session.begin() as ac:
            participant_exists = (await ac.execute(participant_exists_query)).scalar()
            if participant_exists:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="User already exists in the project's participants.",
                )

            user = (await ac.execute(user_query)).scalars().one_or_none()

            if not user:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="User does not exist.",
                )

            ac.add(participant)
            await ac.flush()
            await ac.refresh(participant)

            return ProjectParticipantResponse(
                participation_type=participant.participation_type, user=user
            )

    async def update_project(self, project: Project) -> Project:
        async with self.session.begin() as ac:
            ac.add(project)
            await ac.flush()
            await ac.refresh(project)

            return project

    async def update_project_participant(
        self, participant: ProjectParticipant
    ) -> ProjectParticipantResponse:
        user_query = select(User).where(User.id == participant.user_id)
        async with self.session.begin() as ac:
            user = (await ac.execute(user_query)).scalars().one_or_none()

            if not user:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="User does not exist.",
                )

            ac.add(participant)
            await ac.flush()
            await ac.refresh(participant)

            return ProjectParticipantResponse(
                participation_type=participant.participation_type, user=user
            )

    async def delete(self, project_id: UUID) -> None:
        query = delete(Project).where(Project.id == project_id)
        async with self.session.begin() as ac:
            await ac.execute(query)
            await ac.flush()

    async def get_project_participant(
        self, project_id: UUID, user_id: UUID
    ) -> ProjectParticipant:
        query = select(ProjectParticipant).where(
            ProjectParticipant.project_id == project_id,
            ProjectParticipant.user_id == user_id,
        )

        async with self.session() as ac:
            result = await ac.execute(query)
            return result.scalars().one_or_none()

    async def delete_project_participant(self, project_id: UUID, user_id: UUID) -> None:
        query = delete(ProjectParticipant).where(
            ProjectParticipant.project_id == project_id,
            ProjectParticipant.user_id == user_id,
        )

        async with self.session.begin() as ac:
            await ac.execute(query)
            await ac.flush()

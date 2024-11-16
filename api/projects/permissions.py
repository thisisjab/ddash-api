from typing import Annotated

from fastapi import Depends

from api.orgs.models import Organization
from api.orgs.permissions import OrganizationPermissionService
from api.projects.models import Project
from api.projects.services import ProjectService
from api.users.models import User


class ProjectPermissionService:
    def __init__(
        self,
        organization_permissions_service: Annotated[
            OrganizationPermissionService, Depends()
        ],
        project_service: Annotated[ProjectService, Depends()],
    ) -> None:
        self.organization_permissions_service = organization_permissions_service
        self.project_service = project_service

    async def is_project_participant(
        self,
        project: Project,
        user: User,
    ) -> bool:
        if not (project and user):
            return False

        membership = await self.project_service.get_project_participant(
            project_id=project.id, user_id=user.id
        )

        if membership:
            return True

        return False

    async def is_project_participant_or_organization_manager(
        self, project: Project, user: User, organization: Organization
    ) -> bool:
        return await self.organization_permissions_service.is_organization_manager(
            organization=organization, user=user
        ) or await self.is_project_participant(project=project, user=user)

from api.orgs.models import Organization
from api.orgs.permissions import can_view_organization
from api.orgs.services import OrganizationService
from api.projects.models import Project
from api.projects.services import ProjectService
from api.users.models import User
from api.utils.permissions import permission_decorator


async def can_view_project(
    *,
    organization: Organization,
    organization_service: OrganizationService,
    project: Project,
    project_service: ProjectService,
    user: User,
) -> bool:
    if not (project and organization):
        return False

    if not await can_view_organization(
        organization=organization, user=user, organization_service=organization_service
    ):
        return False

    if organization.manager_id == user.id:
        return True

    project_participant = await project_service.get_project_participant(
        project.id, user.id
    )

    if project_participant:
        return True

    return False


@permission_decorator(raise_exception=True)
async def has_project_view_access(
    *,
    organization: Organization,
    organization_service: OrganizationService,
    project: Project,
    project_service: ProjectService,
    user: User,
) -> bool:
    return await can_view_project(
        organization=organization,
        organization_service=organization_service,
        project=project,
        project_service=project_service,
        user=user,
    )

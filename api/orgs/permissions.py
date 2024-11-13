from api.orgs.models import Organization
from api.orgs.services import OrganizationService
from api.users.models import User
from api.utils.permissions import permission_decorator


async def can_modify_organization(
    *,
    organization: Organization,
    user: User,
) -> bool:
    if not organization:
        return False

    if organization.manager_id == user.id:
        return True

    return False


@permission_decorator(raise_exception=True)
async def has_organization_change_access(
    *,
    organization: Organization,
    user: User,
) -> bool:
    return await can_modify_organization(organization=organization, user=user)


async def can_view_organization(
    organization: Organization,
    organization_service: OrganizationService,
    user: User,
) -> bool:
    if not organization:
        return False

    if organization.manager_id == user.id:
        return True

    membership = await organization_service.get_membership(organization.id, user.id)

    if membership is not None:
        return True

    return False


@permission_decorator(raise_exception=True)
async def has_organization_view_access(
    organization: Organization,
    organization_service: OrganizationService,
    user: User,
) -> bool:
    return await can_view_organization(
        organization=organization, user=user, organization_service=organization_service
    )

from uuid import UUID

from api.orgs.models import Organization
from api.users.models import User


def can_view_users_organizations(*, request_user: User, owner_id: UUID) -> bool:
    # TODO: check for super admin permission after adding superadmin field to user
    return request_user.id == owner_id


def can_access_organization(*, request_user: User, organization: Organization) -> bool:
    # TODO: check for super admin permission after adding superadmin field to user
    return organization.manager_id == request_user.id

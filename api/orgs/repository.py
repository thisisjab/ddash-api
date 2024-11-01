from api.database.repository import RepositoryBase
from api.orgs.models import Organization


class OrganizationRepository(RepositoryBase):
    model = Organization

from typing import Annotated

from fastapi import Depends

from api.orgs.services import OrganizationService

OrganizationServiceDependency = Annotated[OrganizationService, Depends()]

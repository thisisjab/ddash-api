from fastapi import status
from fastapi.routing import APIRouter

from api.orgs.dependencies import OrganizationServiceDependency
from api.orgs.schemas import OrganizationRequest, OrganizationResponse
from api.users.auth.dependencies import AuthenticatedUser

router = APIRouter(prefix="/organizations", tags=["organizations"])


@router.post(
    "", response_model=OrganizationResponse, status_code=status.HTTP_201_CREATED
)
async def create_organization(
    data: OrganizationRequest,
    user: AuthenticatedUser,
    service: OrganizationServiceDependency,
):
    return await service.create_organization_for_user(data=data, user=user)
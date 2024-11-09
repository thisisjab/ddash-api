from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy import and_, delete, exists, select

from api.database.dependencies import AsyncSession
from api.orgs.models import Organization, OrganizationInvitation, OrganizationMembership
from api.orgs.schemas import (
    OrganizationCreateRequest,
    OrganizationInvitationResponse,
    OrganizationPartialUpdateRequest,
    OrganizationResponse,
)
from api.users.models import User
from api.utils.pagination import PaginatedResponse, PaginationParams


class OrganizationService:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_users_organizations(
        self, user: User, pagination_params: PaginationParams
    ) -> PaginatedResponse[OrganizationResponse]:
        """Get all organizations of the user."""

        # TODO: convert `user` to `user_id` since user object is not needed.
        # TODO: union current query with participated organizations.

        query = select(Organization).where(Organization.manager_id == user.id)
        return await PaginatedResponse().paginate(
            query, self.session, pagination_params
        )

    async def get_organization(self, organization_id: UUID) -> Organization:
        """Get single organization with id."""
        query = select(Organization).where(Organization.id == organization_id)

        async with self.session() as ac:
            instance = await ac.execute(query)
            return instance.scalars().one_or_none()

    async def create_organization_for_user(
        self, data: OrganizationCreateRequest, user: User
    ) -> Organization:
        """Create organization for given user."""

        # TODO: convert `user` to `user_id` since user object is not needed.

        async with self.session.begin() as ac:
            instance = Organization(**data.model_dump(), manager_id=user.id)
            ac.add(instance)
            await ac.flush()
            await ac.refresh(instance)

        return instance

    async def update_organization(
        self, organization: Organization, data: OrganizationPartialUpdateRequest
    ) -> Organization:
        """Update organization with given data."""

        # TODO: check if there's better way than iterating over data.
        for k, v in data.model_dump().items():
            setattr(organization, k, v)

        async with self.session.begin() as ac:
            ac.add(organization)
            await ac.flush()
            await ac.refresh(organization)

        return organization

    async def delete_organization(self, organization: Organization) -> None:
        """Delete given organization."""
        # TODO: convert `organization` to `organization_id` since organization object is not needed.
        query = delete(Organization).where(Organization.id == organization.id)
        async with self.session.begin() as ac:
            await ac.execute(query)
            await ac.flush()

    async def invite_user_to_organization(
        self, organization: Organization, user: User
    ) -> OrganizationInvitation:
        """Create an invitation to a given organization for given user."""

        # TODO: convert `user` to `user_id` since user object is not needed.
        # TODO: convert `organization` to `organization_id` since organization object is not needed.

        membership_exists_query = (
            exists(OrganizationMembership)
            .where(
                OrganizationMembership.organization_id == organization.id,
                OrganizationMembership.user_id == user.id,
            )
            .select()
        )
        invitation_exists_query = (
            exists(OrganizationInvitation)
            .where(
                OrganizationInvitation.organization_id == organization.id,
                OrganizationInvitation.user_id == user.id,
            )
            .select()
        )

        async with self.session.begin() as ac:
            membership_result = await ac.execute(membership_exists_query)
            membership_exists = membership_result.scalar()

            if membership_exists:
                raise HTTPException(
                    detail="User is already a member of the organization.",
                    status_code=status.HTTP_400_BAD_REQUEST,
                )

            invitation_result = await ac.execute(invitation_exists_query)
            invitation_exists = invitation_result.scalar()

            if invitation_exists:
                raise HTTPException(
                    detail="User is already invited.",
                    status_code=status.HTTP_400_BAD_REQUEST,
                )

            invitation = OrganizationInvitation(
                organization_id=organization.id, user_id=user.id, accepted=None
            )

            ac.add(invitation)
            await ac.flush()
            await ac.refresh(invitation)

        return invitation

    async def get_user_invitations(
        self, user_id: UUID, pagination_params: PaginationParams
    ) -> PaginatedResponse[OrganizationInvitationResponse]:
        """Get user's all invitations."""

        query = select(OrganizationInvitation).where(
            OrganizationInvitation.user_id == user_id,
            OrganizationInvitation.accepted == None,  # noqa: E711
        )
        return await PaginatedResponse().paginate(
            query, self.session, pagination_params
        )

    async def get_user_pending_invitation_with_organization_id(
        self, user_id: UUID, organization_id: UUID
    ) -> OrganizationInvitation:
        """Get single PENDING (accepted=null) invitation for given user and organization."""
        query = select(OrganizationInvitation).where(
            and_(
                OrganizationInvitation.user_id == user_id,
                OrganizationInvitation.organization_id == organization_id,
                OrganizationInvitation.accepted == None,  # noqa: E711
            )
        )

        async with self.session() as ac:
            instance = await ac.execute(query)
            return instance.scalars().one_or_none()

    async def add_member_to_organization(
        self, organization_id: UUID, user_id: UUID
    ) -> OrganizationMembership:
        """Create a membership in given organization for given user."""

        membership_exists_query = (
            exists(OrganizationMembership)
            .where(
                OrganizationMembership.organization_id == organization_id,
                OrganizationMembership.user_id == user_id,
            )
            .select()
        )

        async with self.session.begin() as ac:
            membership_result = await ac.execute(membership_exists_query)
            membership_exists = membership_result.scalar()

            if membership_exists:
                raise HTTPException(
                    detail="User is already a member of the organization.",
                    status_code=status.HTTP_400_BAD_REQUEST,
                )

            membership = OrganizationMembership(
                organization_id=organization_id, user_id=user_id
            )

            ac.add(membership)
            await ac.flush()
            await ac.refresh(membership)

        return membership

    async def set_invitation_status(
        self, invitation: OrganizationInvitation, accepted: bool
    ) -> OrganizationInvitation:
        """Accept or reject an invitation. If accepted, create the corresponding membership record."""
        async with self.session.begin() as ac:
            invitation.accepted = accepted
            ac.add(invitation)
            await ac.flush()
            await ac.refresh(invitation)

            if invitation.accepted:
                await self.add_member_to_organization(
                    invitation.organization_id, invitation.user_id
                )

        return invitation

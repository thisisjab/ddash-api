from uuid import UUID

from sqlalchemy import ForeignKey, PrimaryKeyConstraint, text, types
from sqlalchemy.orm import Mapped, mapped_column

from api.database.models import BaseDatabaseModel, TimestampedModelMixin


class Organization(BaseDatabaseModel, TimestampedModelMixin):
    """Model representing an organization."""

    __tablename__ = "organizations"

    id: Mapped[UUID] = mapped_column(
        types.Uuid,
        primary_key=True,
        init=False,
        server_default=text("gen_random_uuid()"),
    )

    manager_id: Mapped[UUID] = mapped_column(
        ForeignKey("users.id", ondelete="RESTRICT"), nullable=False
    )
    name: Mapped[str] = mapped_column(types.String(75), nullable=False)
    description: Mapped[str] = mapped_column(types.String(255), nullable=True)

    # TODO: add logo field


class OrganizationMembership(BaseDatabaseModel, TimestampedModelMixin):
    """Model representing a user's membership in an organization."""

    __tablename__ = "organization_memberships"

    organization_id: Mapped[UUID] = mapped_column(
        ForeignKey("organizations.id", ondelete="CASCADE"),
        primary_key=True,
        nullable=False,
    )
    user_id: Mapped[UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), primary_key=True, nullable=False
    )

    __table_args__ = (PrimaryKeyConstraint("organization_id", "user_id"),)


class OrganizationInvitation(BaseDatabaseModel, TimestampedModelMixin):
    """Model representing a user's invitation to an organization."""

    __tablename__ = "organization_invitations"

    accepted: Mapped[bool] = mapped_column(types.Boolean(), nullable=True)
    organization_id: Mapped[UUID] = mapped_column(
        ForeignKey("organizations.id", ondelete="CASCADE"),
        nullable=False,
    )
    user_id: Mapped[UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )

    __table_args__ = (PrimaryKeyConstraint("organization_id", "user_id"),)

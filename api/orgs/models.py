from uuid import UUID

from sqlalchemy import ForeignKey, text, types
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

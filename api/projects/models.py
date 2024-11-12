from datetime import date
from uuid import UUID

from sqlalchemy import (
    Enum,
    ForeignKey,
    PrimaryKeyConstraint,
    text,
    types,
)
from sqlalchemy.orm import Mapped, mapped_column

from api.database.models import BaseDatabaseModel, TimestampedModelMixin
from api.projects.enums import ProjectParticipationType


class Project(BaseDatabaseModel, TimestampedModelMixin):
    __tablename__ = "projects"

    id: Mapped[UUID] = mapped_column(
        types.Uuid,
        primary_key=True,
        init=False,
        server_default=text("gen_random_uuid()"),
    )

    title: Mapped[str] = mapped_column(types.String(75), nullable=False)
    description: Mapped[str] = mapped_column(
        types.Text(),
        nullable=True,
    )

    start_date: Mapped[date] = mapped_column(types.Date(), nullable=True)
    finish_date: Mapped[date] = mapped_column(types.Date(), nullable=True)
    deadline: Mapped[date] = mapped_column(types.Date(), nullable=True)

    organization_id: Mapped[UUID] = mapped_column(
        ForeignKey("organizations.id", ondelete="RESTRICT"), nullable=False
    )


class ProjectParticipant(BaseDatabaseModel, TimestampedModelMixin):
    __tablename__ = "project_participants"

    # NOTE: Since subqueries are not allowed in postgres, I couldn't think of check constraint
    # that prohibits adding users to the project who are not a member of the project's organization.
    # PLease consider this when writing services or adding people to project.

    project_id: Mapped[UUID] = mapped_column(
        ForeignKey("projects.id", ondelete="CASCADE"),
        nullable=False,
    )
    user_id: Mapped[UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    participation_type: Mapped[str] = mapped_column(
        Enum(ProjectParticipationType), nullable=False
    )

    __table_args__ = (PrimaryKeyConstraint("project_id", "user_id"),)

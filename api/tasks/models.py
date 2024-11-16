from datetime import date, datetime
from uuid import UUID

from sqlalchemy import (
    CheckConstraint,
    ForeignKey,
    PrimaryKeyConstraint,
    func,
    text,
    types,
)
from sqlalchemy.orm import Mapped, mapped_column

from api.database.models import BaseDatabaseModel, TimestampedModelMixin
from api.tasks.enums import TaskState


class Task(BaseDatabaseModel, TimestampedModelMixin):
    __tablename__ = "tasks"

    id: Mapped[UUID] = mapped_column(
        types.Uuid,
        primary_key=True,
        init=False,
        server_default=text("gen_random_uuid()"),
    )

    project_id: Mapped[UUID] = mapped_column(
        ForeignKey("projects.id", ondelete="CASCADE"), nullable=False
    )

    title: Mapped[str] = mapped_column(types.String(255), nullable=False)
    description: Mapped[str] = mapped_column(types.Text(), nullable=True)
    start_date: Mapped[date] = mapped_column(types.Date(), nullable=True)
    finish_date: Mapped[date] = mapped_column(types.Date(), nullable=True)
    deadline: Mapped[date] = mapped_column(types.Date(), nullable=True)
    state: Mapped[str] = mapped_column(types.Enum(TaskState), nullable=False)
    # Higher the priority value, higher the priority.
    priority: Mapped[int] = mapped_column(types.SmallInteger(), nullable=False)

    __table_args__ = (
        CheckConstraint("finish_date >= start_date", "finish_date_gt_start_date"),
        # Finished date must be set if state is `COMPLETED` and vice versa.
        CheckConstraint(
            "state = 'COMPLETED' AND finish_date IS NOT NULL OR state != 'COMPLETED' AND finish_date IS NULL",
            "finish_date_present_if_done",
        ),
    )


class TaskAssignee(BaseDatabaseModel):
    __tablename__ = "task_assignees"

    task_id: Mapped[UUID] = mapped_column(ForeignKey("tasks.id"), nullable=False)
    user_id: Mapped[UUID] = mapped_column(ForeignKey("users.id"), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        init=False,
        server_default=func.now(),
    )

    __table_args__ = (PrimaryKeyConstraint("task_id", "user_id"),)

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, EmailStr

from api.tasks.enums import TaskState


class TaskPaginationItemUser(BaseModel):
    id: UUID
    email: EmailStr

    model_config = ConfigDict(from_attributes=True)


class TaskPaginationItem(BaseModel):
    id: UUID
    title: str
    description: str | None
    start_date: datetime | None
    finish_date: datetime | None
    deadline: datetime | None
    state: TaskState
    priority: int
    assignees: list[TaskPaginationItemUser]
    created_at: datetime
    modified_at: datetime

    model_config = ConfigDict(from_attributes=True)

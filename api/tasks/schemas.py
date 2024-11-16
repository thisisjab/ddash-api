from datetime import datetime
from uuid import UUID

from pydantic import BaseModel

from api.tasks.enums import TaskState


class TaskPaginationItem(BaseModel):
    id: UUID
    title: str
    description: str | None
    start_date: datetime | None
    finish_date: datetime | None
    deadline: datetime | None
    state: TaskState
    priority: int
    created_at: datetime
    modified_at: datetime

    # TODO: add assignees later

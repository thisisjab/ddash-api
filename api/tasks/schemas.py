from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, EmailStr, Field, model_validator

from api.tasks.enums import TaskState


class TaskPaginationItemUser(BaseModel):
    id: UUID
    first_name: str
    last_name: str
    display_name: str
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


class TaskCreateRequest(BaseModel):
    title: str = Field(max_length=255)
    description: str | None
    start_date: datetime | None
    finish_date: datetime | None
    deadline: datetime | None
    state: TaskState
    priority: int = Field(ge=0, le=3)

    @model_validator(mode="after")
    def validate_end_date_lt_start_date(self):
        if not (self.finish_date and self.start_date):
            return self

        if self.finish_date < self.start_date:
            raise ValueError("Finish date must be greater than start date.")

        return self

    @model_validator(mode="after")
    def validate_states(self):
        # When state is completed, finish_date must be set.
        if self.state == TaskState.COMPLETED and not self.finish_date:
            raise ValueError("Finish date must be set if task is completed.")

        # When state is NOT completed, finish_date must NOT be set.
        if self.state != TaskState.COMPLETED and self.finish_date:
            raise ValueError("Finish date must not be set if task is not completed.")

        return self


class TaskSingleResponse(BaseModel):
    id: UUID
    project_id: UUID
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


class TaskUpdateRequest(BaseModel):
    title: str = Field(max_length=255)
    description: str | None
    start_date: datetime | None
    finish_date: datetime | None
    deadline: datetime | None
    state: TaskState
    priority: int = Field(ge=0, le=3)

    @model_validator(mode="after")
    def validate_end_date_lt_start_date(self):
        if not (self.finish_date and self.start_date):
            return self

        if self.finish_date < self.start_date:
            raise ValueError("Finish date must be greater than start date.")

        return self

    @model_validator(mode="after")
    def validate_states(self):
        # When state is completed, finish_date must be set.
        if self.state == TaskState.COMPLETED and not self.finish_date:
            raise ValueError("Finish date must be set if task is completed.")

        # When state is NOT completed, finish_date must NOT be set.
        if self.state != TaskState.COMPLETED and self.finish_date:
            raise ValueError("Finish date must not be set if task is not completed.")

        return self


class TaskStateUpdateRequest(BaseModel):
    state: TaskState
    finish_date: datetime | None

    @model_validator(mode="after")
    def validate_states(self):
        # When state is completed, finish_date must be set.
        if self.state == TaskState.COMPLETED and not self.finish_date:
            raise ValueError("Finish date must be set if task is completed.")

        # When state is NOT completed, finish_date must NOT be set.
        if self.state != TaskState.COMPLETED and self.finish_date:
            raise ValueError("Finish date must not be set if task is not completed.")

        return self


class TaskAssigneeCreateOrDeleteRequest(BaseModel):
    user_id: UUID

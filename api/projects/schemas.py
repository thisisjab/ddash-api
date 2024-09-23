from datetime import date, datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, model_validator


class Project(BaseModel):
    id: UUID
    title: str = Field(min_length=3, max_length=75)
    description: str | None
    start_date: date | None
    finish_date: date | None
    deadline: date | None
    creator_id: UUID | str
    created_at: datetime
    modified_at: datetime


class ProjectIn(BaseModel):
    title: str = Field(min_length=3, max_length=75)
    description: str | None
    start_date: date | None
    finish_date: date | None
    deadline: date | None

    @model_validator(mode="after")
    def validate_end_date(self):
        if self.finish_date < self.start_date:
            raise ValueError("Finish date must be greater than start date")

        return self


class ProjectOut(Project):
    model_config = ConfigDict(from_attributes=True)

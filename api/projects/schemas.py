from datetime import date, datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class ProjectCreateRequest(BaseModel):
    title: str = Field(min_length=3, max_length=75)
    description: str | None
    start_date: date | None
    deadline: date | None


class ProjectResponse(BaseModel):
    id: UUID
    title: str = Field(min_length=3, max_length=75)
    description: str | None
    start_date: date | None
    finish_date: date | None
    deadline: date | None
    organization_id: UUID | str
    created_at: datetime
    modified_at: datetime

    model_config = ConfigDict(from_attributes=True)

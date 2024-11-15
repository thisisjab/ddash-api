from datetime import date, datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, model_validator

from api.projects.enums import ProjectParticipationType
from api.users.schemas import UserResponse


class ProjectCreateRequest(BaseModel):
    title: str = Field(min_length=3, max_length=75)
    description: str | None
    start_date: date | None
    deadline: date | None


class ProjectUpdateRequest(BaseModel):
    title: str = Field(min_length=3, max_length=75)
    description: str | None
    start_date: date | None
    finish_date: date | None
    deadline: date | None

    @model_validator(mode="after")
    def validate_end_date(self):
        if not (self.finish_date and self.start_date):
            return self

        if self.finish_date < self.start_date:
            raise ValueError("Finish date must be greater than start date.")

        return self


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


class ProjectParticipantCreateRequest(BaseModel):
    participation_type: ProjectParticipationType
    user_id: UUID


class ProjectParticipantUpdateRequest(BaseModel):
    participation_type: ProjectParticipationType


class ProjectParticipantResponse(BaseModel):
    participation_type: ProjectParticipationType
    user: UserResponse

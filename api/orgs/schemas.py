from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class OrganizationRequest(BaseModel):
    name: str = Field(max_length=75)
    description: str = Field(max_length=255)


class OrganizationResponse(BaseModel):
    id: UUID
    name: str = Field(max_length=75)
    description: str = Field(max_length=255)
    manager_id: UUID
    created_at: datetime
    modified_at: datetime

    model_config = ConfigDict(from_attributes=True)


class OrganizationInviteRequest(BaseModel):
    user_email: EmailStr


class OrganizationInviteResponse(BaseModel): ...

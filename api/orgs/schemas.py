from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class OrganizationCreateRequest(BaseModel):
    name: str = Field(max_length=75)
    description: str = Field(max_length=255)


class OrganizationPartialUpdateRequest(BaseModel):
    name: str = Field(max_length=75, default=None)
    description: str = Field(max_length=255, default=None)


class OrganizationResponse(BaseModel):
    id: UUID
    name: str = Field(max_length=75)
    description: str = Field(max_length=255)
    manager_id: UUID
    created_at: datetime
    modified_at: datetime

    model_config = ConfigDict(from_attributes=True)


class OrganizationSendInvitationRequest(BaseModel):
    email: EmailStr


class OrganizationInvitationResponse(BaseModel):
    organization_name: str
    user_id: UUID
    accepted: bool | None
    created_at: datetime
    modified_at: datetime

    model_config = ConfigDict(from_attributes=True)


class OrganizationInvitationSetStatusRequest(BaseModel):
    accepted: bool

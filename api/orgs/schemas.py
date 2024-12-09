from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, EmailStr, Field

from api.users.schemas import User


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
    class InvitorDetail(BaseModel):
        first_name: str
        last_name: str
        display_name: str
        email: str
        model_config = ConfigDict(from_attributes=True)

    class OrganizationDetail(BaseModel):
        id: UUID
        name: str
        description: str
        model_config = ConfigDict(from_attributes=True)

    organization: OrganizationDetail
    invitor: InvitorDetail
    user_id: UUID
    accepted: bool | None
    created_at: datetime
    modified_at: datetime

    model_config = ConfigDict(from_attributes=True)


class OrganizationInvitationSetStatusRequest(BaseModel):
    accepted: bool


class OrganizationMemberResponse(User):
    class ResponseMetadata(BaseModel):
        is_active: bool
        is_manager: bool
        model_config = ConfigDict(from_attributes=True)

    metadata: ResponseMetadata

    model_config = ConfigDict(from_attributes=True)

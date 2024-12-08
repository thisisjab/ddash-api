from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class User(BaseModel):
    id: UUID
    email: EmailStr
    first_name: str
    last_name: str
    display_name: Optional[str]
    created_at: datetime
    modified_at: datetime


class UserRequest(BaseModel):
    email: EmailStr
    password: str = Field(exclude=True, min_length=5)
    first_name: str = Field(max_length=255)
    last_name: str = Field(max_length=255)
    display_name: Optional[str] = Field(max_length=255)


class UserResponse(User):
    model_config = ConfigDict(from_attributes=True)


class AccessTokenRequest(BaseModel):
    email: EmailStr
    password: str = Field(exclude=True, min_length=5)


class AccessTokenResponse(BaseModel):
    access: str

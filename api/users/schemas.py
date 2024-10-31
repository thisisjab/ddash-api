from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class User(BaseModel):
    id: UUID
    email: EmailStr
    created_at: datetime
    modified_at: datetime


class UserRequest(BaseModel):
    email: EmailStr
    password: str = Field(exclude=True, min_length=5)


class UserResponse(User):
    model_config = ConfigDict(from_attributes=True)


class AccessTokenIn(BaseModel):
    email: EmailStr
    password: str = Field(exclude=True, min_length=5)


class AccessTokenOut(BaseModel):
    access: str

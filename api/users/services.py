import time
from datetime import timedelta
from typing import Annotated
from uuid import UUID

import jwt
from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError
from fastapi import Depends, HTTPException, status
from sqlalchemy import func

from api.config import settings
from api.users.models import User
from api.users.repository import UserRepository
from api.users.schemas import UserRequest, UserResponse


class UserService:
    def __init__(self, repository: Annotated[UserRepository, Depends()]):
        self.repo = repository
        self._ph = PasswordHasher()

    async def create_user(self, data: UserRequest) -> UserResponse:
        if await self.get_user_by_email(data.email):
            raise HTTPException(
                detail="User already exists.",
                status_code=status.HTTP_400_BAD_REQUEST,
            )

        hashed_password = self._hash_password(data.password)
        user = User(email=data.email, password=hashed_password)
        created_user = await self.repo.create(user)
        return UserResponse.model_validate(created_user)

    async def get_user_by_id(self, id_: str | UUID) -> User | None:
        return await self.repo.get(User.id == id_)

    async def get_user_by_email(self, email: str) -> User | None:
        return await self.repo.get(func.lower(User.email) == func.lower(email))

    def _hash_password(self, password: str) -> str:
        return self._ph.hash(password)

    def verify_password(self, raw_password: str, hashed_password: str) -> bool:
        try:
            return self._ph.verify(hashed_password, raw_password)
        except VerifyMismatchError:
            return False


class AuthenticationService:
    def __init__(self, user_service: Annotated[UserService, Depends()]):
        self.user_service = user_service

    def _create_access_token(
        self, user_id: str | UUID, expiry: timedelta | None = None
    ) -> str:
        payload = {
            "user_id": str(user_id),
            "exp": time.time()
            + (
                expiry.total_seconds()
                if expiry
                else settings.ACCESS_TOKEN_EXPIRY_SECONDS
            ),
        }

        return jwt.encode(
            payload=payload, key=settings.ACCESS_TOKEN_SECRET_KEY, algorithm="HS256"
        )

    def _get_user_id_from_access_token(self, token: str) -> str:
        try:
            decoded_token = jwt.decode(
                token,
                key=settings.ACCESS_TOKEN_SECRET_KEY,
                algorithms=["HS256"],
            )

            return decoded_token.get("user_id", None)
        except Exception:
            return None

    async def generate_access_token_for_user(self, email: str, password: str) -> str:
        user: User = await self.user_service.get_user_by_email(email)

        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
            )

        if not self.user_service.verify_password(password, user.password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
            )

        return self._create_access_token(user.id)

    async def get_user_from_access_token(self, access_token: str) -> User | None:
        user_id = self._get_user_id_from_access_token(access_token)

        if not user_id:
            return None

        return await self.user_service.get_user_by_id(user_id)

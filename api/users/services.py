from datetime import timedelta
from typing import Annotated
from uuid import UUID
from argon2 import PasswordHasher
import time
import jwt
from fastapi import Depends, status
from fastapi import HTTPException
from sqlalchemy.engine.result import ScalarResult
from argon2.exceptions import VerifyMismatchError
from sqlalchemy import select
from api.database.dependencies import AsyncSession
from api.users.models import User
from api.users.schemas import UserIn, UserOut
from api.config import settings
from sqlalchemy import func


class UserService:
    def __init__(self, session: AsyncSession):
        self.async_session = session
        self._ph = PasswordHasher()

    async def create_user(self, data: UserIn) -> UserOut:
        async with self.async_session.begin() as session:
            if await self.get_user_by_email(data.email):
                raise HTTPException(
                    detail="User already exists.",
                    status_code=status.HTTP_400_BAD_REQUEST,
                )

            hashed_password = self._hash_password(data.password)
            user = User(email=data.email, password=hashed_password)

            session.add(user)
            await session.flush()
            await session.refresh(user)

            return UserOut.model_validate(user)

    async def get_user_by_email(self, email: str) -> User | None:
        async with self.async_session.begin() as session:
            result: ScalarResult = (
                await session.execute(
                    select(User).where(func.lower(User.email) == func.lower(email))
                )
            ).scalars()

            return result.one_or_none()

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

    async def generate_access_token_for_user(self, email: str, password: str) -> str:
        user: User = await self.user_service.get_user_by_email(email)

        if not user:
            raise HTTPException(
                detail="No active account found with given credentials.",
                status_code=status.HTTP_401_UNAUTHORIZED,
            )

        if not self.user_service.verify_password(password, user.password):
            raise HTTPException(
                detail="No active account found with given credentials.",
                status_code=status.HTTP_401_UNAUTHORIZED,
            )

        return self._create_access_token(user.id)

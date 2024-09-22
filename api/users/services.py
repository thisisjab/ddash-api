from argon2 import PasswordHasher

from fastapi import status
from fastapi import HTTPException
from sqlalchemy.engine.result import ScalarResult
from argon2.exceptions import VerifyMismatchError
from sqlalchemy import select
from api.database.dependencies import AsyncSession
from api.users.models import User
from api.users.schemas import UserIn, UserOut
from sqlalchemy import func


class UserService:
    def __init__(self, session: AsyncSession):
        self.async_session = session
        self._ph = PasswordHasher()

    async def create_user(self, data: UserIn) -> UserOut:
        async with self.async_session.begin() as session:
            if await self.check_user_exists_by_email(data.email):
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

    async def check_user_exists_by_email(self, email: str) -> bool:
        async with self.async_session.begin() as session:
            result: ScalarResult = (
                await session.execute(
                    select(User).where(func.lower(User.email) == func.lower(email))
                )
            ).scalars()

            return bool(result.one_or_none())

    def _hash_password(self, password: str) -> str:
        return self._ph.hash(password)

    def _verify_password(self, raw_password: str, hashed_password: str) -> bool:
        try:
            return self._ph.verify(hashed_password, raw_password)
        except VerifyMismatchError:
            return False

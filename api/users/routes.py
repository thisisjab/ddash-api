from typing import Annotated
from fastapi import Depends
from fastapi.routing import APIRouter

from api.users.schemas import UserIn
from api.users.services import UserService

users_router = APIRouter(prefix="/users", tags=["Users"])


@users_router.post("")
async def create_single_user(data: UserIn, service: Annotated[UserService, Depends()]):
    return await service.create_user(data)


router = APIRouter()
router.include_router(users_router)

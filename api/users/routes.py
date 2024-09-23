from typing import Annotated
from fastapi import Depends
from fastapi.routing import APIRouter

from api.users.schemas import AccessTokenIn, AccessTokenOut, UserIn
from api.users.services import AuthenticationService, UserService

auth_router = APIRouter(prefix="/auth", tags=["Auth"])
users_router = APIRouter(prefix="/users", tags=["Users"])


@auth_router.post("/token", response_model=AccessTokenOut)
async def obtain_access_token(
    data: AccessTokenIn, service: Annotated[AuthenticationService, Depends()]
):
    access_key = await service.generate_access_token_for_user(data.email, data.password)
    return {"access": access_key}


@users_router.post("")
async def create_single_user(data: UserIn, service: Annotated[UserService, Depends()]):
    return await service.create_user(data)


router = APIRouter()
router.include_router(auth_router)
router.include_router(users_router)

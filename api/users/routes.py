from typing import Annotated

from fastapi import Depends, status
from fastapi.routing import APIRouter

from api.users.auth.dependencies import AuthenticatedUser
from api.users.schemas import (
    AccessTokenRequest,
    AccessTokenResponse,
    UserRequest,
    UserResponse,
)
from api.users.services import AuthenticationService, UserService

auth_router = APIRouter(prefix="/auth", tags=["Auth"])
users_router = APIRouter(prefix="/users", tags=["Users"])


@auth_router.post("/token", response_model=AccessTokenResponse)
async def obtain_access_token(
    data: AccessTokenRequest, service: Annotated[AuthenticationService, Depends()]
):
    access_key = await service.generate_access_token_for_user(data.email, data.password)
    return {"access": access_key}


@users_router.post("", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def create_single_user(
    data: UserRequest, service: Annotated[UserService, Depends()]
):
    return await service.create_user(data)


@users_router.get("/me", response_model=UserResponse, status_code=status.HTTP_200_OK)
async def get_user_self(user: AuthenticatedUser):
    return user


router = APIRouter()
router.include_router(auth_router)
router.include_router(users_router)

from typing import Annotated

from fastapi import Depends, status
from fastapi.security import HTTPAuthorizationCredentials
from fastapi.security.api_key import HTTPException

from api.users.auth import JWTBearer
from api.users.models import User
from api.users.services import AuthenticationService

jwt_bearer = JWTBearer()


async def authenticated_user(
    service: Annotated[AuthenticationService, Depends()],
    credentials: Annotated[HTTPAuthorizationCredentials, Depends(jwt_bearer)],
) -> User:
    user = await service.get_user_from_access_token(
        access_token=credentials.credentials,
    )

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="No active account was found with this token or token expired.",
        )

    return user


AuthenticatedUser = Annotated[User, Depends(authenticated_user)]

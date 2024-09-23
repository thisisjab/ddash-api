from fastapi import status
from fastapi.exceptions import HTTPException
from fastapi.requests import Request
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer


class JWTBearer(HTTPBearer):
    def __init__(self, auto_error: bool = True):
        super(JWTBearer, self).__init__(auto_error=auto_error)

    async def __call__(self, request: Request):
        credentials: HTTPAuthorizationCredentials = await super(
            JWTBearer, self
        ).__call__(request)

        if credentials:
            if not credentials.scheme == "Bearer":
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid authentication scheme.",
                )

            # NOTE: token is validated in security dependencies.
            return credentials
        else:
            raise HTTPException(
                status_code=status.H401, detail="Invalid authorization code."
            )

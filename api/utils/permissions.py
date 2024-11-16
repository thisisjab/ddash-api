from typing import Annotated, Any, Callable

from fastapi import HTTPException, status


async def check_permission(
    permission: Callable[..., Any], **kwargs: Annotated[Any, "kwargs from permission"]
) -> None:
    """Raise exception if permission is not satisfied.

    Args:
        permission (Callable): Permission callable.

        kwargs (Any): Kwargs to call permission callable with.

    Raises:
        HTTPException: If permission denied.
    """

    allowed = await permission(**kwargs)

    if not allowed:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN)

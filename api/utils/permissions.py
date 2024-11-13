import functools
from typing import Callable

from fastapi import HTTPException, status


def permission_decorator(raise_exception: bool = True) -> Callable:
    """Global decorator for permission checker functions.

    Args:
        raise_exception (bool): Whether to raise a `HTTPException(status_code=403)`
                                 instead of returning False.

    Returns:
        callable: The decorator function.
    """

    # NOTE: func must be async
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            result = await func(*args, **kwargs)

            if not result:
                if raise_exception:
                    raise HTTPException(status_code=status.HTTP_403_FORBIDDEN)

                return False

            return result

        return wrapper

    return decorator

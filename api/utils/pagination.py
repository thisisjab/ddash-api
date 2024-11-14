import math
from typing import Annotated, Generic, TypeVar

from fastapi import HTTPException, Query, status
from pydantic import BaseModel, Field
from sqlalchemy import func
from sqlalchemy.ext.asyncio import async_sessionmaker
from sqlalchemy.sql.expression import Select

T = TypeVar("T", bound=BaseModel)
DEFAULT_PER_PAGE = 10


class PaginationParams(BaseModel):
    page_size: int = Field(ge=1, le=50, default=DEFAULT_PER_PAGE)
    page: int = Field(gt=0, default=1)


PaginationQueryParams = Annotated[PaginationParams, Query()]


class PaginatedResponse(BaseModel, Generic[T]):
    total_pages: int = 0
    current_page: int = 1
    count: int = 0
    page_size: int = DEFAULT_PER_PAGE
    items: list[T] = []


async def paginate[T](
    query: Select,
    session: async_sessionmaker,
    pagination_params: PaginationParams,
    serialize_items: bool = True,
) -> PaginatedResponse[T] | dict:
    """Paginate a query.

    Args:
        query (Select): Select query.
        session (async_sessionmaker): Session maker class used for counting result.
        pagination_params (PaginationParams): Pagination params passed from request.
            HTTPException is raised when invalid page is accessed.
        serialize_items (bool, optional): Serializer pydantic object or not.
            If False, user should take care of data serialization as
            `counts` and `items` field will be empty. Defaults to True.

    Raises:
        NotImplementedError: When query type is not select.
        HTTPException: When invalid pages is accessed.

    Returns:
        PaginatedResponse: A paginated response object.
    """
    async with session() as ac:
        if isinstance(query, Select):
            count_query = query.with_only_columns(func.count()).order_by(None)
            count_result = await ac.execute(count_query)
            items_count = count_result.scalar()
        else:
            raise NotImplementedError("Pagination query is not supported.")

        response = dict()

        response["page_size"] = pagination_params.page_size
        response["total_pages"] = math.ceil(items_count / pagination_params.page_size)

        if pagination_params.page > response["total_pages"] != 0:
            raise HTTPException(
                detail="Invalid page.", status_code=status.HTTP_400_BAD_REQUEST
            )

        response["current_page"] = pagination_params.page
        limit = pagination_params.page_size
        offset = (pagination_params.page - 1) * limit
        query = query.limit(limit).offset(offset)

        if serialize_items:
            items_result = (await ac.execute(query)).scalars().all()
            response["items"] = items_result
            response["count"] = len(items_result)
            return PaginatedResponse[T](**response)

        items_result = (await ac.execute(query)).all()
        response["items"] = items_result
        response["count"] = len(items_result)
        return response

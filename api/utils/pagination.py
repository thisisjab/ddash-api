import math
from typing import Annotated, Generic, Self, TypeVar

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

    async def paginate(
        self,
        query: Select,
        session: async_sessionmaker,
        pagination_params: PaginationParams,
    ) -> Self:
        async with session() as ac:
            if isinstance(query, Select):
                count_query = query.with_only_columns(func.count()).order_by(None)
                count_result = await ac.execute(count_query)
                items_count = count_result.scalar()
            else:
                raise NotImplementedError("Pagination query is not supported.")

            self.page_size = pagination_params.page_size
            self.total_pages = math.ceil(items_count / pagination_params.page_size)

            if pagination_params.page > self.total_pages != 0:
                raise HTTPException(
                    detail="Invalid page.", status_code=status.HTTP_400_BAD_REQUEST
                )

            self.current_page = pagination_params.page
            limit = pagination_params.page_size
            offset = (pagination_params.page - 1) * limit
            query = query.limit(limit).offset(offset)
            items_result = (await ac.execute(query)).scalars().all()
            self.items = items_result
            self.count = len(items_result)
            return self


#

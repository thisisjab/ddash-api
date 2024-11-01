from typing import Annotated, Generic, Self, TypeVar

from fastapi import Query
from pydantic import BaseModel, Field
from sqlalchemy import ClauseElement

from api.database.repository import RepositoryBase

T = TypeVar("T", bound=BaseModel)


class PaginationParams(BaseModel):
    per_page: int = Field(gt=1, lt=50, default=10)
    page: int = Field(gt=0, default=1)


PaginationQueryParams = Annotated[PaginationParams, Query()]


class PaginatedResponse(BaseModel, Generic[T]):
    total_pages: int = 0
    current_page: int = 1
    count: int = 0
    items: list[T] = []

    async def paginate(
        self,
        repo: RepositoryBase,
        per_page: int = 25,
        page: int = 1,
        filter_clauses: list[ClauseElement] = [],
        order_clauses: list[ClauseElement] = [],
    ) -> Self:
        items_count = await repo.get_all_count()
        self.total_pages = (items_count // per_page) + 1
        self.current_page = page
        limit = per_page
        offset = (page - 1) * per_page
        self.items = await repo.get_all(
            limit=limit,
            offset=offset,
            filter_clauses=filter_clauses,
            order_clauses=order_clauses,
        )
        self.count = len(self.items)
        return self

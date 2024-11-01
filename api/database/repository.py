from typing import List, Optional

from sqlalchemy import func, select
from sqlalchemy.sql.expression import ClauseElement
from sqlalchemy.sql.selectable import Select

from api.database.dependencies import AsyncSession


class RepositoryBase:
    """Base class for all repositories."""

    model = None

    def __init__(self, session: AsyncSession) -> None:
        self.async_session = session

    async def get_all(
        self,
        limit: Optional[int] = None,
        offset: Optional[int] = None,
        filter_clauses: List[ClauseElement] = [],
        order_clauses: List[ClauseElement] = [],
    ) -> Select:
        async with self.async_session.begin() as session:
            q = select(self.model)

            if filter_clauses:
                q = q.filter(*filter_clauses)

            if order_clauses:
                q = q.order_by(*order_clauses)

            if limit:
                q = q.limit(limit)

            if offset:
                q = q.offset(offset)

            result = await session.execute(q)
            return result.scalars().all()

    async def get_all_count(
        self,
        limit: Optional[int] = None,
        offset: Optional[int] = None,
        filter_clauses: List[ClauseElement] = [],
        order_clauses: List[ClauseElement] = [],
    ) -> Select:
        async with self.async_session.begin() as session:
            q = select(func.count())

            if filter_clauses:
                q = q.filter(*filter_clauses)

            if order_clauses:
                q = q.order_by(*order_clauses)

            if limit:
                q = q.limit(limit)

            if offset:
                q = q.offset(offset)

            q = q.select_from(self.model)

            result = await session.execute(q)
            return result.scalar()

    async def get(self, *filter_clauses: list[ClauseElement]):
        async with self.async_session.begin() as session:
            query = select(self.model)

            if len(filter_clauses) < 1:
                raise Exception("Cannot use get without passing filter clauses.")

            query = query.filter(*filter_clauses)

            result = await session.execute(query)
            return result.scalars().one_or_none()

    async def create(self, obj):
        async with self.async_session.begin() as session:
            session.add(obj)
            await session.flush()
            await session.refresh(obj)
            return obj

    async def update(self, obj):
        async with self.async_session.begin() as session:
            session.add(obj)
            await session.flush()
            await session.refresh(obj)
            return obj

    async def delete(self, obj) -> None:
        async with self.async_session.begin() as session:
            session.delete(obj)
            await session.flush()

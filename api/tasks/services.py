from uuid import UUID

from sqlalchemy import select

from api.database.dependencies import AsyncSession
from api.tasks.models import Task
from api.tasks.schemas import TaskPaginationItem
from api.utils.pagination import PaginatedResponse, PaginationParams, paginate


class TaskService:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_tasks_for_project(
        self, project_id: UUID, pagination_params: PaginationParams
    ) -> PaginatedResponse[TaskPaginationItem]:
        query = select(Task).where(Task.project_id == project_id)
        return await paginate(query, self.session, pagination_params)

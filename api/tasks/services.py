from uuid import UUID

from sqlalchemy import select

from api.database.dependencies import AsyncSession
from api.tasks.models import Task, TaskAssignee
from api.tasks.schemas import TaskPaginationItem
from api.users.models import User
from api.utils.pagination import PaginatedResponse, PaginationParams, paginate


class TaskService:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_tasks_for_project(
        self, project_id: UUID, pagination_params: PaginationParams
    ) -> PaginatedResponse[TaskPaginationItem]:
        tasks_query = (
            select(Task)
            .where(Task.project_id == project_id)
            .order_by(Task.created_at.desc())
        )

        paginated_result = await paginate(
            tasks_query, self.session, pagination_params, serialize_items=False
        )

        fetched_tasks = []
        task_ids_to_fetch = []

        for t in paginated_result["items"]:
            fetched_tasks.append(t[0])
            task_ids_to_fetch.append(t[0].id)

        assignees_query = (
            select(TaskAssignee, User)
            .join(TaskAssignee, TaskAssignee.user_id == User.id)
            .where(TaskAssignee.task_id.in_(task_ids_to_fetch))
        )

        async with self.session() as ac:
            assignees = await ac.execute(assignees_query)
            assignees_list = assignees.all()

        items = []

        for t in fetched_tasks:
            task_assignees = []

            for row in assignees_list:
                task_assignee, user = row

                if task_assignee.task_id == t.id:
                    task_assignees.append(user)

            t.assignees = task_assignees
            items.append(TaskPaginationItem.model_validate(t))

        paginated_result["items"] = items

        return paginated_result

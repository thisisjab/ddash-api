from uuid import UUID

from sqlalchemy import select

from api.database.dependencies import AsyncSession
from api.orgs.models import Organization
from api.projects.models import Project
from api.tasks.models import Task, TaskAssignee
from api.tasks.schemas import TaskResponse
from api.users.models import User
from api.utils.pagination import PaginatedResponse, PaginationParams, paginate


class TaskService:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_tasks_for_project(
        self, project_id: UUID, pagination_params: PaginationParams
    ) -> PaginatedResponse[TaskResponse]:
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
            items.append(TaskResponse.model_validate(t))

        paginated_result["items"] = items

        return paginated_result

    async def create_task(self, task: Task) -> Task:
        async with self.session.begin() as ac:
            ac.add(task)
            await ac.flush()
            await ac.refresh(task)
            return task

    async def get_task_with_project_and_organization_and_assignees(
        self,
        task_id: UUID,
    ) -> tuple[Task, list[User], Project, Organization] | None:
        task_query = (
            select(Task, Project, Organization)
            .select_from(Task)
            .join(Project, Project.id == Task.project_id)
            .join(Organization, Organization.id == Project.organization_id)
            .where(Task.id == task_id)
        )
        assignees_query = (
            select(TaskAssignee, User)
            .select_from(TaskAssignee)
            .join(User, User.id == TaskAssignee.user_id)
            .where(TaskAssignee.task_id == task_id)
            .order_by(TaskAssignee.created_at.desc())
        )

        async with self.session() as ac:
            result = (await ac.execute(task_query)).one_or_none()

            if not result:
                return None

            task: Task = result[0]
            project: Project = result[1]
            organization: Organization = result[2]

            task_assignees_result = (await ac.execute(assignees_query)).all()
            assignees: list[User] = [item[1] for item in task_assignees_result]

            return task, assignees, project, organization
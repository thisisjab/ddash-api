from typing import Annotated

from fastapi import Depends

from api.orgs.models import Organization
from api.orgs.permissions import OrganizationPermissionService
from api.tasks.models import Task
from api.tasks.services import TaskService
from api.users.models import User


class TaskPermissionService:
    def __init__(
        self,
        organization_permission_service: Annotated[
            OrganizationPermissionService, Depends()
        ],
        task_service: Annotated[TaskService, Depends()],
    ) -> None:
        self.organization_permission_service = organization_permission_service
        self.task_service = task_service

    async def is_task_assignee(self, task: Task, user: User) -> bool:
        if not (task and user):
            return False

        task_assignee = await self.task_service.get_task_assignee(task.id, user.id)

        if task_assignee:
            return True

        return False

    async def is_task_assignee_or_organization_manager(
        self,
        task: Task,
        user: User,
        organization: Organization,
    ):
        if not (task and user):
            return False

        is_task_assignee = await self.is_task_assignee(task, user)

        if is_task_assignee:
            return True

        is_organization_manager = (
            await self.organization_permission_service.is_organization_manager(
                organization, user
            )
        )

        if is_organization_manager:
            return True

        return False

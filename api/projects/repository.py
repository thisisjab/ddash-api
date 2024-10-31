from api.database.repository import RepositoryBase
from api.projects.models import Project


class ProjectRepository(RepositoryBase):
    model = Project

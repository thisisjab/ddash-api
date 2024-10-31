from api.database.repository import RepositoryBase
from api.users.models import User


class UserRepository(RepositoryBase):
    model = User

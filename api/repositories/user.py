from api.models import User
from api.repositories.base import BaseRepository


class UserRepository(BaseRepository):
    model = User

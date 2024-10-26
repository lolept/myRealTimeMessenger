from api.models import Chat, Message
from api.repositories.base import BaseRepository


class ChatRepository(BaseRepository):
    model = Chat


class MessageRepository(BaseRepository):
    model = Message

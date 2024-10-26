from api.dependencies.redis import get_redis_service
from api.repositories import MessageRepository, ChatRepository, UserRepository
from api.services import ChatService


def get_chat_service():
    return ChatService(
        message_repository=MessageRepository(),
        chat_repository=ChatRepository(),
        redis_service=get_redis_service(),
        user_repository=UserRepository(),
    )

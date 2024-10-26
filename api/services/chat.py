import json
from enum import Enum
from functools import wraps
from typing import Callable

from fastapi import WebSocket, WebSocketDisconnect

from api.exceptions import ChatHTTPExceptions
from api.exceptions.base import BaseWebSocketException
from api.exceptions.chat import ChatWebSocketExceptions
from api.models import Message
from api.repositories import MessageRepository, ChatRepository, UserRepository
from api.schemas import ChatCreateSchema, ChatReadSchema, UserReadSchema, MessagePreviewSchema, MessageCreateSchema
from api.services.redis import RedisService


def exception_handler(func: Callable) -> Callable:
    @wraps(func)
    async def wrapper(*args, **kwargs):
        try:
            return await func(*args, **kwargs)
        except BaseWebSocketException as e:
            await ConnectionManager.send_exception(*args[0], e)
            raise
    
    return wrapper


class ConnectionType(Enum):
    HTTP = 1
    WEBSOCKET = 2


class ChatService:
    
    def __init__(self,
                 message_repository: MessageRepository,
                 chat_repository: ChatRepository,
                 redis_service: RedisService,
                 user_repository: UserRepository, ):
        self.message_repository = message_repository
        self.chat_repository = chat_repository
        self.redis_service = redis_service
        self.user_repository = user_repository
    
    async def _get_messages_previews(self, chat_id: int) -> list[MessagePreviewSchema]:
        messages = await self.message_repository.get_all(sorting_filters=[Message.created.desc()], limit=50,
                                                         chat_id=chat_id)
        message_previews = []
        for message in messages:
            user = await self.user_repository.get_one_or_none(id=message.user_id)
            message_previews.append(MessagePreviewSchema(**message.dict(), user_email=user.email))
        return message_previews
    
    async def _save_message_to_redis(self, chat_id: int, message: MessagePreviewSchema) -> None:
        messages_string = await self.redis_service.get(chat_id)
        if not messages_string:
            messages_string = ""
        else:
            messages_string = ';' + messages_string
        messages_string = json.dumps(message.dict()) + messages_string
        await self.redis_service.set(chat_id, messages_string)
    
    async def _save_messages_to_redis(self, chat_id: int) -> None:
        message_previews = await self._get_messages_previews(chat_id)
        message_string = ';'.join(map(lambda msg: json.dumps(msg.dict()), message_previews))
        await self.redis_service.set(chat_id, message_string)
    
    async def _get_messages_from_redis(self, chat_id: id) -> list[MessagePreviewSchema] | None:
        messages_string = await self.redis_service.get(chat_id)
        if messages_string:
            messages_strings = (await self.redis_service.get(chat_id)).split(';')
            messages = []
            for message_str in messages_strings:
                messages.append(MessagePreviewSchema(**json.loads(message_str)))
            return messages
        return None
    
    async def create_chat(self, chat: ChatCreateSchema, user: UserReadSchema) -> ChatReadSchema:
        return await self.chat_repository.insert(name=chat.name, user_ids=[user.id, ])
    
    async def get_chat(self, chat_id: id, connection_type: ConnectionType = ConnectionType.HTTP) -> ChatReadSchema:
        chat = await self.chat_repository.get_one_or_none(id=chat_id)
        if chat is None:
            if connection_type == ConnectionType.HTTP:
                raise ChatHTTPExceptions.ChatNotFoundException(chat_id=chat_id)
            else:
                raise ChatWebSocketExceptions.ChatNotFoundException(chat_id=chat_id)
        return chat
    
    async def read_messages(self,
                            chat_id: id,
                            user: UserReadSchema,
                            connection_type: ConnectionType = ConnectionType.HTTP) -> list[MessagePreviewSchema]:
        chat = await self.get_chat(chat_id, connection_type)
        if user.id not in chat.user_ids:
            if connection_type == ConnectionType.HTTP:
                raise ChatHTTPExceptions.UserNotInChatException(email=user.email, chat_id=chat.id)
            else:
                raise ChatWebSocketExceptions.UserNotInChatException(email=user.email, chat_id=chat.id)
        messages = await self._get_messages_from_redis(chat_id=chat_id)
        if messages:
            return messages
        await self._save_messages_to_redis(chat_id)
        return await self._get_messages_previews(chat_id)
    
    async def on_update(self, websocket: WebSocket, chat_id: int, user: UserReadSchema) -> None:
        await websocket.accept()
        chat = await self.get_chat(chat_id, ConnectionType.WEBSOCKET)
        if user.id not in chat.user_ids:
            raise ChatWebSocketExceptions.UserNotInChatException(email=user.email, chat_id=chat.id)
        manager = ConnectionManager()
        await manager.connect(websocket, chat_id)
        try:
            while True:
                received_message: MessageCreateSchema = await websocket.receive_json()
                inserted_message = await self.message_repository.insert(
                    **received_message.dict(),
                    user_id=user.id,
                )
                message_preview = MessagePreviewSchema(**inserted_message.dict(), user_email=user.email)
                await manager.broadcast(message_preview)
                await self._save_message_to_redis(chat_id, message_preview)
        except WebSocketDisconnect:
            await manager.disconnect(websocket, chat_id)


class ConnectionManager:
    active_connections: dict[int, list[WebSocket]] = {}
    
    @classmethod
    async def connect(cls, websocket: WebSocket, chat_id: int) -> None:
        if chat_id not in cls.active_connections.keys():
            cls.active_connections[chat_id] = []
        if websocket not in cls.active_connections[chat_id]:
            cls.active_connections[chat_id].append(websocket)
    
    @classmethod
    async def disconnect(cls, websocket: WebSocket, chat_id: int) -> None:
        if chat_id not in cls.active_connections.keys():
            cls.active_connections[chat_id] = []
        cls.active_connections[chat_id].remove(websocket)
    
    @classmethod
    async def broadcast(cls, message: MessagePreviewSchema) -> None:
        for connection in cls.active_connections[message.chat_id]:
            await connection.send_json(message.dict())
    
    @staticmethod
    async def send_exception(websocket: WebSocket, exception: BaseWebSocketException) -> None:
        await websocket.accept()
        await websocket.send_json(exception.dict())
        await websocket.close()

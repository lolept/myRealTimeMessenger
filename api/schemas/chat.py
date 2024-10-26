from datetime import datetime

from pydantic import BaseModel


class MessageCreateSchema(BaseModel):
    chat_id: int
    text: str


class MessageReadSchema(BaseModel):
    id: int
    chat_id: int
    user_id: int
    text: str
    created: datetime
    modified: datetime


class MessagePreviewSchema(BaseModel):
    id: int
    chat_id: int
    user_email: str
    text: str
    created: str
    modified: str


class ChatCreateSchema(BaseModel):
    name: str


class ChatReadSchema(BaseModel):
    id: int
    name: str
    user_ids: list[int]
    created: datetime
    modified: datetime
from fastapi import APIRouter, WebSocket, Depends, Request
from fastapi.templating import Jinja2Templates

from api.dependencies import get_current_active_user
from api.dependencies.chat import get_chat_service
from api.exceptions import AuthHTTPExceptions, ChatHTTPExceptions, BaseHTTPExceptionsContainer
from api.schemas import ChatCreateSchema, ChatReadSchema, UserReadSchema, MessagePreviewSchema
from api.services import ChatService

router = APIRouter(
    prefix="/chat",
    tags=["Chat"],
)


@router.post('/', responses=AuthHTTPExceptions.get_responses_dict([
    AuthHTTPExceptions.UserInactiveException,
    AuthHTTPExceptions.UnauthorisedException,
]))
async def create_chat(
        chat: ChatCreateSchema,
        chat_service: ChatService = Depends(get_chat_service),
        user: UserReadSchema = Depends(get_current_active_user)
) -> ChatReadSchema:
    return await chat_service.create_chat(chat, user)


@router.get('/{chat_id}')
async def read_chat(
        chat_id: int,
        chat_service: ChatService = Depends(get_chat_service)
) -> ChatReadSchema:
    return await chat_service.get_chat(chat_id)


@router.get('/{chat_id}/messages',
            responses=BaseHTTPExceptionsContainer.get_responses_dict([
                AuthHTTPExceptions.UserInactiveException,
                AuthHTTPExceptions.UnauthorisedException,
                ChatHTTPExceptions.ChatNotFoundException,
                ChatHTTPExceptions.UserNotInChatException
            ]))
async def read_messages(
        chat_id: int,
        chat_service: ChatService = Depends(get_chat_service),
        user: UserReadSchema = Depends(get_current_active_user)
) -> list[MessagePreviewSchema]:
    return await chat_service.read_messages(chat_id, user)


@router.get("/")
def get_chat_page(request: Request):  # Temporary
    templates = Jinja2Templates(directory=r"frontend\templates")
    return templates.TemplateResponse("chat.html", {"request": request})


@router.websocket("/ws/{chat_id}")
async def websocket_endpoint(websocket: WebSocket, chat_id: int,
                             chat_service: ChatService = Depends(get_chat_service),
                             user: UserReadSchema = Depends(get_current_active_user)) -> None:
    await chat_service.on_update(websocket, chat_id, user)

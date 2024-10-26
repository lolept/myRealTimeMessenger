from fastapi import Cookie, Depends, Request, WebSocket

from api.config import settings
from api.dependencies import get_auth_jwt_service
from api.exceptions import AuthHTTPExceptions
from api.exceptions.auth import AuthWebSocketExceptions
from api.repositories import UserRepository
from api.schemas import UserReadSchema
from api.services import JWTService


async def get_current_user(
        request: Request = None,
        ws: WebSocket = None,
        token: str = Cookie(default=None, alias=settings.AUTH_COOKIE_NAME),
        jwt_service: JWTService = Depends(get_auth_jwt_service),
) -> UserReadSchema:
    if not token:
        if request:
            raise AuthHTTPExceptions.UnauthorisedException()
        elif ws:
            raise AuthWebSocketExceptions.UnauthorisedException()
    data = await jwt_service.read_jwt(token)
    user_mail: str = data.get("sub")
    if user_mail is None:
        if request:
            raise AuthHTTPExceptions.UnauthorisedException()
        elif ws:
            await ws.accept()
            raise AuthWebSocketExceptions.UnauthorisedException()
    user = await UserRepository().get_one_or_none(email=user_mail)
    if user is None:
        if request:
            raise AuthHTTPExceptions.UnauthorisedException()
        elif ws:
            await ws.accept()
            raise AuthWebSocketExceptions.UnauthorisedException()
    return user


async def get_current_active_user(
        request: Request = None,
        ws: WebSocket = None,
        current_user: UserReadSchema = Depends(get_current_user),
) -> UserReadSchema:
    if not current_user.is_verified:
        if request:
            raise AuthHTTPExceptions.UserInactiveException(email=current_user.email)
        elif ws:
            await ws.accept()
            raise AuthWebSocketExceptions.UserInactiveException(email=current_user.email)
    return current_user

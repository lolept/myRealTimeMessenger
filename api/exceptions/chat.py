from fastapi import status, WebSocketException

from api.exceptions import BaseHTTPExceptionsContainer, BaseHTTPException
from api.exceptions.base import BaseWebSocketExceptionsContainer, BaseWebSocketException


class ChatHTTPExceptions(BaseHTTPExceptionsContainer):
    class ChatNotFoundException(BaseHTTPException):
        status_code = status.HTTP_404_NOT_FOUND
        status_name = "Not Found"
        summary = 'Chat not found'
        detail = 'Chat with id {chat_id} not found'
        
        def __init__(self, chat_id):
            super().__init__(
                chat_id=chat_id
            )
    
    class UserNotInChatException(BaseHTTPException):
        status_code = status.HTTP_400_BAD_REQUEST
        status_name = "Bad Request"
        summary = 'User is not in chat'
        detail = 'User {email} is not in chat with id {chat_id}'
        
        def __init__(self, email, chat_id):
            super().__init__(
                email=email,
                chat_id=chat_id
            )


class ChatWebSocketExceptions(BaseWebSocketExceptionsContainer):
    class ChatNotFoundException(BaseWebSocketException):
        status_code = status.WS_1002_PROTOCOL_ERROR
        detail = 'Chat with id {chat_id} not found'
        
        def __init__(self, chat_id):
            super().__init__(
                chat_id=chat_id
            )
    
    class UserNotInChatException(BaseWebSocketException):
        status_code = status.WS_1002_PROTOCOL_ERROR
        detail = 'User {email} is not in chat with id {chat_id}'
        
        def __init__(self, email, chat_id):
            super().__init__(
                email=email,
                chat_id=chat_id
            )
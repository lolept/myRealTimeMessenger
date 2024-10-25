from fastapi import status

from api.config import settings
from .base import BaseHTTPException, BaseHTTPExceptionsContainer


class AuthHTTPExceptions(BaseHTTPExceptionsContainer):
    class IncorrectPasswordLengthException(BaseHTTPException):
        status_code = status.HTTP_422_UNPROCESSABLE_ENTITY
        status_name = "Validation error"
        summary = 'Incorrect password length'
        min_length = settings.PASSWORD_MIN_LENGTH
        max_length = settings.PASSWORD_MAX_LENGTH
        detail = f'The password length must be between {min_length} and {max_length} characters'
    
    class InvalidEmailFormatException(BaseHTTPException):
        status_code = status.HTTP_422_UNPROCESSABLE_ENTITY
        status_name = "Validation error"
        detail = f'The value must be a proper email address'
        summary = 'Incorrect email format'
    
    class UserAlreadyExistsException(BaseHTTPException):
        status_code = status.HTTP_400_BAD_REQUEST
        status_name = "Bad request"
        detail = 'User with email {email} already exists'
        summary = 'User already exists'
        
        def __init__(self, email: str):
            super().__init__(
                email=email
            )
    
    class EmailErrorException(BaseHTTPException):
        status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
        status_name = "Internal server error"
        detail = 'There was an error while sending an email'
        summary = 'Email error'

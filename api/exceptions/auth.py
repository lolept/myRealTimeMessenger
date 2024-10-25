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
    
    class InvalidVerificationCodeException(BaseHTTPException):
        status_code = status.HTTP_400_BAD_REQUEST
        status_name = "Bad request"
        detail = 'The verification code is invalid'
        summary = 'Invalid verification code'
    
    class UserDoesNotExistException(BaseHTTPException):
        status_code = status.HTTP_404_NOT_FOUND
        status_name = "Not found"
        detail = 'User with email {email} does not exist'
        summary = 'User does not exist'
        
        def __init__(self, email: str):
            super().__init__(
                email=email
            )
    
    class WrongPasswordException(BaseHTTPException):
        status_code = status.HTTP_403_FORBIDDEN
        status_name = "Forbidden"
        detail = 'Wrong password'
        summary = 'Wrong password'
    
    class UserInactiveException(BaseHTTPException):
        status_code = status.HTTP_403_FORBIDDEN
        status_name = "Forbidden"
        detail = 'User {email} is not verified'
        summary = 'User is not verified'
        
        def __init__(self, email: str):
            super().__init__(
                email=email
            )
    
    class UnauthorisedException(BaseHTTPException):
        status_code = status.HTTP_401_UNAUTHORIZED
        status_name = "Unauthorized"
        detail = 'Unauthorized'
        summary = 'Unauthorized'

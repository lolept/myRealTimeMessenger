from fastapi import status

from api.exceptions import BaseHTTPExceptionsContainer, BaseHTTPException


class JWTHTTPExceptions(BaseHTTPExceptionsContainer):
    class InvalidJWTException(BaseHTTPException):
        status_code = status.HTTP_400_BAD_REQUEST
        status_name = "Bad request"
        summary = 'Invalid JWT'
        detail = 'Invalid JWT'

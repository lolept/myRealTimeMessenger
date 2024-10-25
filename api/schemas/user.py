import re
from datetime import datetime

from pydantic import BaseModel, field_validator

from api.config import settings
from api.exceptions import AuthHTTPExceptions


class UserReadSchema(BaseModel):
    id: int
    email: str
    is_verified: bool
    created: datetime
    modified: datetime
    
    class Config:
        from_attributes = True


class UserCreateSchema(BaseModel):
    email: str
    password: str
    
    @field_validator("email")
    def validate_value(cls, email):
        if not re.match(r"^\S+@\S+\.\S+$", email):
            raise AuthHTTPExceptions.InvalidEmailFormatException()
        return email
    
    @field_validator("password")
    def validate_value(cls, password):
        if not (settings.PASSWORD_MIN_LENGTH < len(password) < settings.PASSWORD_MAX_LENGTH):
            raise AuthHTTPExceptions.IncorrectPasswordLengthException()
        return password


class ChangePassword(BaseModel):
    old_password: str
    new_password: str


class UserUpdateSchema(BaseModel):
    password: str


class RemainingMessagesSchema(BaseModel):
    messages: int
    images: int

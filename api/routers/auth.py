from fastapi import APIRouter, Depends, Request

from api.dependencies import get_auth_service, get_mailing_service
from api.exceptions import AuthHTTPExceptions
from api.schemas import UserCreateSchema, UserReadSchema
from api.services import AuthService, MailingService

router = APIRouter(
    prefix="/auth",
    tags=["Auth"],
)


@router.post('/register', responses=AuthHTTPExceptions.get_responses_dict([
    AuthHTTPExceptions.UserAlreadyExistsException,
    AuthHTTPExceptions.IncorrectPasswordLengthException,
    AuthHTTPExceptions.InvalidEmailFormatException,
    AuthHTTPExceptions.EmailErrorException
]))
async def register(new_user: UserCreateSchema,
                   request: Request,
                   auth_service: AuthService = Depends(get_auth_service),
                   mailing_service: MailingService = Depends(get_mailing_service)
                   ) -> UserReadSchema:
    return await auth_service.register(new_user, mailing_service, request)

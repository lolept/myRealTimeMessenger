from fastapi import APIRouter, Depends, Request

from api.dependencies import get_auth_service
from api.exceptions import AuthHTTPExceptions
from api.schemas import UserCreateSchema, UserReadSchema
from api.services import AuthService

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
async def register(
        new_user: UserCreateSchema,
        request: Request,
        auth_service: AuthService = Depends(get_auth_service),
) -> UserReadSchema:
    return await auth_service.register(new_user, request)


@router.get('/verify/', responses=AuthHTTPExceptions.get_responses_dict([
    AuthHTTPExceptions.InvalidVerificationCodeException
]))
async def verify(
        verification_code: str,
        auth_service: AuthService = Depends(get_auth_service)
) -> UserReadSchema:
    return await auth_service.verify_user(verification_code)

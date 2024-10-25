from fastapi import APIRouter, Depends, Request, Response, status

from api.dependencies import get_auth_service
from api.exceptions import AuthHTTPExceptions
from api.schemas import UserCreateSchema, UserReadSchema, UserLoginSchema
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


@router.post('/login', status_code=status.HTTP_204_NO_CONTENT,
             responses=AuthHTTPExceptions.get_responses_dict([
                 AuthHTTPExceptions.UserDoesNotExistException,
                 AuthHTTPExceptions.WrongPasswordException,
             ]))
async def login(
        user: UserLoginSchema,
        auth_service: AuthService = Depends(get_auth_service)
):
    response = Response(status_code=status.HTTP_204_NO_CONTENT)
    await auth_service.login(user, response)
    return response


@router.post('/logout', status_code=status.HTTP_204_NO_CONTENT)
async def logout(
        auth_service: AuthService = Depends(get_auth_service)
):
    response = Response(status_code=status.HTTP_204_NO_CONTENT)
    await auth_service.logout(response)
    return response

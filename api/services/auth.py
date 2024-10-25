import hashlib
from random import randbytes

import argon2
from fastapi import Request

from api.config import settings
from api.exceptions import AuthHTTPExceptions
from api.repositories import UserRepository
from api.schemas import UserCreateSchema, UserReadSchema
from api.services.mailing import MailingService


class AuthService:
    password_salt = settings.PASSWORD_SALT
    
    def __init__(self,
                 user_repository: UserRepository):
        self.user_repository = user_repository
    
    async def register(self,
                       new_user: UserCreateSchema,
                       mailing_service: MailingService,
                       request: Request | None = None) -> UserReadSchema:
        user = await self.user_repository.get_one_or_none(email=new_user.email)
        hashed_password = await self.hash_password(new_user.password)
        if user:
            if user.is_verified:
                raise AuthHTTPExceptions.UserAlreadyExistsException(email=new_user.email)
            verification_code = await self.generate_verification_code()
            await self.send_email_verification_mail(
                new_user.email,
                verification_code,
                mailing_service,
                request
            )
            return await self.user_repository.update(
                filter_args={'email': new_user.email},
                hashed_password=hashed_password,
                verification_code=verification_code)
        verification_code = await self.generate_verification_code()
        await self.send_email_verification_mail(new_user.email, verification_code, mailing_service, request)
        return await self.user_repository.insert(email=new_user.email,
                                                 hashed_password=hashed_password,
                                                 verification_code=verification_code)
    
    @staticmethod
    async def generate_verification_code() -> str:
        token = randbytes(10)
        hashed_code = hashlib.sha256()
        hashed_code.update(token)
        verification_code = hashed_code.hexdigest()
        return verification_code
    
    @classmethod
    async def send_email_verification_mail(cls,
                                           email: str,
                                           verification_code: str,
                                           mailing_service: MailingService,
                                           request: Request | None = None):
        url = f"{request.url.scheme}://{settings.DOMAIN}/auth/verify/{verification_code}"
        try:
            await mailing_service.send_email_verification_mail(email, url)
        except:
            raise AuthHTTPExceptions.EmailErrorException()
    
    @classmethod
    async def hash_password(cls, password: str) -> str:
        password_bytes = password.encode('utf-8')
        hashed_password = argon2.hash_password(password_bytes, salt=cls.password_salt)
        return hashed_password.decode('utf-8')

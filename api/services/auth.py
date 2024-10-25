import asyncio
import datetime
import hashlib
from random import randbytes

import argon2
from fastapi import Request

from api.config import settings
from api.exceptions import AuthHTTPExceptions
from api.repositories import UserRepository
from api.schemas import UserCreateSchema, UserReadSchema
from api.services.mailing import MailingService
from api.services.scheduler import SchedulerService


class AuthService:
    password_salt = settings.PASSWORD_SALT
    verification_code_lifetime = settings.VERIFICATION_CODE_LIFETIME
    
    def __init__(self,
                 user_repository: UserRepository,
                 mailing_service: MailingService,
                 scheduler_service: SchedulerService):
        self.user_repository = user_repository
        self.mailing_service = mailing_service
        self.scheduler_service = scheduler_service
    
    @staticmethod
    async def _generate_verification_code() -> str:
        token = randbytes(10)
        hashed_code = hashlib.sha256()
        hashed_code.update(token)
        verification_code = hashed_code.hexdigest()
        return verification_code
    
    async def _send_email_verification_mail(self,
                                            email: str,
                                            verification_code: str,
                                            request: Request | None = None):
        url = f"{request.url.scheme}://{settings.DOMAIN}/auth/verify?verification_code={verification_code}"
        try:
            await self.mailing_service.send_email_verification_mail(email, url)
        except:
            raise AuthHTTPExceptions.EmailErrorException()
    
    @classmethod
    async def _hash_password(cls, password: str) -> str:
        password_bytes = password.encode('utf-8')
        hashed_password = argon2.hash_password(password_bytes, salt=cls.password_salt)
        return hashed_password.decode('utf-8')
    
    async def delete_unverified_user(self, verification_code: str):
        user = await self.user_repository.get_one_or_none(verification_code=verification_code)
        if not user:
            return
        await self.user_repository.delete(verification_code=verification_code)
    
    async def register(self,
                       new_user: UserCreateSchema,
                       request: Request | None = None) -> UserReadSchema:
        user = await self.user_repository.get_one_or_none(email=new_user.email)
        hashed_password = await self._hash_password(new_user.password)
        if user:
            if user.is_verified:
                raise AuthHTTPExceptions.UserAlreadyExistsException(email=new_user.email)
            verification_code = await self._generate_verification_code()
            await self._send_email_verification_mail(
                new_user.email,
                verification_code,
                request
            )
            self.scheduler_service.add_date_job(
                self.delete_unverified_user,
                run_date=datetime.datetime.now() + datetime.timedelta(seconds=self.verification_code_lifetime),
                verification_code=verification_code
            )
            return await self.user_repository.update(
                filter_args={'email': new_user.email},
                hashed_password=hashed_password,
                verification_code=verification_code)
        verification_code = await self._generate_verification_code()
        await self._send_email_verification_mail(new_user.email, verification_code, request)
        self.scheduler_service.add_date_job(
            self.delete_unverified_user,
            run_date=datetime.datetime.now() + datetime.timedelta(seconds=self.verification_code_lifetime),
            verification_code=verification_code
        )
        return await self.user_repository.insert(email=new_user.email,
                                                 hashed_password=hashed_password,
                                                 verification_code=verification_code)
    
    async def verify_user(self, verification_code: str) -> UserReadSchema:
        user = await self.user_repository.get_one_or_none(verification_code=verification_code)
        if not user:
            raise AuthHTTPExceptions.InvalidVerificationCodeException()
        return await self.user_repository.update(
            filter_args={'verification_code': verification_code},
            verification_code=None,
            is_verified=True
        )

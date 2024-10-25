import datetime
import hashlib
from random import randbytes

import argon2
from fastapi import Request, Response

from api.config import settings
from api.exceptions import AuthHTTPExceptions, BaseHTTPException
from api.repositories import UserRepository
from api.schemas import UserCreateSchema, UserReadSchema, UserLoginSchema
from api.services.jwt import JWTService
from api.services.mailing import MailingService
from api.services.scheduler import SchedulerService


class AuthService:
    password_salt = settings.PASSWORD_SALT
    verification_code_lifetime = settings.VERIFICATION_CODE_LIFETIME
    auth_cookie_lifetime = settings.AUTH_COOKIE_LIFETIME
    auth_cookie_name = settings.AUTH_COOKIE_NAME
    auth_cookie_domain = settings.AUTH_COOKIE_DOMAIN
    site_domain = settings.DOMAIN
    
    def __init__(self,
                 user_repository: UserRepository,
                 mailing_service: MailingService,
                 scheduler_service: SchedulerService,
                 jwt_service: JWTService, ):
        self.user_repository = user_repository
        self.mailing_service = mailing_service
        self.scheduler_service = scheduler_service
        self.jwt_service = jwt_service
    
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
        url = f"{request.url.scheme}://{self.site_domain}/auth/verify?verification_code={verification_code}"
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
    
    async def delete_unverified_users(self):
        users = await self.user_repository.get_all(is_verified=False)
        for user in users:
            await self.user_repository.delete(email=user.email)
    
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
    
    async def login(self, user_login: UserLoginSchema, response: Response):
        user = await self.authenticate_user(user_login)
        data = {"sub": str(user.email), "aud": self.auth_cookie_name}
        token = await self.jwt_service.generate_jwt(data, self.auth_cookie_lifetime)
        response.set_cookie(
            key=self.auth_cookie_name,
            value=token,
            max_age=self.auth_cookie_lifetime,
            domain=self.auth_cookie_domain,
        )
    
    async def authenticate_user(self, user_login: UserLoginSchema) -> UserReadSchema:
        user = await self.user_repository.get_one_or_none(email=user_login.email)
        if not user:
            raise AuthHTTPExceptions.UserDoesNotExistException(email=user_login.email)
        hashed_password = await self._hash_password(user_login.password)
        if hashed_password != user.hashed_password:
            raise AuthHTTPExceptions.WrongPasswordException()
        return user

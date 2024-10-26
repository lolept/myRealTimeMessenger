from dotenv import load_dotenv
from pydantic_settings import BaseSettings

load_dotenv()


class Settings(BaseSettings):
    DB_NAME: str
    DB_HOST: str
    DB_PORT: int
    DB_USER: str
    DB_PASSWORD: str
    
    PASSWORD_SALT: bytes
    PASSWORD_MIN_LENGTH: int
    PASSWORD_MAX_LENGTH: int
    VERIFICATION_CODE_LIFETIME: int
    AUTH_COOKIE_LIFETIME: int
    AUTH_COOKIE_NAME: str
    AUTH_COOKIE_SECRET: str
    AUTH_COOKIE_DOMAIN: str
    
    DOMAIN: str
    
    EMAIL_USERNAME: str
    EMAIL_PASSWORD: str
    EMAIL_FROM: str
    EMAIL_PORT: int
    EMAIL_HOST: str
    EMAIL_TLS: bool
    
    REDIS_HOST: str
    REDIS_PORT: int
    REDIS_DB: int
    
    @property
    def db_url(self) -> str:
        return f"postgresql+asyncpg://{self.DB_USER}:{self.DB_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"


settings = Settings()

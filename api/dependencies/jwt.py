from api.config import settings
from api.services import JWTService


def get_auth_jwt_service():
    return JWTService(
        secret=settings.AUTH_COOKIE_SECRET,
        audience=settings.AUTH_COOKIE_NAME
    )

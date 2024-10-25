from api.dependencies.jwt import get_auth_jwt_service
from api.dependencies.scheduler import get_scheduler_service
from api.dependencies.mailing import get_mailing_service
from api.repositories import UserRepository
from api.services import AuthService


def get_auth_service() -> AuthService:
    return AuthService(
        user_repository=UserRepository(),
        mailing_service=get_mailing_service(),
        scheduler_service=get_scheduler_service(),
        jwt_service=get_auth_jwt_service()
    )

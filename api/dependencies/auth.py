from api.repositories import UserRepository
from api.services import AuthService


def get_auth_service() -> AuthService:
    return AuthService(
        user_repository=UserRepository(),
    )

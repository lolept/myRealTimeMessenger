from api.config import settings
from api.services import RedisService


def get_redis_service() -> RedisService:
    return RedisService(
        host=settings.REDIS_HOST,
        port=settings.REDIS_PORT,
        db=settings.REDIS_DB,
    )

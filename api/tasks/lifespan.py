from api.dependencies import get_scheduler_service, get_auth_service, get_redis_service


async def on_startup():
    get_scheduler_service().scheduler.start()
    await get_auth_service().delete_unverified_users()
    await get_redis_service().flush()

async def on_shutdown():
    get_scheduler_service().scheduler.shutdown()
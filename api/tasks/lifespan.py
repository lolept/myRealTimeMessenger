from api.dependencies import get_scheduler_service, get_auth_service


async def on_startup():
    get_scheduler_service().scheduler.start()
    await get_auth_service().delete_unverified_users()

async def on_shutdown():
    get_scheduler_service().scheduler.shutdown()
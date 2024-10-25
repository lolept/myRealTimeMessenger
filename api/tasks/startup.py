from api.dependencies import get_scheduler_service


async def on_startup():
    get_scheduler_service().scheduler.start()

async def on_shutdown():
    get_scheduler_service().scheduler.shutdown()
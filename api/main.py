from contextlib import asynccontextmanager

from fastapi import FastAPI

from api.routers import auth_router
from api.tasks.startup import on_startup, on_shutdown


@asynccontextmanager
async def lifespan(_: FastAPI):
    await on_startup()
    yield
    await on_shutdown()


app = FastAPI(lifespan=lifespan)

app.include_router(auth_router)

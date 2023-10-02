from contextlib import asynccontextmanager

from fastapi import FastAPI
from pydantic import BaseModel

from src.config import config
from src.db import sessionmanager
from src.iban import router as iban_router


@asynccontextmanager
async def lifespan(_: FastAPI):
    # initialize db connection on app start except for testing
    if not config.TESTING:
        sessionmanager.init(host=str(config.DB_URI))

    # ready to accept and process HTTP requests
    yield

    # close db connection on app shutdown
    if sessionmanager.engine is not None:
        await sessionmanager.close()


app = FastAPI(
    title=config.APP_NAME,
    debug=config.DEBUG,
    lifespan=lifespan
)

app.include_router(iban_router.router, prefix='/api/v1')


class PingResponse(BaseModel):
    ping: str = 'pong'


@app.get("/", response_model=PingResponse)
async def ping():
    return PingResponse()

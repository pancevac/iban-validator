from fastapi import FastAPI
from pydantic import BaseModel

from src.config import config
from src.iban import router as iban_router

app = FastAPI(
    title=config.APP_NAME,
    debug=config.DEBUG
)

app.include_router(iban_router.router, prefix='/api/v1')


class HealthResponse(BaseModel):
    health: str = 'ok'


@app.get("/", response_model=HealthResponse)
async def health():
    return HealthResponse()

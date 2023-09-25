from fastapi import FastAPI

from src.config import config

app = FastAPI(
    title=config.APP_NAME,
    debug=config.DEBUG
)


@app.get("/")
async def health():
    return {'health': 'ok'}

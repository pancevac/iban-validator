from contextlib import asynccontextmanager
from typing import AsyncGenerator, Optional

from arq import create_pool
from arq.connections import RedisSettings, ArqRedis

from src.config import config


@asynccontextmanager
async def get_redis() -> AsyncGenerator[ArqRedis, None]:
    redis: Optional[ArqRedis] = None

    try:
        redis = await create_pool(settings_=RedisSettings().from_dsn(str(config.REDIS_URI)))
        yield redis
    finally:
        if redis is None:
            return

        await redis.aclose()

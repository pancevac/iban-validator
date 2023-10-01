"""
Inspired by https://praciano.com.br/fastapi-and-async-sqlalchemy-20-with-pytest-done-right.html
"""

import contextlib
from typing import Union, AsyncIterator

from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine, AsyncSession, AsyncEngine, AsyncConnection
from sqlalchemy.orm import declarative_base

Base = declarative_base()


class DatabaseSessionManager:
    def __init__(self):
        self._engine: Union[AsyncEngine, None] = None
        self._sessionmaker: Union[async_sessionmaker, None] = None

    def init(self, host: str) -> None:
        self._engine = create_async_engine(host)
        self._sessionmaker = async_sessionmaker(autocommit=False, bind=self._engine)

    @property
    def engine(self) -> Union[AsyncEngine, None]:
        return self._engine

    async def close(self) -> None:
        if self._engine is None:
            raise Exception("DatabaseSessionManager is not initialized")
        await self._engine.dispose()
        self._engine = None
        self._sessionmaker = None

    @contextlib.asynccontextmanager
    async def connect(self) -> AsyncIterator[AsyncConnection]:
        if self._engine is None:
            raise Exception("DatabaseSessionManager is not initialized")

        async with self._engine.begin() as connection:
            try:
                yield connection
            except Exception:
                await connection.rollback()
                raise

    @contextlib.asynccontextmanager
    async def session(self) -> AsyncIterator[AsyncSession]:
        if self._sessionmaker is None:
            raise Exception("DatabaseSessionManager is not initialized")

        session = self._sessionmaker()
        try:
            yield session
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()

    # Used for testing
    @staticmethod
    async def create_all(connection: AsyncConnection) -> None:
        await connection.run_sync(Base.metadata.create_all)

    @staticmethod
    async def drop_all(self, connection: AsyncConnection) -> None:
        await connection.run_sync(Base.metadata.drop_all)


async def get_db() -> AsyncIterator[AsyncSession]:
    async with sessionmanager.session() as session:
        yield session


sessionmanager = DatabaseSessionManager()

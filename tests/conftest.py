import asyncio

import pytest
from fastapi.testclient import TestClient
from pytest_postgresql import factories
from pytest_postgresql.janitor import DatabaseJanitor

from src.db import get_db, sessionmanager
from src.main import app


# create test database
test_db = factories.postgresql_proc(port=None, dbname="test_db")


@pytest.fixture
def client():
    with TestClient(app) as c:
        yield c


@pytest.fixture(scope="session")
def event_loop(request):
    """
    Create a new session-scoped event loop fixture,
    because the default event loop fixture is function-scoped.
    """
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="session", autouse=True)
async def connection_test(test_db, event_loop):
    """
    Create connection and session provided by postgresql_proc fixture.
    When tests are finished, close and dispose our async database engine.
    """
    pg_host = test_db.host
    pg_port = test_db.port
    pg_user = test_db.user
    pg_db = test_db.dbname
    pg_password = test_db.password

    with DatabaseJanitor(
        pg_user, pg_host, pg_port, pg_db, test_db.version, pg_password
    ):
        connection_str = f"postgresql+psycopg://{pg_user}:@{pg_host}:{pg_port}/{pg_db}"
        sessionmanager.init(connection_str)
        yield
        await sessionmanager.close()


@pytest.fixture(scope="function", autouse=True)
async def create_tables(connection_test):
    """
    Create db tables from scratch for each test.
    Having this will ensure that each test is running in isolated environment.
    """
    async with sessionmanager.connect() as connection:
        await sessionmanager.drop_all(connection)
        await sessionmanager.create_all(connection)


@pytest.fixture(scope="function", autouse=True)
async def session_override(connection_test):
    """
    Override database dependency in our app with new testing db dependency that we previously created.
    See https://fastapi.tiangolo.com/advanced/testing-dependencies/
    """
    async def get_db_override():
        async with sessionmanager.session() as session:
            yield session

    app.dependency_overrides[get_db] = get_db_override

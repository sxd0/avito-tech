import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from app.main import app
from app.database import Base
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from app.core.config import settings

DATABASE_TEST_URL = settings.DATABASE_URL + "_test"
test_engine = create_async_engine(DATABASE_TEST_URL, future=True)
TestingSessionLocal = sessionmaker(test_engine, class_=AsyncSession, expire_on_commit=False)

__all__ = ["TestingSessionLocal"]

@pytest_asyncio.fixture(scope="session", autouse=True)
async def setup_test_db():
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
    yield
    await test_engine.dispose()

@pytest_asyncio.fixture()
async def client():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac

@pytest_asyncio.fixture
async def moderator_token(client):
    response = await client.post("/api/dummyLogin", json={"role": "moderator"})
    return response.json()["access_token"]

@pytest_asyncio.fixture
async def employee_token(client):
    response = await client.post("/api/dummyLogin", json={"role": "employee"})
    return response.json()["access_token"]

@pytest_asyncio.fixture
def auth_headers_moderator(moderator_token):
    return {"Authorization": f"Bearer {moderator_token}"}

@pytest_asyncio.fixture
def auth_headers_employee(employee_token):
    return {"Authorization": f"Bearer {employee_token}"}

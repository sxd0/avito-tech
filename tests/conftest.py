import pytest
from httpx import AsyncClient
from app.main import app
from app.database import Base
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from app.core.config import settings

DATABASE_TEST_URL = settings.DATABASE_URL + "_test"

test_engine = create_async_engine(DATABASE_TEST_URL, future=True)
TestingSessionLocal = sessionmaker(test_engine, class_=AsyncSession, expire_on_commit=False)

@pytest.fixture(scope="session", autouse=True)
async def setup_test_db():
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
    yield
    await test_engine.dispose()

@pytest.fixture()
async def client():
    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac
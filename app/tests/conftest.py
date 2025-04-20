import asyncio
import pytest
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import NullPool

from app.database import Base
from app.core.config import settings
from app.main import app
from app.core.security import create_dummy_token

TEST_DATABASE_URL = f"postgresql+asyncpg://{settings.DB_USER}:{settings.DB_PASS}@{settings.DB_HOST}:{settings.DB_PORT}/test_db"

test_engine = create_async_engine(TEST_DATABASE_URL, poolclass=NullPool)
TestAsyncSessionLocal = sessionmaker(test_engine, class_=AsyncSession, expire_on_commit=False)


@pytest.fixture(scope="session")
def event_loop():
    """Создаем новый event loop для каждой сессии тестов"""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="function")
async def setup_test_db():
    """
    Пересоздаем таблицы для каждого теста для изоляции.
    Фикстура с областью видимости function вместо session.
    """
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
    
    yield
    
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest.fixture
def client():
    """Просто возвращаем тестовый клиент без зависимости от setup_test_db"""
    with TestClient(app) as c:
        yield c


@pytest.fixture
def moderator_token():
    return create_dummy_token("moderator")


@pytest.fixture
def employee_token():
    return create_dummy_token("employee")
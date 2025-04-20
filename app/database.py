import os

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase
from sqlalchemy.pool import NullPool

from app.core.config import settings


IS_PYTEST = bool(os.getenv("PYTEST_CURRENT_TEST"))
db_url = settings.DATABASE_URL + "_test" if IS_PYTEST else settings.DATABASE_URL

engine = create_async_engine(
    db_url,
    future=True,
    echo=False,
    poolclass=NullPool,            
)

async_session_maker = sessionmaker(
    engine, class_=AsyncSession, expire_on_commit=False
)


class Base(DeclarativeBase):
    pass

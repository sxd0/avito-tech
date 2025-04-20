from sqlalchemy import delete, insert, select, update
from app.database import async_session_maker
import logging

logger = logging.getLogger(__name__)

class BaseDAO:
    model = None

    def __init__(self, session):
        self.session = session

    async def add(self, data: dict):
        obj = self.model(**data)
        self.session.add(obj)
        await self.session.flush()
        return obj

    @classmethod
    async def find_one_or_none(cls, **filter_by):
        async with async_session_maker() as session:
            try:
                query = select(cls.model).filter_by(**filter_by)
                result = await session.execute(query)
                return result.scalars().one_or_none()
            except Exception as e:
                logger.error(f"Error in find_one_or_none: {str(e)}")
                raise ValueError(f"Database error: {str(e)}")

    @classmethod
    async def find_all(cls, offset: int = 0, limit: int = 100, **filter_by):
        async with async_session_maker() as session:
            try:
                query = select(cls.model).filter_by(**filter_by).offset(offset).limit(limit)
                result = await session.execute(query)
                return result.scalars().all()
            except Exception as e:
                logger.error(f"Error in find_all: {str(e)}")
                raise ValueError(f"Database error: {str(e)}")

from sqlalchemy import delete, insert, select, update
from app.database import async_session_maker
import logging


logger = logging.getLogger(__name__)

class BaseDAO:
    model = None

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

    @classmethod
    async def add(cls, **data):
        async with async_session_maker() as session:
            try:
                stmt = insert(cls.model).values(**data)
                await session.execute(stmt)
                await session.commit()
            except Exception as e:
                logger.error(f"Error in add: {str(e)}")
                raise ValueError(f"Database error: {str(e)}")

    @classmethod
    async def delete(cls, **filter_by):
        async with async_session_maker() as session:
            try:
                stmt = delete(cls.model).filter_by(**filter_by)
                await session.execute(stmt)
                await session.commit()
            except Exception as e:
                logger.error(f"Error in delete: {str(e)}")
                raise ValueError(f"Database error: {str(e)}")

    @classmethod
    async def update(cls, filter_by, **data):
        async with async_session_maker() as session:
            try:
                stmt = update(cls.model).filter_by(**filter_by).values(**data).returning(cls.model)
                result = await session.execute(stmt)
                await session.commit()
                return result.scalars().all()
            except Exception as e:
                logger.error(f"Error in update: {str(e)}")
                raise ValueError(f"Database error: {str(e)}")
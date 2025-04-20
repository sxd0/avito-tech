from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.logger import logger


class BaseDAO:
    model = None

    def __init__(self, session: AsyncSession):
        self.session = session

    async def add(self, data: dict):
        obj = self.model(**data)
        self.session.add(obj)
        await self.session.flush()
        return obj

    async def find_one_or_none(self, **filter_by):
        try:
            res = await self.session.execute(
                select(self.model).filter_by(**filter_by)
            )
            obj = res.scalars().one_or_none()
            res.close()
            return obj
        except Exception as exc:
            logger.error("find_one_or_none: %s", exc)
            raise ValueError(f"Database error: {exc}") from exc

    async def find_all(self, **filter_by):
        try:
            res = await self.session.execute(
                select(self.model).filter_by(**filter_by)
            )
            data = res.scalars().all()
            res.close()
            return data
        except Exception as exc:
            logger.error("find_all: %s", exc)
            raise ValueError(f"Database error: {exc}") from exc

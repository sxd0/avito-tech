from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.logger import logger


class BaseDAO:
    """Экземплярный DAO: работает ТОЛЬКО с self.session,
    поэтому всегда находится в том же event‑loop, что и вызвавший код."""
    model = None

    def __init__(self, session: AsyncSession):
        self.session = session

    # ---------- CRUD ----------
    async def add(self, data: dict):
        obj = self.model(**data)
        self.session.add(obj)
        await self.session.flush()
        return obj

    async def find_one_or_none(self, **filter_by):
        try:
            result = await self.session.execute(
                select(self.model).filter_by(**filter_by)
            )
            return result.scalars().one_or_none()
        except Exception as exc:
            logger.error(f"find_one_or_none: {exc}")
            raise ValueError(f"Database error: {exc}") from exc

    async def find_all(self, **filter_by):
        try:
            result = await self.session.execute(
                select(self.model).filter_by(**filter_by)
            )
            return result.scalars().all()
        except Exception as exc:
            logger.error(f"find_all: {exc}")
            raise ValueError(f"Database error: {exc}") from exc

    async def delete(self, **filter_by):
        obj = await self.find_one_or_none(**filter_by)
        if obj:
            await self.session.delete(obj)
            await self.session.flush()
        return obj

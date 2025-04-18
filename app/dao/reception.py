from sqlalchemy import select, and_
from app.dao.base import BaseDAO
from app.models.reception import Reception
from app.database import async_session_maker


class ReceptionDAO(BaseDAO):
    model = Reception
    
    @classmethod
    async def find_active_reception(cls, pvz_id: str):
        """
        Найти активную (незакрытую) приемку для ПВЗ
        """
        async with async_session_maker() as session:
            query = select(cls.model).filter(
                and_(
                    cls.model.pvz_id == pvz_id,
                    cls.model.status == "in_progress"
                )
            )
            result = await session.execute(query)
            return result.scalars().first()
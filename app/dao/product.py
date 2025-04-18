from sqlalchemy import select, func
from app.dao.base import BaseDAO
from app.models.product import Product
from app.database import async_session_maker


class ProductDAO(BaseDAO):
    model = Product
    
    @classmethod
    async def get_max_order(cls, reception_id: str):
        """
        Получить максимальный порядковый номер товара в приемке
        """
        async with async_session_maker() as session:
            query = select(func.max(cls.model.order_in_reception)).filter(
                cls.model.reception_id == reception_id
            )
            result = await session.execute(query)
            max_order = result.scalar()
            return max_order or 0
            
    @classmethod
    async def get_last_product(cls, reception_id: str):
        """
        Получить последний добавленный товар в приемке (принцип LIFO)
        """
        async with async_session_maker() as session:
            query = select(cls.model).filter(
                cls.model.reception_id == reception_id
            ).order_by(cls.model.order_in_reception.desc())
            result = await session.execute(query)
            return result.scalars().first()
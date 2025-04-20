from sqlalchemy import select, func
from app.dao.base import BaseDAO
from app.models.product import Product

class ProductDAO(BaseDAO):
    model = Product

    def __init__(self, session):
        super().__init__(session)

    async def get_max_order(self, reception_id: str):
        query = select(func.max(self.model.order_in_reception)).filter(
            self.model.reception_id == reception_id
        )
        result = await self.session.execute(query)
        max_order = result.scalar()
        return max_order or 0

    async def get_last_product(self, reception_id: str):
        query = (
            select(self.model)
            .filter(self.model.reception_id == reception_id)
            .order_by(self.model.order_in_reception.desc())
            .limit(1)
        )
        result = await self.session.execute(query)
        return result.scalars().first()

from sqlalchemy import func, select

from app.dao.base import BaseDAO
from app.models.product import Product


class ProductDAO(BaseDAO):
    model = Product

    async def get_max_order(self, reception_id: str) -> int:
        q = select(func.max(self.model.order_in_reception)).filter(
            self.model.reception_id == reception_id
        )
        res = await self.session.execute(q)
        m = res.scalar()
        res.close()
        return m or 0

    async def get_last_product(self, reception_id: str):
        q = (
            select(self.model)
            .filter(self.model.reception_id == reception_id)
            .order_by(self.model.order_in_reception.desc())
            .limit(1)
        )
        res = await self.session.execute(q)
        prod = res.scalars().first()
        res.close()
        return prod

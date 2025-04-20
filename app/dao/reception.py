from sqlalchemy import select
from app.dao.base import BaseDAO
from app.models.reception import Reception

class ReceptionDAO(BaseDAO):
    model = Reception

    def __init__(self, session):
        super().__init__(session)

    async def get_last_open(self, pvz_id):
        stmt = (
            select(Reception)
            .where(Reception.pvz_id == pvz_id, Reception.status == "in_progress")
            .order_by(Reception.date_time.desc())
            .limit(1)
        )
        result = await self.session.execute(stmt)
        return result.scalars().first()

    async def close(self, reception):
        reception.status = "close"
        await self.session.flush()
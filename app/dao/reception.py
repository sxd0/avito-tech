from sqlalchemy import select

from app.dao.base import BaseDAO
from app.models.reception import Reception


class ReceptionDAO(BaseDAO):
    model = Reception

    async def get_last_open(self, pvz_id: str):
        stmt = (
            select(Reception)
            .where(Reception.pvz_id == pvz_id, Reception.status == "in_progress")
            .order_by(Reception.date_time.desc())
            .limit(1)
        )
        res = await self.session.execute(stmt)
        obj = res.scalars().first()
        res.close()
        return obj

    async def close(self, reception: Reception):
        # в БД пишем "close"
        reception.status = "close"
        await self.session.flush()

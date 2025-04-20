from sqlalchemy import and_, select
from app.dao.base import BaseDAO
from app.models.pvz import PVZ
from app.database import async_session_maker


class PVZDAO(BaseDAO):
    model = PVZ

    @classmethod
    async def get_filtered_paginated(cls, start_date=None, end_date=None, page=1, limit=10):
        filters = []

        if start_date:
            filters.append(PVZ.registration_date >= start_date)
        if end_date:
            filters.append(PVZ.registration_date <= end_date)

        stmt = select(PVZ).where(and_(*filters)).offset((page - 1) * limit).limit(limit)
        result = await cls.session.execute(stmt)
        return result.scalars().all()
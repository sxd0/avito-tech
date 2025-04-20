from sqlalchemy import select

from app.dao.base import BaseDAO
from app.models.pvz import PVZ


class PVZDAO(BaseDAO):
    model = PVZ

    async def get_filtered_paginated(
        self, start_date=None, end_date=None, page: int = 1, limit: int = 10
    ):
        filters = []
        if start_date:
            filters.append(PVZ.registration_date >= start_date)
        if end_date:
            filters.append(PVZ.registration_date <= end_date)

        stmt = (
            select(PVZ)
            .where(*filters)
            .offset((page - 1) * limit)
            .limit(limit)
        )
        res = await self.session.execute(stmt)
        data = res.scalars().all()
        res.close()
        return data

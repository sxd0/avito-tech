from sqlalchemy import select
from app.dao.base import BaseDAO
from app.models.pvz import PVZ
from app.database import async_session_maker


class PVZDAO(BaseDAO):
    model = PVZ
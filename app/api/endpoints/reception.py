from fastapi import APIRouter, Depends, HTTPException, status
from app.api.dependencies import get_current_employee
from app.dao.reception import ReceptionDAO
from app.dao.pvz import PVZDAO
from app.schemas.pvz import ReceptionCreateSchema
from app.logger import logger
from app.database import async_session_maker

router = APIRouter(prefix="/receptions", tags=["Приёмки"])

@router.post("", status_code=status.HTTP_201_CREATED)
async def create_reception(reception_data: ReceptionCreateSchema, current_user=Depends(get_current_employee)):
    """Создание новой приёмки товаров (только для сотрудников)"""
    async with async_session_maker() as session:
        pvz = await PVZDAO.find_one_or_none(id=reception_data.pvz_id)
        if not pvz:
            raise HTTPException(status_code=404, detail="ПВЗ не найден")
        reception_dao = ReceptionDAO(session)
        reception = await reception_dao.add(reception_data.model_dump())
        await session.commit()
        logger.info(f"Created reception {reception.id} for PVZ {reception.pvz_id}")
        return reception

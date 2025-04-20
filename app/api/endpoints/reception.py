from fastapi import APIRouter, Depends, HTTPException, status

from app.api.dependencies import get_current_employee
from app.dao.pvz import PVZDAO
from app.dao.reception import ReceptionDAO
from app.database import async_session_maker
from app.logger import logger
from app.schemas.pvz import ReceptionCreateSchema
from app.schemas.reception import ReceptionSchema

router = APIRouter(prefix="/receptions", tags=["Приёмки"])


@router.post("", response_model=ReceptionSchema, status_code=status.HTTP_201_CREATED)
async def create_reception(
    reception_data: ReceptionCreateSchema,
    current_user=Depends(get_current_employee),
):
    async with async_session_maker() as session:
        pvz = await PVZDAO(session).find_one_or_none(id=reception_data.pvz_id)
        if not pvz:
            raise HTTPException(status_code=404, detail="ПВЗ не найден")

        reception = await ReceptionDAO(session).add(reception_data.model_dump())
        await session.commit()
        logger.info("Created reception %s for PVZ %s", reception.id, pvz.id)
        return reception

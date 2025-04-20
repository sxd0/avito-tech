from datetime import datetime
from typing import List, Optional
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, Query, status
from app.api.dependencies import get_current_employee, get_current_moderator, get_current_user
from app.dao.pvz import PVZDAO
from app.dao.reception import ReceptionDAO
from app.logger import logger
from app.database import async_session_maker
from app.schemas.pvz import PVZCreateSchema, PVZSchema
from app.metrics_server import PVZ_CREATED

router = APIRouter(prefix="/pvz", tags=["ПВЗ"])

@router.post("", status_code=status.HTTP_201_CREATED, response_model=PVZSchema)
async def create_pvz(pvz_data: PVZCreateSchema, current_user=Depends(get_current_moderator)):
    """Создание нового ПВЗ (только для модераторов)"""
    async with async_session_maker() as session:
        dao = PVZDAO(session)
        pvz = await dao.add(pvz_data.model_dump())
        await session.commit()
        PVZ_CREATED.inc()
        logger.info(f"Created PVZ {pvz.id}")
        return pvz

@router.get("", response_model=List[PVZSchema])
async def list_pvz(start_date: Optional[datetime] = Query(None), end_date: Optional[datetime] = Query(None), page: int = Query(1), limit: int = Query(10), current_user=Depends(get_current_user)):
    """Получение списка ПВЗ с фильтрацией по дате регистрации"""
    async with async_session_maker() as session:
        dao = PVZDAO(session)
        pvzs = await dao.get_filtered_paginated(start_date=start_date, end_date=end_date, page=page, limit=limit)
        logger.info("List PVZ fetched")
        return pvzs

@router.post("/{pvz_id}/close_last_reception")
async def close_reception(pvz_id: str, current_user=Depends(get_current_employee)):
    """Закрытие последней открытой приёмки для ПВЗ"""
    async with async_session_maker() as session:
        dao = ReceptionDAO(session)
        reception = await dao.get_last_open(pvz_id)
        if not reception:
            raise HTTPException(status_code=404, detail="Нет открытых приемок")
        await dao.close(reception)
        await session.commit()
        logger.info(f"Reception {reception.id} closed for PVZ {pvz_id}")
        return {"status": "closed", "reception_id": reception.id}
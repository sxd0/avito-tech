from datetime import datetime
import uuid
from fastapi import APIRouter, Depends, HTTPException, Query, status
from typing import List, Optional
from pydantic import UUID4
from sqlalchemy import select, and_

from app.logger import logger
from app.api.dependencies import get_current_employee, get_current_moderator, get_current_user
from app.dao.pvz import PVZDAO
from app.dao.reception import ReceptionDAO
from app.dao.product import ProductDAO
from app.database import async_session_maker
from app.metrics_server import PVZ_CREATED
from app.models.pvz import PVZ
from app.models.reception import Reception
from app.models.product import Product
from app.schemas.pvz import PVZCreateSchema, PVZSchema

router = APIRouter(
    prefix="/pvz",
    tags=["ПВЗ"]
)

# @router.post("", status_code=status.HTTP_201_CREATED, response_model=PVZSchema)
# async def create_pvz(
#     pvz_data: PVZCreateSchema, 
#     current_user = Depends(get_current_moderator)
# ):
#     """
#     Создание нового ПВЗ (только для модераторов).
#     - **city**: Город (Москва, Санкт-Петербург или Казань)
#     """
#     if pvz_data.city not in ["Москва", "Санкт-Петербург", "Казань"]:
#         raise HTTPException(
#             status_code=status.HTTP_400_BAD_REQUEST,
#             detail="Город должен быть одним из: Москва, Санкт-Петербург, Казань"
#         )
    

#     new_id = uuid.uuid4()

#     pvz_dict = {
#         "id": new_id,
#         "city": pvz_data.city,
#         "registration_date": datetime.utcnow()
#     }

#     await PVZDAO.add(city=pvz_data.city)
#     pvz = await PVZDAO.find_one_or_none(id=new_id)

#     # created_pvz = await PVZDAO.find_one_or_none(city=pvz_data.city)
#     if not pvz:
#         raise HTTPException(status_code=500, detail="Не удалось создать ПВЗ")

#     return pvz

# @router.post("", response_model=PVZSchema)
# async def create_pvz(pvz_data: PVZCreateSchema, current_user: dict = Depends(get_current_moderator)):
#     if pvz_data.city not in ["Москва", "Санкт-Петербург", "Казань"]:
#         raise HTTPException(status_code=400, detail="Недопустимый город")

#     pvz_id = uuid.uuid4()
#     await PVZDAO.add({
#         "id": pvz_id,
#         "city": pvz_data.city,
#         "registration_date": datetime.utcnow()
#     })

#     pvz = await PVZDAO.find_one_or_none(id=pvz_id)
#     await PVZDAO.add(pvz)
#     PVZ_CREATED.inc()
#     logger.info(f"Создан ПВЗ: {pvz.city} (ID: {pvz.id})")
#     return pvz

@router.post("", status_code=status.HTTP_201_CREATED, response_model=PVZSchema)
async def create_pvz(
    pvz_data: PVZCreateSchema,
    current_user = Depends(get_current_moderator)
):
    async with async_session_maker() as session:
        dao = PVZDAO(session)
        pvz = await dao.add(pvz_data.model_dump())
        await session.commit()
        return pvz




@router.get("", response_model=List[PVZSchema])
async def list_pvz(
    start_date: Optional[datetime] = Query(None),
    end_date: Optional[datetime] = Query(None),
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1, le=100),
    current_user = Depends(get_current_user)
):
    """
    Получение списка ПВЗ с фильтрацией по дате регистрации
    """
    async with async_session_maker() as session:
        pvzs = await PVZDAO(session).get_filtered_paginated(
            start_date=start_date,
            end_date=end_date,
            page=page,
            limit=limit
        )
        return pvzs

@router.get("", response_model=List[dict])
async def get_pvz_list(
    start_date: Optional[datetime] = Query(None, description="Начальная дата диапазона"),
    end_date: Optional[datetime] = Query(None, description="Конечная дата диапазона"),
    page: int = Query(1, ge=1, description="Номер страницы"),
    limit: int = Query(10, ge=1, le=30, description="Количество элементов на странице"),
    current_user = Depends(get_current_user)
):
    """
    Получение списка ПВЗ с фильтрацией по дате приемки и пагинацией.
    Доступно для пользователей с ролью 'employee' или 'moderator'.
    """
    PVZ_CREATED.inc()
    user_role = current_user.role if hasattr(current_user, "role") else current_user.get("role")

    if user_role not in ["employee", "moderator"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Недостаточно прав"
        )
    
    offset = (page - 1) * limit
    
    async with async_session_maker() as session:
        query = select(PVZ)
        
        if start_date or end_date:
            date_filter_conditions = []
            if start_date:
                date_filter_conditions.append(Reception.date_time >= start_date)
            if end_date:
                date_filter_conditions.append(Reception.date_time <= end_date)
            
            if date_filter_conditions:
                pvz_ids_with_receptions = select(Reception.pvz_id).filter(and_(*date_filter_conditions))
                query = query.filter(PVZ.id.in_(pvz_ids_with_receptions))
        
        query = query.offset(offset).limit(limit)
        
        result = await session.execute(query)
        pvzs = result.scalars().all()
        
        response = []
        for pvz in pvzs:
            receptions_query = select(Reception).filter(Reception.pvz_id == pvz.id)
            
            if start_date:
                receptions_query = receptions_query.filter(Reception.date_time >= start_date)
            if end_date:
                receptions_query = receptions_query.filter(Reception.date_time <= end_date)
            
            receptions_result = await session.execute(receptions_query)
            receptions = receptions_result.scalars().all()
            
            receptions_data = []
            for reception in receptions:
                products_query = select(Product).filter(Product.reception_id == reception.id)
                products_result = await session.execute(products_query)
                products = products_result.scalars().all()
                
                receptions_data.append({
                    "reception": reception,
                    "products": products
                })
            
            response.append({
                "pvz": pvz,
                "receptions": receptions_data
            })
        
        return response
    

# @router.post("/{pvz_id}/close_last_reception", status_code=status.HTTP_200_OK)
# async def close_reception(
#     pvz_id: str,
#     current_user = Depends(get_current_employee)
# ):
#     """
#     Закрытие последней открытой приемки товаров в рамках ПВЗ.
#     Доступно только для пользователей с ролью 'employee'.
    
#     - **pvz_id**: ID пункта выдачи заказов
#     """
#     pvz = await PVZDAO.find_one_or_none(id=pvz_id)
#     if not pvz:
#         raise HTTPException(
#             status_code=status.HTTP_404_NOT_FOUND,
#             detail="ПВЗ не найден"
#         )
    
#     active_reception = await ReceptionDAO.find_active_reception(pvz_id)
#     if not active_reception:
#         raise HTTPException(
#             status_code=status.HTTP_400_BAD_REQUEST,
#             detail="У данного ПВЗ нет открытой приемки"
#         )
    
#     await ReceptionDAO.update(
#         filter_by={"id": active_reception.id},
#         status="close"
#     )
    
#     closed_reception = await ReceptionDAO.find_one_or_none(id=active_reception.id)
    
#     return closed_reception

@router.post("/{pvz_id}/close_last_reception", status_code=status.HTTP_200_OK)
async def close_reception(
    pvz_id: str,
    current_user = Depends(get_current_employee)
):
    async with async_session_maker() as session:
        reception_dao = ReceptionDAO(session)
        active_reception = await reception_dao.get_last_open(pvz_id)
        if not active_reception:
            raise HTTPException(status_code=404, detail="Нет открытых приемок")

        active_reception.status = "close"
        await session.commit()
        return {"status": "closed", "reception_id": active_reception.id}


@router.post("/{pvz_id}/delete_last_product")
async def delete_last_product(
    pvz_id: UUID4,
    current_user: dict = Depends(get_current_employee)
):
    pvz = await PVZDAO.find_one_or_none(id=pvz_id)
    if not pvz:
        raise HTTPException(status_code=404, detail="ПВЗ не найден")

    active = await ReceptionDAO.find_active_reception(pvz_id)
    if not active:
        raise HTTPException(status_code=400, detail="Нет открытой приёмки")

    last_product = await ProductDAO.get_last_product(active.id)
    if not last_product:
        raise HTTPException(status_code=400, detail="Нет товаров для удаления")

    await ProductDAO.delete(last_product.id)
    return {"detail": "Удалено успешно"}


@router.post("/{pvz_id}/close_last_reception", status_code=status.HTTP_200_OK)
async def close_last_reception(
    pvz_id: UUID4,
    current_user = Depends(get_current_employee)
):
    """
    Закрытие последней открытой приемки товаров в ПВЗ
    """
    async with async_session_maker() as session:
        reception = await ReceptionDAO(session).get_last_open(pvz_id)
        if not reception:
            raise HTTPException(status_code=404, detail="Нет открытых приемок")

        await ReceptionDAO(session).close(reception)
        return {"status": "closed", "reception_id": reception.id}

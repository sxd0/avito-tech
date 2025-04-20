from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, Query, status
from typing import List, Optional
from sqlalchemy import select, and_

from app.api.dependencies import get_current_employee, get_current_moderator, get_current_user
from app.dao.pvz import PVZDAO
from app.dao.reception import ReceptionDAO
from app.dao.product import ProductDAO
from app.database import async_session_maker
from app.models.pvz import PVZ
from app.models.reception import Reception
from app.models.product import Product
from app.schemas.pvz import PVZCreateSchema, PVZSchema

router = APIRouter(
    prefix="/pvz",
    tags=["ПВЗ"]
)

@router.post("", status_code=status.HTTP_201_CREATED, response_model=PVZSchema)
async def create_pvz(
    pvz_data: PVZCreateSchema, 
    current_user = Depends(get_current_moderator)
):
    """
    Создание нового ПВЗ (только для модераторов).
    - **city**: Город (Москва, Санкт-Петербург или Казань)
    """
    if pvz_data.city not in ["Москва", "Санкт-Петербург", "Казань"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Город должен быть одним из: Москва, Санкт-Петербург, Казань"
        )
    
    pvz = await PVZDAO.add(city=pvz_data.city)
    
    created_pvz = await PVZDAO.find_one_or_none(city=pvz_data.city)
    
    return created_pvz

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
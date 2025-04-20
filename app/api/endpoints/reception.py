from fastapi import APIRouter, Depends, HTTPException, status
from app.api.dependencies import get_current_employee
from app.dao.pvz import PVZDAO
from app.dao.reception import ReceptionDAO
from app.schemas.pvz import ReceptionCreateSchema

router = APIRouter(
    prefix="/receptions",
    tags=["Приемки"]
)

@router.post("", status_code=status.HTTP_201_CREATED)
async def create_reception(
    reception_data: ReceptionCreateSchema,
    current_user = Depends(get_current_employee)
):
    """
    Создание новой приемки товаров.
    Доступно только для пользователей с ролью 'employee'.
    
    - **pvz_id**: ID пункта выдачи заказов
    """
    pvz = await PVZDAO.find_one_or_none(id=reception_data.pvz_id)
    if not pvz:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="ПВЗ не найден"
        )
    
    active_reception = await ReceptionDAO.find_active_reception(reception_data.pvz_id)
    if active_reception:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="У данного ПВЗ уже есть незакрытая приемка"
        )
    
    reception = await ReceptionDAO.add(
        pvz_id=reception_data.pvz_id,
        status="in_progress"
    )
    
    created_reception = await ReceptionDAO.find_active_reception(reception_data.pvz_id)
    
    return created_reception


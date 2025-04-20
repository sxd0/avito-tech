from fastapi import APIRouter, Depends, HTTPException, status
from app.api.dependencies import get_current_employee
from app.dao.pvz import PVZDAO
from app.dao.reception import ReceptionDAO
from app.dao.product import ProductDAO
from app.metrics_server import PRODUCTS_CREATED
from app.schemas.pvz import ProductCreateSchema
from app.logger import logger
from app.database import async_session_maker


router = APIRouter(
    tags=["Товары"]
)

# @router.post("/products", status_code=status.HTTP_201_CREATED)
# async def add_product(
#     product_data: ProductCreateSchema,
#     current_user = Depends(get_current_employee)
# ):
#     """
#     Добавление товара в текущую приемку.
#     Доступно только для пользователей с ролью 'employee'.
    
#     - **type**: Тип товара (электроника, одежда, обувь)
#     - **pvz_id**: ID пункта выдачи заказов
#     """
#     PRODUCTS_CREATED.inc()

#     pvz = await PVZDAO.find_one_or_none(id=product_data.pvz_id)
#     if not pvz:
#         raise HTTPException(
#             status_code=status.HTTP_404_NOT_FOUND,
#             detail="ПВЗ не найден"
#         )
    
#     if product_data.type not in ["электроника", "одежда", "обувь"]:
#         raise HTTPException(
#             status_code=status.HTTP_400_BAD_REQUEST,
#             detail="Тип товара должен быть одним из: электроника, одежда, обувь"
#         )
    
#     active_reception = await ReceptionDAO.find_active_reception(product_data.pvz_id)
#     if not active_reception:
#         raise HTTPException(
#             status_code=status.HTTP_400_BAD_REQUEST,
#             detail="У данного ПВЗ нет открытой приемки"
#         )
    
#     max_order = await ProductDAO.get_max_order(active_reception.id)
    
#     product = await ProductDAO.add(
#         type=product_data.type,
#         reception_id=active_reception.id,
#         order_in_reception=max_order + 1
#     )
    
#     created_product = await ProductDAO.find_one_or_none(
#         reception_id=active_reception.id,
#         order_in_reception=max_order + 1
#     )
#     logger.info(f"Добавлен товар: {product.type} в приёмку {created_product.reception_id}")

#     return created_product

# @router.post("/pvz/{pvz_id}/delete_last_product", status_code=status.HTTP_200_OK)
# async def delete_last_product(
#     pvz_id: str,
#     current_user = Depends(get_current_employee)
# ):
#     """
#     Удаление последнего добавленного товара из текущей приемки (LIFO).
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
    
#     last_product = await ProductDAO.get_last_product(active_reception.id)
#     if not last_product:
#         raise HTTPException(
#             status_code=status.HTTP_400_BAD_REQUEST,
#             detail="В текущей приемке нет товаров"
#         )
    
#     await ProductDAO.delete(id=last_product.id)
    
#     logger.info(f"Удален последний товар из приёмки (ID товара: {last_product.id})")

#     return {"message": "Товар успешно удален"}

# @router.post("/products", status_code=status.HTTP_201_CREATED)
# async def add_product(
#     product_data: ProductCreateSchema,
#     current_user = Depends(get_current_employee)
# ):
#     """
#     Добавление товара в текущую приемку.
#     Доступно только для пользователей с ролью 'employee'.

#     - **type**: Тип товара (электроника, одежда, обувь)
#     - **pvz_id**: ID пункта выдачи заказов
#     """
#     PRODUCTS_CREATED.inc()

#     async with async_session_maker() as session:
#         pvz_dao = PVZDAO(session)
#         pvz = await pvz_dao.find_one_or_none(id=product_data.pvz_id)
#         if not pvz:
#             raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="ПВЗ не найден")

#         reception_dao = ReceptionDAO(session)
#         reception = await reception_dao.get_last_open(pvz.id)
#         if not reception:
#             raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Открытая приёмка не найдена")

#         product_dao = ProductDAO(session)
#         max_order = await product_dao.get_max_order(reception.id)

#         product_dict = product_data.model_dump()
#         product_dict["reception_id"] = reception.id
#         product_dict["order_in_reception"] = max_order + 1

#         product = await product_dao.add(product_dict)
#         await session.commit()
#         return product

@router.post("/products", status_code=status.HTTP_201_CREATED)
async def add_product(
    product_data: ProductCreateSchema,
    current_user = Depends(get_current_employee)
):
    PRODUCTS_CREATED.inc()

    async with async_session_maker() as session:
        pvz_dao = PVZDAO(session)
        pvz = await pvz_dao.find_one_or_none(id=product_data.pvz_id)
        if not pvz:
            raise HTTPException(status_code=404, detail="ПВЗ не найден")

        reception_dao = ReceptionDAO(session)
        reception = await reception_dao.get_last_open(pvz.id)
        if not reception:
            raise HTTPException(status_code=404, detail="Нет открытой приёмки")

        product_dao = ProductDAO(session)
        max_order = await product_dao.get_max_order(reception.id)

        product_dict = product_data.model_dump()
        product_dict.pop("pvz_id", None)
        product_dict["reception_id"] = reception.id
        product_dict["order_in_reception"] = max_order + 1

        product = await product_dao.add(product_dict)
        await session.commit()
        return product


@router.post("/pvz/{pvz_id}/delete_last_product", status_code=status.HTTP_200_OK)
async def delete_last_product(
    pvz_id: str,
    current_user = Depends(get_current_employee)
):
    """
    Удаление последнего добавленного товара из текущей приемки.
    Доступно только для сотрудников.
    """
    async with async_session_maker() as session:
        reception_dao = ReceptionDAO(session)
        reception = await reception_dao.get_last_open(pvz_id)
        if not reception:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Открытая приёмка не найдена")

        product_dao = ProductDAO(session)
        product = await product_dao.get_last_product(reception.id)
        if not product:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Нет товаров в приёмке")

        await session.delete(product)
        await session.commit()
        return {"status": "deleted", "product_id": product.id}
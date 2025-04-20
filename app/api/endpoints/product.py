from fastapi import APIRouter, Depends, HTTPException, status

from app.api.dependencies import get_current_employee
from app.dao.pvz import PVZDAO
from app.dao.reception import ReceptionDAO
from app.dao.product import ProductDAO
from app.database import async_session_maker
from app.metrics_server import PRODUCTS_CREATED
from app.schemas.pvz import ProductCreateSchema
from app.schemas.product import ProductSchema 
from app.logger import logger

router = APIRouter(tags=["Товары"])


@router.post("/products", response_model=ProductSchema, status_code=status.HTTP_201_CREATED)
async def add_product(
    product_data: ProductCreateSchema,
    current_user=Depends(get_current_employee),
):
    """Добавить товар в последнюю открытую приёмку."""
    PRODUCTS_CREATED.inc()

    async with async_session_maker() as session:
        pvz = await PVZDAO(session).find_one_or_none(id=product_data.pvz_id)
        if not pvz:
            raise HTTPException(status_code=404, detail="ПВЗ не найден")

        reception_dao = ReceptionDAO(session)
        reception = await reception_dao.get_last_open(product_data.pvz_id)
        if not reception:
            raise HTTPException(status_code=404, detail="Открытая приёмка не найдена")

        product_dao = ProductDAO(session)
        order = await product_dao.get_max_order(reception.id) + 1

        data = product_data.model_dump()
        data.pop("pvz_id", None)
        data["reception_id"] = reception.id
        data["order_in_reception"] = order

        product = await product_dao.add(data)
        await session.commit()
        logger.info("Product %s added to reception %s", product.id, reception.id)
        return product

@router.post("/pvz/{pvz_id}/delete_last_product", status_code=status.HTTP_200_OK)
async def delete_last_product(
    pvz_id: str, current_user=Depends(get_current_employee)
):
    async with async_session_maker() as session:
        reception = await ReceptionDAO(session).get_last_open(pvz_id)
        if not reception:
            raise HTTPException(status_code=404, detail="Открытая приёмка не найдена")

        product = await ProductDAO(session).get_last_product(reception.id)
        if not product:
            raise HTTPException(status_code=404, detail="Нет товаров в приёмке")

        await session.delete(product)
        await session.commit()
        logger.info("Product %s deleted from reception %s", product.id, reception.id)
        return {"status": "deleted", "product_id": product.id}

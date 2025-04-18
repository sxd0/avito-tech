from fastapi import APIRouter
from app.api.endpoints import auth, pvz, reception, product

router = APIRouter(prefix="/api")

router.include_router(auth.router)
router.include_router(pvz.router)
router.include_router(reception.router)
router.include_router(product.router)
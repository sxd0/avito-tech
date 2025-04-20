from datetime import datetime
from pydantic import UUID4, BaseModel, ConfigDict, Field
from typing import List, Optional

from app.schemas.product import ProductSchema
from app.schemas.reception import ReceptionSchema


class PVZCreateSchema(BaseModel):
    city: str = Field(..., description="Город (Москва, Санкт-Петербург или Казань)")
    
    model_config = ConfigDict(from_attributes=True)


class PVZSchema(BaseModel):
    id: UUID4
    registration_date: datetime
    city: str

class ReceptionWithProducts(BaseModel):
    reception: ReceptionSchema
    products: List[ProductSchema]

class PVZWithReceptions(BaseModel):
    pvz: PVZSchema
    receptions: List[ReceptionWithProducts]


class ReceptionCreateSchema(BaseModel):
    pvz_id: str
    
    model_config = ConfigDict(from_attributes=True)


class ProductCreateSchema(BaseModel):
    type: str
    pvz_id: str
    
    model_config = ConfigDict(from_attributes=True)


class PVZFilterSchema(BaseModel):
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    page: int = 1
    limit: int = 10
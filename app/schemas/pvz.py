from datetime import datetime
from pydantic import BaseModel, ConfigDict, Field
from typing import List, Optional


class PVZCreateSchema(BaseModel):
    city: str = Field(..., description="Город (Москва, Санкт-Петербург или Казань)")
    
    model_config = ConfigDict(from_attributes=True)


class PVZSchema(BaseModel):
    id: str
    registration_date: datetime
    city: str
    
    model_config = ConfigDict(from_attributes=True)


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
from pydantic import BaseModel, UUID4
from datetime import datetime
from typing import Literal

class ProductSchema(BaseModel):
    id: UUID4
    date_time: datetime
    type: Literal["электроника", "одежда", "обувь"]
    reception_id: UUID4

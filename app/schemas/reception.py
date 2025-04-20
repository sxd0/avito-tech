from datetime import datetime
from typing import Literal

from pydantic import BaseModel, UUID4


class ReceptionSchema(BaseModel):
    id: UUID4
    date_time: datetime
    pvz_id: UUID4
    status: Literal["in_progress", "close", "closed"]

from datetime import datetime
import uuid

from sqlalchemy import Column, DateTime, Enum, ForeignKey, String
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.database import Base


class Reception(Base):
    __tablename__ = "receptions"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    date_time = Column(DateTime, default=func.now())
    pvz_id = Column(String, ForeignKey("pvzs.id"))
    status = Column(
        Enum("in_progress", "close", name="reception_status"),
        default="in_progress",
    )

    pvz = relationship("PVZ", back_populates="receptions")
    products = relationship(
        "Product", back_populates="reception", cascade="all, delete-orphan"
    )

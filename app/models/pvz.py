from datetime import datetime
import uuid
from sqlalchemy import Column, String, DateTime, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base


class PVZ(Base):
    __tablename__ = "pvzs"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    registration_date = Column(DateTime, default=func.now())
    city = Column(Enum("Москва", "Санкт-Петербург", "Казань", name="city_type"))
    
    receptions = relationship("Reception", back_populates="pvz", cascade="all, delete-orphan")
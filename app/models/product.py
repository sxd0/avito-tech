from datetime import datetime
import uuid
from sqlalchemy import Column, String, DateTime, Enum, ForeignKey, Integer
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base


class Product(Base):
    __tablename__ = "products"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    date_time = Column(DateTime, default=func.now())
    type = Column(Enum("электроника", "одежда", "обувь", name="product_type"))
    reception_id = Column(String, ForeignKey("receptions.id"))
    
    order_in_reception = Column(Integer)
    
    reception = relationship("Reception", back_populates="products")
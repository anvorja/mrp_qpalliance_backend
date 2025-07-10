# app/models/location.py
from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.base import Base


class Location(Base):
    """
    Modelo para las ubicaciones de almacenamiento.
    """
    __tablename__ = "locations"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), nullable=False, unique=True)

    # Referencias inversas
    products = relationship("Product", back_populates="location")

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    def __repr__(self):
        return f"<Location {self.name}>"
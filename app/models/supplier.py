# app/models/supplier.py
from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.base import Base


class Supplier(Base):
    """
    Modelo para los proveedores.
    """
    __tablename__ = "suppliers"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    contact = Column(String(100), nullable=True)
    email = Column(String(100), nullable=True)
    phone = Column(String(20), nullable=True)

    # Referencias inversas
    products = relationship("Product", back_populates="supplier")

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    def __repr__(self):
        return f"<Supplier {self.name}>"
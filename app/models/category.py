# app/models/category.py
from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.base import Base


class Category(Base):
    """
    Modelo para las categorías de productos.
    """
    __tablename__ = "categories"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), nullable=False, unique=True)

    # Referencias inversas
    products = relationship("Product", back_populates="category")

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    def __repr__(self):
        return f"<Category {self.name}>"
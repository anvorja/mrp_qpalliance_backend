# app/models/product.py
from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.base import Base


class Product(Base):
    """
    Modelo para la tabla de productos.
    """
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    code = Column(String(50), unique=True, nullable=False, index=True)
    current_stock = Column(Float, nullable=False, default=0)
    min_stock = Column(Float, nullable=False, default=0)
    description = Column(Text, nullable=True)
    price = Column(Float, nullable=True)
    qc_status = Column(String(20), nullable=True)  # approved, pending, rejected

    # Relaciones
    category_id = Column(Integer, ForeignKey("categories.id"), nullable=True)
    location_id = Column(Integer, ForeignKey("locations.id"), nullable=True)
    supplier_id = Column(Integer, ForeignKey("suppliers.id"), nullable=True)

    # Referencias inversas
    category = relationship("Category", back_populates="products")
    location = relationship("Location", back_populates="products")
    supplier = relationship("Supplier", back_populates="products")
    movements = relationship("Movement", back_populates="product", cascade="all, delete-orphan")

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    def __repr__(self):
        return f"<Product {self.code}: {self.name}>"

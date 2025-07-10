# app/models/movement.py
from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.base import Base


class Movement(Base):
    """
    Modelo para los movimientos de inventario.
    """
    __tablename__ = "movements"

    id = Column(Integer, primary_key=True, index=True)
    type = Column(String(20), nullable=False)  # in, out, adjustment
    quantity = Column(Float, nullable=False)
    resulting_stock = Column(Float, nullable=False)
    reference = Column(String(50), nullable=True)
    notes = Column(Text, nullable=True)
    user = Column(String(100), nullable=True)  # Podría convertirse en una relación con una tabla de usuarios

    # Relaciones
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    product = relationship("Product", back_populates="movements")

    created_at = Column(DateTime(timezone=True), server_default=func.now())

    def __repr__(self):
        return f"<Movement {self.type}: {self.quantity} of {self.product_id}>"
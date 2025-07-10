# app/schemas/movement.py
from pydantic import BaseModel, Field, ConfigDict, field_validator
from typing import Optional
from datetime import datetime

from app.schemas.product import ProductResponse


class MovementBase(BaseModel):
    """
    Esquema base para movimientos de inventario.
    """
    type: str = Field(..., description="Tipo de movimiento: in, out, adjustment")
    quantity: float = Field(..., description="Cantidad de producto movida")
    product_id: int = Field(..., description="ID del producto asociado")
    reference: Optional[str] = Field(None, max_length=50, description="Referencia del movimiento (orden, etc.)")
    notes: Optional[str] = Field(None, description="Notas adicionales")
    user: Optional[str] = Field(None, max_length=100, description="Usuario que realizó el movimiento")

    model_config = ConfigDict(from_attributes=True)

    @field_validator('type')
    def type_must_be_valid(cls, v):
        valid_types = ["in", "out", "adjustment"]
        if v not in valid_types:
            raise ValueError(f'Tipo debe ser uno de: {", ".join(valid_types)}')
        return v


class MovementCreate(MovementBase):
    """
    Esquema para la creación de movimientos.
    """
    pass


class MovementResponse(MovementBase):
    """
    Esquema para respuestas de movimientos.
    """
    id: int
    resulting_stock: float
    created_at: datetime
    product_name: Optional[str] = None
    product_code: Optional[str] = None


class MovementWithProduct(MovementResponse):
    """
    Esquema para movimientos con información del producto.
    """
    product: ProductResponse
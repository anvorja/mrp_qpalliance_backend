# app/schemas/product.py
from pydantic import BaseModel, Field, field_validator, ConfigDict
from typing import Optional
from datetime import datetime
import re


class ProductBase(BaseModel):
    """
    Esquema base para productos con validaciones comunes.
    """
    name: str = Field(..., min_length=1, max_length=100, description="Nombre del producto")
    code: str = Field(..., min_length=1, max_length=50, description="Código único del producto")
    current_stock: float = Field(..., ge=0, description="Stock actual del producto")
    min_stock: float = Field(..., ge=0, description="Stock mínimo del producto")
    description: Optional[str] = Field(None, description="Descripción detallada del producto")
    price: Optional[float] = Field(None, ge=0, description="Precio unitario del producto")
    qc_status: Optional[str] = Field(None, description="Estado de calidad: approved, pending, rejected")
    category_id: Optional[int] = Field(None, description="ID de la categoría")
    location_id: Optional[int] = Field(None, description="ID de la ubicación")
    supplier_id: Optional[int] = Field(None, description="ID del proveedor")

    model_config = ConfigDict(from_attributes=True)

    @field_validator('code')
    def code_must_be_alphanumeric(cls, v):
        """Validar que el código sea alfanumérico, sin espacios ni caracteres especiales"""
        if not re.match(r'^[a-zA-Z0-9-_]+$', v):
            raise ValueError('El código debe contener solo letras, números, guiones o guiones bajos')
        return v.upper()  # Normalizar códigos a mayúsculas


class ProductCreate(ProductBase):
    """
    Esquema para la creación de productos.
    """
    pass


class ProductUpdate(BaseModel):
    """
    Esquema para actualización parcial de productos.
    """
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    current_stock: Optional[float] = Field(None, ge=0)
    min_stock: Optional[float] = Field(None, ge=0)
    description: Optional[str] = None
    price: Optional[float] = Field(None, ge=0)
    qc_status: Optional[str] = None
    category_id: Optional[int] = None
    location_id: Optional[int] = None
    supplier_id: Optional[int] = None

    model_config = ConfigDict(from_attributes=True)


class ProductInDB(ProductBase):
    """
    Esquema para representar un producto almacenado en la base de datos.
    """
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None


# Modelos para respuesta con relaciones
class CategoryBase(BaseModel):
    name: str
    model_config = ConfigDict(from_attributes=True)


class CategoryResponse(CategoryBase):
    id: int


class LocationBase(BaseModel):
    name: str
    model_config = ConfigDict(from_attributes=True)


class LocationResponse(LocationBase):
    id: int


class SupplierBase(BaseModel):
    name: str
    contact: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    model_config = ConfigDict(from_attributes=True)


class SupplierResponse(SupplierBase):
    id: int


class ProductResponse(ProductInDB):
    """
    Esquema para respuestas de productos.
    """
    category: Optional[CategoryResponse] = None
    location: Optional[LocationResponse] = None
    supplier: Optional[SupplierResponse] = None


class AlertProduct(BaseModel):
    """
    Esquema para productos con alertas de stock bajo.
    """
    id: int
    name: str
    code: str
    current_stock: float
    min_stock: float
    difference: float
    category: Optional[str] = None
    location: Optional[str] = None
    supplier: Optional[str] = None
    daysToStockOut: Optional[int] = Field(None, description="Días estimados para quedarse sin stock")
    lead_time: Optional[int] = Field(None, description="Tiempo estimado de entrega del proveedor")

    model_config = ConfigDict(from_attributes=True)
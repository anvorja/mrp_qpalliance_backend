# app/services/product_service.py
from sqlalchemy.orm import Session, joinedload
from sqlalchemy.exc import IntegrityError

from app.models import Location, Category, Supplier, Product

from app.schemas.product import ProductCreate, ProductUpdate, AlertProduct
from typing import List, Optional, cast


class ProductService:
    """
    Servicio para operaciones relacionadas con productos.
    """

    @staticmethod
    def get_products(db: Session, skip: int = 0, limit: int = 100) -> List[Product]:
        """
        Obtiene lista de productos paginada con sus relaciones.
        """
        products = (db.query(Product)
                    .options(joinedload(Product.category),
                             joinedload(Product.location),
                             joinedload(Product.supplier))
                    .offset(skip)
                    .limit(limit)
                    .all())
        return cast(List[Product], products)

    @staticmethod
    def get_product_by_id(db: Session, product_id: int) -> Optional[Product]:
        """
        Obtiene un producto por su ID con sus relaciones.
        """
        return (db.query(Product)
                .options(joinedload(Product.category),
                         joinedload(Product.location),
                         joinedload(Product.supplier))
                .filter(Product.id == product_id)
                .first())

    @staticmethod
    def get_product_by_code(db: Session, code: str) -> Optional[Product]:
        """
        Obtiene un producto por su código.
        """
        return db.query(Product).filter(Product.code == code.upper()).first()

    @staticmethod
    def create_product(db: Session, product: ProductCreate) -> Product:
        """
        Crea un nuevo producto.
        """
        # Verificar si ya existe un producto con el mismo código
        existing_product = ProductService.get_product_by_code(db, product.code)
        if existing_product:
            raise ValueError(f"Ya existe un producto con el código {product.code}")

        # Crear el diccionario de datos para el nuevo producto
        product_data = product.model_dump(exclude_unset=True)

        # Crear nuevo producto
        try:
            db_product = Product(**product_data)
            db.add(db_product)
            db.commit()
            db.refresh(db_product)
            return db_product
        except IntegrityError:
            db.rollback()
            raise ValueError("Error al crear el producto. Verifique los datos.")

    @staticmethod
    def update_product(db: Session, product_id: int, product_data: ProductUpdate) -> Optional[Product]:
        """
        Actualiza un producto existente.
        """
        db_product = ProductService.get_product_by_id(db, product_id)
        if db_product is None:
            return None

        # Actualizar solo los campos presentes
        update_data = product_data.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(db_product, key, value)

        try:
            db.commit()
            db.refresh(db_product)
            return db_product
        except IntegrityError:
            db.rollback()
            raise ValueError("Error al actualizar el producto.")

    @staticmethod
    def delete_product(db: Session, product_id: int) -> bool:
        """
        Elimina un producto por su ID.
        """
        db_product = ProductService.get_product_by_id(db, product_id)
        if db_product is None:
            return False

        try:
            db.delete(db_product)
            db.commit()
            return True
        except Exception:
            db.rollback()
            raise ValueError("Error al eliminar el producto.")

    @staticmethod
    def get_low_stock_products(db: Session) -> List[AlertProduct]:
        """
        Obtiene productos con stock por debajo del mínimo.
        """
        products = (db.query(Product)
                    .options(joinedload(Product.category),
                             joinedload(Product.location),
                             joinedload(Product.supplier))
                    .filter(Product.current_stock < Product.min_stock)
                    .all())

        # Transformar a modelo de alerta
        alerts = []
        for p in products:
            # Datos básicos
            alert_data = {
                "id": p.id,
                "name": p.name,
                "code": p.code,
                "current_stock": p.current_stock,
                "min_stock": p.min_stock,
                "difference": p.min_stock - p.current_stock,
                "category": p.category.name if p.category else None,
                "location": p.location.name if p.location else None,
                "supplier": p.supplier.name if p.supplier else None,
                # Valores predeterminados para los días
                "daysToStockOut": 15,  # Esto se podría calcular con histórico real
                "lead_time": 7 if p.supplier else 14  # Tiempo estimado según proveedor
            }

            alert = AlertProduct(**alert_data)
            alerts.append(alert)

        return alerts

    @staticmethod
    def get_categories(db: Session) -> List[Category]:
        """
        Obtiene todas las categorías.
        """
        return db.query(Category).all()

    @staticmethod
    def get_locations(db: Session) -> List[Location]:
        """
        Obtiene todas las ubicaciones.
        """
        return db.query(Location).all()

    @staticmethod
    def get_suppliers(db: Session) -> List[Supplier]:
        """
        Obtiene todos los proveedores.
        """
        return db.query(Supplier).all()
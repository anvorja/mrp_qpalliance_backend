# app/services/movement_service.py
from sqlalchemy.orm import Session, joinedload
from sqlalchemy.exc import IntegrityError
from typing import List, Optional
from app.models import Movement, Product
from app.schemas.movement import MovementCreate, MovementResponse

class MovementService:
    """
    Servicio para operaciones relacionadas con movimientos de inventario.
    """

    @staticmethod
    def get_movements(db: Session, skip: int = 0, limit: int = 100, type_filter: Optional[str] = None) -> List[
        Movement]:
        """
        Obtiene lista de movimientos paginada con sus relaciones.
        """
        query = db.query(Movement).options(joinedload(Movement.product))

        # Aplicar filtro por tipo si se proporciona
        if type_filter and type_filter != "all":
            query = query.filter(Movement.type == type_filter)

        # Ordenar por fecha de creación (más reciente primero)
        query = query.order_by(Movement.created_at.desc())

        # Aplicar paginación
        return query.offset(skip).limit(limit).all()

    @staticmethod
    def get_movement_by_id(db: Session, movement_id: int) -> Optional[Movement]:
        """
        Obtiene un movimiento por su ID con sus relaciones.
        """
        return (db.query(Movement)
                .options(joinedload(Movement.product))
                .filter(Movement.id == movement_id)
                .first())

    @staticmethod
    def create_movement(db: Session, movement: MovementCreate) -> Movement:
        """
        Crea un nuevo movimiento de inventario y actualiza el stock del producto.
        """
        # Verificar que el producto existe
        product = db.query(Product).filter(Product.id == movement.product_id).first()
        if not product:
            raise ValueError(f"No existe un producto con el ID {movement.product_id}")

        # Calcular el nuevo stock según el tipo de movimiento
        new_stock = float(product.current_stock)
        if movement.type == "in":
            new_stock += float(movement.quantity)
        elif movement.type == "out":
            if product.current_stock < movement.quantity:
                raise ValueError(f"Stock insuficiente...")
            new_stock -= float(movement.quantity)
        elif movement.type == "adjustment":
            new_stock = max(0.0, float(product.current_stock) + float(movement.quantity))

        # Crear el movimiento
        try:
            db_movement = Movement(
                type=movement.type,
                quantity=movement.quantity,
                resulting_stock=new_stock,
                product_id=movement.product_id,
                reference=movement.reference,
                notes=movement.notes,
                user=movement.user
            )

            # Actualizar el stock del producto
            product.current_stock = new_stock

            db.add(db_movement)
            db.commit()
            db.refresh(db_movement)
            return db_movement
        except IntegrityError:
            db.rollback()
            raise ValueError("Error al crear el movimiento. Verifique los datos.")

    @staticmethod
    def get_product_movements(db: Session, product_id: int, skip: int = 0, limit: int = 100) -> List[Movement]:
        """
        Obtiene los movimientos de un producto específico.
        """
        return (db.query(Movement)
                .filter(Movement.product_id == product_id)
                .order_by(Movement.created_at.desc())
                .offset(skip)
                .limit(limit)
                .all())
# app/api/v1/endpoints/movements.py
from flask import Blueprint, request, jsonify
from app.schemas.movement import MovementCreate, MovementResponse
from app.services.movement_service import MovementService
from app.db.session import get_db
from sqlalchemy.exc import SQLAlchemyError

movements_bp = Blueprint('movements', __name__)


@movements_bp.route('', methods=['GET'])
def get_movements():
    """
    Obtiene la lista de movimientos de inventario.
    """
    try:
        db = next(get_db())
        skip = int(request.args.get('skip', 0))
        limit = int(request.args.get('limit', 100))
        type_filter = request.args.get('type', None)

        # Validar que los parámetros son válidos
        if skip < 0 or limit < 1 or limit > 100:
            return jsonify({
                'error': 'Parámetros de paginación inválidos'
            }), 400

        movements = MovementService.get_movements(db, skip, limit, type_filter)

        # Convertir a formato de respuesta
        result = []
        for movement in movements:
            result.append({
                "id": movement.id,
                "type": movement.type,
                "quantity": movement.quantity,
                "resulting_stock": movement.resulting_stock,
                "reference": movement.reference,
                "notes": movement.notes,
                "user": movement.user,
                "created_at": movement.created_at.isoformat(),
                "product_id": movement.product_id,
                "product_name": movement.product.name,
                "product_code": movement.product.code
            })

        return jsonify(result), 200
    except ValueError:
        return jsonify({
            'error': 'Parámetros de paginación inválidos'
        }), 400
    except SQLAlchemyError as _:
        return jsonify({
            'error': 'Error al consultar movimientos'
        }), 500


@movements_bp.route('', methods=['POST'])
def create_movement():
    """
    Crea un nuevo movimiento de inventario.
    """
    try:
        db = next(get_db())
        data = request.get_json()

        # Validar los datos recibidos
        movement_create = MovementCreate(**data)

        # Intenta crear el movimiento
        new_movement = MovementService.create_movement(db, movement_create)

        # Preparar la respuesta
        response_data = {
            "id": new_movement.id,
            "type": new_movement.type,
            "quantity": new_movement.quantity,
            "resulting_stock": new_movement.resulting_stock,
            "reference": new_movement.reference,
            "notes": new_movement.notes,
            "user": new_movement.user,
            "created_at": new_movement.created_at.isoformat(),
            "product_id": new_movement.product_id
        }

        return jsonify(response_data), 201
    except ValueError as e:
        return jsonify({
            'error': f'Datos inválidos: {str(e)}'
        }), 400
    except SQLAlchemyError as _:
        return jsonify({
            'error': 'Error al crear el movimiento'
        }), 500


@movements_bp.route('/product/<int:product_id>', methods=['GET'])
def get_product_movements(product_id: int):
    """
    Obtiene los movimientos de un producto específico.
    """
    try:
        db = next(get_db())
        skip = int(request.args.get('skip', 0))
        limit = int(request.args.get('limit', 100))

        movements = MovementService.get_product_movements(db, product_id, skip, limit)

        # Convertir a formato de respuesta
        result = []
        for movement in movements:
            result.append({
                "id": movement.id,
                "type": movement.type,
                "quantity": movement.quantity,
                "resulting_stock": movement.resulting_stock,
                "reference": movement.reference,
                "notes": movement.notes,
                "user": movement.user,
                "created_at": movement.created_at.isoformat(),
                "product_id": movement.product_id
            })

        return jsonify(result), 200
    except ValueError:
        return jsonify({
            'error': 'Parámetros de paginación inválidos'
        }), 400
    except SQLAlchemyError as _:
        return jsonify({
            'error': 'Error al consultar movimientos'
        }), 500

# app/api/v1/endpoints/products.py
from flask import Blueprint, request, jsonify

from app.models.product import Product
from app.schemas.product import ProductCreate, ProductUpdate, ProductResponse
from app.services.product_service import ProductService
from app.db.session import get_db
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import joinedload

from app.utils.security import rate_limit, protect_endpoint

# Crear un Blueprint para los endpoints de productos
products_bp = Blueprint('products', __name__)


@products_bp.route('', methods=['GET'])
def get_products():
    """
    Obtiene la lista de productos.
    """
    try:
        db = next(get_db())
        skip = int(request.args.get('skip', 0))
        limit = int(request.args.get('limit', 100))

        # Filtros opcionales
        category = request.args.get('category', None)
        location = request.args.get('location', None)
        supplier = request.args.get('supplier', None)
        search = request.args.get('search', None)
        stock_status = request.args.get('stock_status', None)

        # Obtener productos con sus relaciones
        query = db.query(Product).options(
            joinedload(Product.category),
            joinedload(Product.location),
            joinedload(Product.supplier)
        )

        # Aplicar filtros si existen
        if category and category != "all":
            query = query.filter(Product.category_id == int(category))

        if location and location != "all":
            query = query.filter(Product.location_id == int(location))

        if supplier and supplier != "all":
            query = query.filter(Product.supplier_id == int(supplier))

        if search:
            search_term = f"%{search}%"
            query = query.filter(
                (Product.name.ilike(search_term)) |
                (Product.code.ilike(search_term))
            )

        if stock_status:
            if stock_status == "low":
                query = query.filter(Product.current_stock < Product.min_stock)
            elif stock_status == "ok":
                query = query.filter(Product.current_stock >= Product.min_stock)

        # Contar total antes de aplicar paginación
        total = query.count()

        # Aplicar paginación
        products = query.offset(skip).limit(limit).all()

        # Transformar a respuesta API
        result = []
        for product in products:
            product_data = {
                "id": product.id,
                "name": product.name,
                "code": product.code,
                "current_stock": product.current_stock,
                "min_stock": product.min_stock,
                "description": product.description,
                "price": product.price,
                "qc_status": product.qc_status,
                "created_at": product.created_at.isoformat() if product.created_at else None,
                "updated_at": product.updated_at.isoformat() if product.updated_at else None,
                "category": product.category.name if product.category else None,
                "location": product.location.name if product.location else None,
                "supplier": product.supplier.name if product.supplier else None,
                "category_id": product.category_id,
                "location_id": product.location_id,
                "supplier_id": product.supplier_id
            }
            result.append(product_data)

        # Devolver respuesta paginada
        return jsonify({
            "items": result,
            "total": total,
            "page": skip // limit + 1,
            "pages": (total + limit - 1) // limit if limit > 0 else 0,
            "limit": limit
        }), 200
    except ValueError:
        return jsonify({
            'error': 'Parámetros de paginación inválidos'
        }), 400
    except SQLAlchemyError as e:
        return jsonify({
            'error': f'Error al consultar productos: {str(e)}'
        }), 500

@products_bp.route('', methods=['POST'])
@protect_endpoint()
def create_product(current_user):
    """
    Crea un nuevo producto.
    """
    try:
        db = next(get_db())
        data = request.get_json()

        # Validar los datos recibidos
        product_create = ProductCreate(**data)

        # Intenta crear el producto
        new_product = ProductService.create_product(db, product_create)

        # Obtener producto completo con relaciones
        product_with_relations = ProductService.get_product_by_id(db, new_product.id)

        # Convertir a formato de respuesta
        response_data = {
            "id": product_with_relations.id,
            "name": product_with_relations.name,
            "code": product_with_relations.code,
            "current_stock": product_with_relations.current_stock,
            "min_stock": product_with_relations.min_stock,
            "description": product_with_relations.description,
            "price": product_with_relations.price,
            "qc_status": product_with_relations.qc_status,
            "created_at": product_with_relations.created_at.isoformat() if product_with_relations.created_at else None,
            "updated_at": product_with_relations.updated_at.isoformat() if product_with_relations.updated_at else None,
            "category": product_with_relations.category.name if product_with_relations.category else None,
            "location": product_with_relations.location.name if product_with_relations.location else None,
            "supplier": product_with_relations.supplier.name if product_with_relations.supplier else None,
            "category_id": product_with_relations.category_id,
            "location_id": product_with_relations.location_id,
            "supplier_id": product_with_relations.supplier_id
        }

        return jsonify(response_data), 201
    except ValueError as e:
        return jsonify({
            'error': f'Datos inválidos: {str(e)}'
        }), 400
    except SQLAlchemyError as _:
        return jsonify({
            'error': 'Error al crear el producto'
        }), 500


@products_bp.route('/<int:product_id>', methods=['GET'])
def get_product(product_id: int):
    """
    Obtiene un producto por su ID.
    """
    try:
        db = next(get_db())
        product = ProductService.get_product_by_id(db, product_id)

        if product is None:
            return jsonify({
                'error': 'Producto no encontrado'
            }), 404

        # Convertir a formato de respuesta
        response_data = {
            "id": product.id,
            "name": product.name,
            "code": product.code,
            "current_stock": product.current_stock,
            "min_stock": product.min_stock,
            "description": product.description,
            "price": product.price,
            "qc_status": product.qc_status,
            "created_at": product.created_at.isoformat() if product.created_at else None,
            "updated_at": product.updated_at.isoformat() if product.updated_at else None,
            "category": product.category.name if product.category else None,
            "location": product.location.name if product.location else None,
            "supplier": product.supplier.name if product.supplier else None,
            "category_id": product.category_id,
            "location_id": product.location_id,
            "supplier_id": product.supplier_id
        }

        return jsonify(response_data), 200
    except SQLAlchemyError as e:
        return jsonify({
            'error': f'Error al consultar el producto: {str(e)}'
        }), 500


@products_bp.route('/<int:product_id>', methods=['PUT'])
@protect_endpoint()
def update_product(current_user, product_id: int):
    """
    Actualiza completamente un producto existente.
    Requiere todos los campos del producto.
    """
    try:
        db = next(get_db())
        data = request.get_json()

        # Validar los datos recibidos
        product_update = ProductUpdate(**data)

        # Intenta actualizar el producto
        updated_product = ProductService.update_product(db, product_id, product_update)

        if updated_product is None:
            return jsonify({
                'error': 'Producto no encontrado'
            }), 404

        # Obtener producto completo con relaciones
        product_with_relations = ProductService.get_product_by_id(db, updated_product.id)

        # Convertir a formato de respuesta
        response_data = {
            "id": product_with_relations.id,
            "name": product_with_relations.name,
            "code": product_with_relations.code,
            "current_stock": product_with_relations.current_stock,
            "min_stock": product_with_relations.min_stock,
            "description": product_with_relations.description,
            "price": product_with_relations.price,
            "qc_status": product_with_relations.qc_status,
            "created_at": product_with_relations.created_at.isoformat() if product_with_relations.created_at else None,
            "updated_at": product_with_relations.updated_at.isoformat() if product_with_relations.updated_at else None,
            "category": product_with_relations.category.name if product_with_relations.category else None,
            "location": product_with_relations.location.name if product_with_relations.location else None,
            "supplier": product_with_relations.supplier.name if product_with_relations.supplier else None,
            "category_id": product_with_relations.category_id,
            "location_id": product_with_relations.location_id,
            "supplier_id": product_with_relations.supplier_id
        }

        return jsonify(response_data), 200
    except ValueError as e:
        return jsonify({
            'error': f'Datos inválidos: {str(e)}'
        }), 400
    except SQLAlchemyError as e:
        return jsonify({
            'error': f'Error al actualizar el producto: {str(e)}'
        }), 500


@products_bp.route('/<int:product_id>', methods=['PATCH'])
@protect_endpoint()
def patch_product(current_user, product_id: int):
    """
    Actualiza parcialmente un producto existente.
    Solo requiere los campos que se desean actualizar.
    """
    try:
        db = next(get_db())
        data = request.get_json()

        # Validar los datos recibidos - solo los campos proporcionados
        product_update = ProductUpdate(**data)

        # Intenta actualizar parcialmente el producto
        updated_product = ProductService.update_product(db, product_id, product_update)

        if updated_product is None:
            return jsonify({
                'error': 'Producto no encontrado'
            }), 404

        # Obtener producto completo con relaciones
        product_with_relations = ProductService.get_product_by_id(db, updated_product.id)

        # Convertir a formato de respuesta
        response_data = {
            "id": product_with_relations.id,
            "name": product_with_relations.name,
            "code": product_with_relations.code,
            "current_stock": product_with_relations.current_stock,
            "min_stock": product_with_relations.min_stock,
            "description": product_with_relations.description,
            "price": product_with_relations.price,
            "qc_status": product_with_relations.qc_status,
            "created_at": product_with_relations.created_at.isoformat() if product_with_relations.created_at else None,
            "updated_at": product_with_relations.updated_at.isoformat() if product_with_relations.updated_at else None,
            "category": product_with_relations.category.name if product_with_relations.category else None,
            "location": product_with_relations.location.name if product_with_relations.location else None,
            "supplier": product_with_relations.supplier.name if product_with_relations.supplier else None,
            "category_id": product_with_relations.category_id,
            "location_id": product_with_relations.location_id,
            "supplier_id": product_with_relations.supplier_id
        }

        return jsonify(response_data), 200
    except ValueError as e:
        return jsonify({
            'error': f'Datos inválidos: {str(e)}'
        }), 400
    except SQLAlchemyError as e:
        return jsonify({
            'error': f'Error al actualizar el producto: {str(e)}'
        }), 500


@products_bp.route('/<int:product_id>', methods=['DELETE'])
@protect_endpoint()
def delete_product(current_user, product_id: int):
    """
    Elimina un producto por su ID.
    """
    try:
        db = next(get_db())
        success = ProductService.delete_product(db, product_id)

        if not success:
            return jsonify({
                'error': 'Producto no encontrado'
            }), 404

        return jsonify({
            'message': f'Producto con ID {product_id} eliminado correctamente'
        }), 200
    except SQLAlchemyError as e:
        return jsonify({
            'error': f'Error al eliminar el producto: {str(e)}'
        }), 500


@products_bp.route('/alerts', methods=['GET'])
def get_alerts():
    """
    Obtiene productos con stock por debajo del mínimo.
    """
    try:
        db = next(get_db())
        low_stock_products = ProductService.get_low_stock_products(db)

        # Convertir a formato de respuesta
        result = []
        for product in low_stock_products:
            result.append(product.model_dump())

        return jsonify(result), 200
    except SQLAlchemyError as e:
        return jsonify({
            'error': f'Error al consultar alertas de stock: {str(e)}'
        }), 500
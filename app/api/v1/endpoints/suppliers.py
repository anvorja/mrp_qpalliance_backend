# app/api/v1/endpoints/suppliers.py
from flask import Blueprint, request, jsonify
from app.db.session import get_db
from sqlalchemy.exc import SQLAlchemyError

from app.models import Supplier

suppliers_bp = Blueprint('suppliers', __name__)


@suppliers_bp.route('', methods=['GET'])
def get_suppliers():
    """
    Obtiene todos los proveedores.
    """
    try:
        db = next(get_db())
        suppliers = db.query(Supplier).all()

        result = []
        for supplier in suppliers:
            result.append({
                "id": supplier.id,
                "name": supplier.name,
                "contact": supplier.contact,
                "email": supplier.email,
                "phone": supplier.phone
            })

        return jsonify(result), 200
    except SQLAlchemyError as _:
        return jsonify({
            'error': 'Error al consultar proveedores'
        }), 500


@suppliers_bp.route('', methods=['POST'])
def create_supplier():
    """
    Crea un nuevo proveedor.
    """
    try:
        db = next(get_db())
        data = request.get_json()

        if not data or "name" not in data:
            return jsonify({"error": "El nombre del proveedor es obligatorio"}), 400

        # Validar que el nombre no esté vacío
        if not data["name"].strip():
            return jsonify({"error": "El nombre del proveedor no puede estar vacío"}), 400

        # Verificar si ya existe un proveedor con ese nombre
        existing = db.query(Supplier).filter(Supplier.name == data["name"]).first()
        if existing:
            return jsonify({"error": f"Ya existe un proveedor con el nombre '{data['name']}'"}), 400

        new_supplier = Supplier(
            name=data["name"],
            contact=data.get("contact"),
            email=data.get("email"),
            phone=data.get("phone")
        )
        db.add(new_supplier)

        try:
            db.commit()
            db.refresh(new_supplier)
        except SQLAlchemyError:
            db.rollback()
            raise

        return jsonify({
            "id": new_supplier.id,
            "name": new_supplier.name,
            "contact": new_supplier.contact,
            "email": new_supplier.email,
            "phone": new_supplier.phone
        }), 201
    except SQLAlchemyError as _:
        return jsonify({"error": "Error al crear el proveedor"}), 500
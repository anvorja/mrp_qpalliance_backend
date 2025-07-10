# app/api/v1/endpoints/locations.py
from flask import Blueprint, request, jsonify
from app.db.session import get_db
from sqlalchemy.exc import SQLAlchemyError
from app.models import Location

locations_bp = Blueprint('locations', __name__)


@locations_bp.route('', methods=['GET'])
def get_locations():
    """
    Obtiene todas las ubicaciones.
    """
    try:
        db = next(get_db())
        locations = db.query(Location).all()

        result = []
        for location in locations:
            result.append({
                "id": location.id,
                "name": location.name
            })

        return jsonify(result), 200
    except SQLAlchemyError as _:
        return jsonify({
            'error': 'Error al consultar ubicaciones'
        }), 500


@locations_bp.route('', methods=['POST'])
def create_location():
    """
    Crea una nueva ubicación.
    """
    try:
        db = next(get_db())
        data = request.get_json()

        if not data or "name" not in data:
            return jsonify({"error": "El nombre de la ubicación es obligatorio"}), 400

        # Validar que el nombre no esté vacío
        if not data["name"].strip():
            return jsonify({"error": "El nombre de la ubicación no puede estar vacío"}), 400

        # Verificar si ya existe una ubicación con ese nombre
        existing = db.query(Location).filter(Location.name == data["name"]).first()
        if existing:
            return jsonify({"error": f"Ya existe una ubicación con el nombre '{data['name']}'"}), 400

        new_location = Location(name=data["name"])
        db.add(new_location)

        try:
            db.commit()
            db.refresh(new_location)
        except SQLAlchemyError:
            db.rollback()
            raise

        return jsonify({
            "id": new_location.id,
            "name": new_location.name
        }), 201
    except SQLAlchemyError as _:
        return jsonify({"error": "Error al crear la ubicación"}), 500
# app/api/v1/endpoints/categories.py
from flask import Blueprint, request, jsonify
from app.db.session import get_db
from sqlalchemy.exc import SQLAlchemyError

from app.models import Category

categories_bp = Blueprint('categories', __name__)


@categories_bp.route('', methods=['GET'])
def get_categories():
    """
    Obtiene todas las categorías.
    """
    try:
        db = next(get_db())
        categories = db.query(Category).all()

        result = []
        for category in categories:
            result.append({
                "id": category.id,
                "name": category.name
            })

        return jsonify(result), 200
    except SQLAlchemyError as _:
        return jsonify({
            'error': 'Error al consultar categorías'
        }), 500


@categories_bp.route('', methods=['POST'])
def create_category():
    """
    Crea una nueva categoría.
    """
    try:
        db = next(get_db())
        data = request.get_json()

        if not data or "name" not in data:
            return jsonify({"error": "El nombre de la categoría es obligatorio"}), 400

        # Validar que el nombre no esté vacío
        if not data["name"].strip():
            return jsonify({"error": "El nombre de la categoría no puede estar vacío"}), 400

        # Verificar si ya existe una categoría con ese nombre
        existing = db.query(Category).filter(Category.name == data["name"]).first()
        if existing:
            return jsonify({"error": f"Ya existe una categoría con el nombre '{data['name']}'"}), 400

        new_category = Category(name=data["name"])
        db.add(new_category)

        try:
            db.commit()
            db.refresh(new_category)
        except SQLAlchemyError:
            db.rollback()
            raise

        return jsonify({
            "id": new_category.id,
            "name": new_category.name
        }), 201
    except SQLAlchemyError as _:
        return jsonify({"error": "Error al crear la categoría"}), 500
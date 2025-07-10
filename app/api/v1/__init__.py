# app/api/v1/__init__.py
from flask import Blueprint

from .endpoints.auth import auth_bp
from .endpoints.products import products_bp
from .endpoints.categories import categories_bp
from .endpoints.locations import locations_bp
from .endpoints.suppliers import suppliers_bp
from .endpoints.movements import movements_bp

# Crear un Blueprint principal para la versión 1 de la API
api_v1 = Blueprint('api_v1', __name__, url_prefix='/api/v1')

# Registrar los endpoints
api_v1.register_blueprint(products_bp, url_prefix='/products')
api_v1.register_blueprint(categories_bp, url_prefix='/categories')
api_v1.register_blueprint(locations_bp, url_prefix='/locations')
api_v1.register_blueprint(suppliers_bp, url_prefix='/suppliers')
api_v1.register_blueprint(movements_bp, url_prefix='/movements')
api_v1.register_blueprint(auth_bp, url_prefix='/auth')

# Definir una ruta para verificar el estado de la API
@api_v1.route('/health', methods=['GET'])
def health_check():
    """
    Endpoint para verificar el estado de la API.
    """
    return {'status': 'ok', 'version': '1.0.0'}, 200
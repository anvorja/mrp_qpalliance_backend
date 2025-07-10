# app/main.py
from flask import Flask, jsonify
from flask_cors import CORS
from app.api.v1 import api_v1
from app.db.base import Base, engine
from app.utils.swagger import setup_swagger
import os
import logging
from dotenv import load_dotenv

# Variables de entorno
load_dotenv()

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.StreamHandler()]
)


def create_app():
    """
    Configurar la aplicación Flask.
    """
    app = Flask(__name__)

    # Configuración de seguridad
    app.config['JSON_SORT_KEYS'] = False
    app.config['JSONIFY_PRETTYPRINT_REGULAR'] = True

    # CORS para permitir solicitudes desde el frontend
    CORS(app,
         resources={r"/api/*": {"origins": os.getenv("CORS_ORIGINS", "*")}},
         supports_credentials=True,
         allow_headers=["Content-Type", "Authorization", "X-Requested-With"],
         methods=["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH"]
         )

    # Registrar blueprints de la API
    app.register_blueprint(api_v1)

    setup_swagger(app)

    # Configurar manejo de errores
    @app.errorhandler(404)
    def not_found(e):
        return jsonify({"error": f"Recurso no encontrado: {str(e)}"}), 404

    @app.errorhandler(500)
    def server_error(e):
        return jsonify({"error": f"Error interno del servidor: {str(e)}"}), 500

    # Crear tablas en la base de datos
    Base.metadata.create_all(bind=engine)

    return app


if __name__ == "__main__":
    flask_app = create_app()
    port = int(os.getenv("PORT", 5000))
    flask_app.run(host="0.0.0.0", port=port, debug=os.getenv("DEBUG", "False").lower() == "true")
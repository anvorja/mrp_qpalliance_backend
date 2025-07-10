# app/utils/security.py
from flask import request, jsonify
import re
import bleach
from functools import wraps
from app.auth.auth import token_required as auth_token_required


def sanitize_input(data):
    """
    Sanitiza los datos de entrada para prevenir XSS.
    """
    if isinstance(data, str):
        return bleach.clean(data)
    elif isinstance(data, dict):
        return {k: sanitize_input(v) for k, v in data.items()}
    elif isinstance(data, list):
        return [sanitize_input(i) for i in data]
    return data


def validate_input(data):
    """
    Validar los datos de entrada para prevenir inyección SQL y otros ataques.
    """
    if isinstance(data, str):
        # Detectar posibles inyecciones SQL
        sql_patterns = [
            r'(\s|^)(SELECT|INSERT|UPDATE|DELETE|DROP|UNION|ALTER)(\s|$)',
            r'(\s|^)(FROM|WHERE|GROUP BY|ORDER BY|HAVING)(\s|$)',
            r'(--|#|\\/\\*)',
            r';(\s|$)',
        ]
        for pattern in sql_patterns:
            if re.search(pattern, data, re.IGNORECASE):
                return False
    elif isinstance(data, dict):
        for k, v in data.items():
            if not validate_input(v):
                return False
    elif isinstance(data, list):
        for i in data:
            if not validate_input(i):
                return False
    return True


def protect_endpoint():
    """
    Decorador para proteger endpoints verificando autenticación y
    validando/sanitizando las entradas.
    """
    def decorator(f):
        @wraps(f)
        @auth_token_required
        def decorated_function(current_user, *args, **kwargs):

            if request.is_json:
                try:
                    data = request.get_json()

                    # Validar datos
                    if not validate_input(data):
                        return jsonify({
                            "error": "Datos de entrada inválidos. Se ha detectado un posible intento de inyección."
                        }), 400

                    # Sanitizar datos
                    sanitized_data = sanitize_input(data)

                    # Guardar datos sanitizados en un contexto local para esta solicitud
                    setattr(request, '_sanitized_json', sanitized_data)

                    # Modificar función get_json para que devuelva los datos sanitizados
                    original_get_json = request.get_json

                    def get_sanitized_json(*func_args, **func_kwargs):
                        return getattr(request, '_sanitized_json', original_get_json(*func_args, **func_kwargs))

                    request.get_json = get_sanitized_json

                except Exception as e:
                    return jsonify({"error": f"Error al procesar datos JSON: {str(e)}"}), 400

            # Sanitizar parámetros de consulta
            if request.args:
                for key, value in request.args.items():
                    if not validate_input(value):
                        return jsonify({"error": f"Parámetro de consulta '{key}' inválido."}), 400

            # Pasar el usuario autenticado a la función
            return f(current_user, *args, **kwargs)

        return decorated_function
    return decorator

def rate_limit(limit_per_minute=60):
    """
    Implementación simple de rate limiting.
    En una aplicación de producción, se recomendaría usar Redis u otro
    almacenamiento para mantener el seguimiento de las solicitudes.
    """
    from datetime import datetime, timedelta

    # Almacen en memoria para las solicitudes (IP -> [timestamps])
    request_store = {}

    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            # Obtener la IP del cliente
            client_ip = request.remote_addr

            # Obtener solicitudes actuales
            now = datetime.now()
            minute_ago = now - timedelta(minutes=1)

            # Inicializar si es la primera solicitud
            if client_ip not in request_store:
                request_store[client_ip] = []

            # Filtrar solicitudes antiguas
            request_store[client_ip] = [ts for ts in request_store[client_ip] if ts > minute_ago]

            # Verificar límite
            if len(request_store[client_ip]) >= limit_per_minute:
                return jsonify({
                    "error": "Demasiadas solicitudes. Por favor, inténtelo más tarde.",
                    "retry_after": "60 segundos"
                }), 429

            # Registrar la solicitud
            request_store[client_ip].append(now)

            return f(*args, **kwargs)

        return decorated_function

    return decorator
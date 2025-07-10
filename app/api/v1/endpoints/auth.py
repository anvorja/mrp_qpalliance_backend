# app/api/v1/endpoints/auth.py
from flask import Blueprint, request, jsonify, make_response
from sqlalchemy.exc import SQLAlchemyError
from datetime import datetime, timezone
import os
from app.db.session import get_db
from app.models.user import User
from app.auth.auth import (
    get_password_hash,
    verify_password,
    create_access_token,
    create_refresh_token,
    verify_refresh_token,
    token_required
)

auth_bp = Blueprint('auth', __name__)


# Configurar cookies seguras
def set_auth_cookies(response, access_token, refresh_token):
    # Detectar si estamos en modo de producción
    is_prod = os.getenv("ENVIRONMENT", "development") == "production"

    # Configurar cookie para token de acceso
    response.set_cookie(
        'access_token',
        access_token,
        max_age=30 * 60,  # 30 minutos en segundos
        httponly=True,  # Protege contra XSS
        samesite='Lax',  # Protege contra CSRF
        secure=is_prod,  # Solo HTTPS en producción
        path='/'  # Accesible desde cualquier ruta
    )

    # Configurar cookie para token de refresco
    response.set_cookie(
        'refresh_token',
        refresh_token,
        max_age=7 * 24 * 60 * 60,  # 7 días en segundos
        httponly=True,
        samesite='Lax',
        secure=is_prod,
        path='/'
    )

    # Para mejorar la compatibilidad CORS
    # response.headers.add('Access-Control-Allow-Credentials', 'true')

    return response


@auth_bp.route('/register', methods=['POST'])
def register():
    """
    Registra un nuevo usuario en el sistema.
    """
    try:
        db = next(get_db())
        data = request.get_json()

        if not data or "email" not in data or "password" not in data or "full_name" not in data:
            return jsonify({"error": "Datos incompletos"}), 400

        # Validar que el email no esté vacío
        if not data["email"].strip():
            return jsonify({"error": "El email no puede estar vacío"}), 400

        # Validar que la contraseña no esté vacía y tenga al menos 8 caracteres
        if not data["password"].strip() or len(data["password"]) < 8:
            return jsonify({"error": "La contraseña debe tener al menos 8 caracteres"}), 400

        # Verificar si ya existe un usuario con ese email
        existing = db.query(User).filter(User.email == data["email"]).first()
        if existing:
            return jsonify({"error": f"Ya existe un usuario con el email '{data['email']}'"}), 400

        # Crear nuevo usuario
        hashed_password = get_password_hash(data["password"])
        new_user = User(
            email=data["email"],
            full_name=data["full_name"],
            password=hashed_password,
            role=data.get("role", "user")
        )

        db.add(new_user)

        try:
            db.commit()
            db.refresh(new_user)
        except SQLAlchemyError:
            db.rollback()
            return jsonify({"error": "Error al crear el usuario"}), 500

        # Generar tokens
        access_token = create_access_token(new_user.id)
        refresh_token = create_refresh_token(new_user.id)

        # Preparar respuesta
        response_data = {
            "message": "Usuario registrado exitosamente",
            "user": {
                "id": new_user.id,
                "email": new_user.email,
                "full_name": new_user.full_name,
                "role": new_user.role
            }
        }

        response = make_response(jsonify(response_data), 201)
        return set_auth_cookies(response, access_token, refresh_token)

    except SQLAlchemyError as e:
        return jsonify({"error": f"Error de base de datos: {str(e)}"}), 500
    except Exception as e:
        return jsonify({"error": f"Error inesperado: {str(e)}"}), 500


@auth_bp.route('/login', methods=['POST'])
def login():
    """
    Inicia sesión y devuelve tokens de acceso y refresco.
    """
    try:
        db = next(get_db())
        data = request.get_json()

        if not data or "email" not in data or "password" not in data:
            return jsonify({"error": "Email y contraseña son requeridos"}), 400

        # Buscar usuario por email
        user = db.query(User).filter(User.email == data["email"]).first()

        # Verificar si el usuario existe y la contraseña es correcta
        if not user or not verify_password(data["password"], user.password):
            return jsonify({"error": "Email o contraseña incorrectos"}), 401

        # Verificar si el usuario está activo
        if not user.is_active:
            return jsonify({"error": "Usuario inactivo"}), 401

        # Actualizar último login con timezone aware
        user.last_login = datetime.now(timezone.utc)
        db.commit()

        # Generar tokens
        access_token = create_access_token(user.id)
        refresh_token = create_refresh_token(user.id)

        # Preparar respuesta
        response_data = {
            "message": "Inicio de sesión exitoso",
            "user": {
                "id": user.id,
                "email": user.email,
                "full_name": user.full_name,
                "role": user.role
            }
        }

        response = make_response(jsonify(response_data), 200)
        return set_auth_cookies(response, access_token, refresh_token)

    except SQLAlchemyError as e:
        return jsonify({"error": f"Error de base de datos: {str(e)}"}), 500
    except Exception as e:
        return jsonify({"error": f"Error inesperado: {str(e)}"}), 500


@auth_bp.route('/refresh', methods=['POST'])
def refresh():
    """
    Refresca el token de acceso usando el token de refresco.
    """
    try:
        # Obtener token de refresco de la cookie
        refresh_token = request.cookies.get('refresh_token')

        if not refresh_token:
            return jsonify({"error": "Token de refresco requerido"}), 401

        # Verificar token de refresco
        user_id = verify_refresh_token(refresh_token)

        if not user_id:
            return jsonify({"error": "Token de refresco inválido o expirado"}), 401

        # Obtener usuario
        db = next(get_db())
        user = db.query(User).filter(User.id == user_id).first()

        if not user or not user.is_active:
            return jsonify({"error": "Usuario no encontrado o inactivo"}), 401

        # Generar nuevo token de acceso
        new_access_token = create_access_token(user.id)

        # Preparar respuesta
        response_data = {
            "message": "Token refrescado exitosamente",
        }

        response = make_response(jsonify(response_data), 200)

        # Configurar cookie para nuevo token de acceso - usar la función compartida
        response = set_auth_cookies(response, new_access_token, refresh_token)

        return response

    except Exception as e:
        return jsonify({"error": f"Error inesperado: {str(e)}"}), 500


@auth_bp.route('/logout', methods=['POST'])
def logout():
    """
    Cierra la sesión del usuario eliminando las cookies.
    """
    response = make_response(jsonify({"message": "Sesión cerrada exitosamente"}), 200)

    # Eliminar cookies
    response.delete_cookie('access_token', path='/')
    response.delete_cookie('refresh_token', path='/')

    return response


@auth_bp.route('/me', methods=['GET'])
@token_required
def get_user_profile(current_user):
    """
    Obtiene el perfil del usuario autenticado.
    """
    return jsonify({
        "id": current_user.id,
        "email": current_user.email,
        "full_name": current_user.full_name,
        "role": current_user.role,
        "last_login": current_user.last_login.isoformat() if current_user.last_login else None,
        "created_at": current_user.created_at.isoformat() if current_user.created_at else None
    }), 200
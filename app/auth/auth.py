# app/auth/auth.py
from typing import Optional, Dict, Any
import os
from jose import jwt, JWTError
from jose.exceptions import ExpiredSignatureError
from flask import request, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps
from datetime import datetime, timedelta, timezone
from app.db.session import get_db
from app.models.user import User

# Configuración para JWT
SECRET_KEY = os.getenv("JWT_SECRET_KEY", "your-secret-key-change-in-production")
ACCESS_TOKEN_EXPIRE_MINUTES = 30  # 30 minutos para el token de acceso
REFRESH_TOKEN_EXPIRE_DAYS = 7  # 7 días para el token de refresco
ALGORITHM = "HS256"


# Función para crear tokens JWT
def create_token(data: Dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
    to_encode = data.copy()

    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=15)

    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


# Crear token de acceso
def create_access_token(user_id: int) -> str:
    return create_token(
        data={"sub": str(user_id), "type": "access"},
        expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    )


# Crear token de refresco
def create_refresh_token(user_id: int) -> str:
    return create_token(
        data={"sub": str(user_id), "type": "refresh"},
        expires_delta=timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    )


# Función para verificar contraseña
def verify_password(plain_password: str, hashed_password: str) -> bool:
    return check_password_hash(hashed_password, plain_password)


# Función para obtener contraseña hasheada
def get_password_hash(password: str) -> str:
    return generate_password_hash(password)


# Decorador para proteger rutas
def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None

        # Extraer token de la cookie
        if 'access_token' in request.cookies:
            token = request.cookies.get('access_token')

        # Si no hay token en la cookie, buscar en el encabezado Authorization
        if not token and 'Authorization' in request.headers:
            auth_header = request.headers['Authorization']
            if auth_header.startswith('Bearer '):
                token = auth_header.split(' ')[1]

        if not token:
            return jsonify({'error': 'Token de acceso requerido'}), 401

        try:
            # Decodificar token
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])

            # Verificar que sea un token de acceso
            if payload.get('type') != 'access':
                return jsonify({'error': 'Token inválido'}), 401

            user_id = int(payload['sub'])

            # Obtener el usuario de la base de datos
            db = next(get_db())
            current_user = db.query(User).filter(User.id == user_id).first()

            if current_user is None:
                return jsonify({'error': 'Usuario no encontrado'}), 401

            # Si el usuario está desactivado
            if not current_user.is_active:
                return jsonify({'error': 'Usuario inactivo'}), 401


        except ExpiredSignatureError:
            return jsonify({'error': 'Token expirado'}), 401
        except JWTError:
            return jsonify({'error': 'Token inválido'}), 401

        # Pasar el usuario actual a la función decorada
        return f(current_user, *args, **kwargs)

    return decorated


# Función para verificar token de refresco
def verify_refresh_token(refresh_token: str) -> Optional[int]:
    try:
        payload = jwt.decode(refresh_token, SECRET_KEY, algorithms=[ALGORITHM])

        # Verificar que sea un token de refresco
        if payload.get('type') != 'refresh':
            return None

        user_id = int(payload['sub'])
        return user_id
    except (ExpiredSignatureError, JWTError):
        return None

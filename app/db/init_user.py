# app/db/init_user.py
"""
Script para crear un usuario inicial de prueba en la base de datos.
Ejecución: python -m app.db.init_user
"""

import os
import sys
from sqlalchemy.orm import Session
from app.auth.auth import get_password_hash

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.db.base import engine, Base
from app.models.user import User


def create_test_user():
    """Crea un usuario de prueba en la base de datos."""
    # Crear una sesión
    with Session(engine) as session:
        # Verificar si ya existe el usuario
        test_email = "usertesting@qpalliance.co"
        existing_user = session.query(User).filter(User.email == test_email).first()

        if existing_user:
            print(f"El usuario con email {test_email} ya existe.")
            return

        # Crear contraseña hasheada
        hashed_password = get_password_hash("TestingQp#1")

        # Crear nuevo usuario
        new_user = User(
            email=test_email,
            full_name="Usuario de Prueba",
            password=hashed_password,
            role="admin"
        )

        session.add(new_user)
        session.commit()

        print(f"Usuario creado exitosamente:")
        print(f"Email: {test_email}")
        print(f"Contraseña: TestingQp#1")
        print(f"Rol: {new_user.role}")


if __name__ == "__main__":
    Base.metadata.create_all(bind=engine)

    create_test_user()

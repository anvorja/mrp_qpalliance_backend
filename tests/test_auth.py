# tests/test_auth.py
import unittest
import json
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from app.main import create_app
from app.models.user import User
from app.auth.auth import get_password_hash
from app.db.base import Base, engine
from app.db.session import SessionLocal


class AuthTestCase(unittest.TestCase):
    """Test case para las funcionalidades de autenticación."""

    def setUp(self):
        """Configurar datos de prueba antes de cada test."""
        self.app = create_app()
        self.app.config['TESTING'] = True
        self.client = self.app.test_client()

        # Crear una sesión de base de datos
        self.db = SessionLocal()

        # Crear usuario de prueba
        test_user = User(
            email="test@example.com",
            full_name="Usuario de Prueba",
            password=get_password_hash("Password1!"),
            role="user"
        )

        self.db.add(test_user)
        self.db.commit()
        self.db.refresh(test_user)
        self.test_user_id = test_user.id

        # Datos de prueba para login
        self.user_credentials = {
            "email": "test@example.com",
            "password": "Password1!"
        }

        # Datos de prueba para registro
        self.new_user_data = {
            "email": "new@example.com",
            "password": "NewPass1!",
            "full_name": "Usuario Nuevo"
        }

    def tearDown(self):
        """Limpiar después de cada test."""
        # Eliminar usuario de prueba
        user = self.db.query(User).filter(User.email == "test@example.com").first()
        if user:
            self.db.delete(user)

        # Eliminar usuario nuevo si se creó
        new_user = self.db.query(User).filter(User.email == "new@example.com").first()
        if new_user:
            self.db.delete(new_user)

        self.db.commit()
        self.db.close()

    def test_login(self):
        """Test para verificar que el login funciona correctamente."""
        response = self.client.post(
            '/api/v1/auth/login',
            data=json.dumps(self.user_credentials),
            content_type='application/json'
        )

        data = json.loads(response.data)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['message'], 'Inicio de sesión exitoso')
        self.assertIn('user', data)
        self.assertEqual(data['user']['email'], self.user_credentials['email'])

        # Verificar que se han establecido las cookies
        self.assertIn('access_token', response.headers.getlist('Set-Cookie')[0])
        self.assertIn('refresh_token', response.headers.getlist('Set-Cookie')[1])

    def test_login_incorrect_password(self):
        """Test para verificar que el login falla con contraseña incorrecta."""
        bad_credentials = {
            "email": "test@example.com",
            "password": "WrongPassword"
        }

        response = self.client.post(
            '/api/v1/auth/login',
            data=json.dumps(bad_credentials),
            content_type='application/json'
        )

        data = json.loads(response.data)

        self.assertEqual(response.status_code, 401)
        self.assertIn('error', data)
        self.assertEqual(data['error'], 'Email o contraseña incorrectos')

    def test_login_user_not_found(self):
        """Test para verificar que el login falla con usuario no existente."""
        bad_credentials = {
            "email": "nonexistent@example.com",
            "password": "Password1!"
        }

        response = self.client.post(
            '/api/v1/auth/login',
            data=json.dumps(bad_credentials),
            content_type='application/json'
        )

        data = json.loads(response.data)

        self.assertEqual(response.status_code, 401)
        self.assertIn('error', data)
        self.assertEqual(data['error'], 'Email o contraseña incorrectos')

    def test_register(self):
        """Test para verificar que el registro funciona correctamente."""
        response = self.client.post(
            '/api/v1/auth/register',
            data=json.dumps(self.new_user_data),
            content_type='application/json'
        )

        data = json.loads(response.data)

        self.assertEqual(response.status_code, 201)
        self.assertEqual(data['message'], 'Usuario registrado exitosamente')
        self.assertIn('user', data)
        self.assertEqual(data['user']['email'], self.new_user_data['email'])

        # Verificar que se han establecido las cookies
        self.assertIn('access_token', response.headers.getlist('Set-Cookie')[0])
        self.assertIn('refresh_token', response.headers.getlist('Set-Cookie')[1])

        # Verificar que el usuario se ha creado en la base de datos
        user = self.db.query(User).filter(User.email == self.new_user_data['email']).first()
        self.assertIsNotNone(user)

    def test_register_existing_email(self):
        """Test para verificar que el registro falla con email existente."""
        # Usar el email del usuario de prueba que ya existe
        existing_user_data = {
            "email": "test@example.com",
            "password": "NewPass1!",
            "full_name": "Usuario Duplicado"
        }

        response = self.client.post(
            '/api/v1/auth/register',
            data=json.dumps(existing_user_data),
            content_type='application/json'
        )

        data = json.loads(response.data)

        self.assertEqual(response.status_code, 400)
        self.assertIn('error', data)
        self.assertEqual(data['error'], f"Ya existe un usuario con el email '{existing_user_data['email']}'")

    def test_logout(self):
        """Test para verificar que el logout funciona correctamente."""
        # Primero hacer login para obtener las cookies
        self.client.post(
            '/api/v1/auth/login',
            data=json.dumps(self.user_credentials),
            content_type='application/json'
        )

        # Luego hacer logout
        response = self.client.post('/api/v1/auth/logout')

        data = json.loads(response.data)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['message'], 'Sesión cerrada exitosamente')

        # Verificar que las cookies se han eliminado
        cookie_headers = response.headers.getlist('Set-Cookie')
        self.assertTrue(any('access_token=;' in header for header in cookie_headers))
        self.assertTrue(any('refresh_token=;' in header for header in cookie_headers))

    def test_get_user_profile(self):
        """Test para verificar que se puede obtener el perfil del usuario autenticado."""
        # Primero hacer login para obtener las cookies
        login_response = self.client.post(
            '/api/v1/auth/login',
            data=json.dumps(self.user_credentials),
            content_type='application/json'
        )

        # Extraer las cookies de la respuesta
        cookies = login_response.headers.getlist('Set-Cookie')

        # Hacer la solicitud para obtener el perfil con las cookies
        response = self.client.get(
            '/api/v1/auth/me',
            headers={
                'Cookie': '; '.join(cookies)
            }
        )

        data = json.loads(response.data)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['email'], self.user_credentials['email'])
        self.assertEqual(data['full_name'], 'Usuario de Prueba')
        self.assertEqual(data['role'], 'user')


if __name__ == '__main__':
    unittest.main()

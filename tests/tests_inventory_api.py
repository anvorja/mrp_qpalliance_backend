# tests/tests_inventory_api.py
"""
Tests unitarios para la API de Inventario (módulos de autenticación y productos)
"""
import unittest
import json
import os
from app.main import create_app
from app.db.base import Base, engine
from app.db.session import get_db
from app.auth.auth import get_password_hash
from app.models import User, Product, Category, Location, Supplier

class TestInventoryAPI(unittest.TestCase):
    """Clase para pruebas de API de inventario - Auth y Productos"""

    def setUp(self):
        """Configuración inicial para cada prueba"""
        # Crear aplicación de prueba con base de datos en memoria
        os.environ['DATABASE_URL'] = 'sqlite:///:memory:'
        os.environ['JWT_SECRET_KEY'] = 'test-secret-key'
        self.app = create_app()
        self.app.config['TESTING'] = True
        self.client = self.app.test_client()

        # Crear tablas en base de datos
        with self.app.app_context():
            Base.metadata.create_all(bind=engine)

            # Crear usuario de prueba
            self.create_test_user()

            # Crear datos iniciales para pruebas
            self.create_test_data()

        # Realizar inicio de sesión para obtener cookies de autenticación
        login_response = self.client.post(
            '/api/v1/auth/login',
            json={
                'email': 'test@example.com',
                'password': 'TestPass123'
            }
        )
        self.access_cookie = login_response.headers.getlist('Set-Cookie')[0]
        self.refresh_cookie = login_response.headers.getlist('Set-Cookie')[1]

    def create_test_user(self):
        """Crea un usuario de prueba en la base de datos"""
        db = next(get_db())
        hashed_password = get_password_hash('TestPass123')
        user = User(
            email='test@example.com',
            full_name='Test User',
            password=hashed_password,
            role='admin'
        )
        db.add(user)
        db.commit()

    def create_test_data(self):
        """Crea datos iniciales para pruebas"""
        db = next(get_db())

        # Crear categorías (necesarias para productos)
        category1 = Category(name='Test Category 1')
        category2 = Category(name='Test Category 2')
        db.add_all([category1, category2])
        db.commit()

        # Crear ubicaciones (necesarias para productos)
        location1 = Location(name='Test Location 1')
        location2 = Location(name='Test Location 2')
        db.add_all([location1, location2])
        db.commit()

        # Crear proveedores (necesarios para productos)
        supplier1 = Supplier(
            name='Test Supplier 1',
            contact='Contact 1',
            email='supplier1@example.com',
            phone='123-456-7890'
        )
        supplier2 = Supplier(
            name='Test Supplier 2',
            contact='Contact 2',
            email='supplier2@example.com',
            phone='987-654-3210'
        )
        db.add_all([supplier1, supplier2])
        db.commit()

        # Crear productos
        product1 = Product(
            name='Test Product 1',
            code='TP001',
            current_stock=15,
            min_stock=5,
            description='Test product description 1',
            price=100.50,
            category=category1,
            location=location1,
            supplier=supplier1,
            qc_status='approved'
        )
        product2 = Product(
            name='Test Product 2',
            code='TP002',
            current_stock=2,
            min_stock=10,
            description='Test product description 2',
            price=200.75,
            category=category2,
            location=location2,
            supplier=supplier2,
            qc_status='pending'
        )
        db.add_all([product1, product2])
        db.commit()

    def tearDown(self):
        """Limpieza después de cada prueba"""
        with self.app.app_context():
            Base.metadata.drop_all(bind=engine)

    # Tests para verificación de estado
    def test_health_check(self):
        """Prueba el endpoint de verificación de estado"""
        response = self.client.get('/api/v1/health')
        data = json.loads(response.data)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['status'], 'ok')
        self.assertIn('version', data)

    #=========================================================
    # TESTS DE AUTENTICACIÓN
    #=========================================================

    def test_login_success(self):
        """Prueba inicio de sesión exitoso"""
        response = self.client.post(
            '/api/v1/auth/login',
            json={
                'email': 'test@example.com',
                'password': 'TestPass123'
            }
        )
        data = json.loads(response.data)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['message'], 'Inicio de sesión exitoso')
        self.assertIn('user', data)
        self.assertEqual(data['user']['email'], 'test@example.com')
        self.assertIn('access_token', response.headers.getlist('Set-Cookie')[0])
        self.assertIn('refresh_token', response.headers.getlist('Set-Cookie')[1])

    def test_login_invalid_credentials(self):
        """Prueba inicio de sesión con credenciales inválidas"""
        response = self.client.post(
            '/api/v1/auth/login',
            json={
                'email': 'test@example.com',
                'password': 'WrongPassword'
            }
        )
        data = json.loads(response.data)

        self.assertEqual(response.status_code, 401)
        self.assertIn('error', data)

    def test_register_user(self):
        """Prueba registrar un nuevo usuario"""
        response = self.client.post(
            '/api/v1/auth/register',
            json={
                'email': 'newuser@example.com',
                'password': 'NewUserPass123',
                'full_name': 'New Test User',
                'role': 'user'
            }
        )
        data = json.loads(response.data)

        self.assertEqual(response.status_code, 201)
        self.assertEqual(data['message'], 'Usuario registrado exitosamente')
        self.assertIn('user', data)
        self.assertEqual(data['user']['email'], 'newuser@example.com')
        self.assertEqual(data['user']['full_name'], 'New Test User')

        # Verificar que podemos iniciar sesión con el nuevo usuario
        login_response = self.client.post(
            '/api/v1/auth/login',
            json={
                'email': 'newuser@example.com',
                'password': 'NewUserPass123'
            }
        )
        self.assertEqual(login_response.status_code, 200)

    def test_register_existing_email(self):
        """Prueba registrar un usuario con email ya existente"""
        response = self.client.post(
            '/api/v1/auth/register',
            json={
                'email': 'test@example.com',  # Email ya usado
                'password': 'AnotherPass123',
                'full_name': 'Duplicate Email User',
                'role': 'user'
            }
        )
        data = json.loads(response.data)

        self.assertEqual(response.status_code, 400)
        self.assertIn('error', data)
        self.assertIn('Ya existe un usuario', data['error'])

    def test_logout(self):
        """Prueba cierre de sesión"""
        response = self.client.post(
            '/api/v1/auth/logout',
            headers={'Cookie': self.access_cookie}
        )
        data = json.loads(response.data)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['message'], 'Sesión cerrada exitosamente')

        # Verificar que las cookies sean eliminadas
        self.assertIn('access_token=;', response.headers.getlist('Set-Cookie')[0])
        self.assertIn('refresh_token=;', response.headers.getlist('Set-Cookie')[1])

    def test_get_user_profile(self):
        """Prueba obtener perfil de usuario autenticado"""
        response = self.client.get(
            '/api/v1/auth/me',
            headers={'Cookie': self.access_cookie}
        )
        data = json.loads(response.data)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['email'], 'test@example.com')
        self.assertEqual(data['full_name'], 'Test User')
        self.assertEqual(data['role'], 'admin')

    def test_refresh_token(self):
        """Prueba refrescar el token de acceso"""
        response = self.client.post(
            '/api/v1/auth/refresh',
            headers={'Cookie': self.refresh_cookie}
        )

        self.assertEqual(response.status_code, 200)
        # Verificar que se generó un nuevo token de acceso
        self.assertIn('access_token', response.headers.getlist('Set-Cookie')[0])

    # def test_access_protected_endpoint_without_auth(self):
    #     """Prueba acceder a un endpoint protegido sin autenticación"""
    #     response = self.client.post(
    #         '/api/v1/products',
    #         json={
    #             'name': 'Unauthorized Product',
    #             'code': 'UNAUTH001',
    #             'current_stock': 10,
    #             'min_stock': 5
    #         }
    #     )
    #
    #     self.assertEqual(response.status_code, 401)

    #=========================================================
    # TESTS DE PRODUCTOS
    #=========================================================

    def test_get_products(self):
        """Prueba obtener lista de productos"""
        response = self.client.get('/api/v1/products')
        data = json.loads(response.data)

        self.assertEqual(response.status_code, 200)
        self.assertIn('items', data)
        self.assertIn('total', data)
        self.assertEqual(data['total'], 2)
        self.assertEqual(len(data['items']), 2)

    def test_get_product_by_id(self):
        """Prueba obtener un producto específico por ID"""
        # Primero, obtener todos los productos para conseguir un ID
        response = self.client.get('/api/v1/products')
        data = json.loads(response.data)
        product_id = data['items'][0]['id']

        # Luego, obtener ese producto específico
        response = self.client.get(f'/api/v1/products/{product_id}')
        data = json.loads(response.data)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['id'], product_id)
        self.assertIn('name', data)
        self.assertIn('code', data)
        self.assertIn('current_stock', data)

    def test_get_nonexistent_product(self):
        """Prueba obtener un producto que no existe"""
        response = self.client.get('/api/v1/products/999')
        data = json.loads(response.data)

        self.assertEqual(response.status_code, 404)
        self.assertIn('error', data)

    def test_create_product(self):
        """Prueba crear un nuevo producto"""
        response = self.client.post(
            '/api/v1/products',
            headers={'Cookie': self.access_cookie},
            json={
                'name': 'New Test Product',
                'code': 'NTP001',
                'current_stock': 25,
                'min_stock': 10,
                'description': 'New test product description',
                'price': 150.25,
                'category_id': 1,
                'location_id': 1,
                'supplier_id': 1,
                'qc_status': 'approved'
            }
        )
        data = json.loads(response.data)

        self.assertEqual(response.status_code, 201)
        self.assertEqual(data['name'], 'New Test Product')
        self.assertEqual(data['code'], 'NTP001')
        self.assertEqual(data['current_stock'], 25)

        # Verificar que el producto fue creado en la base de datos
        db_response = self.client.get('/api/v1/products')
        db_data = json.loads(db_response.data)
        self.assertEqual(db_data['total'], 3)

    def test_create_product_duplicate_code(self):
        """Prueba crear un producto con código duplicado"""
        response = self.client.post(
            '/api/v1/products',
            headers={'Cookie': self.access_cookie},
            json={
                'name': 'Duplicate Code Product',
                'code': 'TP001',  # Código ya existente
                'current_stock': 20,
                'min_stock': 5
            }
        )
        data = json.loads(response.data)

        self.assertEqual(response.status_code, 400)
        self.assertIn('error', data)
        self.assertIn('Ya existe un producto', data['error'])

    def test_update_product(self):
        """Prueba actualizar un producto existente"""
        # Obtener un producto existente
        response = self.client.get('/api/v1/products')
        data = json.loads(response.data)
        product_id = data['items'][0]['id']

        # Actualizar el producto
        update_response = self.client.put(
            f'/api/v1/products/{product_id}',
            headers={'Cookie': self.access_cookie},
            json={
                'name': 'Updated Product Name',
                'current_stock': 30,
                'min_stock': 15,
                'price': 125.75
            }
        )
        update_data = json.loads(update_response.data)

        self.assertEqual(update_response.status_code, 200)
        self.assertEqual(update_data['name'], 'Updated Product Name')
        self.assertEqual(update_data['current_stock'], 30)
        self.assertEqual(update_data['min_stock'], 15)
        self.assertEqual(update_data['price'], 125.75)

    def test_partial_update_product(self):
        """Prueba actualizar parcialmente un producto (PATCH)"""
        # Obtener un producto existente
        response = self.client.get('/api/v1/products')
        data = json.loads(response.data)
        product_id = data['items'][0]['id']
        original_name = data['items'][0]['name']

        # Actualizar solo el stock del producto
        patch_response = self.client.patch(
            f'/api/v1/products/{product_id}',
            headers={'Cookie': self.access_cookie},
            json={
                'current_stock': 40
            }
        )
        patch_data = json.loads(patch_response.data)

        self.assertEqual(patch_response.status_code, 200)
        self.assertEqual(patch_data['name'], original_name)  # Nombre no cambia
        self.assertEqual(patch_data['current_stock'], 40)    # Stock sí cambia

    def test_delete_product(self):
        """Prueba eliminar un producto"""
        # Obtener un producto existente
        response = self.client.get('/api/v1/products')
        data = json.loads(response.data)
        initial_count = data['total']
        product_id = data['items'][0]['id']

        # Eliminar el producto
        delete_response = self.client.delete(
            f'/api/v1/products/{product_id}',
            headers={'Cookie': self.access_cookie}
        )

        self.assertEqual(delete_response.status_code, 200)

        # Verificar que el producto fue eliminado
        verify_response = self.client.get('/api/v1/products')
        verify_data = json.loads(verify_response.data)
        self.assertEqual(verify_data['total'], initial_count - 1)

    def test_get_products_with_filters(self):
        """Prueba obtener productos con diferentes filtros"""
        # Filtrar por categoría
        cat_response = self.client.get('/api/v1/products?category=1')
        cat_data = json.loads(cat_response.data)

        self.assertEqual(cat_response.status_code, 200)
        self.assertEqual(cat_data['total'], 1)
        self.assertEqual(cat_data['items'][0]['category_id'], 1)

        # Filtrar por búsqueda de texto
        search_response = self.client.get('/api/v1/products?search=Product 1')
        search_data = json.loads(search_response.data)

        self.assertEqual(search_response.status_code, 200)
        self.assertEqual(search_data['total'], 1)
        self.assertIn('Product 1', search_data['items'][0]['name'])

        # Filtrar por estado de stock
        stock_response = self.client.get('/api/v1/products?stock_status=low')
        stock_data = json.loads(stock_response.data)

        self.assertEqual(stock_response.status_code, 200)
        # Un producto tiene stock 2 y mínimo 10, así que debería estar en "low"
        self.assertGreater(stock_data['total'], 0)

    def test_get_stock_alerts(self):
        """Prueba obtener productos con alerta de stock bajo"""
        response = self.client.get('/api/v1/products/alerts')
        data = json.loads(response.data)

        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(data, list)
        # Producto 2 tiene stock 2, mínimo 10, así que debería aparecer en alertas
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]['code'], 'TP002')
        self.assertTrue(data[0]['current_stock'] < data[0]['min_stock'])

if __name__ == '__main__':
    unittest.main()
# app/utils/swagger.py
from flask import jsonify
from flask_swagger_ui import get_swaggerui_blueprint

# Ruta donde estará disponible la documentación Swagger
SWAGGER_URL = '/api/docs'
# Ruta donde estará el archivo JSON con la especificación
API_URL = '/api/spec'


def create_swagger_spec():
    """
    Crea la especificación OpenAPI/Swagger para la API.
    """
    swagger_spec = {
        "openapi": "3.0.0",
        "info": {
            "title": "Inventory Management API",
            "description": "API para la gestión de inventario de productos industriales",
            "version": "1.0.0",
            "contact": {
                "email": "contact@example.com"
            },
        },
        "servers": [
            {
                "url": "/api/v1",
                "description": "API v1"
            }
        ],
        "tags": [
            {
                "name": "products",
                "description": "Operaciones con productos"
            },
            {
                "name": "categories",
                "description": "Operaciones con categorías de productos"
            },
            {
                "name": "locations",
                "description": "Operaciones con ubicaciones de almacenamiento"
            },
            {
                "name": "suppliers",
                "description": "Operaciones con proveedores"
            },
            {
                "name": "movements",
                "description": "Operaciones con movimientos de inventario"
            },
            {
                "name": "auth",
                "description": "Operaciones de autenticación y gestión de usuarios"
            },
            {
                "name": "health",
                "description": "Verificación del estado de la API"
            }
        ],
        "paths": {
            "/health": {
                "get": {
                    "tags": ["health"],
                    "summary": "Verificar estado de la API",
                    "description": "Retorna el estado actual de la API",
                    "responses": {
                        "200": {
                            "description": "API funcionando correctamente",
                            "content": {
                                "application/json": {
                                    "schema": {
                                        "type": "object",
                                        "properties": {
                                            "status": {
                                                "type": "string",
                                                "example": "ok"
                                            },
                                            "version": {
                                                "type": "string",
                                                "example": "1.0.0"
                                            }
                                        }
                                    }
                                }
                            }
                        }
                    }
                }
            },

            "/auth/register": {
                "post": {
                    "tags": ["auth"],
                    "summary": "Registrar un nuevo usuario",
                    "description": "Crea una nueva cuenta de usuario en el sistema",
                    "requestBody": {
                        "required": True,
                        "content": {
                            "application/json": {
                                "schema": {
                                    "$ref": "#/components/schemas/UserRegister"
                                }
                            }
                        }
                    },
                    "responses": {
                        "201": {
                            "description": "Usuario registrado exitosamente",
                            "content": {
                                "application/json": {
                                    "schema": {
                                        "$ref": "#/components/schemas/UserResponse"
                                    }
                                }
                            }
                        },
                        "400": {
                            "description": "Datos inválidos o usuario ya existente"
                        },
                        "500": {
                            "description": "Error interno del servidor"
                        }
                    }
                }
            },

            "/auth/login": {
                "post": {
                    "tags": ["auth"],
                    "summary": "Iniciar sesión",
                    "description": "Autentica un usuario y devuelve tokens de acceso y refresco",
                    "requestBody": {
                        "required": True,
                        "content": {
                            "application/json": {
                                "schema": {
                                    "$ref": "#/components/schemas/UserLogin"
                                }
                            }
                        }
                    },
                    "responses": {
                        "200": {
                            "description": "Inicio de sesión exitoso",
                            "content": {
                                "application/json": {
                                    "schema": {
                                        "$ref": "#/components/schemas/UserResponse"
                                    }
                                }
                            }
                        },
                        "401": {
                            "description": "Credenciales inválidas o usuario inactivo"
                        },
                        "500": {
                            "description": "Error interno del servidor"
                        }
                    }
                }
            },
            "/auth/refresh": {
                "post": {
                    "tags": ["auth"],
                    "summary": "Refrescar token",
                    "description": "Refresca el token de acceso usando el token de refresco",
                    "responses": {
                        "200": {
                            "description": "Token refrescado exitosamente",
                            "content": {
                                "application/json": {
                                    "schema": {
                                        "type": "object",
                                        "properties": {
                                            "message": {
                                                "type": "string",
                                                "example": "Token refrescado exitosamente"
                                            }
                                        }
                                    }
                                }
                            }
                        },
                        "401": {
                            "description": "Token de refresco inválido o expirado"
                        },
                        "500": {
                            "description": "Error interno del servidor"
                        }
                    }
                }
            },

            "/auth/logout": {
                "post": {
                    "tags": ["auth"],
                    "summary": "Cerrar sesión",
                    "description": "Cierra la sesión del usuario eliminando las cookies",
                    "responses": {
                        "200": {
                            "description": "Sesión cerrada exitosamente",
                            "content": {
                                "application/json": {
                                    "schema": {
                                        "type": "object",
                                        "properties": {
                                            "message": {
                                                "type": "string",
                                                "example": "Sesión cerrada exitosamente"
                                            }
                                        }
                                    }
                                }
                            }
                        }
                    }
                }
            },

            "/auth/me": {
                "get": {
                    "tags": ["auth"],
                    "summary": "Perfil de usuario",
                    "description": "Obtiene el perfil del usuario autenticado",
                    "security": [
                        {
                            "bearerAuth": []
                        }
                    ],
                    "responses": {
                        "200": {
                            "description": "Perfil del usuario",
                            "content": {
                                "application/json": {
                                    "schema": {
                                        "$ref": "#/components/schemas/UserProfile"
                                    }
                                }
                            }
                        },
                        "401": {
                            "description": "No autenticado"
                        },
                        "500": {
                            "description": "Error interno del servidor"
                        }
                    }
                }
            },
            "/products": {
                "get": {
                    "tags": ["products"],
                    "summary": "Obtiene lista de productos",
                    "description": "Retorna una lista paginada de productos",
                    "parameters": [
                        {
                            "name": "skip",
                            "in": "query",
                            "schema": {
                                "type": "integer",
                                "default": 0
                            },
                            "description": "Número de registros a omitir"
                        },
                        {
                            "name": "limit",
                            "in": "query",
                            "schema": {
                                "type": "integer",
                                "default": 100
                            },
                            "description": "Número máximo de registros a retornar"
                        },
                        {
                            "name": "category",
                            "in": "query",
                            "schema": {
                                "type": "string"
                            },
                            "description": "Filtrar por ID de categoría o 'all'"
                        },
                        {
                            "name": "location",
                            "in": "query",
                            "schema": {
                                "type": "string"
                            },
                            "description": "Filtrar por ID de ubicación o 'all'"
                        },
                        {
                            "name": "supplier",
                            "in": "query",
                            "schema": {
                                "type": "string"
                            },
                            "description": "Filtrar por ID de proveedor o 'all'"
                        },
                        {
                            "name": "search",
                            "in": "query",
                            "schema": {
                                "type": "string"
                            },
                            "description": "Buscar por nombre o código"
                        },
                        {
                            "name": "stock_status",
                            "in": "query",
                            "schema": {
                                "type": "string",
                                "enum": ["low", "ok"]
                            },
                            "description": "Filtrar por estado de stock: 'low' (bajo mínimo) o 'ok'"
                        }
                    ],
                    "responses": {
                        "200": {
                            "description": "Operación exitosa",
                            "content": {
                                "application/json": {
                                    "schema": {
                                        "type": "object",
                                        "properties": {
                                            "items": {
                                                "type": "array",
                                                "items": {
                                                    "$ref": "#/components/schemas/ProductResponse"
                                                }
                                            },
                                            "total": {
                                                "type": "integer"
                                            },
                                            "page": {
                                                "type": "integer"
                                            },
                                            "pages": {
                                                "type": "integer"
                                            },
                                            "limit": {
                                                "type": "integer"
                                            }
                                        }
                                    }
                                }
                            }
                        },
                        "400": {
                            "description": "Parámetros de consulta inválidos"
                        },
                        "500": {
                            "description": "Error interno del servidor"
                        }
                    }
                },
                "post": {
                    "tags": ["products"],
                    "summary": "Crea un nuevo producto",
                    "description": "Crea un nuevo producto en el inventario",
                    "security": [
                        {
                            "bearerAuth": []
                        }
                    ],
                    "requestBody": {
                        "required": True,
                        "content": {
                            "application/json": {
                                "schema": {
                                    "$ref": "#/components/schemas/ProductCreate"
                                }
                            }
                        }
                    },
                    "responses": {
                        "201": {
                            "description": "Producto creado exitosamente",
                            "content": {
                                "application/json": {
                                    "schema": {
                                        "$ref": "#/components/schemas/ProductResponse"
                                    }
                                }
                            }
                        },
                        "400": {
                            "description": "Datos inválidos"
                        },
                        "401": {
                            "description": "No autenticado"
                        },
                        "500": {
                            "description": "Error interno del servidor"
                        }
                    }
                }
            },
            "/categories": {
                "get": {
                    "tags": ["categories"],
                    "summary": "Obtiene todas las categorías",
                    "description": "Retorna la lista de todas las categorías",
                    "responses": {
                        "200": {
                            "description": "Operación exitosa",
                            "content": {
                                "application/json": {
                                    "schema": {
                                        "type": "array",
                                        "items": {
                                            "$ref": "#/components/schemas/CategoryResponse"
                                        }
                                    }
                                }
                            }
                        },
                        "500": {
                            "description": "Error interno del servidor"
                        }
                    }
                },
                "post": {
                    "tags": ["categories"],
                    "summary": "Crea una nueva categoría",
                    "description": "Crea una nueva categoría de productos",
                    "security": [
                        {
                            "bearerAuth": []
                        }
                    ],
                    "requestBody": {
                        "required": True,
                        "content": {
                            "application/json": {
                                "schema": {
                                    "$ref": "#/components/schemas/CategoryCreate"
                                }
                            }
                        }
                    },
                    "responses": {
                        "201": {
                            "description": "Categoría creada exitosamente",
                            "content": {
                                "application/json": {
                                    "schema": {
                                        "$ref": "#/components/schemas/CategoryResponse"
                                    }
                                }
                            }
                        },
                        "400": {
                            "description": "Datos inválidos o categoría ya existente"
                        },
                        "401": {
                            "description": "No autenticado"
                        },
                        "500": {
                            "description": "Error interno del servidor"
                        }
                    }
                }
            },
            "/locations": {
                "get": {
                    "tags": ["locations"],
                    "summary": "Obtiene todas las ubicaciones",
                    "description": "Retorna la lista de todas las ubicaciones",
                    "responses": {
                        "200": {
                            "description": "Operación exitosa",
                            "content": {
                                "application/json": {
                                    "schema": {
                                        "type": "array",
                                        "items": {
                                            "$ref": "#/components/schemas/LocationResponse"
                                        }
                                    }
                                }
                            }
                        },
                        "500": {
                            "description": "Error interno del servidor"
                        }
                    }
                },
                "post": {
                    "tags": ["locations"],
                    "summary": "Crea una nueva ubicación",
                    "description": "Crea una nueva ubicación de almacenamiento",
                    "security": [
                        {
                            "bearerAuth": []
                        }
                    ],
                    "requestBody": {
                        "required": True,
                        "content": {
                            "application/json": {
                                "schema": {
                                    "$ref": "#/components/schemas/LocationCreate"
                                }
                            }
                        }
                    },
                    "responses": {
                        "201": {
                            "description": "Ubicación creada exitosamente",
                            "content": {
                                "application/json": {
                                    "schema": {
                                        "$ref": "#/components/schemas/LocationResponse"
                                    }
                                }
                            }
                        },
                        "400": {
                            "description": "Datos inválidos o ubicación ya existente"
                        },
                        "401": {
                            "description": "No autenticado"
                        },
                        "500": {
                            "description": "Error interno del servidor"
                        }
                    }
                }
            },
            "/suppliers": {
                "get": {
                    "tags": ["suppliers"],
                    "summary": "Obtiene todos los proveedores",
                    "description": "Retorna la lista de todos los proveedores",
                    "responses": {
                        "200": {
                            "description": "Operación exitosa",
                            "content": {
                                "application/json": {
                                    "schema": {
                                        "type": "array",
                                        "items": {
                                            "$ref": "#/components/schemas/SupplierResponse"
                                        }
                                    }
                                }
                            }
                        },
                        "500": {
                            "description": "Error interno del servidor"
                        }
                    }
                },
                "post": {
                    "tags": ["suppliers"],
                    "summary": "Crea un nuevo proveedor",
                    "description": "Crea un nuevo proveedor",
                    "security": [
                        {
                            "bearerAuth": []
                        }
                    ],
                    "requestBody": {
                        "required": True,
                        "content": {
                            "application/json": {
                                "schema": {
                                    "$ref": "#/components/schemas/SupplierCreate"
                                }
                            }
                        }
                    },
                    "responses": {
                        "201": {
                            "description": "Proveedor creado exitosamente",
                            "content": {
                                "application/json": {
                                    "schema": {
                                        "$ref": "#/components/schemas/SupplierResponse"
                                    }
                                }
                            }
                        },
                        "400": {
                            "description": "Datos inválidos o proveedor ya existente"
                        },
                        "401": {
                            "description": "No autenticado"
                        },
                        "500": {
                            "description": "Error interno del servidor"
                        }
                    }
                }
            },
            "/movements": {
                "get": {
                    "tags": ["movements"],
                    "summary": "Obtiene lista de movimientos",
                    "description": "Retorna una lista paginada de movimientos de inventario",
                    "parameters": [
                        {
                            "name": "skip",
                            "in": "query",
                            "schema": {
                                "type": "integer",
                                "default": 0
                            },
                            "description": "Número de registros a omitir"
                        },
                        {
                            "name": "limit",
                            "in": "query",
                            "schema": {
                                "type": "integer",
                                "default": 100
                            },
                            "description": "Número máximo de registros a retornar"
                        },
                        {
                            "name": "type",
                            "in": "query",
                            "schema": {
                                "type": "string",
                                "enum": ["in", "out", "adjustment", "all"]
                            },
                            "description": "Filtrar por tipo de movimiento"
                        }
                    ],
                    "responses": {
                        "200": {
                            "description": "Operación exitosa",
                            "content": {
                                "application/json": {
                                    "schema": {
                                        "type": "array",
                                        "items": {
                                            "$ref": "#/components/schemas/MovementResponse"
                                        }
                                    }
                                }
                            }
                        },
                        "400": {
                            "description": "Parámetros de consulta inválidos"
                        },
                        "500": {
                            "description": "Error interno del servidor"
                        }
                    }
                },
                "post": {
                    "tags": ["movements"],
                    "summary": "Crea un nuevo movimiento",
                    "description": "Crea un nuevo movimiento de inventario y actualiza el stock del producto",
                    "security": [
                        {
                            "bearerAuth": []
                        }
                    ],
                    "requestBody": {
                        "required": True,
                        "content": {
                            "application/json": {
                                "schema": {
                                    "$ref": "#/components/schemas/MovementCreate"
                                }
                            }
                        }
                    },
                    "responses": {
                        "201": {
                            "description": "Movimiento creado exitosamente",
                            "content": {
                                "application/json": {
                                    "schema": {
                                        "$ref": "#/components/schemas/MovementResponse"
                                    }
                                }
                            }
                        },
                        "400": {
                            "description": "Datos inválidos o stock insuficiente"
                        },
                        "401": {
                            "description": "No autenticado"
                        },
                        "500": {
                            "description": "Error interno del servidor"
                        }
                    }
                }
            },
            "/movements/product/{product_id}": {
                "get": {
                    "tags": ["movements"],
                    "summary": "Obtiene movimientos de un producto",
                    "description": "Retorna los movimientos de un producto específico",
                    "parameters": [
                        {
                            "name": "product_id",
                            "in": "path",
                            "required": True,
                            "schema": {
                                "type": "integer"
                            },
                            "description": "ID del producto"
                        },
                        {
                            "name": "skip",
                            "in": "query",
                            "schema": {
                                "type": "integer",
                                "default": 0
                            },
                            "description": "Número de registros a omitir"
                        },
                        {
                            "name": "limit",
                            "in": "query",
                            "schema": {
                                "type": "integer",
                                "default": 100
                            },
                            "description": "Número máximo de registros a retornar"
                        }
                    ],
                    "responses": {
                        "200": {
                            "description": "Operación exitosa",
                            "content": {
                                "application/json": {
                                    "schema": {
                                        "type": "array",
                                        "items": {
                                            "$ref": "#/components/schemas/MovementResponse"
                                        }
                                    }
                                }
                            }
                        },
                        "400": {
                            "description": "Parámetros de consulta inválidos"
                        },
                        "500": {
                            "description": "Error interno del servidor"
                        }
                    }
                }
            },
            "/products/{product_id}": {
                "get": {
                    "tags": ["products"],
                    "summary": "Obtiene un producto por su ID",
                    "description": "Retorna un producto específico basado en su ID",
                    "parameters": [
                        {
                            "name": "product_id",
                            "in": "path",
                            "required": True,
                            "schema": {
                                "type": "integer"
                            },
                            "description": "ID del producto"
                        }
                    ],
                    "responses": {
                        "200": {
                            "description": "Operación exitosa",
                            "content": {
                                "application/json": {
                                    "schema": {
                                        "$ref": "#/components/schemas/ProductResponse"
                                    }
                                }
                            }
                        },
                        "404": {
                            "description": "Producto no encontrado"
                        },
                        "500": {
                            "description": "Error interno del servidor"
                        }
                    }
                },
                "put": {
                    "tags": ["products"],
                    "summary": "Actualiza un producto",
                    "description": "Actualiza un producto existente por su ID (actualización completa)",
                    "security": [
                        {
                            "bearerAuth": []
                        }
                    ],
                    "parameters": [
                        {
                            "name": "product_id",
                            "in": "path",
                            "required": True,
                            "schema": {
                                "type": "integer"
                            },
                            "description": "ID del producto a actualizar"
                        }
                    ],
                    "requestBody": {
                        "required": True,
                        "content": {
                            "application/json": {
                                "schema": {
                                    "$ref": "#/components/schemas/ProductUpdate"
                                }
                            }
                        }
                    },
                    "responses": {
                        "200": {
                            "description": "Producto actualizado exitosamente",
                            "content": {
                                "application/json": {
                                    "schema": {
                                        "$ref": "#/components/schemas/ProductResponse"
                                    }
                                }
                            }
                        },
                        "400": {
                            "description": "Datos inválidos"
                        },
                        "401": {
                            "description": "No autenticado"
                        },
                        "404": {
                            "description": "Producto no encontrado"
                        },
                        "500": {
                            "description": "Error interno del servidor"
                        }
                    }
                },
                "patch": {
                    "tags": ["products"],
                    "summary": "Actualiza parcialmente un producto",
                    "description": "Actualiza parcialmente un producto existente por su ID (solo los campos que se envían)",
                    "security": [
                        {
                            "bearerAuth": []
                        }
                    ],
                    "parameters": [
                        {
                            "name": "product_id",
                            "in": "path",
                            "required": True,
                            "schema": {
                                "type": "integer"
                            },
                            "description": "ID del producto a actualizar parcialmente"
                        }
                    ],
                    "requestBody": {
                        "required": True,
                        "content": {
                            "application/json": {
                                "schema": {
                                    "$ref": "#/components/schemas/ProductUpdate"
                                }
                            }
                        }
                    },
                    "responses": {
                        "200": {
                            "description": "Producto actualizado parcialmente con éxito",
                            "content": {
                                "application/json": {
                                    "schema": {
                                        "$ref": "#/components/schemas/ProductResponse"
                                    }
                                }
                            }
                        },
                        "400": {
                            "description": "Datos inválidos"
                        },
                        "401": {
                            "description": "No autenticado"
                        },
                        "404": {
                            "description": "Producto no encontrado"
                        },
                        "500": {
                            "description": "Error interno del servidor"
                        }
                    }
                },
                "delete": {
                    "tags": ["products"],
                    "summary": "Elimina un producto",
                    "description": "Elimina un producto existente por su ID",
                    "security": [
                        {
                            "bearerAuth": []
                        }
                    ],
                    "parameters": [
                        {
                            "name": "product_id",
                            "in": "path",
                            "required": True,
                            "schema": {
                                "type": "integer"
                            },
                            "description": "ID del producto a eliminar"
                        }
                    ],
                    "responses": {
                        "200": {
                            "description": "Producto eliminado exitosamente",
                            "content": {
                                "application/json": {
                                    "schema": {
                                        "type": "object",
                                        "properties": {
                                            "message": {
                                                "type": "string",
                                                "example": "Producto eliminado correctamente"
                                            }
                                        }
                                    }
                                }
                            }
                        },
                        "401": {
                            "description": "No autenticado"
                        },
                        "404": {
                            "description": "Producto no encontrado"
                        },
                        "500": {
                            "description": "Error interno del servidor"
                        }
                    }
                }
            },
            "/products/alerts": {
                "get": {
                    "tags": ["products"],
                    "summary": "Obtiene productos con alerta de stock",
                    "description": "Retorna productos con stock por debajo del mínimo",
                    "responses": {
                        "200": {
                            "description": "Operación exitosa",
                            "content": {
                                "application/json": {
                                    "schema": {
                                        "type": "array",
                                        "items": {
                                            "$ref": "#/components/schemas/AlertProduct"
                                        }
                                    }
                                }
                            }
                        },
                        "500": {
                            "description": "Error interno del servidor"
                        }
                    }
                }
            }
        },
        "components": {
            "securitySchemes": {
                "bearerAuth": {
                    "type": "http",
                    "scheme": "bearer",
                    "bearerFormat": "JWT"
                }
            },
            "schemas": {
                "UserRegister": {
                    "type": "object",
                    "properties": {
                        "email": {
                            "type": "string",
                            "format": "email",
                            "description": "Correo electrónico del usuario (único)"
                        },
                        "full_name": {
                            "type": "string",
                            "description": "Nombre completo del usuario"
                        },
                        "password": {
                            "type": "string",
                            "format": "password",
                            "description": "Contraseña (mínimo 8 caracteres)"
                        },
                        "role": {
                            "type": "string",
                            "enum": ["admin", "user"],
                            "description": "Rol del usuario",
                            "default": "user"
                        }
                    },
                    "required": ["email", "full_name", "password"]
                },
                "UserLogin": {
                    "type": "object",
                    "properties": {
                        "email": {
                            "type": "string",
                            "format": "email",
                            "description": "Correo electrónico del usuario"
                        },
                        "password": {
                            "type": "string",
                            "format": "password",
                            "description": "Contraseña"
                        }
                    },
                    "required": ["email", "password"]
                },
                "UserResponse": {
                    "type": "object",
                    "properties": {
                        "message": {
                            "type": "string",
                            "example": "Usuario registrado exitosamente"
                        },
                        "user": {
                            "type": "object",
                            "properties": {
                                "id": {
                                    "type": "integer",
                                    "description": "ID único del usuario"
                                },
                                "email": {
                                    "type": "string",
                                    "format": "email",
                                    "description": "Correo electrónico del usuario"
                                },
                                "full_name": {
                                    "type": "string",
                                    "description": "Nombre completo del usuario"
                                },
                                "role": {
                                    "type": "string",
                                    "enum": ["admin", "user"],
                                    "description": "Rol del usuario"
                                }
                            }
                        }
                    }
                },
                "UserProfile": {
                    "type": "object",
                    "properties": {
                        "id": {
                            "type": "integer",
                            "description": "ID único del usuario"
                        },
                        "email": {
                            "type": "string",
                            "format": "email",
                            "description": "Correo electrónico del usuario"
                        },
                        "full_name": {
                            "type": "string",
                            "description": "Nombre completo del usuario"
                        },
                        "role": {
                            "type": "string",
                            "enum": ["admin", "user"],
                            "description": "Rol del usuario"
                        },
                        "last_login": {
                            "type": "string",
                            "format": "date-time",
                            "description": "Fecha y hora del último inicio de sesión",
                            "nullable": True
                        },
                        "created_at": {
                            "type": "string",
                            "format": "date-time",
                            "description": "Fecha y hora de creación",
                            "nullable": True
                        }
                    }
                },
                "ProductBase": {
                    "type": "object",
                    "properties": {
                        "name": {
                            "type": "string",
                            "description": "Nombre del producto",
                            "maxLength": 100
                        },
                        "code": {
                            "type": "string",
                            "description": "Código único del producto",
                            "maxLength": 50
                        },
                        "current_stock": {
                            "type": "number",
                            "format": "float",
                            "description": "Stock actual del producto",
                            "minimum": 0
                        },
                        "min_stock": {
                            "type": "number",
                            "format": "float",
                            "description": "Stock mínimo del producto",
                            "minimum": 0
                        },
                        "description": {
                            "type": "string",
                            "description": "Descripción detallada del producto",
                            "nullable": True
                        },
                        "price": {
                            "type": "number",
                            "format": "float",
                            "description": "Precio unitario del producto",
                            "minimum": 0,
                            "nullable": True
                        },
                        "qc_status": {
                            "type": "string",
                            "description": "Estado de control de calidad",
                            "enum": ["approved", "pending", "rejected"],
                            "nullable": True
                        },
                        "category_id": {
                            "type": "integer",
                            "description": "ID de la categoría",
                            "nullable": True
                        },
                        "location_id": {
                            "type": "integer",
                            "description": "ID de la ubicación",
                            "nullable": True
                        },
                        "supplier_id": {
                            "type": "integer",
                            "description": "ID del proveedor",
                            "nullable": True
                        }
                    },
                    "required": ["name", "code", "current_stock", "min_stock"]
                },
                "ProductCreate": {
                    "$ref": "#/components/schemas/ProductBase"
                },
                "ProductUpdate": {
                    "type": "object",
                    "properties": {
                        "name": {
                            "type": "string",
                            "description": "Nombre del producto",
                            "maxLength": 100,
                            "nullable": True
                        },
                        "current_stock": {
                            "type": "number",
                            "format": "float",
                            "description": "Stock actual del producto",
                            "minimum": 0,
                            "nullable": True
                        },
                        "min_stock": {
                            "type": "number",
                            "format": "float",
                            "description": "Stock mínimo del producto",
                            "minimum": 0,
                            "nullable": True
                        },
                        "description": {
                            "type": "string",
                            "description": "Descripción detallada del producto",
                            "nullable": True
                        },
                        "price": {
                            "type": "number",
                            "format": "float",
                            "description": "Precio unitario del producto",
                            "minimum": 0,
                            "nullable": True
                        },
                        "qc_status": {
                            "type": "string",
                            "description": "Estado de control de calidad",
                            "enum": ["approved", "pending", "rejected"],
                            "nullable": True
                        },
                        "category_id": {
                            "type": "integer",
                            "description": "ID de la categoría",
                            "nullable": True
                        },
                        "location_id": {
                            "type": "integer",
                            "description": "ID de la ubicación",
                            "nullable": True
                        },
                        "supplier_id": {
                            "type": "integer",
                            "description": "ID del proveedor",
                            "nullable": True
                        }
                    }
                },
                "ProductResponse": {
                    "allOf": [
                        {
                            "$ref": "#/components/schemas/ProductBase"
                        },
                        {
                            "type": "object",
                            "properties": {
                                "id": {
                                    "type": "integer",
                                    "description": "ID único del producto"
                                },
                                "created_at": {
                                    "type": "string",
                                    "format": "date-time",
                                    "description": "Fecha de creación"
                                },
                                "updated_at": {
                                    "type": "string",
                                    "format": "date-time",
                                    "description": "Fecha de última actualización",
                                    "nullable": True
                                },
                                "category": {
                                    "type": "string",
                                    "description": "Nombre de la categoría",
                                    "nullable": True
                                },
                                "location": {
                                    "type": "string",
                                    "description": "Nombre de la ubicación",
                                    "nullable": True
                                },
                                "supplier": {
                                    "type": "string",
                                    "description": "Nombre del proveedor",
                                    "nullable": True
                                }
                            }
                        }
                    ]
                },
                "CategoryCreate": {
                    "type": "object",
                    "properties": {
                        "name": {
                            "type": "string",
                            "description": "Nombre de la categoría",
                            "maxLength": 50
                        }
                    },
                    "required": ["name"]
                },
                "CategoryResponse": {
                    "type": "object",
                    "properties": {
                        "id": {
                            "type": "integer",
                            "description": "ID único de la categoría"
                        },
                        "name": {
                            "type": "string",
                            "description": "Nombre de la categoría"
                        }
                    }
                },
                "LocationCreate": {
                    "type": "object",
                    "properties": {
                        "name": {
                            "type": "string",
                            "description": "Nombre de la ubicación",
                            "maxLength": 50
                        }},
                    "required": ["name"]
                },
                "LocationResponse": {
                    "type": "object",
                    "properties": {
                        "id": {
                            "type": "integer",
                            "description": "ID único de la ubicación"
                        },
                        "name": {
                            "type": "string",
                            "description": "Nombre de la ubicación"
                        }
                    }
                },
                "SupplierCreate": {
                    "type": "object",
                    "properties": {
                        "name": {
                            "type": "string",
                            "description": "Nombre del proveedor",
                            "maxLength": 100
                        },
                        "contact": {
                            "type": "string",
                            "description": "Persona de contacto",
                            "maxLength": 100,
                            "nullable": True
                        },
                        "email": {
                            "type": "string",
                            "description": "Correo electrónico",
                            "maxLength": 100,
                            "nullable": True
                        },
                        "phone": {
                            "type": "string",
                            "description": "Teléfono de contacto",
                            "maxLength": 20,
                            "nullable": True
                        }
                    },
                    "required": ["name"]
                },
                "SupplierResponse": {
                    "type": "object",
                    "properties": {
                        "id": {
                            "type": "integer",
                            "description": "ID único del proveedor"
                        },
                        "name": {
                            "type": "string",
                            "description": "Nombre del proveedor"
                        },
                        "contact": {
                            "type": "string",
                            "description": "Persona de contacto",
                            "nullable": True
                        },
                        "email": {
                            "type": "string",
                            "description": "Correo electrónico",
                            "nullable": True
                        },
                        "phone": {
                            "type": "string",
                            "description": "Teléfono de contacto",
                            "nullable": True
                        }
                    }
                },
                "MovementCreate": {
                    "type": "object",
                    "properties": {
                        "type": {
                            "type": "string",
                            "description": "Tipo de movimiento",
                            "enum": ["in", "out", "adjustment"]
                        },
                        "quantity": {
                            "type": "number",
                            "format": "float",
                            "description": "Cantidad de producto movida",
                            "minimum": 0
                        },
                        "product_id": {
                            "type": "integer",
                            "description": "ID del producto asociado"
                        },
                        "reference": {
                            "type": "string",
                            "description": "Referencia del movimiento (orden, etc.)",
                            "maxLength": 50,
                            "nullable": True
                        },
                        "notes": {
                            "type": "string",
                            "description": "Notas adicionales",
                            "nullable": True
                        },
                        "user": {
                            "type": "string",
                            "description": "Usuario que realizó el movimiento",
                            "maxLength": 100,
                            "nullable": True
                        }
                    },
                    "required": ["type", "quantity", "product_id"]
                },
                "MovementResponse": {
                    "type": "object",
                    "properties": {
                        "id": {
                            "type": "integer",
                            "description": "ID único del movimiento"
                        },
                        "type": {
                            "type": "string",
                            "description": "Tipo de movimiento: in, out, adjustment"
                        },
                        "quantity": {
                            "type": "number",
                            "format": "float",
                            "description": "Cantidad de producto movida"
                        },
                        "resulting_stock": {
                            "type": "number",
                            "format": "float",
                            "description": "Stock resultante después del movimiento"
                        },
                        "reference": {
                            "type": "string",
                            "description": "Referencia del movimiento",
                            "nullable": True
                        },
                        "notes": {
                            "type": "string",
                            "description": "Notas adicionales",
                            "nullable": True
                        },
                        "user": {
                            "type": "string",
                            "description": "Usuario que realizó el movimiento",
                            "nullable": True
                        },
                        "created_at": {
                            "type": "string",
                            "format": "date-time",
                            "description": "Fecha de creación del movimiento"
                        },
                        "product_id": {
                            "type": "integer",
                            "description": "ID del producto asociado"
                        },
                        "product_name": {
                            "type": "string",
                            "description": "Nombre del producto",
                            "nullable": True
                        },
                        "product_code": {
                            "type": "string",
                            "description": "Código del producto",
                            "nullable": True
                        }
                    }
                },
                "AlertProduct": {
                    "type": "object",
                    "properties": {
                        "id": {
                            "type": "integer",
                            "description": "ID único del producto"
                        },
                        "name": {
                            "type": "string",
                            "description": "Nombre del producto"
                        },
                        "code": {
                            "type": "string",
                            "description": "Código del producto"
                        },
                        "current_stock": {
                            "type": "number",
                            "format": "float",
                            "description": "Stock actual del producto"
                        },
                        "min_stock": {
                            "type": "number",
                            "format": "float",
                            "description": "Stock mínimo del producto"
                        },
                        "difference": {
                            "type": "number",
                            "format": "float",
                            "description": "Diferencia entre stock mínimo y actual"
                        },
                        "category": {
                            "type": "string",
                            "description": "Nombre de la categoría",
                            "nullable": True
                        },
                        "location": {
                            "type": "string",
                            "description": "Nombre de la ubicación",
                            "nullable": True
                        },
                        "supplier": {
                            "type": "string",
                            "description": "Nombre del proveedor",
                            "nullable": True
                        },
                        "daysToStockOut": {
                            "type": "integer",
                            "description": "Días estimados para quedarse sin stock",
                            "nullable": True
                        },
                        "lead_time": {
                            "type": "integer",
                            "description": "Tiempo estimado de entrega del proveedor",
                            "nullable": True
                        }
                    }
                }
            }
        }
    }

    return swagger_spec


def setup_swagger(app):
    """
    Configura Swagger UI para la aplicación Flask.
    """

    # Endpoint para servir la especificación OpenAPI
    @app.route(API_URL)
    def get_spec():
        return jsonify(create_swagger_spec())

    # Crear y registrar el blueprint de Swagger UI
    swaggerui_blueprint = get_swaggerui_blueprint(
        SWAGGER_URL,
        API_URL,
        config={
            'app_name': "Inventory Management API"
        }
    )

    app.register_blueprint(swaggerui_blueprint, url_prefix=SWAGGER_URL)
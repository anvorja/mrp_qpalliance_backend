# app/db/seed-script.py
"""
Script para poblar la base de datos con datos iniciales de prueba.
"""

import os
import sys
from sqlalchemy.orm import Session
import datetime
from random import randint, choice

from app.models import Product, Movement, Supplier, Location, Category

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.db.base import engine, Base

# Datos de categorías
CATEGORIES = [
    "Motores",
    "Sensores",
    "Electrónica",
    "Hidráulica",
    "Transporte",
    "Mecánica",
    "Materiales",
    "Refrigeración",
    "Ferretería"
]

# Datos de ubicaciones
LOCATIONS = [
    "Almacén A",
    "Almacén B",
    "Almacén C",
    "Almacén D"
]

# Datos de proveedores
SUPPLIERS = [
    {"name": "TechSupplies Corp.", "contact": "Juan Pérez", "email": "contacto@techsupplies.com",
     "phone": "123-456-7890"},
    {"name": "ConveyorTech Inc.", "contact": "Ana García", "email": "ventas@conveyortech.com", "phone": "234-567-8901"},
    {"name": "OpticNet Solutions", "contact": "Miguel Rodríguez", "email": "info@opticnet.com",
     "phone": "345-678-9012"},
    {"name": "CoolTech Systems", "contact": "Laura Martínez", "email": "ventas@cooltech.com", "phone": "456-789-0123"},
]

# Lista de productos de ejemplo para insertar
SAMPLE_PRODUCTS = [
    {
        "name": "Motor eléctrico 2HP",
        "code": "P001",
        "current_stock": 15,
        "min_stock": 5,
        "description": "Motor eléctrico de 2HP para aplicaciones industriales",
        "price": 450.00,
        "category": "Motores",
        "location": "Almacén A",
        "supplier": "TechSupplies Corp.",
        "qc_status": "approved"
    },
    {
        "name": "Sensor de proximidad",
        "code": "P002",
        "current_stock": 32,
        "min_stock": 10,
        "description": "Sensor de proximidad infrarrojo",
        "price": 120.50,
        "category": "Sensores",
        "location": "Almacén B",
        "supplier": "OpticNet Solutions",
        "qc_status": "approved"
    },
    {
        "name": "Placa base industrial",
        "code": "P003",
        "current_stock": 8,
        "min_stock": 12,
        "description": "Placa base para equipos de control industrial",
        "price": 350.00,
        "category": "Electrónica",
        "location": "Almacén A",
        "supplier": "TechSupplies Corp.",
        "qc_status": "pending"
    },
    {
        "name": "Válvula hidráulica",
        "code": "P004",
        "current_stock": 25,
        "min_stock": 15,
        "description": "Válvula de control para sistemas hidráulicos",
        "price": 210.75,
        "category": "Hidráulica",
        "location": "Almacén C",
        "supplier": "CoolTech Systems",
        "qc_status": "approved"
    },
    {
        "name": "Cinta transportadora",
        "code": "P005",
        "current_stock": 4,
        "min_stock": 5,
        "description": "Cinta transportadora de 5 metros",
        "price": 1200.00,
        "category": "Transporte",
        "location": "Almacén D",
        "supplier": "ConveyorTech Inc.",
        "qc_status": "pending"
    },
    {
        "name": "Rodamiento industrial",
        "code": "P006",
        "current_stock": 120,
        "min_stock": 50,
        "description": "Rodamiento de alta resistencia",
        "price": 85.25,
        "category": "Mecánica",
        "location": "Almacén B",
        "supplier": "TechSupplies Corp.",
        "qc_status": "approved"
    },
    {
        "name": "Piezas de aluminio",
        "code": "P007",
        "current_stock": 200,
        "min_stock": 100,
        "description": "Piezas de aluminio para ensamblaje",
        "price": 32.50,
        "category": "Materiales",
        "location": "Almacén A",
        "supplier": "ConveyorTech Inc.",
        "qc_status": "approved"
    },
    {
        "name": "Cable de fibra óptica",
        "code": "P008",
        "current_stock": 18,
        "min_stock": 20,
        "description": "Cable de fibra óptica de alta velocidad",
        "price": 45.75,
        "category": "Electrónica",
        "location": "Almacén C",
        "supplier": "OpticNet Solutions",
        "qc_status": "approved"
    },
    {
        "name": "Tornillo hexagonal",
        "code": "P009",
        "current_stock": 500,
        "min_stock": 200,
        "description": "Tornillo hexagonal de acero inoxidable",
        "price": 0.75,
        "category": "Ferretería",
        "location": "Almacén D",
        "supplier": "TechSupplies Corp.",
        "qc_status": "approved"
    },
    {
        "name": "Sistema de refrigeración",
        "code": "P010",
        "current_stock": 7,
        "min_stock": 8,
        "description": "Sistema de refrigeración para equipos industriales",
        "price": 780.00,
        "category": "Refrigeración",
        "location": "Almacén B",
        "supplier": "CoolTech Systems",
        "qc_status": "pending"
    },
    {
        "name": "Batería industrial",
        "code": "P011",
        "current_stock": 12,
        "min_stock": 10,
        "description": "Batería de alta capacidad para equipos",
        "price": 320.00,
        "category": "Electrónica",
        "location": "Almacén A",
        "supplier": "TechSupplies Corp.",
        "qc_status": "approved"
    },
    {
        "name": "Panel solar",
        "code": "P012",
        "current_stock": 5,
        "min_stock": 3,
        "description": "Panel solar fotovoltaico de 250W",
        "price": 450.00,
        "category": "Electrónica",
        "location": "Almacén C",
        "supplier": "OpticNet Solutions",
        "qc_status": "approved"
    },
    {
        "name": "Tarjeta de control",
        "code": "P013",
        "current_stock": 15,
        "min_stock": 8,
        "description": "Tarjeta para control de procesos automáticos",
        "price": 180.00,
        "category": "Electrónica",
        "location": "Almacén B",
        "supplier": "TechSupplies Corp.",
        "qc_status": "pending"
    },
    {
        "name": "Aislante térmico",
        "code": "P014",
        "current_stock": 40,
        "min_stock": 20,
        "description": "Aislante térmico para tuberías",
        "price": 25.75,
        "category": "Materiales",
        "location": "Almacén A",
        "supplier": "CoolTech Systems",
        "qc_status": "approved"
    },
    {
        "name": "Compresor de aire",
        "code": "P015",
        "current_stock": 8,
        "min_stock": 5,
        "description": "Compresor industrial de aire",
        "price": 1200.00,
        "category": "Mecánica",
        "location": "Almacén D",
        "supplier": "ConveyorTech Inc.",
        "qc_status": "approved"
    }
]

# Usuarios de ejemplo para movimientos
USERS = [
    "María López",
    "Carlos Gómez",
    "Ana Martínez",
    "Pedro Sánchez"
]

# Referencias de ejemplo para movimientos
REFERENCES = [
    "OC-12345", "OP-78901", "INV-001", "OC-12346", "OP-78902",
    "OP-78903", "INV-002", "OC-12347", "OP-78904", "OC-12348"
]


def create_sample_data():
    """Crea datos de ejemplo en la base de datos."""
    # Crear una sesión
    with Session(engine) as session:
        # Verificar si ya existen datos
        existing_products = session.query(Product).count()
        if existing_products > 0:
            print(f"La base de datos ya tiene {existing_products} productos.")
            option = input("¿Desea borrar los datos existentes y crear nuevos? (s/n): ")
            if option.lower() != 's':
                print("Operación cancelada.")
                return

            # Borrar datos existentes
            session.query(Movement).delete()
            session.query(Product).delete()
            session.query(Category).delete()
            session.query(Location).delete()
            session.query(Supplier).delete()
            session.commit()
            print("Datos existentes eliminados.")

        # 1. Crear categorías
        category_objects = {}
        for category_name in CATEGORIES:
            category = Category(name=category_name)
            session.add(category)
            category_objects[category_name] = category
        session.commit()

        # 2. Crear ubicaciones
        location_objects = {}
        for location_name in LOCATIONS:
            location = Location(name=location_name)
            session.add(location)
            location_objects[location_name] = location
        session.commit()

        # 3. Crear proveedores
        supplier_objects = {}
        for supplier_data in SUPPLIERS:
            supplier = Supplier(**supplier_data)
            session.add(supplier)
            supplier_objects[supplier_data["name"]] = supplier
        session.commit()

        # 4. Crear productos
        product_objects = {}
        for product_data in SAMPLE_PRODUCTS:
            # Obtener objetos relacionados
            category = category_objects.get(product_data.pop("category"))
            location = location_objects.get(product_data.pop("location"))
            supplier = supplier_objects.get(product_data.pop("supplier"))

            # Crear producto
            product = Product(
                **product_data,
                category=category,
                location=location,
                supplier=supplier
            )
            session.add(product)
            product_objects[product.code] = product
        session.commit()

        # 5. Crear movimientos de inventario
        movement_types = ["in", "out", "adjustment"]
        for product in product_objects.values():
            # Crear entre 1 y 5 movimientos por producto
            num_movements = randint(1, 5)
            current_stock = 0

            for i in range(num_movements):
                movement_type = choice(movement_types)
                if movement_type == "in":
                    quantity = randint(5, 20)
                elif movement_type == "out":
                    quantity = -randint(1, 10)
                else:  # adjustment
                    quantity = choice([-3, -2, -1, 1, 2, 3])

                # Calcular stock resultante
                current_stock += quantity if movement_type != "out" else -quantity

                # Fecha aleatoria en los últimos 30 días
                random_days = randint(1, 30)
                movement_date = datetime.datetime.now() - datetime.timedelta(days=random_days)

                movement = Movement(
                    type=movement_type,
                    quantity=abs(quantity),
                    resulting_stock=max(0, current_stock),
                    product=product,
                    reference=choice(REFERENCES),
                    notes=f"Movimiento de {abs(quantity)} unidades de {product.name}",
                    user=choice(USERS),
                    created_at=movement_date
                )
                session.add(movement)

            # Actualizar el stock actual del producto para que coincida con el último movimiento
            product.current_stock = max(0, current_stock)
        session.commit()

        print(f"Se han creado {len(CATEGORIES)} categorías, {len(LOCATIONS)} ubicaciones, "
              f"{len(SUPPLIERS)} proveedores, {len(SAMPLE_PRODUCTS)} productos y movimientos de inventario.")

        # Mostrar algunos productos para verificar
        products = session.query(Product).limit(5).all()
        print("\nAlgunos productos creados:")
        for product in products:
            print(f"- {product.code}: {product.name} (Stock: {product.current_stock}/{product.min_stock})")

        # Mostrar productos con alerta
        alerts = session.query(Product).filter(Product.current_stock < Product.min_stock).all()
        print(f"\nProductos con alerta de stock bajo: {len(alerts)}")
        for product in alerts:
            print(f"- {product.code}: {product.name} (Stock: {product.current_stock}/{product.min_stock})")


if __name__ == "__main__":
    create_sample_data()
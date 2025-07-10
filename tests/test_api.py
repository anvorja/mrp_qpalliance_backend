import requests
import json

# URL base de la API
BASE_URL = "http://localhost:5000/api/v1"

# Probar el endpoint de salud
try:
    health_response = requests.get(f"{BASE_URL}/health")
    print(f"Health check: {health_response.status_code}")
    print(json.dumps(health_response.json(), indent=2))
except Exception as e:
    print(f"Error al verificar salud: {e}")

# Probar el login
try:
    login_data = {
        "email": "usertesting@qpalliance.co",
        "password": "TestingQp#1"
    }
    login_response = requests.post(
        f"{BASE_URL}/auth/login", 
        json=login_data
    )
    print(f"\nLogin: {login_response.status_code}")
    if login_response.ok:
        print(json.dumps(login_response.json(), indent=2))
    else:
        print(f"Error: {login_response.text}")
except Exception as e:
    print(f"Error al intentar login: {e}")

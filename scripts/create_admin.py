"""
Script para crear un usuario administrador
Ejecutar: python scripts/create_admin.py
"""
from passlib.context import CryptContext
import sys

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Uso: python scripts/create_admin.py <contraseña>")
        print("Ejemplo: python scripts/create_admin.py admin123")
        sys.exit(1)
    
    password = sys.argv[1]
    hashed = pwd_context.hash(password)
    print(f"\nHash generado para la contraseña '{password}':")
    print(f"{hashed}\n")
    print("Puedes usar este hash en el script SQL o insertar directamente:")
    print(f"INSERT INTO usuarios (email, nombre, apellido, hashed_password, es_administrador)")
    print(f"VALUES ('admin@hotel.com', 'Administrador', 'Sistema', '{hashed}', TRUE);")

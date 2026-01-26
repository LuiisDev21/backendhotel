"""
Script para inicializar la base de datos
Ejecutar: python scripts/init_database.py
"""
import sys
import os

# Agregar el directorio raíz al path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.database import engine, Base
from app.models import Usuario, Habitacion, Reserva, Pago


def init_db():
    """Crea todas las tablas en la base de datos"""
    try:
        print("=" * 50)
        print("Inicializando base de datos...")
        print("=" * 50)
        
        # Verificar conexión
        print("\n1. Verificando conexion a la base de datos...")
        with engine.connect() as conn:
            print("[OK] Conexion establecida correctamente")
        
        # Crear tablas
        print("\n2. Creando tablas...")
        Base.metadata.create_all(bind=engine)
        print("[OK] Tablas creadas correctamente")
        
        print("\n" + "=" * 50)
        print("[OK] Base de datos inicializada correctamente")
        print("=" * 50)
        
    except Exception as e:
        print(f"\n[ERROR] Error al inicializar la base de datos:")
        print(f"   {str(e)}")
        print("\nVerifica:")
        print("   1. Que el archivo .env tenga DATABASE_URL configurado correctamente")
        print("   2. Que la base de datos exista y sea accesible")
        print("   3. Que las credenciales sean correctas")
        sys.exit(1)


if __name__ == "__main__":
    init_db()

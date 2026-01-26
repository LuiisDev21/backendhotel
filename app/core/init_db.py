"""
Script para inicializar la base de datos
Ejecutar: python -m app.core.init_db
"""
from app.core.database import engine, Base
from app.models import Usuario, Habitacion, Reserva, Pago


def init_db():
    """Crea todas las tablas en la base de datos"""
    try:
        print("Creando tablas en la base de datos...")
        Base.metadata.create_all(bind=engine)
        print("✅ Tablas creadas correctamente")
    except Exception as e:
        print(f"❌ Error al crear tablas: {e}")
        raise


if __name__ == "__main__":
    init_db()

"""
Script para inicializar la base de datos.
Ejecutar: python -m app.core.init_db
"""
import logging
from app.core.database import engine, Base
from app.models import Usuario, Habitacion, Reserva, TransaccionPago

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)


def init_db():
    try:
        logger.info("Creando tablas...")
        Base.metadata.create_all(bind=engine)
        logger.info("Tablas creadas correctamente")
    except Exception as e:
        logger.exception("Error al crear tablas: %s", e)
        raise


if __name__ == "__main__":
    init_db()

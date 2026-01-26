from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from app.core.config import settings

# Configuración del engine con pool de conexiones mejorado
engine = create_engine(
    settings.DATABASE_URL,
    pool_pre_ping=True,  # Verifica conexiones antes de usarlas
    pool_recycle=300,    # Recicla conexiones cada 5 minutos
    pool_size=5,         # Tamaño del pool de conexiones
    max_overflow=10,     # Conexiones adicionales permitidas
    echo=False           # Cambiar a True para ver queries SQL
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()

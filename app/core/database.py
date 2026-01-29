"""  
Configuración de la base de datos, se define la configuración de la base de datos con SQLAlchemy.
- engine: Crea el motor de la base de datos.
- SessionLocal: Crea la sesión de la base de datos.
- Base: Crea el modelo de la base de datos.
- ObtenerSesionBD: Obtiene la sesión de la base de datos.
"""
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from app.core.config import settings


engine = create_engine(
    settings.DATABASE_URL,
    pool_pre_ping=True,   
    pool_recycle=300,    
    pool_size=settings.POOL_SIZE,
    max_overflow=settings.MAX_OVERFLOW,
    echo=False,          
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def ObtenerSesionBD():
    SesionBD = SessionLocal()
    try:
        yield SesionBD
    except Exception:
        SesionBD.rollback()
        raise
    finally:
        SesionBD.close()

"""
Modelo de TipoHabitacion con SQLAlchemy.
"""
from sqlalchemy import Column, Integer, String, Numeric, Boolean, Text, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base


class TipoHabitacion(Base):
    __tablename__ = "tipos_habitacion"

    id = Column(Integer, primary_key=True, index=True)
    codigo = Column(String(50), unique=True, nullable=False, index=True)
    nombre = Column(String(100), nullable=False)
    descripcion = Column(Text, nullable=True)
    capacidad_maxima = Column(Integer, nullable=False)
    precio_base = Column(Numeric(12, 2), nullable=False)
    activo = Column(Boolean, default=True, index=True)
    fecha_creacion = Column(DateTime(timezone=True), server_default=func.now())
    fecha_actualizacion = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    habitaciones = relationship("Habitacion", back_populates="tipo_habitacion")

"""
Modelo de Permiso (RBAC).
"""
from sqlalchemy import Column, Integer, String, Text, ForeignKey, Table, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base

# Tabla de asociación N:M entre roles y permisos
rol_permisos = Table(
    "rol_permisos",
    Base.metadata,
    Column("rol_id", Integer, ForeignKey("roles.id", ondelete="CASCADE"), primary_key=True),
    Column("permiso_id", Integer, ForeignKey("permisos.id", ondelete="CASCADE"), primary_key=True),
    Column("fecha_asignacion", DateTime(timezone=True), server_default=func.now()),
)


class Permiso(Base):
    __tablename__ = "permisos"

    id = Column(Integer, primary_key=True, index=True)
    codigo = Column(String(100), unique=True, nullable=False, index=True)
    nombre = Column(String(150), nullable=False)
    modulo = Column(String(50), nullable=False)
    descripcion = Column(Text, nullable=True)
    fecha_creacion = Column(DateTime(timezone=True), server_default=func.now())

    roles = relationship(
        "Rol",
        secondary=rol_permisos,
        back_populates="permisos"
    )

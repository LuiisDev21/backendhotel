"""
Modelo de Rol (RBAC).
"""
from sqlalchemy import Column, Integer, String, Boolean, Text
from sqlalchemy import DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base
from app.models.usuario_roles_table import usuario_roles


class Rol(Base):
    __tablename__ = "roles"

    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(50), unique=True, nullable=False)
    descripcion = Column(Text, nullable=True)
    activo = Column(Boolean, default=True)
    fecha_creacion = Column(DateTime(timezone=True), server_default=func.now())
    fecha_actualizacion = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    permisos = relationship(
        "Permiso",
        secondary="rol_permisos",
        back_populates="roles",
        lazy="selectin"
    )
    usuarios = relationship(
        "Usuario",
        secondary=usuario_roles,
        back_populates="roles",
        primaryjoin="Rol.id == usuario_roles.c.rol_id",
        secondaryjoin="usuario_roles.c.usuario_id == Usuario.id",
    )

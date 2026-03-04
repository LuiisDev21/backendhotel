"""
Modelo de Usuario con SQLAlchemy.
"""
from sqlalchemy import Column, Integer, String, Boolean, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base
from app.models.usuario_roles_table import usuario_roles
from app.models.sesion_usuario import SesionUsuario


class Usuario(Base):
    __tablename__ = "usuarios"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    nombre = Column(String(100), nullable=False)
    apellido = Column(String(100), nullable=False)
    telefono = Column(String(20), nullable=True)
    hashed_password = Column(String(255), nullable=False)
    activo = Column(Boolean, default=True, index=True)
    email_verificado = Column(Boolean, default=False)
    intentos_fallidos = Column(Integer, default=0)
    bloqueado_hasta = Column(DateTime(timezone=True), nullable=True)
    fecha_ultimo_login = Column(DateTime(timezone=True), nullable=True)
    fecha_creacion = Column(DateTime(timezone=True), server_default=func.now())
    fecha_actualizacion = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    roles = relationship(
        "Rol",
        secondary=usuario_roles,
        back_populates="usuarios",
        lazy="selectin",
        primaryjoin="Usuario.id == usuario_roles.c.usuario_id",
        secondaryjoin="usuario_roles.c.rol_id == Rol.id",
    )
    sesiones = relationship(
        "SesionUsuario",
        back_populates="usuario",
        lazy="selectin",
        foreign_keys=[SesionUsuario.usuario_id],
    )
    reservas = relationship("Reserva", back_populates="usuario")
    auditorias = relationship("Auditoria", back_populates="usuario")

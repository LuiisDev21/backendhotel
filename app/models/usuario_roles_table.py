"""
Tabla de asociación N:M entre usuarios y roles.
Definida en módulo aparte para evitar importaciones circulares y poder
especificar primaryjoin/secondaryjoin en usuario.py y rol.py.
"""
from sqlalchemy import Column, Integer, DateTime, Table, ForeignKey
from sqlalchemy.sql import func
from app.core.database import Base

usuario_roles = Table(
    "usuario_roles",
    Base.metadata,
    Column("usuario_id", Integer, ForeignKey("usuarios.id", ondelete="CASCADE"), primary_key=True),
    Column("rol_id", Integer, ForeignKey("roles.id", ondelete="CASCADE"), primary_key=True),
    Column("asignado_por", Integer, ForeignKey("usuarios.id", ondelete="SET NULL"), nullable=True),
    Column("fecha_asignacion", DateTime(timezone=True), server_default=func.now()),
    Column("fecha_expiracion", DateTime(timezone=True), nullable=True),
)

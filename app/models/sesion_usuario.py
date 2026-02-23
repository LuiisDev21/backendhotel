"""
Modelo de Sesión de usuario (refresh tokens).
"""
import uuid
from sqlalchemy import Column, Integer, String, Boolean, Text, ForeignKey, DateTime
from sqlalchemy.dialects.postgresql import INET, UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base


class SesionUsuario(Base):
    __tablename__ = "sesiones_usuario"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    usuario_id = Column(Integer, ForeignKey("usuarios.id", ondelete="CASCADE"), nullable=False)
    refresh_token_hash = Column(String(255), unique=True, nullable=False)
    ip_address = Column(INET, nullable=True)
    user_agent = Column(Text, nullable=True)
    dispositivo = Column(String(100), nullable=True)
    activa = Column(Boolean, default=True)
    fecha_creacion = Column(DateTime(timezone=True), server_default=func.now())
    fecha_expiracion = Column(DateTime(timezone=True), nullable=False)
    fecha_ultimo_uso = Column(DateTime(timezone=True), server_default=func.now())
    revocada_en = Column(DateTime(timezone=True), nullable=True)
    revocada_por = Column(Integer, ForeignKey("usuarios.id", ondelete="SET NULL"), nullable=True)

    usuario = relationship(
        "Usuario",
        back_populates="sesiones",
        foreign_keys=[usuario_id],
    )

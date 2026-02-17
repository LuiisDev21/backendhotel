"""
Modelo de Auditoria, se define el modelo de auditoría con SQLAlchemy.
"""
from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Text, JSON
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship
from datetime import datetime
import enum
from app.core.database import Base
from app.core.enum_type import EnumType


class AccionAuditoria(str, enum.Enum):
    CREATE = "CREATE"
    UPDATE = "UPDATE"
    DELETE = "DELETE"
    LOGIN = "LOGIN"
    LOGOUT = "LOGOUT"
    RESERVA_CREATE = "RESERVA_CREATE"
    RESERVA_CANCEL = "RESERVA_CANCEL"
    RESERVA_CONFIRM = "RESERVA_CONFIRM"
    PAGO_PROCESS = "PAGO_PROCESS"
    PAGO_REFUND = "PAGO_REFUND"


class Auditoria(Base):
    __tablename__ = "auditoria"

    id = Column(Integer, primary_key=True, index=True)
    tabla_afectada = Column(String(100), nullable=False, index=True)
    registro_id = Column(Integer, nullable=True, index=True)
    accion = Column(EnumType(AccionAuditoria), nullable=False, index=True)
    usuario_id = Column(Integer, ForeignKey("usuarios.id"), nullable=True, index=True)
    datos_anteriores = Column(JSONB, nullable=True)
    datos_nuevos = Column(JSONB, nullable=True)
    ip_address = Column(String(45), nullable=True)
    user_agent = Column(Text, nullable=True)
    fecha_accion = Column(DateTime, default=datetime.utcnow, index=True)
    observaciones = Column(Text, nullable=True)

    usuario = relationship("Usuario", back_populates="auditorias")

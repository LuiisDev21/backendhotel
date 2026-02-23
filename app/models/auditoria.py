"""
Modelo de Auditoría con SQLAlchemy.
"""
from sqlalchemy import Column, BigInteger, Integer, String, ForeignKey, Text, DateTime
from sqlalchemy.dialects.postgresql import JSONB, INET
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum
from app.core.database import Base
from app.core.enum_type import EnumType


class AccionAuditoria(str, enum.Enum):
    CREATE = "CREATE"
    UPDATE = "UPDATE"
    DELETE = "DELETE"
    LOGIN = "LOGIN"
    LOGOUT = "LOGOUT"
    LOGIN_FAILED = "LOGIN_FAILED"
    RESERVA_CREATE = "RESERVA_CREATE"
    RESERVA_CANCEL = "RESERVA_CANCEL"
    RESERVA_CONFIRM = "RESERVA_CONFIRM"
    RESERVA_CHECKIN = "RESERVA_CHECKIN"
    RESERVA_CHECKOUT = "RESERVA_CHECKOUT"
    PAGO_PROCESS = "PAGO_PROCESS"
    PAGO_REFUND = "PAGO_REFUND"
    PAGO_FAILED = "PAGO_FAILED"
    USUARIO_BLOQUEO = "USUARIO_BLOQUEO"
    USUARIO_DESBLOQUEO = "USUARIO_DESBLOQUEO"
    CONFIGURACION_CAMBIO = "CONFIGURACION_CAMBIO"


class Auditoria(Base):
    __tablename__ = "auditoria"

    id = Column(BigInteger, primary_key=True, index=True, autoincrement=True)
    tabla_afectada = Column(String(100), nullable=False, index=True)
    registro_id = Column(BigInteger, nullable=True, index=True)
    accion = Column(EnumType(AccionAuditoria), nullable=False, index=True)
    usuario_id = Column(Integer, ForeignKey("usuarios.id", ondelete="SET NULL"), nullable=True, index=True)
    datos_anteriores = Column(JSONB, nullable=True)
    datos_nuevos = Column(JSONB, nullable=True)
    ip_address = Column(INET, nullable=True)
    user_agent = Column(Text, nullable=True)
    endpoint = Column(String(255), nullable=True)
    fecha_accion = Column(DateTime(timezone=True), server_default=func.now(), index=True)
    observaciones = Column(Text, nullable=True)

    usuario = relationship("Usuario", back_populates="auditorias")

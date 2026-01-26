from pydantic import BaseModel
from typing import Optional
from decimal import Decimal
from datetime import date, datetime
from app.models.reserva import EstadoReserva


class ReservaBase(BaseModel):
    habitacion_id: int
    fecha_entrada: date
    fecha_salida: date
    numero_huespedes: int
    notas: Optional[str] = None


class ReservaCreate(ReservaBase):
    pass


class ReservaUpdate(BaseModel):
    fecha_entrada: Optional[date] = None
    fecha_salida: Optional[date] = None
    numero_huespedes: Optional[int] = None
    estado: Optional[EstadoReserva] = None
    notas: Optional[str] = None


class ReservaResponse(ReservaBase):
    id: int
    usuario_id: int
    precio_total: Decimal
    estado: EstadoReserva
    fecha_creacion: datetime
    fecha_actualizacion: datetime

    class Config:
        from_attributes = True

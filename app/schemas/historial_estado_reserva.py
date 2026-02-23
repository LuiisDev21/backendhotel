from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from app.models.reserva import EstadoReserva


class HistorialEstadoReservaResponse(BaseModel):
    id: int
    reserva_id: int
    estado_anterior: Optional[EstadoReserva] = None
    estado_nuevo: EstadoReserva
    motivo: Optional[str] = None
    cambiado_por: Optional[int] = None
    fecha_cambio: datetime

    class Config:
        from_attributes = True

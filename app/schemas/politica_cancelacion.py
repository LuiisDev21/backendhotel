from pydantic import BaseModel
from typing import Optional
from decimal import Decimal
from datetime import datetime


class PoliticaCancelacionBase(BaseModel):
    nombre: str
    descripcion: Optional[str] = None
    horas_anticipacion: int
    porcentaje_penalizacion: Decimal = 0
    aplica_a_tipo_habitacion_id: Optional[int] = None
    activa: bool = True


class PoliticaCancelacionCreate(PoliticaCancelacionBase):
    pass


class PoliticaCancelacionResponse(PoliticaCancelacionBase):
    id: int
    fecha_creacion: datetime

    class Config:
        from_attributes = True

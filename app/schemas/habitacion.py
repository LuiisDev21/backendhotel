from pydantic import BaseModel
from typing import Optional
from decimal import Decimal
from datetime import datetime


class Habitacion(BaseModel):
    numero: str
    tipo: str
    descripcion: Optional[str] = None
    capacidad: int
    precio_por_noche: Decimal
    disponible: bool = True
    imagen_url: Optional[str] = None


class HabitacionCreate(Habitacion):
    pass


class HabitacionUpdate(BaseModel):
    tipo: Optional[str] = None
    descripcion: Optional[str] = None
    capacidad: Optional[int] = None
    precio_por_noche: Optional[Decimal] = None
    disponible: Optional[bool] = None
    imagen_url: Optional[str] = None


class HabitacionResponse(Habitacion):
    id: int
    fecha_creacion: datetime

    class Config:
        from_attributes = True

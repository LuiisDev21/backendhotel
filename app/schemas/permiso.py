from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class PermisoBase(BaseModel):
    codigo: str
    nombre: str
    modulo: str
    descripcion: Optional[str] = None


class PermisoResponse(PermisoBase):
    id: int
    fecha_creacion: datetime

    class Config:
        from_attributes = True

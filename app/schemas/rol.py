from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class RolBase(BaseModel):
    nombre: str
    descripcion: Optional[str] = None
    activo: bool = True


class RolCreate(RolBase):
    pass


class RolUpdate(BaseModel):
    nombre: Optional[str] = None
    descripcion: Optional[str] = None
    activo: Optional[bool] = None


class RolResponse(RolBase):
    id: int
    fecha_creacion: datetime
    fecha_actualizacion: datetime

    class Config:
        from_attributes = True

from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from uuid import UUID


class SesionUsuarioResponse(BaseModel):
    id: UUID
    usuario_id: int
    activa: bool
    fecha_creacion: datetime
    fecha_expiracion: datetime
    fecha_ultimo_uso: datetime

    class Config:
        from_attributes = True

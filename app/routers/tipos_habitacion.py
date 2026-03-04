"""
Routers de Tipos de Habitación, se definen los routers de tipos de habitación para la API.
- ListarTiposHabitacion: Lista todos los tipos de habitación activos.
- ObtenerTipoHabitacion: Obtiene un tipo de habitación por su ID.
"""
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import List
from app.core.database import ObtenerSesionBD
from app.schemas.habitacion import TipoHabitacionResponse
from app.repositories.tipo_habitacion_repository import TipoHabitacionRepository

router = APIRouter(prefix="/tipos-habitacion", tags=["Tipos de Habitación"])


@router.get("", response_model=List[TipoHabitacionResponse])
def ListarTiposHabitacion(
    SoloActivos: bool = Query(True),
    Saltar: int = Query(0, ge=0),
    Limite: int = Query(100, ge=1, le=100),
    SesionBD: Session = Depends(ObtenerSesionBD)
):
    """Lista todos los tipos de habitación."""
    Repositorio = TipoHabitacionRepository(SesionBD)
    return Repositorio.ObtenerTodos(SoloActivos=SoloActivos, Saltar=Saltar, Limite=Limite)


@router.get("/{tipo_id}", response_model=TipoHabitacionResponse)
def ObtenerTipoHabitacion(
    tipo_id: int,
    SesionBD: Session = Depends(ObtenerSesionBD)
):
    """Obtiene un tipo de habitación por su ID."""
    Repositorio = TipoHabitacionRepository(SesionBD)
    TipoHabitacion = Repositorio.ObtenerPorId(tipo_id)
    if not TipoHabitacion:
        from fastapi import HTTPException, status
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tipo de habitación no encontrado"
        )
    return TipoHabitacion

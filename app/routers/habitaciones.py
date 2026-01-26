from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import Optional, List
from datetime import date
from app.core.database import ObtenerSesionBD
from app.core.dependencies import ObtenerAdministradorActual, ObtenerUsuarioActual
from app.schemas.habitacion import HabitacionCreate, HabitacionUpdate, HabitacionResponse
from app.services.habitacion_service import HabitacionService
from app.models.usuario import Usuario

router = APIRouter(prefix="/habitaciones", tags=["Habitaciones"])


@router.post("", response_model=HabitacionResponse, dependencies=[Depends(ObtenerAdministradorActual)])
def CrearHabitacion(DatosHabitacion: HabitacionCreate, SesionBD: Session = Depends(ObtenerSesionBD)):
    Servicio = HabitacionService(SesionBD)
    return Servicio.CrearHabitacion(DatosHabitacion)


@router.get("", response_model=List[HabitacionResponse])
def ListarHabitaciones(
    Saltar: int = Query(0, ge=0),
    Limite: int = Query(100, ge=1, le=100),
    SesionBD: Session = Depends(ObtenerSesionBD)
):
    Servicio = HabitacionService(SesionBD)
    return Servicio.ListarHabitaciones(Saltar=Saltar, Limite=Limite)


@router.get("/buscar", response_model=List[HabitacionResponse])
def BuscarHabitacionesDisponibles(
    FechaEntrada: date = Query(...),
    FechaSalida: date = Query(...),
    Capacidad: Optional[int] = Query(None, ge=1),
    Tipo: Optional[str] = None,
    SesionBD: Session = Depends(ObtenerSesionBD)
):
    Servicio = HabitacionService(SesionBD)
    return Servicio.BuscarDisponibles(
        FechaEntrada=FechaEntrada,
        FechaSalida=FechaSalida,
        Capacidad=Capacidad,
        Tipo=Tipo
    )


@router.get("/{habitacion_id}", response_model=HabitacionResponse)
def ObtenerHabitacion(habitacion_id: int, SesionBD: Session = Depends(ObtenerSesionBD)):
    Servicio = HabitacionService(SesionBD)
    return Servicio.ObtenerHabitacion(habitacion_id)


@router.put("/{habitacion_id}", response_model=HabitacionResponse, dependencies=[Depends(ObtenerAdministradorActual)])
def ActualizarHabitacion(
    habitacion_id: int,
    DatosHabitacion: HabitacionUpdate,
    SesionBD: Session = Depends(ObtenerSesionBD)
):
    Servicio = HabitacionService(SesionBD)
    return Servicio.ActualizarHabitacion(habitacion_id, DatosHabitacion)


@router.delete("/{habitacion_id}", dependencies=[Depends(ObtenerAdministradorActual)])
def EliminarHabitacion(habitacion_id: int, SesionBD: Session = Depends(ObtenerSesionBD)):
    Servicio = HabitacionService(SesionBD)
    Servicio.EliminarHabitacion(habitacion_id)
    return {"message": "Habitación eliminada correctamente"}

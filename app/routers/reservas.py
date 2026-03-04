""" 
Routers de Reservas, se definen los routers de reservas para la API.
- CrearReserva: Crea una nueva reserva.
- ListarMisReservas: Lista todas las reservas de un usuario.
- ListarTodasReservas: Lista todas las reservas.
- ObtenerReserva: Obtiene una reserva por su ID.
- ActualizarReserva: Actualiza una reserva existente.
- CancelarReserva: Cancela una reserva existente.
"""
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import List
from app.core.database import ObtenerSesionBD
from app.core.dependencies import ObtenerUsuario, TienePermiso, ObtenerReservaConPermiso
from app.schemas.reserva import ReservaCreate, ReservaUpdate, ReservaResponse, ReservaPrecioPreview
from app.schemas.historial_estado_reserva import HistorialEstadoReservaResponse
from app.services.reserva_service import ServicioReserva
from app.models.usuario import Usuario

router = APIRouter(prefix="/reservas", tags=["Reservas"])


@router.post("", response_model=ReservaResponse, status_code=201)
def CrearReserva(
    DatosReserva: ReservaCreate,
    UsuarioActual: Usuario = Depends(ObtenerUsuario),
    SesionBD: Session = Depends(ObtenerSesionBD)
):
    Servicio = ServicioReserva(SesionBD, UsuarioId=UsuarioActual.id)
    return Servicio.CrearReserva(UsuarioActual.id, DatosReserva)


@router.post("/previsualizar-precio", response_model=ReservaPrecioPreview)
def PrevisualizarPrecioReserva(
    DatosReserva: ReservaCreate,
    UsuarioActual: Usuario = Depends(ObtenerUsuario),
    SesionBD: Session = Depends(ObtenerSesionBD)
):
    """Devuelve el desglose de precios para una reserva sin crearla."""
    Servicio = ServicioReserva(SesionBD, UsuarioId=UsuarioActual.id)
    return Servicio.PrevisualizarPrecio(UsuarioActual.id, DatosReserva)


@router.get("", response_model=List[ReservaResponse])
def ListarMisReservas(
    Saltar: int = Query(0, ge=0),
    Limite: int = Query(100, ge=1, le=100),
    UsuarioActual: Usuario = Depends(ObtenerUsuario),
    SesionBD: Session = Depends(ObtenerSesionBD)
):
    Servicio = ServicioReserva(SesionBD)
    return Servicio.ListarReservasUsuario(UsuarioActual.id, Saltar=Saltar, Limite=Limite)


@router.get("/todas", response_model=List[ReservaResponse], dependencies=[Depends(TienePermiso("reservas.ver_todas"))])
def ListarTodasReservas(
    Saltar: int = Query(0, ge=0),
    Limite: int = Query(100, ge=1, le=100),
    SesionBD: Session = Depends(ObtenerSesionBD)
):
    Servicio = ServicioReserva(SesionBD)
    return Servicio.ListarTodasReservas(Saltar=Saltar, Limite=Limite)


@router.get("/{reserva_id}/historial-estados", response_model=List[HistorialEstadoReservaResponse])
def ObtenerHistorialEstadosReserva(
    ReservaEncontrada = Depends(ObtenerReservaConPermiso()),
    SesionBD: Session = Depends(ObtenerSesionBD)
):
    """Obtiene el historial de cambios de estado de una reserva. Mismo permiso que ver la reserva."""
    Servicio = ServicioReserva(SesionBD)
    return Servicio.ObtenerHistorialEstados(ReservaEncontrada.id)


@router.get("/{reserva_id}", response_model=ReservaResponse)
def ObtenerReserva(ReservaEncontrada = Depends(ObtenerReservaConPermiso())):
    """Obtiene una reserva. Acceso: dueño de la reserva o permiso reservas.ver_todas."""
    return ReservaEncontrada


@router.put("/{reserva_id}", response_model=ReservaResponse)
def ActualizarReserva(
    DatosReserva: ReservaUpdate,
    ReservaEncontrada = Depends(ObtenerReservaConPermiso()),
    UsuarioActual: Usuario = Depends(ObtenerUsuario),
    SesionBD: Session = Depends(ObtenerSesionBD)
):
    Servicio = ServicioReserva(SesionBD, UsuarioId=UsuarioActual.id)
    return Servicio.ActualizarReserva(ReservaEncontrada.id, DatosReserva)


@router.post("/{reserva_id}/cancelar", response_model=ReservaResponse)
def CancelarReserva(
    ReservaEncontrada = Depends(ObtenerReservaConPermiso("reservas.cancelar")),
    UsuarioActual: Usuario = Depends(ObtenerUsuario),
    SesionBD: Session = Depends(ObtenerSesionBD)
):
    Servicio = ServicioReserva(SesionBD, UsuarioId=UsuarioActual.id)
    return Servicio.CancelarReserva(ReservaEncontrada.id)

"""
Routers de Transacciones de pago (1:N por reserva). RBAC: pagos.procesar, pagos.reembolsar.
"""
from fastapi import APIRouter, Depends, Query, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.core.database import ObtenerSesionBD
from app.core.dependencies import ObtenerUsuario, TienePermiso, UsuarioTienePermiso
from app.schemas.transaccion_pago import (
    TransaccionPagoCreate,
    TransaccionPagoUpdate,
    TransaccionPagoResponse,
)
from app.services.transaccion_pago_service import ServicioTransaccionPago
from app.models.usuario import Usuario

router = APIRouter(prefix="/pagos", tags=["Pagos"])


def _puede_ver_transacciones_reserva(UsuarioActual: Usuario, reserva_id: int, SesionBD: Session) -> bool:
    from app.repositories.reserva_repository import ReservaRepository
    repo = ReservaRepository(SesionBD)
    r = repo.ObtenerPorId(reserva_id)
    if not r:
        return False
    return r.usuario_id == UsuarioActual.id or UsuarioTienePermiso(UsuarioActual, "pagos.procesar")


@router.post("", response_model=TransaccionPagoResponse, status_code=201)
def CrearTransaccion(
    Datos: TransaccionPagoCreate,
    UsuarioActual: Usuario = Depends(ObtenerUsuario),
    SesionBD: Session = Depends(ObtenerSesionBD)
):
    if not _puede_ver_transacciones_reserva(UsuarioActual, Datos.reserva_id, SesionBD):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tiene permiso para crear transacciones en esta reserva"
        )
    Servicio = ServicioTransaccionPago(SesionBD, UsuarioId=UsuarioActual.id)
    return Servicio.CrearTransaccion(Datos, UsuarioId=UsuarioActual.id)


@router.get("", response_model=List[TransaccionPagoResponse], dependencies=[Depends(TienePermiso("pagos.procesar"))])
def ListarTransacciones(
    Saltar: int = Query(0, ge=0),
    Limite: int = Query(100, ge=1, le=100),
    SesionBD: Session = Depends(ObtenerSesionBD)
):
    Servicio = ServicioTransaccionPago(SesionBD)
    return Servicio.ListarTodas(Saltar=Saltar, Limite=Limite)


@router.get("/reserva/{reserva_id}", response_model=List[TransaccionPagoResponse])
def ListarTransaccionesPorReserva(
    reserva_id: int,
    UsuarioActual: Usuario = Depends(ObtenerUsuario),
    SesionBD: Session = Depends(ObtenerSesionBD)
):
    if not _puede_ver_transacciones_reserva(UsuarioActual, reserva_id, SesionBD):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tiene permiso para ver las transacciones de esta reserva"
        )
    Servicio = ServicioTransaccionPago(SesionBD)
    return Servicio.ObtenerPorReserva(reserva_id)


@router.get("/{transaccion_id}", response_model=TransaccionPagoResponse)
def ObtenerTransaccion(
    transaccion_id: int,
    UsuarioActual: Usuario = Depends(ObtenerUsuario),
    SesionBD: Session = Depends(ObtenerSesionBD)
):
    Servicio = ServicioTransaccionPago(SesionBD)
    t = Servicio.ObtenerTransaccion(transaccion_id)
    if not _puede_ver_transacciones_reserva(UsuarioActual, t.reserva_id, SesionBD):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tiene permiso para ver esta transacción"
        )
    return t


@router.post("/{transaccion_id}/procesar", response_model=TransaccionPagoResponse, dependencies=[Depends(TienePermiso("pagos.procesar"))])
def ProcesarTransaccion(
    transaccion_id: int,
    UsuarioActual: Usuario = Depends(ObtenerUsuario),
    SesionBD: Session = Depends(ObtenerSesionBD)
):
    Servicio = ServicioTransaccionPago(SesionBD, UsuarioId=UsuarioActual.id)
    return Servicio.ProcesarTransaccion(transaccion_id, UsuarioId=UsuarioActual.id)


@router.put("/{transaccion_id}", response_model=TransaccionPagoResponse, dependencies=[Depends(TienePermiso("pagos.procesar"))])
def ActualizarTransaccion(
    transaccion_id: int,
    Datos: TransaccionPagoUpdate,
    UsuarioActual: Usuario = Depends(ObtenerUsuario),
    SesionBD: Session = Depends(ObtenerSesionBD)
):
    Servicio = ServicioTransaccionPago(SesionBD, UsuarioId=UsuarioActual.id)
    return Servicio.ActualizarTransaccion(transaccion_id, Datos, UsuarioId=UsuarioActual.id)


@router.post("/{transaccion_id}/reembolsar", response_model=TransaccionPagoResponse, dependencies=[Depends(TienePermiso("pagos.reembolsar"))])
def ReembolsarTransaccion(
    transaccion_id: int,
    UsuarioActual: Usuario = Depends(ObtenerUsuario),
    SesionBD: Session = Depends(ObtenerSesionBD)
):
    Servicio = ServicioTransaccionPago(SesionBD, UsuarioId=UsuarioActual.id)
    return Servicio.Reembolsar(transaccion_id, UsuarioId=UsuarioActual.id)

"""
Routers de reportes: endpoints para estadísticas, ingresos, ocupación, auditoría y ranking de clientes.
Solo administradores.
"""
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import Optional, List
from datetime import date, datetime, time

from app.core.database import ObtenerSesionBD
from app.core.dependencies import TienePermiso
from app.schemas.reporte import (
    EstadisticasReservasResponse,
    IngresosPorPeriodoResponse,
    OcupacionResponse,
    AuditoriaLogItemResponse,
    ClienteRankingItemResponse,
    DashboardResponse,
)
from app.services.reporte_service import ServicioReportes

router = APIRouter(prefix="/reportes", tags=["Reportes"], dependencies=[Depends(TienePermiso("reportes.ver"))])


@router.get("/estadisticas-reservas", response_model=EstadisticasReservasResponse)
def ObtenerEstadisticasReservas(
    fecha_inicio: Optional[date] = Query(None),
    fecha_fin: Optional[date] = Query(None),
    SesionBD: Session = Depends(ObtenerSesionBD),
):
    """Estadísticas de reservas por período (totales por estado, ingresos, promedio)."""
    servicio = ServicioReportes(SesionBD)
    return servicio.ObtenerEstadisticasReservas(fecha_inicio, fecha_fin)


@router.get("/ingresos", response_model=IngresosPorPeriodoResponse)
def ObtenerIngresos(
    fecha_inicio: Optional[date] = Query(None),
    fecha_fin: Optional[date] = Query(None),
    SesionBD: Session = Depends(ObtenerSesionBD),
):
    """Ingresos por período (total y desglose por método de pago)."""
    servicio = ServicioReportes(SesionBD)
    return servicio.ObtenerIngresos(fecha_inicio, fecha_fin)


@router.get("/ocupacion", response_model=OcupacionResponse)
def ObtenerOcupacion(
    fecha_inicio: date = Query(...),
    fecha_fin: date = Query(...),
    agrupar_por: str = Query("habitacion", regex="^(habitacion|tipo)$"),
    SesionBD: Session = Depends(ObtenerSesionBD),
):
    """Ocupación por habitación o por tipo de habitación (noches e ingresos)."""
    servicio = ServicioReportes(SesionBD)
    return servicio.ObtenerOcupacion(fecha_inicio, fecha_fin, agrupar_por)


@router.get("/auditoria", response_model=List[AuditoriaLogItemResponse])
def ObtenerAuditoria(
    fecha_desde: Optional[date] = Query(None),
    fecha_hasta: Optional[date] = Query(None),
    usuario_id: Optional[int] = Query(None),
    accion: Optional[str] = Query(None),
    tabla_afectada: Optional[str] = Query(None),
    Saltar: int = Query(0, ge=0),
    Limite: int = Query(100, ge=1, le=500),
    SesionBD: Session = Depends(ObtenerSesionBD),
):
    """Log de auditoría con filtros opcionales."""
    servicio = ServicioReportes(SesionBD)
    fd = datetime.combine(fecha_desde, time.min) if fecha_desde else None
    fh = datetime.combine(fecha_hasta, time.max) if fecha_hasta else None
    return servicio.ObtenerAuditoria(
        FechaDesde=fd,
        FechaHasta=fh,
        UsuarioId=usuario_id,
        Accion=accion,
        TablaAfectada=tabla_afectada,
        Saltar=Saltar,
        Limite=Limite,
    )


@router.get("/clientes", response_model=List[ClienteRankingItemResponse])
def ObtenerRankingClientes(
    fecha_inicio: Optional[date] = Query(None),
    fecha_fin: Optional[date] = Query(None),
    orden: str = Query("gastado", regex="^(reservas|gastado)$"),
    Limite: int = Query(50, ge=1, le=200),
    SesionBD: Session = Depends(ObtenerSesionBD),
):
    """Ranking de clientes por número de reservas o por total gastado."""
    servicio = ServicioReportes(SesionBD)
    return servicio.ObtenerRankingClientes(fecha_inicio, fecha_fin, orden, Limite)


@router.get("/dashboard", response_model=DashboardResponse)
def ObtenerDashboard(
    fecha_inicio: Optional[date] = Query(None),
    fecha_fin: Optional[date] = Query(None),
    SesionBD: Session = Depends(ObtenerSesionBD),
):
    """Resumen ejecutivo: estadísticas de reservas + ingresos del período."""
    servicio = ServicioReportes(SesionBD)
    return servicio.ObtenerDashboard(fecha_inicio, fecha_fin)

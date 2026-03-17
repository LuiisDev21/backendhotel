"""
Routers de reportes: endpoints para estadísticas, ingresos, ocupación, auditoría y ranking de clientes.
Solo administradores.
"""
from fastapi import APIRouter, Depends, Query, HTTPException, status, Response
from sqlalchemy.orm import Session
from typing import Optional, List
from datetime import date, datetime, time

from app.core.export_reportes import ExportarCSV, ExportarXLSX, ExportarPDFTabla
from app.core.database import ObtenerSesionBD
from app.core.dependencies import TienePermiso
from app.schemas.reporte import (
    EstadisticasReservasResponse,
    IngresosPorPeriodoResponse,
    IngresosPorTipoResponse,
    OcupacionResponse,
    AuditoriaListResponse,
    ClienteRankingItemResponse,
    ComparativaResponse,
    TendenciasResponse,
    ReembolsosDisputasResponse,
    KpisHoyResponse,
    DashboardResponse,
    DashboardCompletoResponse,
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


@router.get("/auditoria", response_model=AuditoriaListResponse)
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


@router.get("/ingresos-por-tipo", response_model=IngresosPorTipoResponse)
def ObtenerIngresosPorTipo(
    fecha_inicio: Optional[date] = Query(None),
    fecha_fin: Optional[date] = Query(None),
    SesionBD: Session = Depends(ObtenerSesionBD),
):
    """Ingresos y cantidad de reservas agrupados por tipo de habitación."""
    servicio = ServicioReportes(SesionBD)
    return servicio.ObtenerIngresosPorTipo(fecha_inicio, fecha_fin)


@router.get("/comparativa", response_model=ComparativaResponse)
def ObtenerComparativaPeriodos(
    fecha_inicio: Optional[date] = Query(None),
    fecha_fin: Optional[date] = Query(None),
    SesionBD: Session = Depends(ObtenerSesionBD),
):
    """Compara reservas e ingresos del período actual contra período anterior equivalente."""
    servicio = ServicioReportes(SesionBD)
    return servicio.ObtenerComparativa(fecha_inicio, fecha_fin)


@router.get("/tendencias", response_model=TendenciasResponse)
def ObtenerTendencias(
    tipo: str = Query("ingresos", pattern="^(ingresos|reservas)$"),
    agrupar_por: str = Query("dia", pattern="^(dia|semana)$"),
    fecha_inicio: date = Query(...),
    fecha_fin: date = Query(...),
    SesionBD: Session = Depends(ObtenerSesionBD),
):
    """Serie temporal de ingresos o reservas, agrupada por día o semana."""
    servicio = ServicioReportes(SesionBD)
    return servicio.ObtenerTendencias(tipo, agrupar_por, fecha_inicio, fecha_fin)


@router.get("/reembolsos-disputas", response_model=ReembolsosDisputasResponse)
def ObtenerReembolsosDisputas(
    fecha_inicio: Optional[date] = Query(None),
    fecha_fin: Optional[date] = Query(None),
    SesionBD: Session = Depends(ObtenerSesionBD),
):
    """Resumen de reembolsos y transacciones en disputa."""
    servicio = ServicioReportes(SesionBD)
    return servicio.ObtenerReembolsosDisputas(fecha_inicio, fecha_fin)


@router.get("/kpis-hoy", response_model=KpisHoyResponse)
def ObtenerKpisHoy(
    SesionBD: Session = Depends(ObtenerSesionBD),
):
    """KPIs del día: reservas creadas hoy, check-ins pendientes y pagos pendientes de procesar."""
    servicio = ServicioReportes(SesionBD)
    return servicio.ObtenerKpisHoy()


@router.get("/dashboard-completo", response_model=DashboardCompletoResponse)
def ObtenerDashboardCompleto(
    fecha_inicio: Optional[date] = Query(None),
    fecha_fin: Optional[date] = Query(None),
    SesionBD: Session = Depends(ObtenerSesionBD),
):
    """Dashboard agregado con estadísticas, ocupación, top clientes, auditoría reciente y KPIs diarios."""
    servicio = ServicioReportes(SesionBD)
    return servicio.ObtenerDashboardCompleto(fecha_inicio, fecha_fin)


@router.get("/exportar/ingresos")
def ExportarIngresos(
    formato: str = Query("csv", pattern="^(csv|xlsx|pdf)$"),
    fecha_inicio: Optional[date] = Query(None),
    fecha_fin: Optional[date] = Query(None),
    SesionBD: Session = Depends(ObtenerSesionBD),
):
    servicio = ServicioReportes(SesionBD)
    data = servicio.ObtenerIngresos(fecha_inicio, fecha_fin)
    filas = [
        {
            "metodo_pago": item.metodo_pago,
            "cantidad": item.cantidad,
            "monto": item.monto,
        }
        for item in (data.por_metodo_pago or [])
    ]
    filas.append({
        "metodo_pago": "TOTAL",
        "cantidad": data.cantidad_pagos,
        "monto": data.total_ingresos,
    })
    return _responder_exportacion(
        formato=formato,
        nombre_base="ingresos",
        titulo="Reporte de ingresos",
        subtitulo=f"Periodo: {fecha_inicio or 'inicio'} a {fecha_fin or 'hoy'}",
        filas=filas,
        columnas=["metodo_pago", "cantidad", "monto"],
        encabezados=["Metodo de pago", "Cantidad", "Monto"],
    )


@router.get("/exportar/ocupacion")
def ExportarOcupacion(
    formato: str = Query("csv", pattern="^(csv|xlsx|pdf)$"),
    fecha_inicio: date = Query(...),
    fecha_fin: date = Query(...),
    agrupar_por: str = Query("habitacion", pattern="^(habitacion|tipo)$"),
    SesionBD: Session = Depends(ObtenerSesionBD),
):
    servicio = ServicioReportes(SesionBD)
    data = servicio.ObtenerOcupacion(fecha_inicio, fecha_fin, agrupar_por)
    filas = [
        {
            "identificador": item.identificador,
            "nombre": item.nombre,
            "noches_ocupadas": item.noches_ocupadas,
            "noches_disponibles": item.noches_disponibles,
            "porcentaje_ocupacion": item.porcentaje_ocupacion,
            "ingresos": item.ingresos,
        }
        for item in data.items
    ]
    return _responder_exportacion(
        formato=formato,
        nombre_base=f"ocupacion_{agrupar_por}",
        titulo="Reporte de ocupacion",
        subtitulo=f"Periodo: {fecha_inicio} a {fecha_fin}",
        filas=filas,
        columnas=[
            "identificador",
            "nombre",
            "noches_ocupadas",
            "noches_disponibles",
            "porcentaje_ocupacion",
            "ingresos",
        ],
        encabezados=[
            "Identificador",
            "Nombre",
            "Noches ocupadas",
            "Noches disponibles",
            "% ocupacion",
            "Ingresos",
        ],
    )


@router.get("/exportar/clientes")
def ExportarClientes(
    formato: str = Query("csv", pattern="^(csv|xlsx|pdf)$"),
    fecha_inicio: Optional[date] = Query(None),
    fecha_fin: Optional[date] = Query(None),
    orden: str = Query("gastado", pattern="^(reservas|gastado)$"),
    limite: int = Query(50, ge=1, le=500),
    SesionBD: Session = Depends(ObtenerSesionBD),
):
    servicio = ServicioReportes(SesionBD)
    data = servicio.ObtenerRankingClientes(fecha_inicio, fecha_fin, orden, limite)
    filas = [
        {
            "usuario_id": item.usuario_id,
            "nombre": item.nombre,
            "email": item.email,
            "total_reservas": item.total_reservas,
            "total_gastado": item.total_gastado,
            "promedio_por_reserva": item.promedio_por_reserva,
            "ultima_reserva": item.ultima_reserva,
        }
        for item in data
    ]
    return _responder_exportacion(
        formato=formato,
        nombre_base="clientes",
        titulo="Ranking de clientes",
        subtitulo=f"Periodo: {fecha_inicio or 'inicio'} a {fecha_fin or 'hoy'}",
        filas=filas,
        columnas=[
            "usuario_id",
            "nombre",
            "email",
            "total_reservas",
            "total_gastado",
            "promedio_por_reserva",
            "ultima_reserva",
        ],
        encabezados=[
            "ID",
            "Nombre",
            "Email",
            "Total reservas",
            "Total gastado",
            "Promedio por reserva",
            "Ultima reserva",
        ],
    )


@router.get("/exportar/auditoria")
def ExportarAuditoria(
    formato: str = Query("csv", pattern="^(csv|xlsx|pdf)$"),
    fecha_desde: Optional[date] = Query(None),
    fecha_hasta: Optional[date] = Query(None),
    usuario_id: Optional[int] = Query(None),
    accion: Optional[str] = Query(None),
    tabla_afectada: Optional[str] = Query(None),
    limite: int = Query(500, ge=1, le=5000),
    SesionBD: Session = Depends(ObtenerSesionBD),
):
    servicio = ServicioReportes(SesionBD)
    fd = datetime.combine(fecha_desde, time.min) if fecha_desde else None
    fh = datetime.combine(fecha_hasta, time.max) if fecha_hasta else None
    data = servicio.ObtenerAuditoria(
        FechaDesde=fd,
        FechaHasta=fh,
        UsuarioId=usuario_id,
        Accion=accion,
        TablaAfectada=tabla_afectada,
        Saltar=0,
        Limite=limite,
    )
    filas = [
        {
            "id": item.id,
            "tabla_afectada": item.tabla_afectada,
            "registro_id": item.registro_id,
            "accion": item.accion,
            "usuario_id": item.usuario_id,
            "usuario_nombre": item.usuario_nombre,
            "fecha_accion": item.fecha_accion,
            "resumen_cambio": item.resumen_cambio,
            "observaciones": item.observaciones,
        }
        for item in data.items
    ]
    return _responder_exportacion(
        formato=formato,
        nombre_base="auditoria",
        titulo="Reporte de auditoria",
        subtitulo=f"Resultados: {data.total}",
        filas=filas,
        columnas=[
            "id",
            "tabla_afectada",
            "registro_id",
            "accion",
            "usuario_id",
            "usuario_nombre",
            "fecha_accion",
            "resumen_cambio",
            "observaciones",
        ],
        encabezados=[
            "ID",
            "Tabla",
            "Registro",
            "Accion",
            "Usuario ID",
            "Usuario",
            "Fecha",
            "Resumen",
            "Observaciones",
        ],
    )


@router.get("/exportar/ingresos-por-tipo")
def ExportarIngresosPorTipo(
    formato: str = Query("csv", pattern="^(csv|xlsx|pdf)$"),
    fecha_inicio: Optional[date] = Query(None),
    fecha_fin: Optional[date] = Query(None),
    SesionBD: Session = Depends(ObtenerSesionBD),
):
    servicio = ServicioReportes(SesionBD)
    data = servicio.ObtenerIngresosPorTipo(fecha_inicio, fecha_fin)
    filas = [
        {
            "identificador": item.identificador,
            "nombre": item.nombre,
            "cantidad_reservas": item.cantidad_reservas,
            "ingresos": item.ingresos,
        }
        for item in data.items
    ]
    return _responder_exportacion(
        formato=formato,
        nombre_base="ingresos_por_tipo",
        titulo="Ingresos por tipo de habitacion",
        subtitulo=f"Periodo: {fecha_inicio or 'inicio'} a {fecha_fin or 'hoy'}",
        filas=filas,
        columnas=["identificador", "nombre", "cantidad_reservas", "ingresos"],
        encabezados=["Codigo", "Tipo", "Cantidad reservas", "Ingresos"],
    )


def _responder_exportacion(
    formato: str,
    nombre_base: str,
    titulo: str,
    subtitulo: str,
    filas: List[dict],
    columnas: List[str],
    encabezados: List[str],
) -> Response:
    fecha_archivo = date.today().isoformat()
    if formato == "csv":
        contenido = ExportarCSV(filas, columnas, encabezados)
        return Response(
            content=contenido,
            media_type="text/csv; charset=utf-8",
            headers={"Content-Disposition": f'attachment; filename="{nombre_base}_{fecha_archivo}.csv"'},
        )
    if formato == "xlsx":
        contenido = ExportarXLSX(filas, columnas, encabezados, nombre_hoja=nombre_base)
        return Response(
            content=contenido,
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            headers={"Content-Disposition": f'attachment; filename="{nombre_base}_{fecha_archivo}.xlsx"'},
        )
    if formato == "pdf":
        contenido = ExportarPDFTabla(titulo, subtitulo, filas, columnas, encabezados)
        return Response(
            content=contenido,
            media_type="application/pdf",
            headers={"Content-Disposition": f'attachment; filename="{nombre_base}_{fecha_archivo}.pdf"'},
        )
    raise HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail="Formato no soportado. Use csv, xlsx o pdf.",
    )

"""
Servicio de reportes: orquesta repositorios y procedimientos almacenados para reportes.
"""
from sqlalchemy.orm import Session
from typing import Optional, List
from datetime import date, datetime
from decimal import Decimal

from app.repositories.stored_procedures import StoredProcedures
from app.repositories.reporte_repository import ReporteRepository
from app.repositories.auditoria_repository import AuditoriaRepository
from app.schemas.reporte import (
    EstadisticasReservasResponse,
    IngresosPorPeriodoResponse,
    IngresoPorMetodoItem,
    OcupacionItemResponse,
    OcupacionResponse,
    AuditoriaLogItemResponse,
    ClienteRankingItemResponse,
    DashboardResponse,
)


class ServicioReportes:
    def __init__(self, SesionBD: Session):
        self.SesionBD = SesionBD
        self.StoredProcedures = StoredProcedures(SesionBD)
        self.RepoReporte = ReporteRepository(SesionBD)
        self.RepoAuditoria = AuditoriaRepository(SesionBD)

    def ObtenerEstadisticasReservas(
        self,
        FechaInicio: Optional[date] = None,
        FechaFin: Optional[date] = None
    ) -> EstadisticasReservasResponse:
        raw = self.StoredProcedures.ObtenerEstadisticasReservas(FechaInicio, FechaFin)
        if not raw:
            return EstadisticasReservasResponse(
                total_reservas=0,
                reservas_pendientes=0,
                reservas_confirmadas=0,
                reservas_canceladas=0,
                reservas_completadas=0,
                ingresos_totales=0.0,
                promedio_reserva=0.0,
            )
        return EstadisticasReservasResponse(
            total_reservas=int(raw.get("total_reservas", 0) or 0),
            reservas_pendientes=int(raw.get("reservas_pendientes", 0) or 0),
            reservas_confirmadas=int(raw.get("reservas_confirmadas", 0) or 0),
            reservas_canceladas=int(raw.get("reservas_canceladas", 0) or 0),
            reservas_completadas=int(raw.get("reservas_completadas", 0) or 0),
            ingresos_totales=float(raw.get("ingresos_totales", 0) or 0),
            promedio_reserva=float(raw.get("promedio_reserva", 0) or 0),
        )

    def ObtenerIngresos(
        self,
        FechaInicio: Optional[date] = None,
        FechaFin: Optional[date] = None
    ) -> IngresosPorPeriodoResponse:
        data = self.RepoReporte.ObtenerIngresosPorPeriodo(FechaInicio, FechaFin)
        por_metodo = [
            IngresoPorMetodoItem(
                metodo_pago=p["metodo_pago"],
                cantidad=p["cantidad"],
                monto=p["monto"]
            )
            for p in data.get("por_metodo_pago", [])
        ]
        return IngresosPorPeriodoResponse(
            total_ingresos=data["total_ingresos"],
            cantidad_pagos=data["cantidad_pagos"],
            por_metodo_pago=por_metodo,
        )

    def ObtenerOcupacion(
        self,
        FechaInicio: date,
        FechaFin: date,
        AgruparPor: str = "habitacion"
    ) -> OcupacionResponse:
        if AgruparPor not in ("habitacion", "tipo"):
            AgruparPor = "habitacion"
        items = self.RepoReporte.ObtenerOcupacion(FechaInicio, FechaFin, AgruparPor)
        return OcupacionResponse(
            items=[OcupacionItemResponse(**x) for x in items]
        )

    def ObtenerAuditoria(
        self,
        FechaDesde: Optional[datetime] = None,
        FechaHasta: Optional[datetime] = None,
        UsuarioId: Optional[int] = None,
        Accion: Optional[str] = None,
        TablaAfectada: Optional[str] = None,
        Saltar: int = 0,
        Limite: int = 100
    ) -> List[AuditoriaLogItemResponse]:
        registros = self.RepoAuditoria.ListarConFiltros(
            FechaDesde=FechaDesde,
            FechaHasta=FechaHasta,
            UsuarioId=UsuarioId,
            Accion=Accion,
            TablaAfectada=TablaAfectada,
            Saltar=Saltar,
            Limite=Limite,
        )
        out = []
        for a in registros:
            nombre = None
            if a.usuario_id and a.usuario:
                nombre = f"{a.usuario.nombre} {a.usuario.apellido}"
            elif a.usuario_id:
                nombre = str(a.usuario_id)
            out.append(
                AuditoriaLogItemResponse(
                    id=a.id,
                    tabla_afectada=a.tabla_afectada,
                    registro_id=a.registro_id,
                    accion=a.accion.value if hasattr(a.accion, "value") else str(a.accion),
                    usuario_id=a.usuario_id,
                    usuario_nombre=nombre,
                    fecha_accion=a.fecha_accion,
                    observaciones=a.observaciones,
                )
            )
        return out

    def ObtenerRankingClientes(
        self,
        FechaInicio: Optional[date] = None,
        FechaFin: Optional[date] = None,
        Orden: str = "gastado",
        Limite: int = 50
    ) -> List[ClienteRankingItemResponse]:
        rows = self.RepoReporte.ObtenerRankingClientes(
            FechaInicio=FechaInicio,
            FechaFin=FechaFin,
            Orden=Orden,
            Limite=Limite,
        )
        return [ClienteRankingItemResponse(**r) for r in rows]

    def ObtenerDashboard(
        self,
        FechaInicio: Optional[date] = None,
        FechaFin: Optional[date] = None
    ) -> DashboardResponse:
        stats = self.ObtenerEstadisticasReservas(FechaInicio, FechaFin)
        ingresos_data = self.RepoReporte.ObtenerIngresosPorPeriodo(FechaInicio, FechaFin)
        return DashboardResponse(
            estadisticas_reservas=stats,
            total_ingresos=ingresos_data["total_ingresos"],
            cantidad_pagos=ingresos_data["cantidad_pagos"],
        )

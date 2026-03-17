"""
Servicio de reportes: orquesta repositorios y procedimientos almacenados para reportes.
"""
from sqlalchemy.orm import Session
from typing import Optional, List
from datetime import date, datetime, timedelta
from cachetools import TTLCache

from app.repositories.stored_procedures import StoredProcedures
from app.repositories.reporte_repository import ReporteRepository
from app.repositories.auditoria_repository import AuditoriaRepository
from app.schemas.reporte import (
    EstadisticasReservasResponse,
    IngresosPorPeriodoResponse,
    IngresoPorMetodoItem,
    IngresosPorTipoResponse,
    IngresosPorTipoItemResponse,
    OcupacionItemResponse,
    OcupacionResponse,
    AuditoriaLogItemResponse,
    AuditoriaListResponse,
    ClienteRankingItemResponse,
    ComparativaPeriodoItemResponse,
    ComparativaResponse,
    TendenciaPuntoResponse,
    TendenciasResponse,
    ReembolsosDisputasResponse,
    KpisHoyResponse,
    DashboardResponse,
    DashboardCompletoResponse,
)


class ServicioReportes:
    _cache_estadisticas = TTLCache(maxsize=256, ttl=600)
    _cache_dashboard = TTLCache(maxsize=128, ttl=300)

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
        cache_key = (FechaInicio.isoformat() if FechaInicio else None, FechaFin.isoformat() if FechaFin else None)
        if cache_key in self._cache_estadisticas:
            return self._cache_estadisticas[cache_key]

        raw = self.StoredProcedures.ObtenerEstadisticasReservas(FechaInicio, FechaFin)
        if not raw:
            resp = EstadisticasReservasResponse(
                total_reservas=0,
                reservas_pendientes=0,
                reservas_confirmadas=0,
                reservas_canceladas=0,
                reservas_completadas=0,
                reservas_no_show=0,
                ingresos_totales=0.0,
                promedio_reserva=0.0,
                tasa_cancelacion=0.0,
            )
            self._cache_estadisticas[cache_key] = resp
            return resp

        resp = EstadisticasReservasResponse(
            total_reservas=int(raw.get("total_reservas", 0) or 0),
            reservas_pendientes=int(raw.get("reservas_pendientes", 0) or 0),
            reservas_confirmadas=int(raw.get("reservas_confirmadas", 0) or 0),
            reservas_canceladas=int(raw.get("reservas_canceladas", 0) or 0),
            reservas_completadas=int(raw.get("reservas_completadas", 0) or 0),
            reservas_no_show=int(raw.get("reservas_no_show", 0) or 0),
            ingresos_totales=float(raw.get("ingresos_totales", 0) or 0),
            promedio_reserva=float(raw.get("promedio_reserva", 0) or 0),
            tasa_cancelacion=float(raw.get("tasa_cancelacion", 0) or 0),
        )
        self._cache_estadisticas[cache_key] = resp
        return resp

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
        total_ocupadas = sum(int(x.get("noches_ocupadas", 0) or 0) for x in items)
        total_disponibles = sum(int(x.get("noches_disponibles", 0) or 0) for x in items)
        porcentaje_global = 0.0
        if total_disponibles > 0:
            porcentaje_global = round((total_ocupadas / total_disponibles) * 100, 2)
        return OcupacionResponse(
            items=[OcupacionItemResponse(**x) for x in items],
            total_noches_ocupadas=total_ocupadas,
            total_noches_disponibles=total_disponibles,
            porcentaje_ocupacion_global=porcentaje_global,
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
    ) -> AuditoriaListResponse:
        registros = self.RepoAuditoria.ListarConFiltros(
            FechaDesde=FechaDesde,
            FechaHasta=FechaHasta,
            UsuarioId=UsuarioId,
            Accion=Accion,
            TablaAfectada=TablaAfectada,
            Saltar=Saltar,
            Limite=Limite,
        )
        total = self.RepoAuditoria.ContarConFiltros(
            FechaDesde=FechaDesde,
            FechaHasta=FechaHasta,
            UsuarioId=UsuarioId,
            Accion=Accion,
            TablaAfectada=TablaAfectada,
        )
        out = [self._mapear_auditoria_item(a) for a in registros]
        return AuditoriaListResponse(items=out, total=total)

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
        cache_key = (FechaInicio.isoformat() if FechaInicio else None, FechaFin.isoformat() if FechaFin else None)
        if cache_key in self._cache_dashboard:
            return self._cache_dashboard[cache_key]

        stats = self.ObtenerEstadisticasReservas(FechaInicio, FechaFin)
        ingresos_data = self.RepoReporte.ObtenerIngresosPorPeriodo(FechaInicio, FechaFin)
        resp = DashboardResponse(
            estadisticas_reservas=stats,
            total_ingresos=ingresos_data["total_ingresos"],
            cantidad_pagos=ingresos_data["cantidad_pagos"],
        )
        self._cache_dashboard[cache_key] = resp
        return resp

    def ObtenerIngresosPorTipo(
        self,
        FechaInicio: Optional[date] = None,
        FechaFin: Optional[date] = None
    ) -> IngresosPorTipoResponse:
        rows = self.RepoReporte.ObtenerIngresosPorTipoHabitacion(FechaInicio, FechaFin)
        return IngresosPorTipoResponse(
            items=[IngresosPorTipoItemResponse(**r) for r in rows]
        )

    def ObtenerComparativa(
        self,
        FechaInicio: Optional[date] = None,
        FechaFin: Optional[date] = None,
    ) -> ComparativaResponse:
        inicio, fin = self._normalizar_rango(FechaInicio, FechaFin)
        dias = max((fin - inicio).days + 1, 1)
        fin_anterior = inicio - timedelta(days=1)
        inicio_anterior = fin_anterior - timedelta(days=dias - 1)

        actual = self.ObtenerEstadisticasReservas(inicio, fin)
        anterior = self.ObtenerEstadisticasReservas(inicio_anterior, fin_anterior)

        return ComparativaResponse(
            periodo_actual=ComparativaPeriodoItemResponse(
                total_reservas=actual.total_reservas,
                ingresos_totales=actual.ingresos_totales,
            ),
            periodo_anterior=ComparativaPeriodoItemResponse(
                total_reservas=anterior.total_reservas,
                ingresos_totales=anterior.ingresos_totales,
            ),
            variacion_reservas_pct=self._variacion_pct(actual.total_reservas, anterior.total_reservas),
            variacion_ingresos_pct=self._variacion_pct(actual.ingresos_totales, anterior.ingresos_totales),
        )

    def ObtenerTendencias(
        self,
        Tipo: str,
        AgruparPor: str,
        FechaInicio: date,
        FechaFin: date,
    ) -> TendenciasResponse:
        rows = self.RepoReporte.ObtenerTendencias(Tipo, AgruparPor, FechaInicio, FechaFin)
        return TendenciasResponse(
            tipo=Tipo,
            agrupar_por=AgruparPor,
            puntos=[TendenciaPuntoResponse(**r) for r in rows],
        )

    def ObtenerReembolsosDisputas(
        self,
        FechaInicio: Optional[date] = None,
        FechaFin: Optional[date] = None,
    ) -> ReembolsosDisputasResponse:
        data = self.RepoReporte.ObtenerReembolsosDisputas(FechaInicio, FechaFin)
        return ReembolsosDisputasResponse(**data)

    def ObtenerKpisHoy(self) -> KpisHoyResponse:
        hoy = date.today()
        data = self.RepoReporte.ObtenerKpisHoy(hoy)
        return KpisHoyResponse(**data)

    def ObtenerDashboardCompleto(
        self,
        FechaInicio: Optional[date] = None,
        FechaFin: Optional[date] = None
    ) -> DashboardCompletoResponse:
        inicio, fin = self._normalizar_rango(FechaInicio, FechaFin)
        dashboard = self.ObtenerDashboard(inicio, fin)
        ocupacion = self.ObtenerOcupacion(inicio, fin, "habitacion")
        top_clientes = self.ObtenerRankingClientes(inicio, fin, "gastado", 5)

        auditoria = self.RepoAuditoria.ListarConFiltros(
            FechaDesde=None,
            FechaHasta=None,
            UsuarioId=None,
            Accion=None,
            TablaAfectada=None,
            Saltar=0,
            Limite=10,
        )
        ultimos = [self._mapear_auditoria_item(a) for a in auditoria]
        kpis_hoy = self.ObtenerKpisHoy()

        return DashboardCompletoResponse(
            estadisticas_reservas=dashboard.estadisticas_reservas,
            total_ingresos=dashboard.total_ingresos,
            cantidad_pagos=dashboard.cantidad_pagos,
            ocupacion_global=ocupacion.porcentaje_ocupacion_global,
            top_clientes=top_clientes,
            ultimos_eventos_auditoria=ultimos,
            kpis_hoy=kpis_hoy,
        )

    @staticmethod
    def _variacion_pct(valor_actual: float, valor_anterior: float) -> float:
        if valor_anterior == 0:
            return 100.0 if valor_actual > 0 else 0.0
        return round(((valor_actual - valor_anterior) / valor_anterior) * 100, 2)

    @staticmethod
    def _normalizar_rango(
        FechaInicio: Optional[date],
        FechaFin: Optional[date],
    ) -> tuple[date, date]:
        fin = FechaFin or date.today()
        inicio = FechaInicio or (fin - timedelta(days=29))
        if inicio > fin:
            inicio, fin = fin, inicio
        return inicio, fin

    @staticmethod
    def _mapear_auditoria_item(a) -> AuditoriaLogItemResponse:
        nombre = None
        if a.usuario_id and a.usuario:
            nombre = f"{a.usuario.nombre} {a.usuario.apellido}"
        elif a.usuario_id:
            nombre = str(a.usuario_id)
        return AuditoriaLogItemResponse(
            id=a.id,
            tabla_afectada=a.tabla_afectada,
            registro_id=a.registro_id,
            accion=a.accion.value if hasattr(a.accion, "value") else str(a.accion),
            usuario_id=a.usuario_id,
            usuario_nombre=nombre,
            fecha_accion=a.fecha_accion,
            observaciones=a.observaciones,
            resumen_cambio=a.resumen_cambio,
            campos_modificados=a.campos_modificados,
        )

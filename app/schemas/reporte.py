"""
Schemas para respuestas de reportes.
"""
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime


class EstadisticasReservasResponse(BaseModel):
    total_reservas: int
    reservas_pendientes: int
    reservas_confirmadas: int
    reservas_canceladas: int
    reservas_completadas: int
    reservas_no_show: int
    ingresos_totales: float
    promedio_reserva: float
    tasa_cancelacion: float


class IngresoPorMetodoItem(BaseModel):
    metodo_pago: str
    cantidad: int
    monto: float


class IngresosPorPeriodoResponse(BaseModel):
    total_ingresos: float
    cantidad_pagos: int
    por_metodo_pago: Optional[List[IngresoPorMetodoItem]] = None


class OcupacionItemResponse(BaseModel):
    identificador: str
    nombre: str
    noches_ocupadas: int
    ingresos: float
    noches_disponibles: Optional[int] = None
    porcentaje_ocupacion: Optional[float] = None


class OcupacionResponse(BaseModel):
    items: List[OcupacionItemResponse]
    total_noches_ocupadas: Optional[int] = None
    total_noches_disponibles: Optional[int] = None
    porcentaje_ocupacion_global: Optional[float] = None


class AuditoriaLogItemResponse(BaseModel):
    id: int
    tabla_afectada: str
    registro_id: Optional[int] = None
    accion: str
    usuario_id: Optional[int] = None
    usuario_nombre: Optional[str] = None
    fecha_accion: datetime
    observaciones: Optional[str] = None
    resumen_cambio: Optional[str] = None
    campos_modificados: Optional[List[str]] = None

    class Config:
        from_attributes = True


class ClienteRankingItemResponse(BaseModel):
    usuario_id: int
    nombre: str
    email: str
    total_reservas: int
    total_gastado: float
    ultima_reserva: Optional[datetime] = None
    promedio_por_reserva: Optional[float] = None


class AuditoriaListResponse(BaseModel):
    items: List[AuditoriaLogItemResponse]
    total: int


class IngresosPorTipoItemResponse(BaseModel):
    identificador: str
    nombre: str
    cantidad_reservas: int
    ingresos: float


class IngresosPorTipoResponse(BaseModel):
    items: List[IngresosPorTipoItemResponse]


class ComparativaPeriodoItemResponse(BaseModel):
    total_reservas: int
    ingresos_totales: float


class ComparativaResponse(BaseModel):
    periodo_actual: ComparativaPeriodoItemResponse
    periodo_anterior: ComparativaPeriodoItemResponse
    variacion_reservas_pct: float
    variacion_ingresos_pct: float


class TendenciaPuntoResponse(BaseModel):
    periodo: str
    valor: float


class TendenciasResponse(BaseModel):
    tipo: str
    agrupar_por: str
    puntos: List[TendenciaPuntoResponse]


class ReembolsosDisputasResponse(BaseModel):
    total_reembolsado: float
    cantidad_reembolsos: int
    cantidad_disputas: int
    monto_disputado: float


class KpisHoyResponse(BaseModel):
    reservas_hoy: int
    checkins_pendientes: int
    pagos_pendientes_procesar: int


class DashboardResponse(BaseModel):
    estadisticas_reservas: EstadisticasReservasResponse
    total_ingresos: float
    cantidad_pagos: int


class DashboardCompletoResponse(BaseModel):
    estadisticas_reservas: EstadisticasReservasResponse
    total_ingresos: float
    cantidad_pagos: int
    ocupacion_global: Optional[float] = None
    top_clientes: List[ClienteRankingItemResponse]
    ultimos_eventos_auditoria: List[AuditoriaLogItemResponse]
    kpis_hoy: KpisHoyResponse

"""
Schemas para respuestas de reportes.
"""
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
from decimal import Decimal


class EstadisticasReservasResponse(BaseModel):
    total_reservas: int
    reservas_pendientes: int
    reservas_confirmadas: int
    reservas_canceladas: int
    reservas_completadas: int
    ingresos_totales: float
    promedio_reserva: float


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


class OcupacionResponse(BaseModel):
    items: List[OcupacionItemResponse]


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


class DashboardResponse(BaseModel):
    estadisticas_reservas: EstadisticasReservasResponse
    total_ingresos: float
    cantidad_pagos: int

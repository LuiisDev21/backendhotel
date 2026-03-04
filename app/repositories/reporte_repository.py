"""
Repositorio de reportes: consultas agregadas para ingresos, ocupación y ranking de clientes.
"""
from sqlalchemy.orm import Session
from sqlalchemy import text, func
from typing import Optional, List, Dict, Any
from datetime import date
from decimal import Decimal

from app.models.transaccion_pago import TransaccionPago, EstadoPago, TipoTransaccion
from app.models.reserva import Reserva, EstadoReserva
from app.models.habitacion import Habitacion
from app.models.tipo_habitacion import TipoHabitacion
from app.models.usuario import Usuario


class ReporteRepository:
    def __init__(self, SesionBD: Session):
        self.SesionBD = SesionBD

    def ObtenerIngresosPorPeriodo(
        self,
        FechaInicio: Optional[date] = None,
        FechaFin: Optional[date] = None
    ) -> Dict[str, Any]:
        """Ingresos totales y por método de pago (transacciones tipo cargo completadas)."""
        q = self.SesionBD.query(
            func.coalesce(func.sum(TransaccionPago.monto), 0).label("total"),
            func.count(TransaccionPago.id).label("cantidad")
        ).filter(
            TransaccionPago.estado == EstadoPago.COMPLETADO,
            TransaccionPago.tipo == TipoTransaccion.CARGO
        )
        if FechaInicio is not None:
            q = q.filter(TransaccionPago.fecha_pago >= FechaInicio)
        if FechaFin is not None:
            q = q.filter(TransaccionPago.fecha_pago <= FechaFin)
        row = q.first()
        total = float(row.total) if row and row.total is not None else 0.0
        cantidad = row.cantidad or 0

        q2 = self.SesionBD.query(
            TransaccionPago.metodo_pago,
            func.count(TransaccionPago.id).label("cantidad"),
            func.sum(TransaccionPago.monto).label("monto")
        ).filter(
            TransaccionPago.estado == EstadoPago.COMPLETADO,
            TransaccionPago.tipo == TipoTransaccion.CARGO
        )
        if FechaInicio is not None:
            q2 = q2.filter(TransaccionPago.fecha_pago >= FechaInicio)
        if FechaFin is not None:
            q2 = q2.filter(TransaccionPago.fecha_pago <= FechaFin)
        q2 = q2.group_by(TransaccionPago.metodo_pago)
        por_metodo = [
            {
                "metodo_pago": str(r.metodo_pago.value) if hasattr(r.metodo_pago, "value") else str(r.metodo_pago),
                "cantidad": r.cantidad,
                "monto": float(r.monto) if r.monto else 0.0
            }
            for r in q2.all()
        ]
        return {"total_ingresos": total, "cantidad_pagos": cantidad, "por_metodo_pago": por_metodo}

    def ObtenerOcupacion(
        self,
        FechaInicio: date,
        FechaFin: date,
        AgruparPor: str
    ) -> List[Dict[str, Any]]:
        """Ocupación por habitación o por tipo. AgruparPor: 'habitacion' | 'tipo'."""
        if AgruparPor == "habitacion":
            sql = text("""
                SELECT
                    h.id AS id,
                    h.numero AS identificador,
                    h.numero AS nombre,
                    COALESCE(SUM(
                        (LEAST(r.fecha_salida, :f_fin)::date - GREATEST(r.fecha_entrada, :f_inicio)::date)
                    ), 0)::int AS noches_ocupadas,
                    COALESCE(SUM(r.precio_total), 0) AS ingresos
                FROM habitaciones h
                LEFT JOIN reservas r ON r.habitacion_id = h.id
                    AND r.estado != 'cancelada'
                    AND r.fecha_entrada <= :f_fin
                    AND r.fecha_salida >= :f_inicio
                GROUP BY h.id, h.numero
                ORDER BY noches_ocupadas DESC
            """)
        else:
            sql = text("""
                SELECT
                    th.id AS id,
                    th.codigo AS identificador,
                    th.nombre AS nombre,
                    COALESCE(SUM(
                        (LEAST(r.fecha_salida, :f_fin)::date - GREATEST(r.fecha_entrada, :f_inicio)::date)
                    ), 0)::int AS noches_ocupadas,
                    COALESCE(SUM(r.precio_total), 0) AS ingresos
                FROM tipos_habitacion th
                LEFT JOIN habitaciones h ON h.tipo_habitacion_id = th.id
                LEFT JOIN reservas r ON r.habitacion_id = h.id
                    AND r.estado != 'cancelada'
                    AND r.fecha_entrada <= :f_fin
                    AND r.fecha_salida >= :f_inicio
                GROUP BY th.id, th.codigo, th.nombre
                ORDER BY noches_ocupadas DESC
            """)
        result = self.SesionBD.execute(
            sql,
            {"f_inicio": FechaInicio, "f_fin": FechaFin}
        )
        return [
            {
                "identificador": str(row.identificador),
                "nombre": str(row.nombre),
                "noches_ocupadas": int(row.noches_ocupadas or 0),
                "ingresos": float(row.ingresos or 0)
            }
            for row in result
        ]

    def ObtenerRankingClientes(
        self,
        FechaInicio: Optional[date] = None,
        FechaFin: Optional[date] = None,
        Orden: str = "gastado",
        Limite: int = 50
    ) -> List[Dict[str, Any]]:
        """Ranking de clientes por total reservas o por total gastado (reservas no canceladas)."""
        q = (
            self.SesionBD.query(
                Usuario.id.label("usuario_id"),
                func.concat(Usuario.nombre, " ", Usuario.apellido).label("nombre"),
                Usuario.email,
                func.count(Reserva.id).label("total_reservas"),
                func.coalesce(func.sum(Reserva.precio_total), 0).label("total_gastado")
            )
            .join(Reserva, Reserva.usuario_id == Usuario.id)
            .filter(Reserva.estado != EstadoReserva.CANCELADA)
        )
        if FechaInicio is not None:
            q = q.filter(Reserva.fecha_creacion >= FechaInicio)
        if FechaFin is not None:
            q = q.filter(Reserva.fecha_creacion <= FechaFin)
        q = q.group_by(Usuario.id, Usuario.nombre, Usuario.apellido, Usuario.email)
        if Orden == "reservas":
            q = q.order_by(func.count(Reserva.id).desc())
        else:
            q = q.order_by(func.sum(Reserva.precio_total).desc())
        q = q.limit(Limite)
        rows = q.all()
        return [
            {
                "usuario_id": r.usuario_id,
                "nombre": r.nombre,
                "email": r.email,
                "total_reservas": r.total_reservas,
                "total_gastado": float(r.total_gastado or 0)
            }
            for r in rows
        ]

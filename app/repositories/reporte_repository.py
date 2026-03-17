"""
Repositorio de reportes: consultas agregadas para ingresos, ocupación y ranking de clientes.
"""
from sqlalchemy.orm import Session
from sqlalchemy import text, func
from typing import Optional, List, Dict, Any
from datetime import date
import json
import time

from app.models.transaccion_pago import TransaccionPago, EstadoPago, TipoTransaccion
from app.models.reserva import Reserva, EstadoReserva
from app.models.habitacion import Habitacion
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
        periodo_noches = max((FechaFin - FechaInicio).days, 1)
        if AgruparPor == "habitacion":
            sql = text("""
                SELECT
                    h.id AS id,
                    h.numero AS identificador,
                    h.numero AS nombre,
                    1::int AS total_habitaciones,
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
                    COUNT(DISTINCT h.id)::int AS total_habitaciones,
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
            self._mapear_ocupacion_row(row, periodo_noches)
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
                func.coalesce(func.sum(Reserva.precio_total), 0).label("total_gastado"),
                func.max(Reserva.fecha_creacion).label("ultima_reserva"),
                func.coalesce(func.avg(Reserva.precio_total), 0).label("promedio_por_reserva"),
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
                "total_gastado": float(r.total_gastado or 0),
                "ultima_reserva": r.ultima_reserva,
                "promedio_por_reserva": float(r.promedio_por_reserva or 0),
            }
            for r in rows
        ]

    def ObtenerIngresosPorTipoHabitacion(
        self,
        FechaInicio: Optional[date] = None,
        FechaFin: Optional[date] = None,
    ) -> List[Dict[str, Any]]:
        # region agent log
        self._debug_log(
            run_id="run1",
            hypothesis_id="H1",
            location="app/repositories/reporte_repository.py:169",
            message="entry ObtenerIngresosPorTipoHabitacion",
            data={
                "fecha_inicio": str(FechaInicio) if FechaInicio else None,
                "fecha_fin": str(FechaFin) if FechaFin else None,
            },
        )
        # endregion
        sql = text("""
            SELECT
                th.codigo AS identificador,
                th.nombre AS nombre,
                COUNT(r.id)::int AS cantidad_reservas,
                COALESCE(SUM(r.precio_total), 0) AS ingresos
            FROM tipos_habitacion th
            LEFT JOIN habitaciones h ON h.tipo_habitacion_id = th.id
            LEFT JOIN reservas r ON r.habitacion_id = h.id
                AND r.estado != 'cancelada'
                AND (:fecha_inicio IS NULL OR r.fecha_creacion >= CAST(:fecha_inicio AS TIMESTAMPTZ))
                AND (:fecha_fin IS NULL OR r.fecha_creacion <= CAST(:fecha_fin AS TIMESTAMPTZ) + INTERVAL '1 day')
            GROUP BY th.id, th.codigo, th.nombre
            ORDER BY ingresos DESC
        """)
        params = {"fecha_inicio": FechaInicio, "fecha_fin": FechaFin}
        # region agent log
        self._debug_log(
            run_id="run1",
            hypothesis_id="H2",
            location="app/repositories/reporte_repository.py:196",
            message="before execute ObtenerIngresosPorTipoHabitacion",
            data={
                "has_double_colon_bind": ":fecha_inicio::" in str(sql),
                "params_keys": list(params.keys()),
                "sql_preview": str(sql)[:220],
            },
        )
        # endregion
        try:
            rows = self.SesionBD.execute(sql, params)
        except Exception as exc:
            # region agent log
            self._debug_log(
                run_id="run1",
                hypothesis_id="H1",
                location="app/repositories/reporte_repository.py:210",
                message="execute error ObtenerIngresosPorTipoHabitacion",
                data={"error_type": type(exc).__name__, "error": str(exc)[:400]},
            )
            # endregion
            raise
        return [
            {
                "identificador": str(r.identificador),
                "nombre": str(r.nombre),
                "cantidad_reservas": int(r.cantidad_reservas or 0),
                "ingresos": float(r.ingresos or 0),
            }
            for r in rows
        ]

    def ObtenerTendencias(
        self,
        Tipo: str,
        AgruparPor: str,
        FechaInicio: date,
        FechaFin: date,
    ) -> List[Dict[str, Any]]:
        # region agent log
        self._debug_log(
            run_id="run1",
            hypothesis_id="H3",
            location="app/repositories/reporte_repository.py:228",
            message="entry ObtenerTendencias",
            data={
                "tipo": Tipo,
                "agrupar_por": AgruparPor,
                "fecha_inicio": str(FechaInicio),
                "fecha_fin": str(FechaFin),
            },
        )
        # endregion
        unidad = "day" if AgruparPor == "dia" else "week"
        if Tipo == "ingresos":
            sql = text(f"""
                SELECT
                    DATE_TRUNC('{unidad}', tp.fecha_pago) AS periodo,
                    COALESCE(SUM(tp.monto), 0) AS valor
                FROM transacciones_pago tp
                WHERE tp.estado = 'completado'
                  AND tp.tipo = 'cargo'
                  AND tp.fecha_pago >= CAST(:fecha_inicio AS TIMESTAMPTZ)
                  AND tp.fecha_pago < CAST(:fecha_fin AS TIMESTAMPTZ) + INTERVAL '1 day'
                GROUP BY DATE_TRUNC('{unidad}', tp.fecha_pago)
                ORDER BY periodo ASC
            """)
        else:
            sql = text(f"""
                SELECT
                    DATE_TRUNC('{unidad}', r.fecha_creacion) AS periodo,
                    COUNT(r.id)::numeric AS valor
                FROM reservas r
                WHERE r.fecha_creacion >= CAST(:fecha_inicio AS TIMESTAMPTZ)
                  AND r.fecha_creacion < CAST(:fecha_fin AS TIMESTAMPTZ) + INTERVAL '1 day'
                GROUP BY DATE_TRUNC('{unidad}', r.fecha_creacion)
                ORDER BY periodo ASC
            """)
        params = {"fecha_inicio": FechaInicio, "fecha_fin": FechaFin}
        # region agent log
        self._debug_log(
            run_id="run1",
            hypothesis_id="H4",
            location="app/repositories/reporte_repository.py:273",
            message="before execute ObtenerTendencias",
            data={
                "unidad": unidad,
                "has_double_colon_bind": ":fecha_inicio::" in str(sql),
                "params_keys": list(params.keys()),
                "sql_preview": str(sql)[:220],
            },
        )
        # endregion
        try:
            rows = self.SesionBD.execute(sql, params)
        except Exception as exc:
            # region agent log
            self._debug_log(
                run_id="run1",
                hypothesis_id="H4",
                location="app/repositories/reporte_repository.py:288",
                message="execute error ObtenerTendencias",
                data={"error_type": type(exc).__name__, "error": str(exc)[:400]},
            )
            # endregion
            raise
        return [
            {
                "periodo": row.periodo.isoformat() if row.periodo else "",
                "valor": float(row.valor or 0),
            }
            for row in rows
        ]

    def ObtenerReembolsosDisputas(
        self,
        FechaInicio: Optional[date] = None,
        FechaFin: Optional[date] = None,
    ) -> Dict[str, Any]:
        q_reembolso = self.SesionBD.query(
            func.coalesce(func.sum(TransaccionPago.monto), 0).label("total"),
            func.count(TransaccionPago.id).label("cantidad"),
        ).filter(
            TransaccionPago.tipo == TipoTransaccion.REEMBOLSO,
            TransaccionPago.estado == EstadoPago.COMPLETADO,
        )
        if FechaInicio is not None:
            q_reembolso = q_reembolso.filter(TransaccionPago.fecha_pago >= FechaInicio)
        if FechaFin is not None:
            q_reembolso = q_reembolso.filter(TransaccionPago.fecha_pago <= FechaFin)
        row_reembolso = q_reembolso.first()

        q_disputa = self.SesionBD.query(
            func.count(TransaccionPago.id).label("cantidad_disputas"),
            func.coalesce(func.sum(TransaccionPago.monto), 0).label("monto_disputado"),
        ).filter(TransaccionPago.estado == EstadoPago.DISPUTADO)
        if FechaInicio is not None:
            q_disputa = q_disputa.filter(TransaccionPago.fecha_creacion >= FechaInicio)
        if FechaFin is not None:
            q_disputa = q_disputa.filter(TransaccionPago.fecha_creacion <= FechaFin)
        row_disputa = q_disputa.first()

        return {
            "total_reembolsado": abs(float(row_reembolso.total or 0)),
            "cantidad_reembolsos": int(row_reembolso.cantidad or 0),
            "cantidad_disputas": int(row_disputa.cantidad_disputas or 0),
            "monto_disputado": abs(float(row_disputa.monto_disputado or 0)),
        }

    def ObtenerKpisHoy(self, Hoy: date) -> Dict[str, int]:
        reservas_hoy = self.SesionBD.query(func.count(Reserva.id)).filter(
            func.date(Reserva.fecha_creacion) == Hoy
        ).scalar() or 0

        checkins_pendientes = self.SesionBD.query(func.count(Reserva.id)).filter(
            Reserva.fecha_entrada == Hoy,
            Reserva.estado.in_([EstadoReserva.PENDIENTE, EstadoReserva.CONFIRMADA]),
        ).scalar() or 0

        pagos_pendientes = self.SesionBD.query(func.count(TransaccionPago.id)).filter(
            TransaccionPago.estado.in_([EstadoPago.PENDIENTE, EstadoPago.EN_PROCESO]),
        ).scalar() or 0

        return {
            "reservas_hoy": int(reservas_hoy),
            "checkins_pendientes": int(checkins_pendientes),
            "pagos_pendientes_procesar": int(pagos_pendientes),
        }

    @staticmethod
    def _mapear_ocupacion_row(row: Any, periodo_noches: int) -> Dict[str, Any]:
        total_habitaciones = int(row.total_habitaciones or 0)
        noches_disponibles = total_habitaciones * periodo_noches
        noches_ocupadas = int(row.noches_ocupadas or 0)
        porcentaje = 0.0
        if noches_disponibles > 0:
            porcentaje = round((noches_ocupadas / noches_disponibles) * 100, 2)
        return {
            "identificador": str(row.identificador),
            "nombre": str(row.nombre),
            "noches_ocupadas": noches_ocupadas,
            "ingresos": float(row.ingresos or 0),
            "noches_disponibles": noches_disponibles,
            "porcentaje_ocupacion": porcentaje,
        }

    @staticmethod
    def _debug_log(run_id: str, hypothesis_id: str, location: str, message: str, data: Dict[str, Any]) -> None:
        try:
            payload = {
                "sessionId": "8ce88b",
                "runId": run_id,
                "hypothesisId": hypothesis_id,
                "location": location,
                "message": message,
                "data": data,
                "timestamp": int(time.time() * 1000),
            }
            with open("/Users/luis/Desktop/backendhotel/.cursor/debug-8ce88b.log", "a", encoding="utf-8") as f:
                f.write(json.dumps(payload, default=str) + "\n")
        except Exception:
            pass

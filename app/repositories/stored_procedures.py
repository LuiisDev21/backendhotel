"""
Módulo para ejecutar procedimientos almacenados de PostgreSQL.
"""
from sqlalchemy.orm import Session
from sqlalchemy import text
from typing import Optional, List, Dict, Any
from datetime import date
from decimal import Decimal
from app.core.auditoria_helper import registrar_auditoria
from app.models.auditoria import AccionAuditoria


class StoredProcedures:
    def __init__(self, SesionBD: Session):
        self.SesionBD = SesionBD

    def CrearHabitacion(
        self,
        Numero: str,
        TipoHabitacionId: int,
        Descripcion: Optional[str],
        Capacidad: int,
        PrecioPorNoche: Decimal,
        Estado: str = "disponible",
        ImagenUrl: Optional[str] = None,
        Piso: Optional[int] = None,
        Caracteristicas: Optional[dict] = None,
        UsuarioId: Optional[int] = None
    ) -> Dict[str, Any]:
        """Ejecuta sp_crear_habitacion (database_final: estado, piso, caracteristicas)."""
        query = text("""
            SELECT * FROM sp_crear_habitacion(
                :numero,
                :tipo_habitacion_id,
                :descripcion,
                :capacidad,
                :precio_por_noche,
                :estado,
                :imagen_url,
                :piso,
                :caracteristicas,
                :usuario_id
            )
        """)
        import json
        params = {
            "numero": Numero,
            "tipo_habitacion_id": TipoHabitacionId,
            "descripcion": Descripcion,
            "capacidad": Capacidad,
            "precio_por_noche": float(PrecioPorNoche),
            "estado": Estado,
            "imagen_url": ImagenUrl,
            "piso": Piso,
            "caracteristicas": json.dumps(Caracteristicas) if Caracteristicas else None,
            "usuario_id": UsuarioId
        }
        result = self.SesionBD.execute(query, params)
        row = result.fetchone()
        self.SesionBD.commit()
        if row:
            return dict(row._mapping)
        raise Exception("No se pudo crear la habitación")

    def BuscarHabitacionesDisponibles(
        self,
        FechaEntrada: date,
        FechaSalida: date,
        Capacidad: Optional[int] = None,
        TipoHabitacionId: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        query = text("""
            SELECT * FROM sp_buscar_habitaciones_disponibles(
                :fecha_entrada,
                :fecha_salida,
                :capacidad,
                :tipo_habitacion_id
            )
        """)
        result = self.SesionBD.execute(
            query,
            {
                "fecha_entrada": FechaEntrada,
                "fecha_salida": FechaSalida,
                "capacidad": Capacidad,
                "tipo_habitacion_id": TipoHabitacionId
            }
        )
        rows = result.fetchall()
        return [dict(row._mapping) for row in rows]

    def CrearReserva(
        self,
        UsuarioId: int,
        HabitacionId: int,
        FechaEntrada: date,
        FechaSalida: date,
        NumeroHuespedes: int,
        Notas: Optional[str] = None,
        UsuarioAuditoriaId: Optional[int] = None,
        CanalReserva: str = "web",
        PoliticaCancelacionId: Optional[int] = None
    ) -> Dict[str, Any]:
        """Ejecuta sp_crear_reserva (id BIGINT, canal_reserva, politica_cancelacion_id)."""
        query = text("""
            SELECT * FROM sp_crear_reserva(
                :usuario_id,
                :habitacion_id,
                :fecha_entrada,
                :fecha_salida,
                :numero_huespedes,
                :notas,
                :usuario_auditoria_id,
                :canal_reserva,
                :politica_cancelacion_id
            )
        """)
        result = self.SesionBD.execute(
            query,
            {
                "usuario_id": UsuarioId,
                "habitacion_id": HabitacionId,
                "fecha_entrada": FechaEntrada,
                "fecha_salida": FechaSalida,
                "numero_huespedes": NumeroHuespedes,
                "notas": Notas,
                "usuario_auditoria_id": UsuarioAuditoriaId,
                "canal_reserva": CanalReserva,
                "politica_cancelacion_id": PoliticaCancelacionId
            }
        )
        self.SesionBD.commit()
        row = result.fetchone()
        if row:
            return dict(row._mapping)
        raise Exception("No se pudo crear la reserva")

    def ProcesarPago(
        self,
        ReservaId: int,
        Monto: Decimal,
        MetodoPago: str,
        Tipo: str = "cargo",
        NumeroTransaccion: Optional[str] = None,
        ReferenciaExterna: Optional[str] = None,
        PasarelaPago: Optional[str] = None,
        UsuarioId: Optional[int] = None
    ) -> Dict[str, Any]:
        """Ejecuta sp_procesar_pago (transacciones_pago, tipo, referencia_externa, pasarela)."""
        query = text("""
            SELECT * FROM sp_procesar_pago(
                :reserva_id,
                :monto,
                :metodo_pago,
                :tipo,
                :numero_transaccion,
                :referencia_externa,
                :pasarela_pago,
                :usuario_id
            )
        """)
        params = {
            "reserva_id": ReservaId,
            "monto": float(Monto),
            "metodo_pago": MetodoPago,
            "tipo": Tipo,
            "numero_transaccion": NumeroTransaccion,
            "referencia_externa": ReferenciaExterna,
            "pasarela_pago": PasarelaPago,
            "usuario_id": UsuarioId
        }
        try:
            result = self.SesionBD.execute(query, params)
            self.SesionBD.commit()
            row = result.fetchone()
            if row:
                return dict(row._mapping)
            raise Exception("No se pudo procesar el pago")
        except Exception as e:
            self.SesionBD.rollback()
            observacion = f"reserva_id={ReservaId}, monto={Monto}, metodo_pago={MetodoPago}, tipo={Tipo}: {str(e)[:200]}"
            msg_corto = str(e)[:80] if str(e) else "Error en SP"
            registrar_auditoria(
                SesionBD=self.SesionBD,
                TablaAfectada="transacciones_pago",
                Accion=AccionAuditoria.PAGO_FAILED,
                RegistroId=None,
                UsuarioId=UsuarioId,
                Observaciones=observacion,
                ResumenCambio=f"Pago fallido: {msg_corto}",
            )
            raise

    def ObtenerEstadisticasReservas(
        self,
        FechaInicio: Optional[date] = None,
        FechaFin: Optional[date] = None
    ) -> Dict[str, Any]:
        query = text("""
            SELECT * FROM sp_obtener_estadisticas_reservas(
                :fecha_inicio,
                :fecha_fin
            )
        """)
        result = self.SesionBD.execute(
            query,
            {"fecha_inicio": FechaInicio, "fecha_fin": FechaFin}
        )
        row = result.fetchone()
        if row:
            return dict(row._mapping)
        return {}

"""
Módulo para ejecutar procedimientos almacenados de PostgreSQL.
Este módulo proporciona funciones para llamar a los procedimientos almacenados
de manera eficiente y tipada.
"""
from sqlalchemy.orm import Session
from sqlalchemy import text
from typing import Optional, List, Dict, Any
from datetime import date
from decimal import Decimal
from app.models.habitacion import Habitacion
from app.models.reserva import Reserva
from app.models.pago import Pago


class StoredProcedures:
    """Clase para ejecutar procedimientos almacenados."""
    
    def __init__(self, SesionBD: Session):
        self.SesionBD = SesionBD

    def CrearHabitacion(
        self,
        Numero: str,
        TipoHabitacionId: int,
        Descripcion: Optional[str],
        Capacidad: int,
        PrecioPorNoche: Decimal,
        Disponible: bool = True,
        ImagenUrl: Optional[str] = None,
        UsuarioId: Optional[int] = None
    ) -> Dict[str, Any]:
        """Ejecuta el procedimiento almacenado sp_crear_habitacion."""
        query = text("""
            SELECT * FROM sp_crear_habitacion(
                :numero,
                :tipo_habitacion_id,
                :descripcion,
                :capacidad,
                :precio_por_noche,
                :disponible,
                :imagen_url,
                :usuario_id
            )
        """)
        
        result = self.SesionBD.execute(
            query,
            {
                "numero": Numero,
                "tipo_habitacion_id": TipoHabitacionId,
                "descripcion": Descripcion,
                "capacidad": Capacidad,
                "precio_por_noche": float(PrecioPorNoche),
                "disponible": Disponible,
                "imagen_url": ImagenUrl,
                "usuario_id": UsuarioId
            }
        )
        self.SesionBD.commit()
        
        row = result.fetchone()
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
        """Ejecuta el procedimiento almacenado sp_buscar_habitaciones_disponibles."""
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
        UsuarioAuditoriaId: Optional[int] = None
    ) -> Dict[str, Any]:
        """Ejecuta el procedimiento almacenado sp_crear_reserva."""
        query = text("""
            SELECT * FROM sp_crear_reserva(
                :usuario_id,
                :habitacion_id,
                :fecha_entrada,
                :fecha_salida,
                :numero_huespedes,
                :notas,
                :usuario_auditoria_id
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
                "usuario_auditoria_id": UsuarioAuditoriaId
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
        NumeroTransaccion: Optional[str] = None,
        UsuarioId: Optional[int] = None
    ) -> Dict[str, Any]:
        """Ejecuta el procedimiento almacenado sp_procesar_pago."""
        query = text("""
            SELECT * FROM sp_procesar_pago(
                :reserva_id,
                :monto,
                :metodo_pago,
                :numero_transaccion,
                :usuario_id
            )
        """)
        
        result = self.SesionBD.execute(
            query,
            {
                "reserva_id": ReservaId,
                "monto": float(Monto),
                "metodo_pago": MetodoPago,
                "numero_transaccion": NumeroTransaccion,
                "usuario_id": UsuarioId
            }
        )
        self.SesionBD.commit()
        
        row = result.fetchone()
        if row:
            return dict(row._mapping)
        raise Exception("No se pudo procesar el pago")

    def ObtenerEstadisticasReservas(
        self,
        FechaInicio: Optional[date] = None,
        FechaFin: Optional[date] = None
    ) -> Dict[str, Any]:
        """Ejecuta el procedimiento almacenado sp_obtener_estadisticas_reservas."""
        query = text("""
            SELECT * FROM sp_obtener_estadisticas_reservas(
                :fecha_inicio,
                :fecha_fin
            )
        """)
        
        result = self.SesionBD.execute(
            query,
            {
                "fecha_inicio": FechaInicio,
                "fecha_fin": FechaFin
            }
        )
        
        row = result.fetchone()
        if row:
            return dict(row._mapping)
        return {}

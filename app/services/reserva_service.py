""" 
Servicio de Reservas, se define el servicio de reservas con SQLAlchemy.
- CalcularPrecioTotal: Calcula el precio total de una reserva.
- CrearReserva: Crea una nueva reserva.
- ObtenerReserva: Obtiene una reserva por su ID.
- ListarReservasUsuario: Lista todas las reservas de un usuario.
- ListarTodasReservas: Lista todas las reservas.
- ActualizarReserva: Actualiza una reserva existente.
- CancelarReserva: Cancela una reserva existente.
"""
from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from datetime import date, timedelta, datetime, timezone
from decimal import Decimal
from typing import List, Optional
import uuid
from app.models.reserva import Reserva, EstadoReserva
from app.models.habitacion import Habitacion
from app.models.transaccion_pago import TransaccionPago, TipoTransaccion, EstadoPago, MetodoPago
from app.repositories.reserva_repository import ReservaRepository
from app.repositories.habitacion_repository import HabitacionRepository
from app.repositories.politica_cancelacion_repository import PoliticaCancelacionRepository
from app.repositories.transaccion_pago_repository import TransaccionPagoRepository
from app.schemas.reserva import ReservaCreate, ReservaUpdate
from app.core.auditoria_helper import registrar_auditoria, convertir_modelo_a_dict
from app.models.auditoria import AccionAuditoria


class ServicioReserva:
    def __init__(self, SesionBD: Session, UsuarioId: Optional[int] = None):
        self.Repositorio = ReservaRepository(SesionBD)
        self.RepositorioHabitacion = HabitacionRepository(SesionBD)
        self.RepoPolitica = PoliticaCancelacionRepository(SesionBD)
        self.RepoTransaccion = TransaccionPagoRepository(SesionBD)
        self.SesionBD = SesionBD
        self.UsuarioId = UsuarioId

    def CalcularPrecioTotal(
        self,
        Habitacion: Habitacion,
        FechaEntrada: date,
        FechaSalida: date
        ) -> Decimal:
        NumeroNoches = (FechaSalida - FechaEntrada).days
        if NumeroNoches <= 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="La fecha de salida debe ser posterior a la fecha de entrada"
            )
        return Decimal(str(Habitacion.precio_por_noche)) * Decimal(str(NumeroNoches))

    def CrearReserva(
        self,
        IdUsuario: int,
        DatosReserva: ReservaCreate
        ) -> Reserva:
        HabitacionEncontrada = self.RepositorioHabitacion.ObtenerPorId(DatosReserva.habitacion_id)
        if not HabitacionEncontrada:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Habitacion no encontrada"
            )
        
        if getattr(HabitacionEncontrada, "estado", "disponible") != "disponible":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="La habitación no está disponible"
            )
        
        if DatosReserva.numero_huespedes > HabitacionEncontrada.capacidad:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"La habitacion solo puede alojar {HabitacionEncontrada.capacidad} huéspedes"
            )
        
        HabitacionesDisponibles = self.RepositorioHabitacion.BuscarDisponibles(
            DatosReserva.fecha_entrada,
            DatosReserva.fecha_salida
        )
        
        if HabitacionEncontrada not in HabitacionesDisponibles:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="La habitacion no esta disponible en las fechas seleccionadas"
            )
        
        # Política de cancelación: se toma de la habitación (definida por admin), no del cliente
        politica_id = getattr(HabitacionEncontrada, "politica_cancelacion_id", None)
        # El SP calcula precio_total y precio_por_noche_snapshot; se requieren valores dummy para el modelo
        ReservaNueva = Reserva(
            usuario_id=IdUsuario,
            habitacion_id=DatosReserva.habitacion_id,
            fecha_entrada=DatosReserva.fecha_entrada,
            fecha_salida=DatosReserva.fecha_salida,
            numero_huespedes=DatosReserva.numero_huespedes,
            precio_total=Decimal("0"),
            precio_por_noche_snapshot=Decimal("0"),
            codigo_reserva="",
            notas=DatosReserva.notas,
            estado=EstadoReserva.PENDIENTE,
            canal_reserva=getattr(DatosReserva, "canal_reserva", None) or "web",
            politica_cancelacion_id=politica_id,
        )
        return self.Repositorio.Crear(
            ReservaNueva,
            UsuarioAuditoriaId=self.UsuarioId,
            CanalReserva=getattr(DatosReserva, "canal_reserva", None) or "web"
        )

    def ObtenerReserva(self, IdReserva: int) -> Reserva:
        ReservaEncontrada = self.Repositorio.ObtenerPorId(IdReserva)
        if not ReservaEncontrada:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Reserva no encontrada"
            )
        return ReservaEncontrada

    def ObtenerHistorialEstados(self, IdReserva: int) -> List:
        return self.Repositorio.ObtenerHistorialEstados(IdReserva)

    def ListarReservasUsuario(
        self,
        IdUsuario: int,
        Saltar: int = 0,
        Limite: int = 100
    ) -> List[Reserva]:
        return self.Repositorio.ObtenerPorUsuario(IdUsuario, Saltar=Saltar, Limite=Limite)

    def ListarTodasReservas(self, Saltar: int = 0, Limite: int = 100) -> List[Reserva]:
        return self.Repositorio.ObtenerTodas(Saltar=Saltar, Limite=Limite)

    def ActualizarReserva(
        self,
        IdReserva: int,
        DatosReserva: ReservaUpdate
    ) -> Reserva:
        ReservaEncontrada = self.ObtenerReserva(IdReserva)
        DatosActualizacion = DatosReserva.model_dump(exclude_unset=True)

        # Validaciones de cambio de estado
        if "estado" in DatosActualizacion:
            nuevo_estado = DatosActualizacion["estado"]
            if nuevo_estado == EstadoReserva.NO_SHOW:
                if ReservaEncontrada.estado != EstadoReserva.CONFIRMADA:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail="Solo se puede marcar no-show en reservas confirmadas"
                    )
                if ReservaEncontrada.fecha_entrada >= date.today():
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail="Solo se puede marcar no-show cuando la fecha de entrada ya pasó"
                    )
            elif nuevo_estado == EstadoReserva.COMPLETADA:
                if ReservaEncontrada.estado not in (EstadoReserva.CONFIRMADA, EstadoReserva.PENDIENTE):
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail="Solo se puede marcar completada en reservas confirmadas o pendientes"
                    )

        if "fecha_entrada" in DatosActualizacion or "fecha_salida" in DatosActualizacion:
            FechaEntrada = DatosActualizacion.get("fecha_entrada", ReservaEncontrada.fecha_entrada)
            FechaSalida = DatosActualizacion.get("fecha_salida", ReservaEncontrada.fecha_salida)
            
            HabitacionEncontrada = self.RepositorioHabitacion.ObtenerPorId(ReservaEncontrada.habitacion_id)
            HabitacionesDisponibles = self.RepositorioHabitacion.BuscarDisponibles(FechaEntrada, FechaSalida)
            
            if HabitacionEncontrada not in HabitacionesDisponibles:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="La habitacion no esta disponible en las nuevas fechas"
                )
            
            ReservaEncontrada.precio_total = self.CalcularPrecioTotal(HabitacionEncontrada, FechaEntrada, FechaSalida)
        
        DatosAnteriores = convertir_modelo_a_dict(ReservaEncontrada)
        
        for Campo, Valor in DatosActualizacion.items():
            setattr(ReservaEncontrada, Campo, Valor)
        
        ReservaActualizada = self.Repositorio.Actualizar(ReservaEncontrada)
        
        # Registrar auditoría
        registrar_auditoria(
            SesionBD=self.SesionBD,
            TablaAfectada="reservas",
            Accion=AccionAuditoria.UPDATE,
            RegistroId=IdReserva,
            UsuarioId=self.UsuarioId,
            DatosAnteriores=DatosAnteriores,
            DatosNuevos=convertir_modelo_a_dict(ReservaActualizada)
        )
        
        return ReservaActualizada

    def CancelarReserva(self, IdReserva: int) -> Reserva:
        ReservaEncontrada = self.ObtenerReserva(IdReserva)
        if ReservaEncontrada.estado == EstadoReserva.CANCELADA:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="La reserva ya esta cancelada"
            )

        # Aplicar penalización según política de cancelación solo si el cliente ya pagó (reserva confirmada)
        if (
            ReservaEncontrada.estado == EstadoReserva.CONFIRMADA
            and ReservaEncontrada.politica_cancelacion_id
        ):
            politica = self.RepoPolitica.ObtenerPorId(ReservaEncontrada.politica_cancelacion_id)
            if politica and float(politica.porcentaje_penalizacion or 0) > 0:
                hoy = date.today()
                fecha_entrada = ReservaEncontrada.fecha_entrada
                # Horas aproximadas hasta el check-in (medianoche del día de entrada)
                horas_hasta_entrada = (fecha_entrada - hoy).days * 24
                # Si cancelamos con menos de horas_anticipacion antes del check-in, aplicamos penalización
                if horas_hasta_entrada < politica.horas_anticipacion:
                    monto_penalizacion = (Decimal(str(politica.porcentaje_penalizacion)) / Decimal("100")) * ReservaEncontrada.precio_total
                    if monto_penalizacion > 0:
                        transaccion_penalizacion = TransaccionPago(
                            reserva_id=IdReserva,
                            tipo=TipoTransaccion.PENALIZACION,
                            monto=monto_penalizacion,
                            metodo_pago=MetodoPago.EFECTIVO,
                            estado=EstadoPago.COMPLETADO,
                            numero_transaccion=str(uuid.uuid4()),
                            notas="Penalización por cancelación fuera de plazo",
                            procesado_por=self.UsuarioId,
                            fecha_pago=datetime.now(timezone.utc),
                        )
                        self.RepoTransaccion.Crear(transaccion_penalizacion)
                        registrar_auditoria(
                            SesionBD=self.SesionBD,
                            TablaAfectada="transacciones_pago",
                            Accion=AccionAuditoria.CREATE,
                            RegistroId=transaccion_penalizacion.id,
                            UsuarioId=self.UsuarioId,
                            DatosNuevos=convertir_modelo_a_dict(transaccion_penalizacion),
                            Observaciones="Penalización por cancelación"
                        )

        DatosAnteriores = convertir_modelo_a_dict(ReservaEncontrada)
        ReservaEncontrada.estado = EstadoReserva.CANCELADA
        ReservaCancelada = self.Repositorio.Actualizar(ReservaEncontrada)

        # Registrar auditoría
        registrar_auditoria(
            SesionBD=self.SesionBD,
            TablaAfectada="reservas",
            Accion=AccionAuditoria.RESERVA_CANCEL,
            RegistroId=IdReserva,
            UsuarioId=self.UsuarioId,
            DatosAnteriores=DatosAnteriores,
            DatosNuevos=convertir_modelo_a_dict(ReservaCancelada),
            Observaciones="Reserva cancelada"
        )

        return ReservaCancelada

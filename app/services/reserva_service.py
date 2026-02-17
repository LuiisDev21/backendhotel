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
from datetime import date, timedelta
from decimal import Decimal
from typing import List, Optional
from app.models.reserva import Reserva, EstadoReserva
from app.models.habitacion import Habitacion
from app.repositories.reserva_repository import ReservaRepository
from app.repositories.habitacion_repository import HabitacionRepository
from app.schemas.reserva import ReservaCreate, ReservaUpdate
from app.core.auditoria_helper import registrar_auditoria, convertir_modelo_a_dict
from app.models.auditoria import AccionAuditoria


class ServicioReserva:
    def __init__(self, SesionBD: Session, UsuarioId: Optional[int] = None):
        self.Repositorio = ReservaRepository(SesionBD)
        self.RepositorioHabitacion = HabitacionRepository(SesionBD)
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
        
        if not HabitacionEncontrada.disponible:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="La habitación no esta disponible"
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
        
        PrecioTotal = self.CalcularPrecioTotal(
            HabitacionEncontrada,
            DatosReserva.fecha_entrada,
            DatosReserva.fecha_salida
        )
        
        # El procedimiento almacenado valida todo y calcula el precio automáticamente
        ReservaNueva = Reserva(
            usuario_id=IdUsuario,
            habitacion_id=DatosReserva.habitacion_id,
            fecha_entrada=DatosReserva.fecha_entrada,
            fecha_salida=DatosReserva.fecha_salida,
            numero_huespedes=DatosReserva.numero_huespedes,
            precio_total=PrecioTotal,  # Se recalcula en el procedimiento almacenado
            notas=DatosReserva.notas,
            estado=EstadoReserva.PENDIENTE
        )
        
        # Usar procedimiento almacenado que valida y crea la reserva
        # La auditoría se registra automáticamente en el procedimiento almacenado
        return self.Repositorio.Crear(ReservaNueva, UsuarioAuditoriaId=self.UsuarioId)

    def ObtenerReserva(self, IdReserva: int) -> Reserva:
        ReservaEncontrada = self.Repositorio.ObtenerPorId(IdReserva)
        if not ReservaEncontrada:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Reserva no encontrada"
            )
        return ReservaEncontrada

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

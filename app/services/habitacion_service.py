""" 
Servicio de Habitaciones, se define el servicio de la habitacion con SQLAlchemy.
- CrearHabitacion: Crea una nueva habitación usando procedimiento almacenado.
- ObtenerHabitacion: Obtiene una habitación por su ID.
- ListarHabitaciones: Lista todas las habitaciones.
- BuscarDisponibles: Busca las habitaciones disponibles usando procedimiento almacenado.
- ActualizarHabitacion: Actualiza una habitación existente.
- EliminarHabitacion: Elimina una habitación existente.
"""
from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from datetime import date
from typing import Optional, List
from app.models.habitacion import Habitacion
from app.models.reserva import Reserva, EstadoReserva
from app.models.transaccion_pago import TransaccionPago
from app.repositories.habitacion_repository import HabitacionRepository
from app.repositories.tipo_habitacion_repository import TipoHabitacionRepository
from app.schemas.habitacion import HabitacionCreate, HabitacionUpdate
from app.core.auditoria_helper import registrar_auditoria, convertir_modelo_a_dict
from app.models.auditoria import AccionAuditoria


class ServicioHabitacion:
    def __init__(self, SesionBD: Session, UsuarioId: Optional[int] = None):
        self.Repositorio = HabitacionRepository(SesionBD)
        self.RepositorioTipo = TipoHabitacionRepository(SesionBD)
        self.SesionBD = SesionBD
        self.UsuarioId = UsuarioId

    def CrearHabitacion(self, DatosHabitacion: HabitacionCreate) -> Habitacion:
        # Validar que el tipo de habitación exista
        TipoHabitacion = self.RepositorioTipo.ObtenerPorId(DatosHabitacion.tipo_habitacion_id)
        if not TipoHabitacion or not TipoHabitacion.activo:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="El tipo de habitación especificado no existe o no está activo"
            )
        
        # El procedimiento almacenado valida el número único
        HabitacionNueva = Habitacion(**DatosHabitacion.model_dump())
        HabitacionCreada = self.Repositorio.Crear(HabitacionNueva, UsuarioId=self.UsuarioId)
        
        # La auditoría se registra automáticamente en el procedimiento almacenado
        return HabitacionCreada

    def ObtenerHabitacion(self, IdHabitacion: int) -> Habitacion:
        HabitacionEncontrada = self.Repositorio.ObtenerPorId(IdHabitacion)
        if not HabitacionEncontrada:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Habitacion no encontrada"
            )
        return HabitacionEncontrada

    def ListarHabitaciones(self, Saltar: int = 0, Limite: int = 100) -> List[Habitacion]:
        return self.Repositorio.ObtenerTodas(Saltar=Saltar, Limite=Limite)

    def BuscarDisponibles(
        self,
        FechaEntrada: date,
        FechaSalida: date,
        Capacidad: Optional[int] = None,
        TipoHabitacionId: Optional[int] = None
    ) -> List[Habitacion]:
        if FechaEntrada >= FechaSalida:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="La fecha de entrada debe ser anterior a la fecha de salida"
            )
        
        # El procedimiento almacenado valida las fechas y busca disponibilidad
        return self.Repositorio.BuscarDisponibles(
            FechaEntrada=FechaEntrada,
            FechaSalida=FechaSalida,
            Capacidad=Capacidad,
            TipoHabitacionId=TipoHabitacionId
        )

    def ActualizarHabitacion(
        self,
        IdHabitacion: int,
        DatosHabitacion: HabitacionUpdate
    ) -> Habitacion:
        HabitacionEncontrada = self.ObtenerHabitacion(IdHabitacion)
        DatosAnteriores = convertir_modelo_a_dict(HabitacionEncontrada)
        
        DatosActualizacion = DatosHabitacion.model_dump(exclude_unset=True)
        
        # Validar tipo_habitacion_id si se está actualizando
        if 'tipo_habitacion_id' in DatosActualizacion:
            TipoHabitacion = self.RepositorioTipo.ObtenerPorId(DatosActualizacion['tipo_habitacion_id'])
            if not TipoHabitacion or not TipoHabitacion.activo:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="El tipo de habitación especificado no existe o no está activo"
                )
        
        for Campo, Valor in DatosActualizacion.items():
            setattr(HabitacionEncontrada, Campo, Valor)
        
        HabitacionActualizada = self.Repositorio.Actualizar(HabitacionEncontrada)
        
        # Registrar auditoría
        registrar_auditoria(
            SesionBD=self.SesionBD,
            TablaAfectada="habitaciones",
            Accion=AccionAuditoria.UPDATE,
            RegistroId=IdHabitacion,
            UsuarioId=self.UsuarioId,
            DatosAnteriores=DatosAnteriores,
            DatosNuevos=convertir_modelo_a_dict(HabitacionActualizada)
        )
        
        return HabitacionActualizada

    def EliminarHabitacion(self, IdHabitacion: int):
        HabitacionEncontrada = self.ObtenerHabitacion(IdHabitacion)
        
        ReservasActivas = self.SesionBD.query(Reserva).filter(
            Reserva.habitacion_id == IdHabitacion,
            Reserva.estado.in_([EstadoReserva.PENDIENTE, EstadoReserva.CONFIRMADA])
        ).count()
        
        if ReservasActivas > 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"No se puede eliminar la habitacion porque tiene {ReservasActivas} reserva(s) activa(s) (pendiente(s) o confirmada(s)). Por favor, completa o cancela las reservas primero."
            )
        
        # Obtener IDs de reservas completadas o canceladas asociadas a esta habitación
        ReservasAEliminar = self.SesionBD.query(Reserva.id).filter(
            Reserva.habitacion_id == IdHabitacion,
            Reserva.estado.in_([EstadoReserva.COMPLETADA, EstadoReserva.CANCELADA])
        ).all()
        IdsReservas = [r.id for r in ReservasAEliminar]
        
        if IdsReservas:
            # Eliminar las transacciones de pago asociadas a esas reservas
            self.SesionBD.query(TransaccionPago).filter(
                TransaccionPago.reserva_id.in_(IdsReservas)
            ).delete(synchronize_session=False)

            # Eliminar las reservas completadas o canceladas
            self.SesionBD.query(Reserva).filter(
                Reserva.id.in_(IdsReservas)
            ).delete(synchronize_session=False)
        
        # Registrar auditoría antes de eliminar
        DatosAnteriores = convertir_modelo_a_dict(HabitacionEncontrada)
        registrar_auditoria(
            SesionBD=self.SesionBD,
            TablaAfectada="habitaciones",
            Accion=AccionAuditoria.DELETE,
            RegistroId=IdHabitacion,
            UsuarioId=self.UsuarioId,
            DatosAnteriores=DatosAnteriores,
            Observaciones="Habitación eliminada"
        )
        
        self.Repositorio.Eliminar(HabitacionEncontrada)
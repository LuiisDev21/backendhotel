"""  
Servicio de Pagos, se define el servicio de pagos con SQLAlchemy.
- CrearPago: Crea un nuevo pago.
- ObtenerPago: Obtiene un pago por su ID.
- ObtenerPagoPorReserva: Obtiene un pago por su reserva ID.
- ListarPagos: Lista todos los pagos.
- ProcesarPago: Procesa un pago.
- ActualizarPago: Actualiza un pago existente.
- ReembolsarPago: Reembolsa un pago existente.
"""
from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from datetime import datetime
from typing import List, Optional
from app.models.pago import Pago, EstadoPago
from app.models.reserva import Reserva, EstadoReserva
from app.repositories.pago_repository import PagoRepository
from app.repositories.reserva_repository import ReservaRepository
from app.schemas.pago import PagoCreate, PagoUpdate
from app.core.auditoria_helper import registrar_auditoria, convertir_modelo_a_dict
from app.models.auditoria import AccionAuditoria
import uuid


class ServicioPagos:
    def __init__(self, SesionBD: Session):
        self.Repositorio = PagoRepository(SesionBD)
        self.RepositorioReserva = ReservaRepository(SesionBD)
        self.SesionBD = SesionBD

    def CrearPago(self, DatosPago: PagoCreate) -> Pago:
        ReservaEncontrada = self.RepositorioReserva.ObtenerPorId(DatosPago.reserva_id)
        if not ReservaEncontrada:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Reserva no encontrada"
            )
        
        if self.Repositorio.ObtenerPorReserva(DatosPago.reserva_id):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Ya existe un pago para esta reserva"
            )
        
        PagoNuevo = Pago(
            reserva_id=DatosPago.reserva_id,
            monto=ReservaEncontrada.precio_total,
            metodo_pago=DatosPago.metodo_pago,
            estado=EstadoPago.PENDIENTE,
            numero_transaccion=str(uuid.uuid4())
        )
        
        PagoCreado = self.Repositorio.Crear(PagoNuevo)
        
        # Registrar auditoría
        registrar_auditoria(
            SesionBD=self.SesionBD,
            TablaAfectada="pagos",
            Accion=AccionAuditoria.CREATE,
            RegistroId=PagoCreado.id,
            UsuarioId=None,  # El usuario se obtiene del contexto de la reserva
            DatosNuevos=convertir_modelo_a_dict(PagoCreado),
            Observaciones="Pago creado"
        )
        
        return PagoCreado

    def ObtenerPago(self, IdPago: int) -> Pago:
        PagoEncontrado = self.Repositorio.ObtenerPorId(IdPago)
        if not PagoEncontrado:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Pago no encontrado"
            )
        return PagoEncontrado

    def ObtenerPagoPorReserva(self, IdReserva: int) -> Pago:
        PagoEncontrado = self.Repositorio.ObtenerPorReserva(IdReserva)
        if not PagoEncontrado:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No se encontro pago para esta reserva"
            )
        return PagoEncontrado

    def ListarPagos(self, Saltar: int = 0, Limite: int = 100) -> List[Pago]:
        return self.Repositorio.ObtenerTodos(Saltar=Saltar, Limite=Limite)

    def ProcesarPago(self, IdPago: int, UsuarioId: Optional[int] = None) -> Pago:
        PagoEncontrado = self.ObtenerPago(IdPago)
        
        if PagoEncontrado.estado == EstadoPago.COMPLETADO:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="El pago ya fue procesado"
            )
        
        # Actualizar el pago directamente (no usar procedimiento almacenado que crea uno nuevo)
        PagoEncontrado.estado = EstadoPago.COMPLETADO
        PagoEncontrado.fecha_pago = datetime.utcnow()
        
        # Actualizar estado de reserva a confirmada
        ReservaEncontrada = self.RepositorioReserva.ObtenerPorId(PagoEncontrado.reserva_id)
        if ReservaEncontrada:
            ReservaEncontrada.estado = EstadoReserva.CONFIRMADA
        
        # Guardar cambios
        self.SesionBD.commit()
        self.SesionBD.refresh(PagoEncontrado)
        
        # Registrar auditoría
        registrar_auditoria(
            SesionBD=self.SesionBD,
            TablaAfectada="pagos",
            Accion=AccionAuditoria.PAGO_PROCESS,
            RegistroId=IdPago,
            UsuarioId=UsuarioId,
            DatosNuevos=convertir_modelo_a_dict(PagoEncontrado),
            Observaciones="Pago procesado exitosamente"
        )
        
        return PagoEncontrado

    def ActualizarPago(
        self,
        IdPago: int,
        DatosPago: PagoUpdate,
        UsuarioId: Optional[int] = None
        ) -> Pago:
        PagoEncontrado = self.ObtenerPago(IdPago)
        DatosAnteriores = convertir_modelo_a_dict(PagoEncontrado)
        
        DatosActualizacion = DatosPago.model_dump(exclude_unset=True)
        
        for Campo, Valor in DatosActualizacion.items():
            setattr(PagoEncontrado, Campo, Valor)
        
        PagoActualizado = self.Repositorio.Actualizar(PagoEncontrado)
        
        # Registrar auditoría
        from app.core.auditoria_helper import registrar_auditoria, convertir_modelo_a_dict
        from app.models.auditoria import AccionAuditoria
        
        registrar_auditoria(
            SesionBD=self.SesionBD,
            TablaAfectada="pagos",
            Accion=AccionAuditoria.UPDATE,
            RegistroId=IdPago,
            UsuarioId=UsuarioId,
            DatosAnteriores=DatosAnteriores,
            DatosNuevos=convertir_modelo_a_dict(PagoActualizado)
        )
        
        return PagoActualizado

    def ReembolsarPago(self, IdPago: int, UsuarioId: Optional[int] = None) -> Pago:
        PagoEncontrado = self.ObtenerPago(IdPago)
        
        if PagoEncontrado.estado != EstadoPago.COMPLETADO:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Solo se pueden reembolsar pagos completados"
            )
        
        DatosAnteriores = convertir_modelo_a_dict(PagoEncontrado)
        PagoEncontrado.estado = EstadoPago.REEMBOLSADO
        
        ReservaEncontrada = self.RepositorioReserva.ObtenerPorId(PagoEncontrado.reserva_id)
        if ReservaEncontrada:
            ReservaEncontrada.estado = EstadoReserva.CANCELADA
        
        self.SesionBD.commit()
        self.SesionBD.refresh(PagoEncontrado)
        
        # Registrar auditoría
        registrar_auditoria(
            SesionBD=self.SesionBD,
            TablaAfectada="pagos",
            Accion=AccionAuditoria.PAGO_REFUND,
            RegistroId=IdPago,
            UsuarioId=UsuarioId,
            DatosAnteriores=DatosAnteriores,
            DatosNuevos=convertir_modelo_a_dict(PagoEncontrado),
            Observaciones="Pago reembolsado"
        )
        
        return PagoEncontrado

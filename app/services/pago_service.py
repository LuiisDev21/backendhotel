from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from datetime import datetime
from typing import List
from app.models.pago import Pago, EstadoPago
from app.models.reserva import Reserva, EstadoReserva
from app.repositories.pago_repository import PagoRepository
from app.repositories.reserva_repository import ReservaRepository
from app.schemas.pago import PagoCreate, PagoUpdate
import uuid


class PagoService:
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
        
        return self.Repositorio.Crear(PagoNuevo)

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
                detail="No se encontró pago para esta reserva"
            )
        return PagoEncontrado

    def ListarPagos(self, Saltar: int = 0, Limite: int = 100) -> List[Pago]:
        return self.Repositorio.ObtenerTodos(Saltar=Saltar, Limite=Limite)

    def ProcesarPago(self, IdPago: int) -> Pago:
        PagoEncontrado = self.ObtenerPago(IdPago)
        
        if PagoEncontrado.estado == EstadoPago.COMPLETADO:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="El pago ya fue procesado"
            )
        
        PagoEncontrado.estado = EstadoPago.COMPLETADO
        PagoEncontrado.fecha_pago = datetime.utcnow()
        
        ReservaEncontrada = self.RepositorioReserva.ObtenerPorId(PagoEncontrado.reserva_id)
        ReservaEncontrada.estado = EstadoReserva.CONFIRMADA
        
        self.SesionBD.commit()
        self.SesionBD.refresh(PagoEncontrado)
        
        return PagoEncontrado

    def ActualizarPago(
        self,
        IdPago: int,
        DatosPago: PagoUpdate
    ) -> Pago:
        PagoEncontrado = self.ObtenerPago(IdPago)
        DatosActualizacion = DatosPago.model_dump(exclude_unset=True)
        
        for Campo, Valor in DatosActualizacion.items():
            setattr(PagoEncontrado, Campo, Valor)
        
        return self.Repositorio.Actualizar(PagoEncontrado)

    def ReembolsarPago(self, IdPago: int) -> Pago:
        PagoEncontrado = self.ObtenerPago(IdPago)
        
        if PagoEncontrado.estado != EstadoPago.COMPLETADO:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Solo se pueden reembolsar pagos completados"
            )
        
        PagoEncontrado.estado = EstadoPago.REEMBOLSADO
        
        ReservaEncontrada = self.RepositorioReserva.ObtenerPorId(PagoEncontrado.reserva_id)
        ReservaEncontrada.estado = EstadoReserva.CANCELADA
        
        self.SesionBD.commit()
        self.SesionBD.refresh(PagoEncontrado)
        
        return PagoEncontrado

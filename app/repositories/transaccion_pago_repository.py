"""
Repositorio de Transacciones de pago (1:N por reserva).
"""
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import Optional, List
from decimal import Decimal
from app.models.transaccion_pago import TransaccionPago, TipoTransaccion, EstadoPago


class TransaccionPagoRepository:
    def __init__(self, SesionBD: Session):
        self.SesionBD = SesionBD

    def ObtenerPorId(self, IdTransaccion: int) -> Optional[TransaccionPago]:
        return (
            self.SesionBD.query(TransaccionPago)
            .filter(TransaccionPago.id == IdTransaccion)
            .first()
        )

    def ObtenerPorReserva(self, IdReserva: int) -> List[TransaccionPago]:
        return (
            self.SesionBD.query(TransaccionPago)
            .filter(TransaccionPago.reserva_id == IdReserva)
            .order_by(TransaccionPago.fecha_creacion)
            .all()
        )

    def SumaCargosCompletadosPorReserva(self, IdReserva: int) -> Decimal:
        """Suma de montos de transacciones tipo cargo y estado completado."""
        r = (
            self.SesionBD.query(func.coalesce(func.sum(TransaccionPago.monto), 0))
            .filter(
                TransaccionPago.reserva_id == IdReserva,
                TransaccionPago.tipo == TipoTransaccion.CARGO,
                TransaccionPago.estado == EstadoPago.COMPLETADO,
            )
            .scalar()
        )
        return Decimal(str(r)) if r is not None else Decimal("0")

    def Crear(self, Transaccion: TransaccionPago) -> TransaccionPago:
        self.SesionBD.add(Transaccion)
        self.SesionBD.commit()
        self.SesionBD.refresh(Transaccion)
        return Transaccion

    def Actualizar(self, Transaccion: TransaccionPago) -> TransaccionPago:
        self.SesionBD.commit()
        self.SesionBD.refresh(Transaccion)
        return Transaccion

    def ObtenerTodos(self, Saltar: int = 0, Limite: int = 100) -> List[TransaccionPago]:
        return (
            self.SesionBD.query(TransaccionPago)
            .offset(Saltar)
            .limit(Limite)
            .all()
        )

""" 
Repositorio de Pago, se define el repositorio de pago con SQLAlchemy.
- ObtenerPorId: Obtiene un pago por su ID.
- ObtenerPorReserva: Obtiene un pago por su reserva ID.
- ObtenerPorNumeroTransaccion: Obtiene un pago por su numero de transaccion.
- ObtenerTodos: Obtiene todos los pagos.
- Crear: Crea un nuevo pago usando procedimiento almacenado.
- Actualizar: Actualiza un pago existente.
- ProcesarPago: Procesa un pago usando procedimiento almacenado.
"""
from sqlalchemy.orm import Session
from typing import Optional, List
from decimal import Decimal
from app.models.pago import Pago, MetodoPago
from app.repositories.stored_procedures import StoredProcedures


class PagoRepository:
    def __init__(self, SesionBD: Session):
        self.SesionBD = SesionBD
        self.StoredProcedures = StoredProcedures(SesionBD)

    def ObtenerPorId(self, IdPago: int) -> Optional[Pago]:
        return self.SesionBD.query(Pago).filter(Pago.id == IdPago).first()

    def ObtenerPorReserva(self, IdReserva: int) -> Optional[Pago]:
        return self.SesionBD.query(Pago).filter(Pago.reserva_id == IdReserva).first()

    def ObtenerPorNumeroTransaccion(self, NumeroTransaccion: str) -> Optional[Pago]:
        return self.SesionBD.query(Pago).filter(Pago.numero_transaccion == NumeroTransaccion).first()

    def ObtenerTodos(self, Saltar: int = 0, Limite: int = 100) -> List[Pago]:
        return self.SesionBD.query(Pago).offset(Saltar).limit(Limite).all()

    def Crear(self, PagoNuevo: Pago) -> Pago:
        self.SesionBD.add(PagoNuevo)
        self.SesionBD.commit()
        self.SesionBD.refresh(PagoNuevo)
        return PagoNuevo

    def ProcesarPago(
        self,
        ReservaId: int,
        Monto: Decimal,
        MetodoPago: MetodoPago,
        NumeroTransaccion: Optional[str] = None,
        UsuarioId: Optional[int] = None
    ) -> Pago:
        """Procesa un pago usando el procedimiento almacenado."""
        try:
            resultado = self.StoredProcedures.ProcesarPago(
                ReservaId=ReservaId,
                Monto=Monto,
                MetodoPago=MetodoPago.value,
                NumeroTransaccion=NumeroTransaccion,
                UsuarioId=UsuarioId
            )
            
            # Obtener el pago creado
            return self.ObtenerPorId(resultado['id'])
        except Exception as e:
            self.SesionBD.rollback()
            raise

    def Actualizar(self, PagoActualizado: Pago) -> Pago:
        self.SesionBD.commit()
        self.SesionBD.refresh(PagoActualizado)
        return PagoActualizado

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
    def __init__(self, db: Session):
        self.repository = PagoRepository(db)
        self.reserva_repo = ReservaRepository(db)
        self.db = db

    def crear_pago(self, pago_data: PagoCreate) -> Pago:
        reserva = self.reserva_repo.get_by_id(pago_data.reserva_id)
        if not reserva:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Reserva no encontrada"
            )
        
        if self.repository.get_by_reserva(pago_data.reserva_id):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Ya existe un pago para esta reserva"
            )
        
        nuevo_pago = Pago(
            reserva_id=pago_data.reserva_id,
            monto=reserva.precio_total,
            metodo_pago=pago_data.metodo_pago,
            estado=EstadoPago.PENDIENTE,
            numero_transaccion=str(uuid.uuid4())
        )
        
        return self.repository.create(nuevo_pago)

    def obtener_pago(self, pago_id: int) -> Pago:
        pago = self.repository.get_by_id(pago_id)
        if not pago:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Pago no encontrado"
            )
        return pago

    def obtener_pago_por_reserva(self, reserva_id: int) -> Pago:
        pago = self.repository.get_by_reserva(reserva_id)
        if not pago:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No se encontró pago para esta reserva"
            )
        return pago

    def listar_pagos(self, skip: int = 0, limit: int = 100) -> List[Pago]:
        return self.repository.get_all(skip=skip, limit=limit)

    def procesar_pago(self, pago_id: int) -> Pago:
        pago = self.obtener_pago(pago_id)
        
        if pago.estado == EstadoPago.COMPLETADO:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="El pago ya fue procesado"
            )
        
        pago.estado = EstadoPago.COMPLETADO
        pago.fecha_pago = datetime.utcnow()
        
        reserva = self.reserva_repo.get_by_id(pago.reserva_id)
        reserva.estado = EstadoReserva.CONFIRMADA
        
        self.db.commit()
        self.db.refresh(pago)
        
        return pago

    def actualizar_pago(
        self,
        pago_id: int,
        pago_data: PagoUpdate
    ) -> Pago:
        pago = self.obtener_pago(pago_id)
        update_data = pago_data.model_dump(exclude_unset=True)
        
        for field, value in update_data.items():
            setattr(pago, field, value)
        
        return self.repository.update(pago)

    def reembolsar_pago(self, pago_id: int) -> Pago:
        pago = self.obtener_pago(pago_id)
        
        if pago.estado != EstadoPago.COMPLETADO:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Solo se pueden reembolsar pagos completados"
            )
        
        pago.estado = EstadoPago.REEMBOLSADO
        
        reserva = self.reserva_repo.get_by_id(pago.reserva_id)
        reserva.estado = EstadoReserva.CANCELADA
        
        self.db.commit()
        self.db.refresh(pago)
        
        return pago

"""
Servicio de Transacciones de pago (1:N por reserva).
- Crear transacción (cargo/depósito).
- Procesar (marcar completado y confirmar reserva si suma >= precio_total).
- Reembolso como nueva transacción tipo reembolso.
"""
from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from datetime import datetime, timezone
from typing import List, Optional
from decimal import Decimal
import uuid
from app.models.transaccion_pago import TransaccionPago, EstadoPago, TipoTransaccion, MetodoPago
from app.models.reserva import Reserva, EstadoReserva
from app.repositories.transaccion_pago_repository import TransaccionPagoRepository
from app.repositories.reserva_repository import ReservaRepository
from app.repositories.stored_procedures import StoredProcedures
from app.schemas.transaccion_pago import TransaccionPagoCreate, TransaccionPagoUpdate
from app.core.auditoria_helper import registrar_auditoria, convertir_modelo_a_dict
from app.models.auditoria import AccionAuditoria


class ServicioTransaccionPago:
    def __init__(self, SesionBD: Session, UsuarioId: Optional[int] = None):
        self.Repositorio = TransaccionPagoRepository(SesionBD)
        self.RepositorioReserva = ReservaRepository(SesionBD)
        self.StoredProcedures = StoredProcedures(SesionBD)
        self.SesionBD = SesionBD
        self.UsuarioId = UsuarioId

    def CrearTransaccion(
        self,
        Datos: TransaccionPagoCreate,
        UsuarioId: Optional[int] = None
    ) -> TransaccionPago:
        ReservaEncontrada = self.RepositorioReserva.ObtenerPorId(Datos.reserva_id)
        if not ReservaEncontrada:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Reserva no encontrada"
            )
        if ReservaEncontrada.estado == EstadoReserva.CANCELADA:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No se puede registrar pago en una reserva cancelada"
            )
        numero_transaccion = Datos.numero_transaccion or str(uuid.uuid4())
        transaccion = TransaccionPago(
            reserva_id=Datos.reserva_id,
            tipo=Datos.tipo,
            monto=Datos.monto,
            metodo_pago=Datos.metodo_pago,
            estado=EstadoPago.PENDIENTE,
            numero_transaccion=numero_transaccion,
            referencia_externa=Datos.referencia_externa,
            pasarela_pago=Datos.pasarela_pago,
            moneda=Datos.moneda,
            notas=Datos.notas,
        )
        creada = self.Repositorio.Crear(transaccion)
        registrar_auditoria(
            SesionBD=self.SesionBD,
            TablaAfectada="transacciones_pago",
            Accion=AccionAuditoria.CREATE,
            RegistroId=creada.id,
            UsuarioId=UsuarioId or self.UsuarioId,
            DatosNuevos=convertir_modelo_a_dict(creada),
            Observaciones="Transacción creada"
        )
        return creada

    def ProcesarConSP(
        self,
        ReservaId: int,
        Monto: Decimal,
        MetodoPago: MetodoPago,
        Tipo: str = "cargo",
        NumeroTransaccion: Optional[str] = None,
        ReferenciaExterna: Optional[str] = None,
        PasarelaPago: Optional[str] = None,
    ) -> TransaccionPago:
        """Crea y marca como completada una transacción vía SP (y confirma reserva si aplica)."""
        resultado = self.StoredProcedures.ProcesarPago(
            ReservaId=ReservaId,
            Monto=Monto,
            MetodoPago=MetodoPago.value,
            Tipo=Tipo,
            NumeroTransaccion=NumeroTransaccion,
            ReferenciaExterna=ReferenciaExterna,
            PasarelaPago=PasarelaPago,
            UsuarioId=self.UsuarioId
        )
        return self.Repositorio.ObtenerPorId(int(resultado["id"]))

    def ObtenerTransaccion(self, IdTransaccion: int) -> TransaccionPago:
        t = self.Repositorio.ObtenerPorId(IdTransaccion)
        if not t:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Transacción no encontrada"
            )
        return t

    def ObtenerPorReserva(self, IdReserva: int) -> List[TransaccionPago]:
        return self.Repositorio.ObtenerPorReserva(IdReserva)

    def ListarTodas(self, Saltar: int = 0, Limite: int = 100) -> List[TransaccionPago]:
        return self.Repositorio.ObtenerTodos(Saltar=Saltar, Limite=Limite)

    def ProcesarTransaccion(
        self,
        IdTransaccion: int,
        UsuarioId: Optional[int] = None
    ) -> TransaccionPago:
        """Marca la transacción como completada y confirma la reserva si el total pagado >= precio_total."""
        t = self.ObtenerTransaccion(IdTransaccion)
        if t.estado == EstadoPago.COMPLETADO:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="La transacción ya está procesada"
            )
        t.estado = EstadoPago.COMPLETADO
        t.fecha_pago = datetime.now(timezone.utc)
        t.procesado_por = UsuarioId or self.UsuarioId
        self.Repositorio.Actualizar(t)
        reserva = self.RepositorioReserva.ObtenerPorId(t.reserva_id)
        if reserva and reserva.estado != EstadoReserva.CANCELADA:
            suma = self.Repositorio.SumaCargosCompletadosPorReserva(reserva.id)
            if suma >= reserva.precio_total:
                reserva.estado = EstadoReserva.CONFIRMADA
                self.RepositorioReserva.Actualizar(reserva)
        registrar_auditoria(
            SesionBD=self.SesionBD,
            TablaAfectada="transacciones_pago",
            Accion=AccionAuditoria.PAGO_PROCESS,
            RegistroId=IdTransaccion,
            UsuarioId=UsuarioId or self.UsuarioId,
            DatosNuevos=convertir_modelo_a_dict(t),
            Observaciones="Pago procesado"
        )
        return t

    def ActualizarTransaccion(
        self,
        IdTransaccion: int,
        Datos: TransaccionPagoUpdate,
        UsuarioId: Optional[int] = None
    ) -> TransaccionPago:
        t = self.ObtenerTransaccion(IdTransaccion)
        datos_ant = convertir_modelo_a_dict(t)
        dump = Datos.model_dump(exclude_unset=True)
        for k, v in dump.items():
            setattr(t, k, v)
        self.Repositorio.Actualizar(t)
        registrar_auditoria(
            SesionBD=self.SesionBD,
            TablaAfectada="transacciones_pago",
            Accion=AccionAuditoria.UPDATE,
            RegistroId=IdTransaccion,
            UsuarioId=UsuarioId or self.UsuarioId,
            DatosAnteriores=datos_ant,
            DatosNuevos=convertir_modelo_a_dict(t)
        )
        return t

    def Reembolsar(
        self,
        IdTransaccion: int,
        MontoReembolso: Optional[Decimal] = None,
        UsuarioId: Optional[int] = None
    ) -> TransaccionPago:
        """Registra un reembolso como nueva transacción tipo reembolso (monto negativo o según criterio)."""
        t = self.ObtenerTransaccion(IdTransaccion)
        if t.estado != EstadoPago.COMPLETADO:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Solo se pueden reembolsar transacciones completadas"
            )
        monto = MontoReembolso if MontoReembolso is not None else t.monto
        # Reembolso: monto negativo en la BD (comentario en database_final)
        reembolso = TransaccionPago(
            reserva_id=t.reserva_id,
            tipo=TipoTransaccion.REEMBOLSO,
            monto=-abs(monto),
            metodo_pago=t.metodo_pago,
            estado=EstadoPago.COMPLETADO,
            numero_transaccion=str(uuid.uuid4()),
            notas=f"Reembolso de transacción {t.id}",
            procesado_por=UsuarioId or self.UsuarioId,
            fecha_pago=datetime.now(timezone.utc),
        )
        creada = self.Repositorio.Crear(reembolso)
        registrar_auditoria(
            SesionBD=self.SesionBD,
            TablaAfectada="transacciones_pago",
            Accion=AccionAuditoria.PAGO_REFUND,
            RegistroId=creada.id,
            UsuarioId=UsuarioId or self.UsuarioId,
            DatosNuevos=convertir_modelo_a_dict(creada),
            Observaciones="Reembolso registrado"
        )
        return creada

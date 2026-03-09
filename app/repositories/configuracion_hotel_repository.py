"""
Repositorio de Configuración del hotel (lectura por clave, listar, actualizar).
"""
from sqlalchemy.orm import Session
from typing import Optional, List
from app.models.configuracion_hotel import ConfiguracionHotel
from app.core.auditoria_helper import registrar_auditoria, convertir_modelo_a_dict
from app.models.auditoria import AccionAuditoria


class ConfiguracionHotelRepository:
    def __init__(self, SesionBD: Session):
        self.SesionBD = SesionBD

    def ObtenerPorClave(self, Clave: str) -> Optional[ConfiguracionHotel]:
        return (
            self.SesionBD.query(ConfiguracionHotel)
            .filter(ConfiguracionHotel.clave == Clave)
            .first()
        )

    def ListarTodos(self, Saltar: int = 0, Limite: int = 500) -> List[ConfiguracionHotel]:
        return (
            self.SesionBD.query(ConfiguracionHotel)
            .order_by(ConfiguracionHotel.clave)
            .offset(Saltar)
            .limit(Limite)
            .all()
        )

    def ActualizarValor(
        self,
        Clave: str,
        Valor: str,
        UsuarioId: Optional[int] = None
    ) -> Optional[ConfiguracionHotel]:
        row = self.ObtenerPorClave(Clave)
        if not row:
            return None
        if not row.modificable:
            return None
        datos_anteriores = convertir_modelo_a_dict(row)
        row.valor = Valor
        if UsuarioId is not None:
            row.actualizado_por = UsuarioId
        self.SesionBD.commit()
        self.SesionBD.refresh(row)
        datos_nuevos = convertir_modelo_a_dict(row)
        v_ant = datos_anteriores.get("valor")
        v_nuevo = datos_nuevos.get("valor")
        s_ant = str(v_ant) if v_ant is not None else ""
        s_nuevo = str(v_nuevo) if v_nuevo is not None else ""
        if len(s_ant) > 40:
            s_ant = s_ant[:37] + "..."
        if len(s_nuevo) > 40:
            s_nuevo = s_nuevo[:37] + "..."
        resumen = f"Configuración {Clave}: {s_ant} → {s_nuevo}"
        registrar_auditoria(
            SesionBD=self.SesionBD,
            TablaAfectada="configuracion_hotel",
            Accion=AccionAuditoria.CONFIGURACION_CAMBIO,
            RegistroId=None,
            UsuarioId=UsuarioId,
            DatosAnteriores=datos_anteriores,
            DatosNuevos=datos_nuevos,
            ResumenCambio=resumen,
            CamposModificados=["valor", "actualizado_por"],
        )
        return row

    def ObtenerValorEntero(self, Clave: str, Default: int = 0) -> int:
        row = self.ObtenerPorClave(Clave)
        if row is None:
            return Default
        try:
            return int(row.valor)
        except (ValueError, TypeError):
            return Default

"""
Módulo de ayuda para auditoría.
Proporciona funciones utilitarias para registrar acciones de auditoría de manera consistente.
"""
from sqlalchemy.orm import Session
from typing import Optional, Dict, Any
from decimal import Decimal
from datetime import datetime, date
from app.repositories.auditoria_repository import AuditoriaRepository
from app.models.auditoria import AccionAuditoria
from app.models.usuario import Usuario


def registrar_auditoria(
    SesionBD: Session,
    TablaAfectada: str,
    Accion: AccionAuditoria,
    RegistroId: Optional[int] = None,
    UsuarioId: Optional[int] = None,
    DatosAnteriores: Optional[Dict[str, Any]] = None,
    DatosNuevos: Optional[Dict[str, Any]] = None,
    IpAddress: Optional[str] = None,
    UserAgent: Optional[str] = None,
    Observaciones: Optional[str] = None
) -> None:
    """
    Registra una acción de auditoría de manera centralizada.
    
    Args:
        SesionBD: Sesión de base de datos
        TablaAfectada: Nombre de la tabla afectada
        Accion: Tipo de acción realizada
        RegistroId: ID del registro afectado
        UsuarioId: ID del usuario que realizó la acción
        DatosAnteriores: Datos anteriores (para UPDATE)
        DatosNuevos: Datos nuevos (para CREATE/UPDATE)
        IpAddress: Dirección IP del cliente
        UserAgent: User agent del cliente
        Observaciones: Observaciones adicionales
    """
    try:
        RepositorioAuditoria = AuditoriaRepository(SesionBD)
        RepositorioAuditoria.Crear(
            TablaAfectada=TablaAfectada,
            Accion=Accion,
            RegistroId=RegistroId,
            UsuarioId=UsuarioId,
            DatosAnteriores=DatosAnteriores,
            DatosNuevos=DatosNuevos,
            IpAddress=IpAddress,
            UserAgent=UserAgent,
            Observaciones=Observaciones
        )
    except Exception as e:
        # Log del error pero no fallar la operación principal si falla la auditoría
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f"Error al registrar auditoría: {str(e)}", exc_info=True)


def convertir_modelo_a_dict(Modelo: Any) -> Dict[str, Any]:
    """
    Convierte un modelo SQLAlchemy a diccionario para auditoría.
    
    Args:
        Modelo: Instancia de modelo SQLAlchemy
        
    Returns:
        Diccionario con los datos del modelo
    """
    if not Modelo:
        return {}
    
    datos = {}
    for columna in Modelo.__table__.columns:
        valor = getattr(Modelo, columna.name, None)
        
        # Convertir tipos especiales a tipos serializables para JSON
        if valor is None:
            datos[columna.name] = None
        elif isinstance(valor, Decimal):
            # Convertir Decimal a float para JSON
            datos[columna.name] = float(valor)
        elif isinstance(valor, (datetime, date)):
            # Convertir datetime/date a string ISO
            datos[columna.name] = valor.isoformat()
        elif hasattr(valor, 'value'):  # Enum
            datos[columna.name] = valor.value
        elif hasattr(valor, 'isoformat'):  # datetime, date (fallback)
            datos[columna.name] = valor.isoformat()
        else:
            datos[columna.name] = valor
    
    return datos

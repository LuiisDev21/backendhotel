"""
Repositorio de Usuario con SQLAlchemy.
"""
import logging
from sqlalchemy.orm import Session, selectinload
from sqlalchemy import delete
from typing import Optional, List
from app.models.usuario import Usuario
from app.models.rol import Rol
from app.models.usuario_roles_table import usuario_roles


class UsuarioRepository:
    def __init__(self, SesionBD: Session):
        self.SesionBD = SesionBD

    def ObtenerPorId(
        self,
        IdUsuario: int,
        ConRolesPermisos: bool = False
    ) -> Optional[Usuario]:
        q = self.SesionBD.query(Usuario).filter(Usuario.id == IdUsuario)
        if ConRolesPermisos:
            q = q.options(
                selectinload(Usuario.roles).selectinload(Rol.permisos)
            )
        return q.first()

    def ObtenerPorEmail(self, Email: str) -> Optional[Usuario]:
        try:
            return self.SesionBD.query(Usuario).filter(Usuario.email == Email).first()
        except Exception as e:
            self.SesionBD.rollback()
            logging.getLogger(__name__).exception("Error en ObtenerPorEmail: %s", e)
            raise

    def Crear(self, NuevoUsuario: Usuario) -> Usuario:
        try:
            self.SesionBD.add(NuevoUsuario)
            self.SesionBD.commit()
            self.SesionBD.refresh(NuevoUsuario)
            return NuevoUsuario
        except Exception as e:
            self.SesionBD.rollback()
            logging.getLogger(__name__).exception("Error en Crear usuario: %s", e)
            raise

    def Actualizar(self, UsuarioActualizado: Usuario) -> Usuario:
        self.SesionBD.commit()
        self.SesionBD.refresh(UsuarioActualizado)
        return UsuarioActualizado

    def ObtenerTodos(self, Saltar: int = 0, Limite: int = 100):
        return self.SesionBD.query(Usuario).offset(Saltar).limit(Limite).all()

    def AsignarRoles(self, UsuarioId: int, RolIds: List[int], AsignadoPorId: Optional[int] = None) -> Usuario:
        """Reemplaza los roles del usuario por la lista dada."""
        self.SesionBD.execute(delete(usuario_roles).where(usuario_roles.c.usuario_id == UsuarioId))
        for rol_id in RolIds:
            self.SesionBD.execute(
                usuario_roles.insert().values(
                    usuario_id=UsuarioId,
                    rol_id=rol_id,
                    asignado_por=AsignadoPorId,
                )
            )
        self.SesionBD.commit()
        return self.ObtenerPorId(UsuarioId, ConRolesPermisos=True)

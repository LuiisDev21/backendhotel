""" 
Repositorio de Usuario, se define el repositorio de usuario con SQLAlchemy.
- ObtenerPorId: Obtiene un usuario por su ID.
- ObtenerTodos: Obtiene todos los usuarios.
- ObtenerPorEmail: Obtiene un usuario por su email.
- Crear: Crea un nuevo usuario.
- Actualizar: Actualiza un usuario existente.
"""
from sqlalchemy.orm import Session
from typing import Optional
from app.models.usuario import Usuario


class UsuarioRepository:
    def __init__(self, SesionBD: Session):
        self.SesionBD = SesionBD

    def ObtenerPorId(self, IdUsuario: int) -> Optional[Usuario]:
        return self.SesionBD.query(Usuario).filter(Usuario.id == IdUsuario).first()

    def ObtenerPorEmail(self, Email: str) -> Optional[Usuario]:
        try:
            return self.SesionBD.query(Usuario).filter(Usuario.email == Email).first()
        except Exception:
            self.SesionBD.rollback()
            raise

    def Crear(self, NuevoUsuario: Usuario) -> Usuario:
        try:
            self.SesionBD.add(NuevoUsuario)
            self.SesionBD.commit()
            self.SesionBD.refresh(NuevoUsuario)
            return NuevoUsuario
        except Exception:
            self.SesionBD.rollback()
            raise

    def Actualizar(self, UsuarioActualizado: Usuario) -> Usuario:
        self.SesionBD.commit()
        self.SesionBD.refresh(UsuarioActualizado)
        return UsuarioActualizado

    def ObtenerTodos(self, Saltar: int = 0, Limite: int = 100):
        return self.SesionBD.query(Usuario).offset(Saltar).limit(Limite).all()

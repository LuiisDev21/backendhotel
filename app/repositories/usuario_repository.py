from sqlalchemy.orm import Session
from typing import Optional
from app.models.usuario import Usuario


class UsuarioRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, usuario_id: int) -> Optional[Usuario]:
        return self.db.query(Usuario).filter(Usuario.id == usuario_id).first()

    def get_by_email(self, email: str) -> Optional[Usuario]:
        try:
            return self.db.query(Usuario).filter(Usuario.email == email).first()
        except Exception:
            self.db.rollback()
            raise

    def create(self, usuario: Usuario) -> Usuario:
        try:
            self.db.add(usuario)
            self.db.commit()
            self.db.refresh(usuario)
            return usuario
        except Exception:
            self.db.rollback()
            raise

    def update(self, usuario: Usuario) -> Usuario:
        self.db.commit()
        self.db.refresh(usuario)
        return usuario

    def get_all(self, skip: int = 0, limit: int = 100):
        return self.db.query(Usuario).offset(skip).limit(limit).all()

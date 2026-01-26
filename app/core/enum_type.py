from sqlalchemy import TypeDecorator, String
import enum


class EnumType(TypeDecorator):
    """TypeDecorator para convertir enums de Python a strings en la base de datos"""
    impl = String
    cache_ok = True

    def __init__(self, enum_class, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.enum_class = enum_class

    def process_bind_param(self, value, dialect):
        """Convierte el enum a su valor string al guardar en la BD"""
        if value is None:
            return None
        if isinstance(value, enum.Enum):
            return value.value
        return value

    def process_result_value(self, value, dialect):
        """Convierte el string de la BD al enum al leer"""
        if value is None:
            return None
        return self.enum_class(value)

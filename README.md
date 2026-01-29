# RoyalPalms Backend - API REST

## Tabla de Contenidos

1. [Introducción al Proyecto](#capitulo-1-introducción-al-proyecto)
2. [Arquitectura y Estructura del Proyecto](#capitulo-2-arquitectura-y-estructura-del-proyecto)
3. [Configuración e Instalación](#capitulo-3-configuración-e-instalación)
4. [Base de Datos y Modelos](#capitulo-4-base-de-datos-y-modelos)
5. [Schemas y Validación de Datos](#capitulo-5-schemas-y-validación-de-datos)
6. [Repositorios: Acceso a Datos](#capitulo-6-repositorios-acceso-a-datos)
7. [Servicios: Lógica de Negocio](#capitulo-7-servicios-lógica-de-negocio)
8. [Autenticación y Seguridad](#capitulo-8-autenticación-y-seguridad)
9. [Routers y Endpoints API](#capitulo-9-routers-y-endpoints-api)
10. [Dependencias y Middleware](#capitulo-10-dependencias-y-middleware)
11. [Manejo de Errores y Validaciones](#capitulo-11-manejo-de-errores-y-validaciones)
12. [Despliegue y Producción](#capitulo-12-despliegue-y-producción)
13. [Buenas Prácticas y Patrones](#capitulo-13-buenas-prácticas-y-patrones)
14. [Casos de Uso y Ejemplos](#capitulo-14-casos-de-uso-y-ejemplos)

---

## Capítulo 1: Introducción al Proyecto

### 1.1 ¿Qué es este Proyecto?

Este proyecto es un **Sistema Web de Reservas de Hotel** construido con **FastAPI**, un framework moderno de Python para crear APIs REST. El sistema permite:

- **Gestión de Usuarios**: Registro, autenticación y autorización
- **Gestión de Habitaciones**: CRUD completo de habitaciones del hotel
- **Sistema de Reservas**: Creación, modificación y cancelación de reservas
- **Sistema de Pagos**: Procesamiento y gestión de pagos asociados a reservas

### 1.2 Tecnologías Utilizadas

#### Backend Framework
- **FastAPI**: Framework web moderno, rápido y fácil de usar
- **Uvicorn**: Servidor ASGI de alto rendimiento

#### Base de Datos
- **PostgreSQL**: Base de datos relacional robusta
- **SQLAlchemy**: ORM (Object-Relational Mapping) para Python

#### Autenticación y Seguridad
- **JWT (JSON Web Tokens)**: Para autenticación stateless
- **Bcrypt**: Para encriptación de contraseñas
- **OAuth2**: Estándar de autenticación

#### Validación y Configuración
- **Pydantic**: Validación de datos y configuración
- **python-dotenv**: Manejo de variables de entorno

### 1.3 Características Principales

1. **Arquitectura en Capas**: Separación clara de responsabilidades
2. **API RESTful**: Endpoints bien estructurados siguiendo convenciones REST
3. **Documentación Automática**: Swagger/OpenAPI integrado
4. **Validación Automática**: Validación de datos en tiempo de ejecución
5. **Seguridad Robusta**: Autenticación JWT y encriptación de contraseñas
6. **Código en Español**: Nombres de funciones y variables en español con PascalCase

### 1.4 Estructura General del Proyecto

```
backendhotel/
├── app/
│   ├── core/           # Configuración y utilidades centrales
│   ├── models/         # Modelos de base de datos (SQLAlchemy)
│   ├── schemas/        # Esquemas de validación (Pydantic)
│   ├── repositories/   # Acceso a datos
│   ├── services/       # Lógica de negocio
│   ├── routers/       # Endpoints de la API
│   └── main.py        # Aplicación principal
├── scripts/            # Scripts de utilidad
├── database.sql        # Script SQL para crear tablas
└── requirements.txt    # Dependencias del proyecto
```

---

## Capítulo 2: Arquitectura y Estructura del Proyecto

### 2.1 Arquitectura en Capas

El proyecto sigue una **arquitectura en capas** que separa las responsabilidades:

```
┌─────────────────────────────────────┐
│         ROUTERS (API Endpoints)      │  ← Capa de Presentación
├─────────────────────────────────────┤
│         SERVICES (Lógica Negocio)    │  ← Capa de Negocio
├─────────────────────────────────────┤
│      REPOSITORIES (Acceso Datos)     │  ← Capa de Datos
├─────────────────────────────────────┤
│         MODELS (Entidades BD)        │  ← Capa de Persistencia
└─────────────────────────────────────┘
```

#### Flujo de Datos

1. **Request HTTP** → Router recibe la petición
2. **Router** → Valida datos con Schema y llama al Service
3. **Service** → Aplica lógica de negocio y llama al Repository
4. **Repository** → Ejecuta consultas SQL a través de SQLAlchemy
5. **Model** → Mapea datos de la base de datos a objetos Python
6. **Response** → Datos se serializan y retornan al cliente

### 2.2 Capa de Presentación: Routers

**Ubicación**: `app/routers/`

Los routers definen los **endpoints HTTP** de la API. Cada router maneja un recurso específico:

- `auth.py`: Autenticación (login, registro)
- `habitaciones.py`: Gestión de habitaciones
- `reservas.py`: Gestión de reservas
- `pagos.py`: Gestión de pagos

**Responsabilidades**:
- Recibir requests HTTP
- Validar datos de entrada (usando Schemas)
- Llamar a los servicios correspondientes
- Retornar respuestas HTTP

### 2.3 Capa de Negocio: Services

**Ubicación**: `app/services/`

Los servicios contienen la **lógica de negocio** del sistema:

- Validaciones de reglas de negocio
- Transformaciones de datos
- Orquestación de múltiples repositorios
- Manejo de excepciones de negocio

**Ejemplo**: Al crear una reserva, el servicio valida:
- Que la habitación exista
- Que esté disponible
- Que las fechas sean válidas
- Que la capacidad sea suficiente

### 2.4 Capa de Datos: Repositories

**Ubicación**: `app/repositories/`

Los repositorios encapsulan el **acceso a la base de datos**:

- Operaciones CRUD (Create, Read, Update, Delete)
- Consultas complejas
- Transacciones de base de datos

**Ventajas**:
- Abstrae SQLAlchemy del resto del código
- Facilita testing (se puede mockear)
- Centraliza lógica de acceso a datos

### 2.5 Capa de Persistencia: Models

**Ubicación**: `app/models/`

Los modelos definen la **estructura de las tablas** en la base de datos usando SQLAlchemy:

- Columnas y tipos de datos
- Relaciones entre tablas
- Restricciones y validaciones a nivel de BD

### 2.6 Capa de Validación: Schemas

**Ubicación**: `app/schemas/`

Los schemas definen la **estructura y validación** de datos usando Pydantic:

- Validación de tipos
- Validación de reglas de negocio
- Serialización/Deserialización
- Documentación automática

### 2.7 Capa Core: Configuración y Utilidades

**Ubicación**: `app/core/`

Contiene configuración y utilidades compartidas:

- `config.py`: Configuración de la aplicación
- `database.py`: Configuración de SQLAlchemy
- `security.py`: Funciones de seguridad (JWT, hash)
- `dependencies.py`: Dependencias de FastAPI

---

## Capítulo 3: Configuración e Instalación

### 3.1 Requisitos Previos

- **Python 3.8+**
- **PostgreSQL 12+**
- **pip** (gestor de paquetes de Python)

### 3.2 Instalación de Dependencias

```bash
pip install -r requirements.txt
```

#### Dependencias Principales

```python
fastapi==0.104.1
uvicorn[standard]==0.24.0
sqlalchemy==2.0.23
psycopg2-binary==2.9.9
python-dotenv==1.0.0
python-jose[cryptography]==3.3.0
passlib[bcrypt]==1.7.4
bcrypt==3.2.2
pydantic==2.5.0
pydantic-settings==2.1.0
python-multipart==0.0.6
supabase>=2.8.0
pydantic[email]
```

### 3.3 Configuración de Variables de Entorno

Crear archivo `.env` en la raíz del proyecto:

```env
DATABASE_URL=postgresql://usuario:contraseña@localhost:5432/nombre_bd
SECRET_KEY=
SUPABASE_URL=
SUPABASE_KEY=
SUPABASE_BUCKET=
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
API_V1_PREFIX=/api/v1
PROJECT_NAME=RoyalPalms API
```

#### Explicación de Variables

- **DATABASE_URL**: URL de conexión a PostgreSQL
- **SECRET_KEY**: Clave secreta para firmar tokens JWT (debe ser segura)
- **ALGORITHM**: Algoritmo de encriptación JWT (HS256)
- **ACCESS_TOKEN_EXPIRE_MINUTES**: Tiempo de expiración de tokens (30 min)
- **API_V1_PREFIX**: Prefijo para todas las rutas API

### 3.4 Configuración de la Base de Datos

#### 3.4.1 Crear Base de Datos

```sql
CREATE DATABASE nombre_bd;
```

#### 3.4.2 Ejecutar Script SQL

```bash
psql -U usuario -d nombre_bd -f database.sql
```

O usar el script Python:

```bash
python scripts/init_database.py
```

### 3.5 Iniciar el Servidor

```bash
uvicorn app.main:app --reload
```

El servidor estará disponible en: `http://127.0.0.1:8000`

#### Documentación Interactiva

- **Swagger UI**: `http://127.0.0.1:8000/docs`

### 3.6 Estructura de Configuración

El archivo `app/core/config.py` carga las variables de entorno:

```python
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    DATABASE_URL: str
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    API_V1_PREFIX: str = "/api/v1"
    PROJECT_NAME: str = "RoyalPalms API"

    class Config:
        env_file = ".env"
        case_sensitive = True

settings = Settings()
```

**Ventajas de Pydantic Settings**:
- Validación automática de tipos
- Valores por defecto
- Carga desde archivo `.env`
- Sensible a mayúsculas/minúsculas

---

## Capítulo 4: Base de Datos y Modelos

### 4.1 Configuración de SQLAlchemy

**Archivo**: `app/core/database.py`

```python
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

engine = create_engine(
    settings.DATABASE_URL,
    pool_pre_ping=True,   
    pool_recycle=300,    
    pool_size=settings.POOL_SIZE,
    max_overflow=settings.MAX_OVERFLOW,
    echo=False,          
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()
```

#### Explicación de Parámetros

- **pool_pre_ping**: Verifica que la conexión esté activa antes de usarla
- **pool_recycle**: Tiempo en segundos antes de reciclar conexiones
- **pool_size**: Número de conexiones en el pool
- **max_overflow**: Conexiones adicionales permitidas
- **echo**: Si es `True`, imprime todas las queries SQL

### 4.2 Gestión de Sesiones

```python
def ObtenerSesionBD():
    SesionBD = SessionLocal()
    try:
        yield SesionBD
    except Exception:
        SesionBD.rollback()
        raise
    finally:
        SesionBD.close()
```

**Patrón Generator**: Usa `yield` para crear un contexto que:
1. Crea la sesión
2. La retorna para usar
3. Hace rollback en caso de error
4. Cierra la sesión automáticamente

### 4.3 Modelo de Usuario

**Archivo**: `app/models/usuario.py`

```python
from sqlalchemy import Column, Integer, String, Boolean, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime
from app.core.database import Base

class Usuario(Base):
    __tablename__ = "usuarios"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    nombre = Column(String, nullable=False)
    apellido = Column(String, nullable=False)
    telefono = Column(String, nullable=True)
    hashed_password = Column(String, nullable=False)
    es_administrador = Column(Boolean, default=False)
    activo = Column(Boolean, default=True)
    fecha_creacion = Column(DateTime, default=datetime.utcnow)

    reservas = relationship("Reserva", back_populates="usuario")
```

#### Explicación de Columnas

- **id**: Clave primaria autoincremental
- **email**: Único e indexado para búsquedas rápidas
- **hashed_password**: Contraseña encriptada (nunca texto plano)
- **es_administrador**: Flag para permisos especiales
- **activo**: Permite desactivar usuarios sin eliminarlos
- **reservas**: Relación uno-a-muchos con Reserva

### 4.4 Modelo de Habitación

**Archivo**: `app/models/habitacion.py`

```python
class Habitacion(Base):
    __tablename__ = "habitaciones"

    id = Column(Integer, primary_key=True, index=True)
    numero = Column(String, unique=True, nullable=False, index=True)
    tipo = Column(String, nullable=False)
    descripcion = Column(Text, nullable=True)
    capacidad = Column(Integer, nullable=False)
    precio_por_noche = Column(Numeric(10, 2), nullable=False)
    disponible = Column(Boolean, default=True)
    fecha_creacion = Column(DateTime, default=datetime.utcnow)

    reservas = relationship("Reserva", back_populates="habitacion")
```

#### Tipos de Datos SQLAlchemy

- **Integer**: Números enteros
- **String**: Texto de longitud variable
- **Text**: Texto largo sin límite
- **Numeric(10, 2)**: Decimal con 10 dígitos, 2 decimales
- **Boolean**: Verdadero/Falso
- **DateTime**: Fecha y hora
- **Date**: Solo fecha

### 4.5 Modelo de Reserva

**Archivo**: `app/models/reserva.py`

```python
from sqlalchemy import Column, Integer, String, ForeignKey, Date, DateTime, Numeric
from app.core.enum_type import EnumType

class EstadoReserva(str, enum.Enum):
    PENDIENTE = "pendiente"
    CONFIRMADA = "confirmada"
    CANCELADA = "cancelada"
    COMPLETADA = "completada"

class Reserva(Base):
    __tablename__ = "reservas"

    id = Column(Integer, primary_key=True, index=True)
    usuario_id = Column(Integer, ForeignKey("usuarios.id"), nullable=False)
    habitacion_id = Column(Integer, ForeignKey("habitaciones.id"), nullable=False)
    fecha_entrada = Column(Date, nullable=False)
    fecha_salida = Column(Date, nullable=False)
    numero_huespedes = Column(Integer, nullable=False)
    precio_total = Column(Numeric(10, 2), nullable=False)
    estado = Column(EnumType(EstadoReserva), default=EstadoReserva.PENDIENTE)
    notas = Column(String, nullable=True)
    fecha_creacion = Column(DateTime, default=datetime.utcnow)
    fecha_actualizacion = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    usuario = relationship("Usuario", back_populates="reservas")
    habitacion = relationship("Habitacion", back_populates="reservas")
    pago = relationship("Pago", back_populates="reserva", uselist=False)
```

#### Conceptos Importantes

**Foreign Keys**: Relaciones entre tablas
- `usuario_id` referencia a `usuarios.id`
- `habitacion_id` referencia a `habitaciones.id`

**Relationships**: Acceso bidireccional entre modelos
- `usuario.reservas` → Lista de reservas del usuario
- `reserva.usuario` → Usuario que hizo la reserva

**Enums**: Valores predefinidos
- `EstadoReserva` define estados válidos
- `EnumType` maneja la conversión entre Python y PostgreSQL

### 4.6 Modelo de Pago

**Archivo**: `app/models/pago.py`

```python
class MetodoPago(str, enum.Enum):
    TARJETA_CREDITO = "tarjeta_credito"
    TARJETA_DEBITO = "tarjeta_debito"
    EFECTIVO = "efectivo"
    TRANSFERENCIA = "transferencia"

class EstadoPago(str, enum.Enum):
    PENDIENTE = "pendiente"
    COMPLETADO = "completado"
    RECHAZADO = "rechazado"
    REEMBOLSADO = "reembolsado"

class Pago(Base):
    __tablename__ = "pagos"

    id = Column(Integer, primary_key=True, index=True)
    reserva_id = Column(Integer, ForeignKey("reservas.id"), unique=True, nullable=False)
    monto = Column(Numeric(10, 2), nullable=False)
    metodo_pago = Column(EnumType(MetodoPago), nullable=False)
    estado = Column(EnumType(EstadoPago), default=EstadoPago.PENDIENTE)
    numero_transaccion = Column(String, unique=True, nullable=True)
    fecha_pago = Column(DateTime, nullable=True)
    fecha_creacion = Column(DateTime, default=datetime.utcnow)

    reserva = relationship("Reserva", back_populates="pago")
```

#### Relación Uno-a-Uno

- `reserva_id` tiene `unique=True` → Una reserva tiene un solo pago
- `uselist=False` en relationship → Retorna un objeto, no una lista

### 4.7 Crear Tablas en la Base de Datos

```python
from app.core.database import Base, engine
from app.models import usuario, habitacion, reserva, pago

Base.metadata.create_all(bind=engine)
```

O usar el script:

```bash
python scripts/init_database.py
```

---

## Capítulo 5: Schemas y Validación de Datos

### 5.1 ¿Qué son los Schemas?

Los **Schemas** (esquemas) definen la estructura y validación de datos usando **Pydantic**. Son diferentes a los Models de SQLAlchemy:

- **Models**: Estructura de la base de datos
- **Schemas**: Estructura de datos de entrada/salida de la API

### 5.2 Schema de Habitación

**Archivo**: `app/schemas/habitacion.py`

```python
from pydantic import BaseModel
from typing import Optional
from decimal import Decimal
from datetime import datetime

class Habitacion(BaseModel):
    numero: str
    tipo: str
    descripcion: Optional[str] = None
    capacidad: int
    precio_por_noche: Decimal
    disponible: bool = True

class HabitacionCreate(Habitacion):
    pass

class HabitacionUpdate(BaseModel):
    tipo: Optional[str] = None
    descripcion: Optional[str] = None
    capacidad: Optional[int] = None
    precio_por_noche: Optional[Decimal] = None
    disponible: Optional[bool] = None

class HabitacionResponse(Habitacion):
    id: int
    fecha_creacion: datetime

    class Config:
        from_attributes = True
```

### 5.3 Schema de Reserva con Campos Computados

**Archivo**: `app/schemas/reserva.py`

El schema de respuesta de reservas incluye campos computados que extraen información de las relaciones:

```python
from pydantic import BaseModel, model_validator
from typing import Optional, Any

class ReservaResponse(ReservaBase):
    id: int
    usuario_id: int
    precio_total: Decimal
    estado: EstadoReserva
    fecha_creacion: datetime
    fecha_actualizacion: datetime
    numero_habitacion: Optional[str] = None  # Campo computado
    nombre_usuario: Optional[str] = None     # Campo computado

    class Config:
        from_attributes = True
    
    @model_validator(mode='before')
    @classmethod
    def extraer_datos_relaciones(cls, data: Any) -> Any:
        # Extraer datos de las relaciones ORM antes de validar
        if hasattr(data, '__dict__'):
            if hasattr(data, 'habitacion') and data.habitacion:
                data.__dict__['numero_habitacion'] = data.habitacion.numero
            if hasattr(data, 'usuario') and data.usuario:
                data.__dict__['nombre_usuario'] = f"{data.usuario.nombre} {data.usuario.apellido}"
        return data
```

**Ventajas de campos computados:**
- La API devuelve información legible (nombres en lugar de IDs)
- No se necesitan consultas adicionales en el frontend
- Los datos originales (IDs) siguen disponibles

### 5.3 Patrón de Herencia de Schemas

#### Habitacion
- Contiene campos comunes
- No se usa directamente, es una clase base

#### HabitacionCreate
- Hereda de `Habitacion`
- Usado para crear nuevas habitaciones
- Todos los campos son requeridos (excepto opcionales)

#### HabitacionUpdate
- Campos opcionales
- Permite actualizar solo algunos campos
- Usa `exclude_unset=True` para ignorar campos no enviados

#### HabitacionResponse
- Hereda de `Habitacion` + campos adicionales
- Usado para respuestas de la API
- `from_attributes = True` permite crear desde objetos SQLAlchemy

### 5.4 Schema de Usuario

**Archivo**: `app/schemas/usuario.py`

```python
class UsuarioCreate(BaseModel):
    email: str
    password: str
    nombre: str
    apellido: str
    telefono: Optional[str] = None

class UsuarioLogin(BaseModel):
    email: str
    password: str

class UsuarioResponse(BaseModel):
    id: int
    email: str
    nombre: str
    apellido: str
    telefono: Optional[str]
    es_administrador: bool
    activo: bool
    fecha_creacion: datetime

    class Config:
        from_attributes = True
```

#### Seguridad en Schemas

- **UsuarioCreate**: Incluye `password` (texto plano)
- **UsuarioResponse**: **NO** incluye `password` ni `hashed_password`
- Nunca exponer contraseñas en respuestas

### 5.5 Validaciones con Pydantic

#### Validación de Tipos

```python
class ReservaCreate(BaseModel):
    habitacion_id: int          # Debe ser entero
    fecha_entrada: date        # Debe ser fecha válida
    fecha_salida: date         # Debe ser fecha válida
    numero_huespedes: int      # Debe ser entero positivo
```

#### Validación Personalizada

```python
from pydantic import validator

class ReservaCreate(BaseModel):
    fecha_entrada: date
    fecha_salida: date
    
    @validator('fecha_salida')
    def fecha_salida_debe_ser_posterior(cls, v, values):
        if 'fecha_entrada' in values and v <= values['fecha_entrada']:
            raise ValueError('La fecha de salida debe ser posterior a la entrada')
        return v
```

### 5.6 Serialización Automática

Pydantic convierte automáticamente:

```python
# De objeto SQLAlchemy a dict
habitacion = Habitacion(...)
schema = HabitacionResponse.from_orm(habitacion)
# O con from_attributes=True
schema = HabitacionResponse.model_validate(habitacion)

# De dict a objeto Pydantic
datos = {"numero": "101", "tipo": "simple", ...}
schema = HabitacionCreate(**datos)
```

---

## Capítulo 6: Repositorios: Acceso a Datos

### 6.1 ¿Qué es un Repositorio?

Un **Repositorio** encapsula toda la lógica de acceso a datos. Es una capa de abstracción entre el código de negocio y la base de datos.

**Ventajas**:
- Centraliza consultas SQL
- Facilita testing (se puede mockear)
- Abstrae SQLAlchemy del resto del código
- Permite cambiar de BD sin afectar servicios

### 6.2 Estructura de un Repositorio

**Archivo**: `app/repositories/habitacion_repository.py`

```python
from sqlalchemy.orm import Session
from typing import Optional, List
from app.models.habitacion import Habitacion

class HabitacionRepository:
    def __init__(self, SesionBD: Session):
        self.SesionBD = SesionBD
```

**Patrón**: El repositorio recibe la sesión de BD en el constructor.

### 6.3 Operaciones CRUD Básicas

#### CREATE - Crear

```python
def Crear(self, HabitacionNueva: Habitacion) -> Habitacion:
    self.SesionBD.add(HabitacionNueva)
    self.SesionBD.commit()
    self.SesionBD.refresh(HabitacionNueva)
    return HabitacionNueva
```

**Pasos**:
1. `add()`: Agrega el objeto a la sesión
2. `commit()`: Guarda en la base de datos
3. `refresh()`: Actualiza el objeto con datos de BD (ID, timestamps)

#### READ - Leer

```python
def ObtenerPorId(self, IdHabitacion: int) -> Optional[Habitacion]:
    return self.SesionBD.query(Habitacion).filter(Habitacion.id == IdHabitacion).first()

def ObtenerTodas(self, Saltar: int = 0, Limite: int = 100) -> List[Habitacion]:
    return self.SesionBD.query(Habitacion).offset(Saltar).limit(Limite).all()
```

**Métodos de Query**:
- `query(Modelo)`: Inicia una consulta
- `filter(condición)`: Aplica filtros WHERE
- `first()`: Retorna el primer resultado o None
- `all()`: Retorna todos los resultados
- `offset(n)`: Salta n registros (paginación)
- `limit(n)`: Limita a n registros

#### UPDATE - Actualizar

```python
def Actualizar(self, HabitacionActualizada: Habitacion) -> Habitacion:
    self.SesionBD.commit()
    self.SesionBD.refresh(HabitacionActualizada)
    return HabitacionActualizada
```

**Nota**: El objeto ya debe estar modificado. Solo se hace commit.

#### DELETE - Eliminar

```python
def Eliminar(self, HabitacionAEliminar: Habitacion):
    self.SesionBD.delete(HabitacionAEliminar)
    self.SesionBD.commit()
```

### 6.4 Consultas con Filtros

#### Filtro Simple

```python
def ObtenerPorNumero(self, Numero: str) -> Optional[Habitacion]:
    return self.SesionBD.query(Habitacion).filter(
        Habitacion.numero == Numero
    ).first()
```

#### Múltiples Filtros

```python
def BuscarPorTipoYCapacidad(self, Tipo: str, CapacidadMinima: int):
    return self.SesionBD.query(Habitacion).filter(
        Habitacion.tipo == Tipo,
        Habitacion.capacidad >= CapacidadMinima
    ).all()
```

#### Filtros con AND y OR

```python
from sqlalchemy import and_, or_

def BuscarCompleja(self):
    return self.SesionBD.query(Habitacion).filter(
        and_(
            Habitacion.disponible == True,
            or_(
                Habitacion.tipo == "suite",
                Habitacion.capacidad >= 4
            )
        )
    ).all()
```

### 6.5 Consultas con Joins

#### Join Implícito (usando relationships)

```python
# Acceder a relaciones definidas en el modelo
reserva = self.SesionBD.query(Reserva).first()
habitacion = reserva.habitacion  # Join automático
usuario = reserva.usuario       # Join automático
```

#### Join Explícito (Eager Loading)

```python
from sqlalchemy.orm import joinedload

def ObtenerReservaConRelaciones(self, IdReserva: int):
    return self.SesionBD.query(Reserva).options(
        joinedload(Reserva.habitacion),
        joinedload(Reserva.usuario)
    ).filter(Reserva.id == IdReserva).first()
```

**Ventaja**: Carga relaciones en una sola query (evita N+1 queries).

**Ejemplo real del proyecto** (`reserva_repository.py`):
```python
def ObtenerTodas(self, Saltar: int = 0, Limite: int = 100) -> List[Reserva]:
    return self.SesionBD.query(Reserva).options(
        joinedload(Reserva.habitacion),
        joinedload(Reserva.usuario)
    ).offset(Saltar).limit(Limite).all()
```

Esto permite que el schema `ReservaResponse` acceda a `reserva.habitacion.numero` y `reserva.usuario.nombre` sin queries adicionales.

### 6.6 Consulta Compleja: Habitaciones Disponibles

```python
def BuscarDisponibles(
    self, 
    FechaEntrada: date, 
    FechaSalida: date, 
    Capacidad: Optional[int] = None,
    Tipo: Optional[str] = None
) -> List[Habitacion]:
    # Subconsulta: habitaciones ocupadas
    HabitacionesOcupadas = self.SesionBD.query(Reserva.habitacion_id).filter(
        and_(
            cast(Reserva.estado, String) != EstadoReserva.CANCELADA.value,
            or_(
                and_(Reserva.fecha_entrada <= FechaEntrada, 
                     Reserva.fecha_salida > FechaEntrada),
                and_(Reserva.fecha_entrada < FechaSalida, 
                     Reserva.fecha_salida >= FechaSalida),
                and_(Reserva.fecha_entrada >= FechaEntrada, 
                     Reserva.fecha_salida <= FechaSalida)
            )
        )
    ).distinct()
    
    IdsHabitacionesOcupadas = [Fila[0] for Fila in HabitacionesOcupadas]

    # Consulta principal
    Consulta = self.SesionBD.query(Habitacion).filter(
        Habitacion.disponible == True
    )
    
    # Excluir habitaciones ocupadas
    if IdsHabitacionesOcupadas:
        Consulta = Consulta.filter(~Habitacion.id.in_(IdsHabitacionesOcupadas))

    # Filtros opcionales
    if Capacidad:
        Consulta = Consulta.filter(Habitacion.capacidad >= Capacidad)
    
    if Tipo:
        Consulta = Consulta.filter(Habitacion.tipo == Tipo)

    return Consulta.all()
```

**Lógica**:
1. Encuentra habitaciones con reservas en conflicto de fechas
2. Excluye habitaciones canceladas
3. Filtra habitaciones disponibles
4. Aplica filtros opcionales

### 6.7 Manejo de Transacciones

```python
def CrearConTransaccion(self, HabitacionNueva: Habitacion):
    try:
        self.SesionBD.add(HabitacionNueva)
        self.SesionBD.commit()
        return HabitacionNueva
    except Exception:
        self.SesionBD.rollback()
        raise
```

**Importante**: Siempre hacer rollback en caso de error.

---

## Capítulo 7: Servicios: Lógica de Negocio

### 7.1 ¿Qué es un Servicio?

Un **Servicio** contiene la **lógica de negocio** de la aplicación. Coordina entre repositorios y aplica reglas de negocio.

**Responsabilidades**:
- Validar reglas de negocio
- Orquestar múltiples repositorios
- Transformar datos
- Manejar excepciones de negocio

### 7.2 Estructura de un Servicio

**Archivo**: `app/services/habitacion_service.py`

```python
from sqlalchemy.orm import Session
from app.repositories.habitacion_repository import HabitacionRepository
from app.schemas.habitacion import HabitacionCreate, HabitacionUpdate

class ServicioHabitacion:
    def __init__(self, SesionBD: Session):
        self.Repositorio = HabitacionRepository(SesionBD)
        self.SesionBD = SesionBD
```

### 7.3 Crear con Validaciones

```python
def CrearHabitacion(self, DatosHabitacion: HabitacionCreate) -> Habitacion:
    # Validación de negocio: número único
    if self.Repositorio.ObtenerPorNumero(DatosHabitacion.numero):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Ya existe una habitación con ese número"
        )
    
    # Crear objeto del modelo
    HabitacionNueva = Habitacion(**DatosHabitacion.model_dump())
    
    # Guardar en BD
    return self.Repositorio.Crear(HabitacionNueva)
```

**Flujo**:
1. Validar reglas de negocio
2. Crear objeto del modelo desde el schema
3. Llamar al repositorio para guardar

### 7.4 Obtener con Validación

```python
def ObtenerHabitacion(self, IdHabitacion: int) -> Habitacion:
    HabitacionEncontrada = self.Repositorio.ObtenerPorId(IdHabitacion)
    if not HabitacionEncontrada:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Habitación no encontrada"
        )
    return HabitacionEncontrada
```

**Patrón**: Validar existencia antes de retornar.

### 7.5 Actualizar Parcial

```python
def ActualizarHabitacion(
    self,
    IdHabitacion: int,
    DatosHabitacion: HabitacionUpdate
) -> Habitacion:
    # Obtener habitación existente
    HabitacionEncontrada = self.ObtenerHabitacion(IdHabitacion)
    
    # Solo campos enviados (exclude_unset=True)
    DatosActualizacion = DatosHabitacion.model_dump(exclude_unset=True)
    
    # Actualizar campos
    for Campo, Valor in DatosActualizacion.items():
        setattr(HabitacionEncontrada, Campo, Valor)
    
    # Guardar cambios
    return self.Repositorio.Actualizar(HabitacionEncontrada)
```

**`exclude_unset=True`**: Solo incluye campos que fueron enviados en el request.

### 7.6 Servicio Complejo: Crear Reserva

**Archivo**: `app/services/reserva_service.py`

```python
def CrearReserva(
    self,
    IdUsuario: int,
    DatosReserva: ReservaCreate
) -> Reserva:
    # 1. Validar que la habitación exista
    HabitacionEncontrada = self.RepositorioHabitacion.ObtenerPorId(
        DatosReserva.habitacion_id
    )
    if not HabitacionEncontrada:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Habitación no encontrada"
        )
    
    # 2. Validar que esté disponible
    if not HabitacionEncontrada.disponible:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="La habitación no está disponible"
        )
    
    # 3. Validar capacidad
    if DatosReserva.numero_huespedes > HabitacionEncontrada.capacidad:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"La habitación solo puede alojar {HabitacionEncontrada.capacidad} huéspedes"
        )
    
    # 4. Validar disponibilidad en fechas
    HabitacionesDisponibles = self.RepositorioHabitacion.BuscarDisponibles(
        DatosReserva.fecha_entrada,
        DatosReserva.fecha_salida
    )
    
    if HabitacionEncontrada not in HabitacionesDisponibles:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="La habitación no está disponible en las fechas seleccionadas"
        )
    
    # 5. Calcular precio total
    PrecioTotal = self.CalcularPrecioTotal(
        HabitacionEncontrada,
        DatosReserva.fecha_entrada,
        DatosReserva.fecha_salida
    )
    
    # 6. Crear reserva
    ReservaNueva = Reserva(
        usuario_id=IdUsuario,
        habitacion_id=DatosReserva.habitacion_id,
        fecha_entrada=DatosReserva.fecha_entrada,
        fecha_salida=DatosReserva.fecha_salida,
        numero_huespedes=DatosReserva.numero_huespedes,
        precio_total=PrecioTotal,
        notas=DatosReserva.notas,
        estado=EstadoReserva.PENDIENTE
    )
    
    return self.Repositorio.Crear(ReservaNueva)
```

**Lógica Compleja**:
1. Múltiples validaciones
2. Consulta de disponibilidad
3. Cálculo de precio
4. Creación del objeto

### 7.7 Métodos Auxiliares

```python
def CalcularPrecioTotal(
    self,
    Habitacion: Habitacion,
    FechaEntrada: date,
    FechaSalida: date
) -> Decimal:
    NumeroNoches = (FechaSalida - FechaEntrada).days
    if NumeroNoches <= 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="La fecha de salida debe ser posterior a la fecha de entrada"
        )
    return Decimal(str(Habitacion.precio_por_noche)) * Decimal(str(NumeroNoches))
```

**Separación de Responsabilidades**: Métodos pequeños y enfocados.

### 7.8 Eliminación con Validación de Dependencias

Un ejemplo de lógica de negocio compleja es la eliminación de habitaciones:

```python
def EliminarHabitacion(self, IdHabitacion: int):
    HabitacionEncontrada = self.ObtenerHabitacion(IdHabitacion)
    
    # Verificar si hay reservas activas (pendientes o confirmadas)
    ReservasActivas = self.SesionBD.query(Reserva).filter(
        Reserva.habitacion_id == IdHabitacion,
        Reserva.estado.in_([EstadoReserva.PENDIENTE, EstadoReserva.CONFIRMADA])
    ).count()
    
    if ReservasActivas > 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"No se puede eliminar porque tiene {ReservasActivas} reserva(s) activa(s)"
        )
    
    # Obtener IDs de reservas completadas o canceladas
    ReservasAEliminar = self.SesionBD.query(Reserva.id).filter(
        Reserva.habitacion_id == IdHabitacion,
        Reserva.estado.in_([EstadoReserva.COMPLETADA, EstadoReserva.CANCELADA])
    ).all()
    IdsReservas = [r.id for r in ReservasAEliminar]
    
    if IdsReservas:
        # Eliminar pagos asociados primero (por integridad referencial)
        self.SesionBD.query(Pago).filter(
            Pago.reserva_id.in_(IdsReservas)
        ).delete(synchronize_session=False)
        
        # Eliminar reservas completadas/canceladas
        self.SesionBD.query(Reserva).filter(
            Reserva.id.in_(IdsReservas)
        ).delete(synchronize_session=False)
    
    self.Repositorio.Eliminar(HabitacionEncontrada)
```

**Lógica de Negocio**:
1. No permitir eliminar si hay reservas activas
2. Si solo hay reservas finalizadas, eliminarlas junto con sus pagos
3. Respetar el orden de eliminación por integridad referencial (pagos → reservas → habitación)

---

## Capítulo 8: Autenticación y Seguridad

### 8.1 Sistema de Autenticación JWT

El proyecto usa **JWT (JSON Web Tokens)** para autenticación stateless.

**Ventajas**:
- No requiere sesiones en servidor
- Escalable (cualquier servidor puede validar)
- Incluye información del usuario en el token

### 8.2 Hash de Contraseñas

**Archivo**: `app/core/security.py`

```python
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def HashearContra(Contrasena: str) -> str:
    return pwd_context.hash(Contrasena)

def VerificarContrasena(ContrasenaPlana: str, ContrasenaEncriptada: str) -> bool:
    return pwd_context.verify(ContrasenaPlana, ContrasenaEncriptada)
```

**Bcrypt**:
- Algoritmo de hash unidireccional
- Incluye "salt" automático
- Resistente a ataques de fuerza bruta

**Nunca**:
- ❌ Guardar contraseñas en texto plano
- ❌ Enviar contraseñas en respuestas
- ❌ Loggear contraseñas

### 8.3 Crear Token JWT

```python
from datetime import datetime, timedelta
from jose import jwt

def CrearTokenAcceso(Datos: dict, TiempoExpiracion: Optional[timedelta] = None) -> str:
    DatosACodificar = Datos.copy()
    
    # Calcular expiración
    if TiempoExpiracion:
        FechaExpiracion = datetime.utcnow() + TiempoExpiracion
    else:
        FechaExpiracion = datetime.utcnow() + timedelta(
            minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
        )
    
    # Agregar expiración
    DatosACodificar.update({"exp": FechaExpiracion})
    
    # Codificar token
    TokenCodificado = jwt.encode(
        DatosACodificar, 
        settings.SECRET_KEY, 
        algorithm=settings.ALGORITHM
    )
    return TokenCodificado
```

**Estructura del Token**:
```json
{
  "sub": "123",           // Subject (ID del usuario)
  "exp": 1234567890       // Expiración (timestamp)
}
```

### 8.4 Decodificar y Validar Token

```python
def DecodificarTokenAcceso(Token: str) -> Optional[dict]:
    try:
        Payload = jwt.decode(
            Token, 
            settings.SECRET_KEY, 
            algorithms=[settings.ALGORITHM]
        )
        return Payload
    except JWTError:
        return None
```

**Validaciones Automáticas**:
- Firma criptográfica
- Fecha de expiración
- Algoritmo correcto

### 8.5 Dependencia de Autenticación

**Archivo**: `app/core/dependencies.py`

```python
from fastapi.security import OAuth2PasswordBearer

oauth2_scheme = OAuth2PasswordBearer(tokenUrl=f"/api/v1/auth/login")

async def ObtenerUsuario(
    Token: str = Depends(oauth2_scheme),
    SesionBD: Session = Depends(ObtenerSesionBD)
):
    # 1. Decodificar token
    Payload = DecodificarTokenAcceso(Token)
    if Payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido o expirado"
        )
    
    # 2. Obtener ID de usuario
    IdUsuarioStr = Payload.get("sub")
    if IdUsuarioStr is None:
        raise HTTPException(...)
    
    # 3. Convertir a entero
    try:
        IdUsuario = int(IdUsuarioStr)
    except (ValueError, TypeError):
        raise HTTPException(...)
    
    # 4. Buscar usuario en BD
    RepositorioUsuario = UsuarioRepository(SesionBD)
    UsuarioEncontrado = RepositorioUsuario.ObtenerPorId(IdUsuario)
    if UsuarioEncontrado is None:
        raise HTTPException(...)
    
    # 5. Validar que esté activo
    if not UsuarioEncontrado.activo:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Usuario inactivo"
        )
    
    return UsuarioEncontrado
```

**OAuth2PasswordBearer**:
- Extrae automáticamente el token del header `Authorization: Bearer <token>`
- Define el endpoint de login para documentación

### 8.6 Dependencia de Administrador

```python
async def ObtenerAdministrador(
    UsuarioActual = Depends(ObtenerUsuario)
):
    if not UsuarioActual.es_administrador:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tiene permisos de administrador"
        )
    return UsuarioActual
```

**Composición de Dependencias**: Reutiliza `ObtenerUsuario` y agrega validación adicional.

### 8.7 Flujo de Autenticación

#### 1. Registro

```python
@router.post("/register")
def RegistrarUsuario(DatosUsuario: UsuarioCreate, SesionBD: Session = Depends(ObtenerSesionBD)):
    Servicio = ServicioUsuarios(SesionBD)
    return Servicio.CrearUsuario(DatosUsuario)
```

#### 2. Login

```python
@router.post("/login")
def IniciarSesion(DatosLogin: UsuarioLogin, SesionBD: Session = Depends(ObtenerSesionBD)):
    Servicio = ServicioUsuarios(SesionBD)
    return Servicio.AutenticarUsuario(DatosLogin)
```

**En el Servicio**:
```python
def AutenticarUsuario(self, DatosLogin: UsuarioLogin) -> Token:
    # 1. Buscar usuario
    UsuarioEncontrado = self.Repositorio.ObtenerPorEmail(DatosLogin.email)
    
    # 2. Verificar contraseña
    if not UsuarioEncontrado or not VerificarContrasena(
        DatosLogin.password, 
        UsuarioEncontrado.hashed_password
    ):
        raise HTTPException(...)
    
    # 3. Validar que esté activo
    if not UsuarioEncontrado.activo:
        raise HTTPException(...)
    
    # 4. Crear token
    TiempoExpiracion = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    TokenAcceso = CrearTokenAcceso(
        Datos={"sub": str(UsuarioEncontrado.id)},
        TiempoExpiracion=TiempoExpiracion
    )
    
    return Token(access_token=TokenAcceso, token_type="bearer")
```

#### 3. Usar Token en Requests

```http
GET /api/v1/auth/me
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

### 8.8 Seguridad de la SECRET_KEY

**Importante**:
- Debe ser una cadena larga y aleatoria
- Nunca commitear en el repositorio
- Cambiar invalida todos los tokens existentes

**Generar una segura**:
```python
import secrets
print(secrets.token_urlsafe(32))
```

---

## Capítulo 9: Routers y Endpoints API

### 9.1 ¿Qué es un Router?

Un **Router** en FastAPI agrupa endpoints relacionados. Es similar a un "Blueprint" en Flask.

### 9.2 Estructura de un Router

**Archivo**: `app/routers/habitaciones.py`

```python
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from app.core.database import ObtenerSesionBD
from app.core.dependencies import ObtenerAdministrador

router = APIRouter(prefix="/habitaciones", tags=["Habitaciones"])
```

**Parámetros**:
- `prefix`: Prefijo para todas las rutas
- `tags`: Agrupa endpoints en la documentación

### 9.3 Endpoint GET - Listar

```python
@router.get("", response_model=List[HabitacionResponse])
def ListarHabitaciones(
    Saltar: int = Query(0, ge=0),
    Limite: int = Query(100, ge=1, le=100),
    SesionBD: Session = Depends(ObtenerSesionBD)
):
    Servicio = ServicioHabitacion(SesionBD)
    return Servicio.ListarHabitaciones(Saltar=Saltar, Limite=Limite)
```

**Query Parameters**:
- `Query(0, ge=0)`: Valor por defecto 0, mínimo 0
- `Query(100, ge=1, le=100)`: Valor por defecto 100, entre 1 y 100

**Ruta resultante**: `GET /api/v1/habitaciones?skip=0&limit=100`

### 9.4 Endpoint POST - Crear

```python
@router.post("", 
    response_model=HabitacionResponse, 
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(ObtenerAdministrador)]
)
def CrearHabitacion(
    DatosHabitacion: HabitacionCreate, 
    SesionBD: Session = Depends(ObtenerSesionBD)
):
    Servicio = ServicioHabitacion(SesionBD)
    return Servicio.CrearHabitacion(DatosHabitacion)
```

**Características**:
- `response_model`: Define el schema de respuesta
- `status_code`: Código HTTP de respuesta (201 Created)
- `dependencies`: Requiere autenticación de administrador

### 9.5 Endpoint GET con Parámetro de Ruta

```python
@router.get("/{habitacion_id}", response_model=HabitacionResponse)
def ObtenerHabitacion(
    habitacion_id: int, 
    SesionBD: Session = Depends(ObtenerSesionBD)
):
    Servicio = ServicioHabitacion(SesionBD)
    return Servicio.ObtenerHabitacion(habitacion_id)
```

**Parámetro de Ruta**: `{habitacion_id}` se convierte en parámetro de función.

**Ruta resultante**: `GET /api/v1/habitaciones/123`

### 9.6 Endpoint PUT - Actualizar

```python
@router.put("/{habitacion_id}", 
    response_model=HabitacionResponse, 
    dependencies=[Depends(ObtenerAdministrador)]
)
def ActualizarHabitacion(
    habitacion_id: int,
    DatosHabitacion: HabitacionUpdate,
    SesionBD: Session = Depends(ObtenerSesionBD)
):
    Servicio = ServicioHabitacion(SesionBD)
    return Servicio.ActualizarHabitacion(habitacion_id, DatosHabitacion)
```

### 9.7 Endpoint DELETE - Eliminar

```python
@router.delete("/{habitacion_id}", 
    dependencies=[Depends(ObtenerAdministrador)]
)
def EliminarHabitacion(
    habitacion_id: int, 
    SesionBD: Session = Depends(ObtenerSesionBD)
):
    Servicio = ServicioHabitacion(SesionBD)
    Servicio.EliminarHabitacion(habitacion_id)
    return {"message": "Habitación eliminada correctamente"}
```

### 9.8 Endpoint con Autenticación de Usuario

```python
@router.post("", response_model=ReservaResponse, status_code=201)
def CrearReserva(
    DatosReserva: ReservaCreate,
    UsuarioActual: Usuario = Depends(ObtenerUsuario),
    SesionBD: Session = Depends(ObtenerSesionBD)
):
    Servicio = ServicioReserva(SesionBD)
    return Servicio.CrearReserva(UsuarioActual.id, DatosReserva)
```

**Ventaja**: `UsuarioActual` ya está validado y disponible.

### 9.9 Endpoint con Validación de Permisos

```python
@router.get("/{reserva_id}", response_model=ReservaResponse)
def ObtenerReserva(
    reserva_id: int,
    UsuarioActual: Usuario = Depends(ObtenerUsuario),
    SesionBD: Session = Depends(ObtenerSesionBD)
):
    Servicio = ServicioReserva(SesionBD)
    ReservaEncontrada = Servicio.ObtenerReserva(reserva_id)
    
    # Validar permisos
    if not UsuarioActual.es_administrador and ReservaEncontrada.usuario_id != UsuarioActual.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tiene permiso para ver esta reserva"
        )
    
    return ReservaEncontrada
```

### 9.10 Registrar Routers en la Aplicación

**Archivo**: `app/main.py`

```python
from app.routers import auth, habitaciones, reservas, pagos

app.include_router(auth.router, prefix=settings.API_V1_PREFIX)
app.include_router(habitaciones.router, prefix=settings.API_V1_PREFIX)
app.include_router(reservas.router, prefix=settings.API_V1_PREFIX)
app.include_router(pagos.router, prefix=settings.API_V1_PREFIX)
```

**Rutas finales**:
- `/api/v1/auth/*`
- `/api/v1/habitaciones/*`
- `/api/v1/reservas/*`
- `/api/v1/pagos/*`

---

## Capítulo 10: Dependencias y Middleware

### 10.1 ¿Qué son las Dependencias?

Las **Dependencias** en FastAPI son funciones que se ejecutan antes del endpoint y pueden:
- Validar datos
- Autenticar usuarios
- Inyectar servicios
- Modificar requests/responses

### 10.2 Dependencia de Sesión de BD

```python
def ObtenerSesionBD():
    SesionBD = SessionLocal()
    try:
        yield SesionBD
    except Exception:
        SesionBD.rollback()
        raise
    finally:
        SesionBD.close()
```

**Generator Function** (`yield`):
- Crea la sesión
- La retorna para usar
- Hace cleanup automático

### 10.3 Dependencia de Usuario Actual

```python
async def ObtenerUsuario(
    Token: str = Depends(oauth2_scheme),
    SesionBD: Session = Depends(ObtenerSesionBD)
):
    # Validar token y retornar usuario
    ...
```

**Composición**: Usa otras dependencias (`oauth2_scheme`, `ObtenerSesionBD`).

### 10.4 Middleware CORS

**Archivo**: `app/main.py`

```python
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],           # Permitir todos los orígenes
    allow_credentials=True,         # Permitir cookies
    allow_methods=["*"],            # Permitir todos los métodos
    allow_headers=["*"],           # Permitir todos los headers
)
```

**CORS (Cross-Origin Resource Sharing)**:
- Permite que frontend en otro dominio acceda a la API
- En producción, especificar orígenes permitidos:
  ```python
  allow_origins=["https://royalpalms.com"]
  ```

### 10.5 Middleware Personalizado

```python
from fastapi import Request
import time

@app.middleware("http")
async def AgregarTiempoProcesamiento(request: Request, call_next):
    InicioTiempo = time.time()
    response = await call_next(request)
    TiempoProcesamiento = time.time() - InicioTiempo
    response.headers["X-Process-Time"] = str(TiempoProcesamiento)
    return response
```

**Casos de Uso**:
- Logging de requests
- Medición de tiempo
- Modificación de headers
- Rate limiting

---

## Capítulo 11: Manejo de Errores y Validaciones

### 11.1 HTTPException

FastAPI usa `HTTPException` para errores HTTP:

```python
from fastapi import HTTPException, status

raise HTTPException(
    status_code=status.HTTP_404_NOT_FOUND,
    detail="Recurso no encontrado"
)
```

**Códigos HTTP Comunes**:
- `200 OK`: Éxito
- `201 Created`: Recurso creado
- `400 Bad Request`: Datos inválidos
- `401 Unauthorized`: No autenticado
- `403 Forbidden`: Sin permisos
- `404 Not Found`: Recurso no existe
- `500 Internal Server Error`: Error del servidor

### 11.2 Validación Automática de Pydantic

FastAPI valida automáticamente usando Pydantic:

```python
@router.post("/habitaciones")
def CrearHabitacion(DatosHabitacion: HabitacionCreate):
    # Si DatosHabitacion no cumple el schema, FastAPI retorna 422 automáticamente
    ...
```

**Error 422 Unprocessable Entity**: Datos no válidos según el schema.

### 11.3 Validación de Query Parameters

```python
@router.get("/habitaciones")
def Listar(
    Saltar: int = Query(0, ge=0),      # ge = greater or equal
    Limite: int = Query(100, ge=1, le=100)  # le = less or equal
):
    ...
```

**Validaciones**:
- `ge`: Mayor o igual que
- `le`: Menor o igual que
- `gt`: Mayor que
- `lt`: Menor que

### 11.4 Manejo de Excepciones de Base de Datos

```python
def Crear(self, HabitacionNueva: Habitacion) -> Habitacion:
    try:
        self.SesionBD.add(HabitacionNueva)
        self.SesionBD.commit()
        return HabitacionNueva
    except IntegrityError:
        self.SesionBD.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Violación de restricción única"
        )
```

### 11.5 Handler Global de Excepciones

```python
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

@app.exception_handler(ValueError)
async def ManejarValorError(request: Request, exc: ValueError):
    return JSONResponse(
        status_code=400,
        content={"detail": str(exc)}
    )
```

---

## Capítulo 12: Despliegue y Producción

### 12.1 Configuración para Producción

#### Variables de Entorno

```env
DATABASE_URL=postgresql://usuario:contraseña@servidor:5432/bd
SECRET_KEY=clave_super_segura_generada_aleatoriamente
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
API_V1_PREFIX=/api/v1
PROJECT_NAME=RoyalPalms API
```

#### Configuración de CORS

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://royalpalms.com"],  # Especificar orígenes
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["*"],
)
```

### 12.2 Servidor de Producción

#### Uvicorn con Workers

```bash
uvicorn app.main:app \
    --host 0.0.0.0 \
    --port 8000 \
    --workers 4
```

**Workers**: Múltiples procesos para manejar más requests.

#### Gunicorn + Uvicorn

```bash
gunicorn app.main:app \
    -w 4 \
    -k uvicorn.workers.UvicornWorker \
    --bind 0.0.0.0:8000
```

### 12.3 Variables de Entorno en Producción

- **Docker**: Usar `docker-compose.yml` con `env_file`
- **Cloud**: Configurar en el panel de control
- **Servidor**: Usar archivo `.env` (asegurar permisos)

### 12.4 Base de Datos en Producción

#### Configuración del Pool

```python
engine = create_engine(
    settings.DATABASE_URL,
    pool_pre_ping=True,
    pool_recycle=300,
    pool_size=10,          # Aumentar para producción
    max_overflow=20,       # Aumentar para producción
    echo=False
)
```

#### Backup Regular

```bash
pg_dump -U usuario nombre_bd > backup.sql
```

### 12.5 Logging

```python
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('app.log'),
        logging.StreamHandler()
    ]
)
```

### 12.6 Monitoreo

- **Health Check**: Endpoint `/health`
- **Métricas**: Tiempo de respuesta, errores
- **Logs**: Registrar requests importantes

---

## Capítulo 13: Buenas Prácticas y Patrones

### 13.1 Arquitectura en Capas

**Separación de Responsabilidades**:
- Routers: Solo HTTP
- Services: Lógica de negocio
- Repositories: Acceso a datos
- Models: Estructura de BD

### 13.2 Nomenclatura

**PascalCase para Funciones y Variables**:
```python
def CrearHabitacion(DatosHabitacion: HabitacionCreate):
    HabitacionNueva = Habitacion(...)
    return Repositorio.Crear(HabitacionNueva)
```



### 13.3 Manejo de Transacciones

**Siempre hacer rollback en errores**:
```python
try:
    self.SesionBD.add(objeto)
    self.SesionBD.commit()
except Exception:
    self.SesionBD.rollback()
    raise
```

### 13.4 Validaciones

**Múltiples Niveles**:
1. Schema (Pydantic): Validación de tipos
2. Service: Validación de reglas de negocio
3. Database: Restricciones de integridad

### 13.5 Seguridad

**Nunca**:
- ❌ Exponer contraseñas en respuestas
- ❌ Loggear información sensible
- ❌ Commitear SECRET_KEY
- ❌ Usar contraseñas débiles

**Siempre**:
- ✅ Hash de contraseñas
- ✅ Validar tokens
- ✅ Usar HTTPS en producción
- ✅ Validar permisos

### 13.6 Testing

**Estructura de Tests**:
```python
def test_crear_habitacion():
    # Arrange
    datos = HabitacionCreate(...)
    
    # Act
    resultado = servicio.CrearHabitacion(datos)
    
    # Assert
    assert resultado.id is not None
```

### 13.7 Documentación

- **Docstrings**: Documentar funciones complejas
- **Type Hints**: Siempre usar tipos
- **Schemas**: Documentación automática de API

---

## Capítulo 14: Casos de Uso y Ejemplos

### 14.1 Flujo Completo: Crear Reserva

#### 1. Cliente hace Request

```http
POST /api/v1/reservas
Authorization: Bearer <token>
Content-Type: application/json

{
  "habitacion_id": 1,
  "fecha_entrada": "2024-01-15",
  "fecha_salida": "2024-01-20",
  "numero_huespedes": 2,
  "notas": "Cama extra"
}
```

#### 2. Router recibe Request

```python
@router.post("", response_model=ReservaResponse)
def CrearReserva(
    DatosReserva: ReservaCreate,
    UsuarioActual: Usuario = Depends(ObtenerUsuario),
    SesionBD: Session = Depends(ObtenerSesionBD)
):
    Servicio = ServicioReserva(SesionBD)
    return Servicio.CrearReserva(UsuarioActual.id, DatosReserva)
```

#### 3. Service valida y crea

```python
def CrearReserva(self, IdUsuario: int, DatosReserva: ReservaCreate):
    # Validaciones...
    # Crear objeto...
    return self.Repositorio.Crear(ReservaNueva)
```

#### 4. Repository guarda en BD

```python
def Crear(self, ReservaNueva: Reserva):
    self.SesionBD.add(ReservaNueva)
    self.SesionBD.commit()
    return ReservaNueva
```

#### 5. Response al Cliente

```json
{
  "id": 123,
  "usuario_id": 1,
  "habitacion_id": 1,
  "fecha_entrada": "2024-01-15",
  "fecha_salida": "2024-01-20",
  "numero_huespedes": 2,
  "precio_total": "500.00",
  "estado": "pendiente",
  "notas": "Cama extra",
  "fecha_creacion": "2024-01-10T10:00:00"
}
```

### 14.2 Ejemplo: Buscar Habitaciones Disponibles

```python
# Request
GET /api/v1/habitaciones/buscar?fecha_entrada=2024-01-15&fecha_salida=2024-01-20&capacidad=2

# Repository ejecuta consulta compleja
def BuscarDisponibles(self, FechaEntrada, FechaSalida, Capacidad):
    # Subconsulta: habitaciones ocupadas
    # Consulta principal: habitaciones disponibles
    # Filtros opcionales
    return Consulta.all()

# Response
[
  {
    "id": 1,
    "numero": "101",
    "tipo": "doble",
    "capacidad": 2,
    "precio_por_noche": "100.00"
  },
  ...
]
```

### 14.3 Ejemplo: Procesar Pago

```python
# 1. Crear pago
POST /api/v1/pagos
{
  "reserva_id": 123,
  "metodo_pago": "tarjeta_credito"
}

# 2. Procesar pago (admin)
POST /api/v1/pagos/456/procesar

# Service actualiza estado
pago.estado = EstadoPago.COMPLETADO
reserva.estado = EstadoReserva.CONFIRMADA
```


## Conclusión

Este documento cubre todos los aspectos del proyecto:

1. **Arquitectura**: Capas definidas
2. **Base de Datos**: Modelos y relaciones
3. **API REST**: Endpoints estructurados
4. **Seguridad**: Autenticación JWT 


### Recursos Adicionales

- [Documentación FastAPI](https://fastapi.tiangolo.com/)
- [Documentación SQLAlchemy](https://docs.sqlalchemy.org/)
- [Documentación Pydantic](https://docs.pydantic.dev/)
- [JWT.io](https://jwt.io/) - Para entender tokens JWT

---

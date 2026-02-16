# Guía de Estilo y Arquitectura para `backendhotel`

## 1. Introducción

Este documento establece las directrices de arquitectura, estructura de código y convenciones de nomenclatura para el proyecto `backendhotel`. El objetivo es mantener un código consistente, legible y mantenible a medida que el proyecto evoluciona. Todo el código nuevo debe adherirse a estas guías.

## 2. Arquitectura General

El proyecto sigue una **arquitectura por capas** clásica, diseñada para separar responsabilidades y desacoplar los componentes. El flujo de una solicitud HTTP es el siguiente:

**Router → Service → Repository → Model (SQLAlchemy)**

- **Routers (`app/routers/`)**: Define los endpoints de la API con FastAPI. Su única responsabilidad es recibir las solicitudes HTTP, validar los datos de entrada (usando dependencias y schemas Pydantic), y pasar la solicitud al servicio correspondiente. No contiene lógica de negocio.
- **Services (`app/services/`)**: Contiene la lógica de negocio principal. Orquesta las operaciones, realiza validaciones de negocio complejas y coordina la interacción entre diferentes repositorios si es necesario. Lanza excepciones HTTP (`HTTPException`) ante errores de negocio.
- **Repositories (`app/repositories/`)**: Es la capa de acceso a datos. Se encarga exclusivamente de las interacciones con la base de datos (CRUD). Utiliza SQLAlchemy para construir y ejecutar consultas. Retorna objetos modelo de SQLAlchemy.
- **Models (`app/models/`)**: Define las tablas de la base de datos como clases de SQLAlchemy (ORM). Representa la estructura de los datos.
- **Schemas (`app/schemas/`)**: Define la forma de los datos para la validación de la API (entrada y salida) usando Pydantic. Sirven como la "interfaz" de la API.
- **Core (`app/core/`)**: Contiene la configuración central, la gestión de la base de datos, la seguridad (autenticación, hashing), y otras dependencias transversales.

## 3. Estructura de Directorios

La estructura del proyecto está organizada por funcionalidad y capa, promoviendo una clara separación de conceptos.

```
backendhotel/
├── app/
│   ├── core/           # Configuración, BD, seguridad, dependencias
│   ├── models/         # Modelos de datos SQLAlchemy
│   ├── repositories/   # Lógica de acceso a datos
│   ├── routers/        # Endpoints de la API (FastAPI)
│   ├── schemas/        # Schemas de validación (Pydantic)
│   ├── services/       # Lógica de negocio
│   └── main.py         # Punto de entrada de la aplicación FastAPI
├── docs/
│   └── DOCUMENTACION_ENDPOINTS.md
├── .env.example        # Plantilla de variables de entorno
├── Dockerfile          # Definición del contenedor Docker
├── requirements.txt    # Dependencias de Python
└── agents.md           # Esta guía
```

## 4. Convenciones de Nomenclatura

Se utilizan dos convenciones principales: **`PascalCase`** para clases y funciones/métodos, y **`snake_case`** para todo lo demás. Esta distinción es crucial para la legibilidad del código.

| Elemento | Convención | Ejemplos |
| :--- | :--- | :--- |
| **Clases** | `PascalCase` | `class ServicioHabitacion:`, `class HabitacionRepository:`, `class Habitacion(Base):`, `class HabitacionCreate(BaseModel):` |
| **Métodos y Funciones** | `PascalCase` | `def CrearHabitacion(...)`, `def ObtenerPorId(...)`, `def VerificarContrasena(...)`, `def ObtenerUsuario(...)` |
| **Variables y Parámetros** | `PascalCase` | `HabitacionEncontrada`, `DatosReserva`, `SesionBD`, `IdUsuario` |
| **Atributos de Instancia** | `PascalCase` | `self.Repositorio`, `self.SesionBD` |
| **Archivos Python** | `snake_case` | `habitacion_service.py`, `reserva_repository.py` |
| **Paquetes/Directorios** | `snake_case` | `app/core/`, `app/services/` |
| **Tablas en BD** | `snake_case` | `__tablename__ = "habitaciones"` |
| **Columnas en BD / Atributos de Modelo** | `snake_case` | `precio_por_noche`, `fecha_creacion`, `es_administrador` |
| **Campos de Schema Pydantic** | `snake_case` | `precio_por_noche`, `access_token`, `numero_huespedes` |
| **Variables Globales / Instancias** | `snake_case` | `router = APIRouter()`, `settings = Settings()` |
| **Parámetros de Ruta/Query en API** | `snake_case` | `@router.get("/{habitacion_id}")` |

### Resumen Práctico:

- **Usa `PascalCase` para todo lo que sea un bloque de código ejecutable (clases, métodos, funciones) y las variables que manejan dentro de esos bloques.**
- **Usa `snake_case` para la estructura del proyecto (archivos, directorios) y para los nombres que definen datos (columnas de BD, campos de schemas).**

## 5. Patrones de Código y Buenas Prácticas

### Docstrings

- Cada módulo (archivo `.py`) debe comenzar con un `docstring` de triple comilla que describa su propósito general. Es útil incluir una lista de las funciones o clases más importantes que define.

  ```python
  """
  Servicio de Habitaciones, se define la lógica de negocio para las habitaciones.
  - CrearHabitacion: Crea una nueva habitación.
  - ObtenerHabitacion: Obtiene una habitación por su ID.
  - ...
  """
  ```

### Capa de Servicios (`services`)

- El constructor siempre recibe la sesión de la base de datos: `def __init__(self, SesionBD: Session):`.
- Instancia los repositorios necesarios: `self.Repositorio = HabitacionRepository(SesionBD)`.
- Centraliza la lógica de negocio. Si una operación requiere datos de múltiples tablas, el servicio coordina los diferentes repositorios.
- Es el lugar adecuado para lanzar `HTTPException` en caso de errores de validación de negocio (ej: "La habitación no está disponible en esas fechas").

### Capa de Repositorios (`repositories`)

- Su única responsabilidad es interactuar con la base de datos. No debe contener lógica de negocio.
- Los métodos deben ser genéricos y reutilizables (ej: `ObtenerPorId`, `Crear`, `Actualizar`).
- Utiliza `Saltar` y `Limite` como parámetros para implementar la paginación en los métodos que devuelven listas.

### Capa de Routers (`routers`)

- Mantiene la definición de los endpoints lo más simple posible.
- Utiliza `Depends` para la inyección de dependencias, principalmente `ObtenerSesionBD` y las funciones de autenticación como `ObtenerUsuario`.
- Delega toda la lógica al servicio correspondiente: `Servicio = ServicioUsuarios(SesionBD)`.

### Schemas Pydantic (`schemas`)

- Sigue la estructura `Base` → `Create` → `Update` → `Response`.
  - `...Base`: Campos comunes.
  - `...Create`: Hereda de `Base` y añade campos necesarios para la creación (ej: `password`).
  - `...Update`: Todos los campos son opcionales (`Optional[T] = None`).
  - `...Response`: Hereda de `Base` y añade campos que se devuelven desde la BD (ej: `id`, `fecha_creacion`). Debe incluir `class Config: from_attributes = True`.

## 6. Flujo de Trabajo: Añadir una Nueva Entidad

Para ilustrar cómo aplicar estas guías, aquí está el proceso para añadir una nueva entidad, por ejemplo, `Producto`.

1.  **Modelo (`app/models/producto.py`)**: Crear la clase `Producto(Base)` con sus columnas en `snake_case`.

2.  **Schema (`app/schemas/producto.py`)**: Definir `ProductoBase`, `ProductoCreate`, `ProductoUpdate` y `ProductoResponse` siguiendo las convenciones.

3.  **Repositorio (`app/repositories/producto_repository.py`)**: Crear `ProductoRepository` con métodos `PascalCase` como `ObtenerPorId`, `Crear`, etc.

4.  **Servicio (`app/services/producto_service.py`)**: Crear `ServicioProducto`, que utiliza `ProductoRepository` para implementar la lógica de negocio (`CrearProducto`, `ActualizarProducto`, etc.).

5.  **Router (`app/routers/productos.py`)**: Crear un nuevo `router` y definir los endpoints (`CrearProducto`, `ObtenerProducto`) que dependen de `ObtenerSesionBD` y llaman a los métodos del `ServicioProducto`.

6.  **Principal (`app/main.py`)**: Incluir el nuevo router en la aplicación principal: `app.include_router(productos.router, ...)`.

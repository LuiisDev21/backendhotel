# RoyalPalms Backend — API REST

API REST del sistema de reservas de hotel **RoyalPalms**. Backend desarrollado con **FastAPI**, **PostgreSQL** y **SQLAlchemy**, con autenticación JWT, control de acceso por roles (RBAC), procedimientos almacenados y auditoría inmutable.

---

## Tabla de contenidos

1. [Descripción del proyecto](#1-descripción-del-proyecto)
2. [Tecnologías](#2-tecnologías)
3. [Estructura del proyecto](#3-estructura-del-proyecto)
4. [Requisitos e instalación](#4-requisitos-e-instalación)
5. [Configuración](#5-configuración)
6. [Base de datos](#6-base-de-datos)
7. [Arquitectura y capas](#7-arquitectura-y-capas)
8. [Autenticación y autorización](#8-autenticación-y-autorización)
9. [API — Resumen de endpoints](#9-api--resumen-de-endpoints)
10. [Referencias](#13-referencias)

---

## 1. Descripción del proyecto

Sistema backend para la gestión de un hotel que permite:

- **Usuarios y roles**: Registro, login, refresh token, logout, actualización de perfil (nombre, apellido, teléfono) y asignación de roles por permisos (RBAC). Nuevos usuarios reciben el rol **huésped** por defecto.
- **Tipos y habitaciones**: Catálogo de tipos de habitación y CRUD de habitaciones con estado, política de cancelación e imagen (Supabase Storage).
- **Reservas**: Creación mediante procedimiento almacenado (con desglose de precios), previsualización de precio antes de confirmar, listado (propias o todas para admin), actualización, cancelación y historial de estados. No se permite cancelar reservas **completadas** ni **no-show**.
- **Pagos**: Una sola transacción de pago total por reserva (sin pagos parciales). Cargos, reembolsos y estados en disputa; coherencia contable (cargos positivos, reembolsos negativos) y reembolso de pagos en disputa según políticas.
- **Políticas de cancelación**: Catálogo consultable; penalizaciones aplicadas al cancelar reservas confirmadas según la política de la habitación.
- **Configuración**: Parámetros del hotel (moneda, impuestos, intentos de login, etc.) vía tabla `configuracion_hotel`.
- **Reportes**: Estadísticas de reservas, ingresos, ocupación, auditoría, ranking de clientes y dashboard (administrador).
- **Auditoría**: Registro inmutable de acciones (trigger que impide UPDATE/DELETE en la tabla de auditoría).

Prefijo base de la API: **`/api/v1`**.

---

## 2. Tecnologías

| Área              | Tecnología                          |
|-------------------|-------------------------------------|
| Framework         | FastAPI                             |
| Servidor ASGI     | Uvicorn                             |
| Base de datos     | PostgreSQL                          |
| ORM               | SQLAlchemy 2.x                      |
| Autenticación     | JWT (python-jose), OAuth2 Bearer    |
| Contraseñas       | Bcrypt (passlib)                    |
| Validación        | Pydantic v2                         |
| Configuración     | pydantic-settings, python-dotenv    |
| Almacenamiento   | Supabase Storage (imágenes habitaciones) |

---

## 3. Estructura del proyecto

```
backendhotel/
├── app/
│   ├── core/                 # Configuración, BD, seguridad, dependencias
│   │   ├── config.py
│   │   ├── database.py
│   │   ├── security.py
│   │   ├── dependencies.py   # ObtenerUsuario, TienePermiso (RBAC)
│   │   ├── enum_type.py
│   │   └── auditoria_helper.py
│   ├── models/               # Modelos SQLAlchemy
│   ├── schemas/              # Schemas Pydantic (entrada/salida API)
│   ├── repositories/         # Acceso a datos y procedimientos almacenados
│   ├── services/             # Lógica de negocio
│   ├── routers/              # Endpoints por recurso
│   └── main.py
├── database.sql              # Esquema completo (tablas, catálogos, SPs, triggers, vistas)
├── requirements.txt
├── .env.example
└── README.md
```

**Routers**: `auth`, `habitaciones`, `tipos_habitacion`, `reservas`, `pagos`, `reportes`, `politicas_cancelacion`, `configuracion`.

---

## 4. Requisitos e instalación

- **Python** 3.10+
- **PostgreSQL** 12+
- **pip**

```bash
# Clonar o abrir el proyecto
cd backendhotel

# Entorno virtual (recomendado)
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate

# Dependencias
pip install -r requirements.txt
```

---

## 5. Configuración

Copiar `.env.example` a `.env` y completar valores:

| Variable                     | Requerida | Descripción |
|-----------------------------|-----------|-------------|
| `DATABASE_URL`              | Sí        | URL de conexión PostgreSQL (ej. `postgresql://user:pass@host:5432/db`) |
| `SECRET_KEY`                | Sí        | Clave para firmar JWT (generar con `secrets.token_urlsafe(32)`) |
| `ALGORITHM`                 | No        | Algoritmo JWT (default: HS256) |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | No     | Minutos de validez del access token (default: 30) |
| `API_V1_PREFIX`             | No        | Prefijo de rutas (default: /api/v1) |
| `PROJECT_NAME`              | No        | Nombre de la API |
| `SUPABASE_URL` / `SUPABASE_KEY` / `SUPABASE_BUCKET` | No* | Subida de imágenes de habitaciones |
| `POOL_SIZE` / `MAX_OVERFLOW`| No        | Pool de conexiones SQLAlchemy |

\* Necesarios si se usan imágenes de habitaciones en Supabase.

---

## 6. Base de datos

- **Esquema principal**: ejecutar `database.sql` sobre una base PostgreSQL vacía para crear tablas, catálogos, índices, triggers, funciones y procedimientos almacenados.
- **Modelo de datos**:
  - **Catálogos** (sin ENUMs rígidos): `catalogo_estado_reserva`, `catalogo_metodo_pago`, `catalogo_estado_pago`, `catalogo_tipo_transaccion`, `catalogo_accion_auditoria`.
  - **Reservas**: desglose enterprise (moneda, tasa_cambio, subtotal, impuestos, descuentos, otros_cargos, precio_total) con CHECK de coherencia.
  - **Transacciones de pago**: tipo y monto coherentes (cargos/depósitos/ajuste/penalización > 0; reembolso < 0).
  - **Concurrencia**: bloqueo por habitación (`pg_advisory_xact_lock`) en la validación de solapamiento de reservas.
  - **Auditoría**: trigger que impide UPDATE/DELETE en la tabla `auditoria`.

**Procedimientos almacenados utilizados**: `sp_crear_habitacion`, `sp_buscar_habitaciones_disponibles`, `sp_crear_reserva`, `sp_procesar_pago`, `sp_obtener_estadisticas_reservas`. La función `registrar_auditoria` inserta en `auditoria` (parámetro `accion` como VARCHAR según catálogo).

```bash
# Ejemplo: ejecutar script en PostgreSQL
psql -U usuario -d nombre_bd -f database.sql
```

---

## 7. Arquitectura y capas

- **Routers**: Reciben peticiones HTTP, validan con schemas y delegan en servicios. Exigen autenticación y, donde aplica, permisos RBAC.
- **Services**: Lógica de negocio (validaciones, reglas de reservas/pagos/cancelación, llamadas a repositorios y a procedimientos almacenados).
- **Repositories**: Acceso a datos (CRUD, consultas, ejecución de SPs).
- **Models**: Entidades SQLAlchemy mapeadas a tablas.
- **Schemas**: Contratos Pydantic para request/response.

Flujo típico: **Request → Router → Service → Repository → BD**; respuesta serializada con los schemas de respuesta.

---

## 8. Autenticación y autorización

- **Login**: `POST /api/v1/auth/login` (email, password). Devuelve `access_token`, `refresh_token`, `token_type`, `expires_in`. Protección por intentos fallidos y bloqueo temporal (configurable vía `configuracion_hotel`).
- **Refresh**: `POST /api/v1/auth/refresh` con body `{ "refresh_token": "..." }`. Devuelve un nuevo access token; el refresh se almacena hasheado en `sesiones_usuario`.
- **Logout**: `POST /api/v1/auth/logout` con body `{ "refresh_token": "..." }`. Revoca la sesión asociada al token.
- **Usuario actual**: `GET /api/v1/auth/me` (header `Authorization: Bearer <access_token>`). Incluye roles y permisos.
- **Actualizar perfil**: `PUT /api/v1/auth/me` con body opcional `{ "nombre", "apellido", "telefono" }`.

**RBAC**: Los endpoints protegidos usan la dependencia `TienePermiso("codigo.permiso")`. Ejemplos de permisos: `usuarios.gestionar`, `habitaciones.gestionar`, `reservas.ver_todas`, `pagos.procesar`, `pagos.reembolsar`, `configuracion.modificar`. Los roles y sus permisos están en BD; el usuario se carga con roles y permisos para decidir acceso.

---

## 9. API — Resumen de endpoints

Todos bajo el prefijo **`/api/v1`**. Salvo indicación, requieren `Authorization: Bearer <access_token>`.

### Autenticación (`/auth`)

| Método | Ruta | Descripción | Auth |
|--------|------|-------------|------|
| POST   | `/auth/register` | Registro (asigna rol huésped) | No |
| POST   | `/auth/login` | Login (access + refresh token) | No |
| POST   | `/auth/refresh` | Nuevo access token | No (refresh_token en body) |
| POST   | `/auth/logout` | Cerrar sesión (revocar refresh) | No (refresh_token en body) |
| GET    | `/auth/me` | Usuario actual con roles | Sí |
| PUT    | `/auth/me` | Actualizar nombre, apellido, teléfono | Sí |
| GET    | `/auth/usuarios` | Listar usuarios | Sí + `usuarios.gestionar` |
| GET    | `/auth/roles` | Listar roles (id, nombre) | No* |
| PUT    | `/auth/usuarios/{usuario_id}/roles` | Asignar roles a usuario | Sí + `usuarios.gestionar` |

### Tipos de habitación (`/tipos-habitacion`)

| Método | Ruta | Descripción |
|--------|------|-------------|
| GET    | `/tipos-habitacion` | Listar tipos |
| GET    | `/tipos-habitacion/{tipo_id}` | Obtener por ID |

### Habitaciones (`/habitaciones`)

| Método | Ruta | Descripción | Permiso |
|--------|------|-------------|---------|
| POST   | `/habitaciones` | Crear habitación | `habitaciones.gestionar` |
| GET    | `/habitaciones` | Listar | Sí |
| GET    | `/habitaciones/buscar` | Disponibles por fechas/capacidad/tipo | Sí |
| GET    | `/habitaciones/{id}` | Obtener por ID | Sí |
| PUT    | `/habitaciones/{id}` | Actualizar | `habitaciones.gestionar` |
| DELETE | `/habitaciones/{id}` | Eliminar (validación de reservas activas) | `habitaciones.gestionar` |
| POST   | `/habitaciones/{id}/imagen` | Subir imagen (Supabase) | `habitaciones.gestionar` |

### Reservas (`/reservas`)

| Método | Ruta | Descripción | Permiso |
|--------|------|-------------|---------|
| POST   | `/reservas` | Crear reserva (vía SP, con desglose de precios) | Sí |
| POST   | `/reservas/previsualizar-precio` | Desglose de precio sin crear reserva | Sí |
| GET    | `/reservas` | Mis reservas | Sí |
| GET    | `/reservas/todas` | Todas las reservas | `reservas.ver_todas` |
| GET    | `/reservas/{id}` | Obtener reserva | Sí (propia o permiso) |
| GET    | `/reservas/{id}/historial-estados` | Historial de estados | Sí (propia o permiso) |
| PUT    | `/reservas/{id}` | Actualizar (fechas, etc.; recalcula precios) | Sí (propia o permiso) |
| POST   | `/reservas/{id}/cancelar` | Cancelar (no permitido si completada/no-show) | Sí (propia o permiso) |

### Pagos (`/pagos`)

| Método | Ruta | Descripción | Permiso |
|--------|------|-------------|---------|
| POST   | `/pagos` | Crear transacción (cargo; monto = pendiente total) | Sí (propia reserva) |
| GET    | `/pagos` | Listar todas las transacciones | `pagos.procesar` |
| GET    | `/pagos/reserva/{reserva_id}` | Transacciones de una reserva | Sí (propia reserva) o `pagos.procesar` |
| GET    | `/pagos/{id}` | Obtener transacción | Sí (propia reserva) o `pagos.procesar` |
| POST   | `/pagos/{id}/procesar` | Marcar como completado; confirma reserva si aplica | `pagos.procesar` |
| PUT    | `/pagos/{id}` | Actualizar transacción | `pagos.procesar` |
| POST   | `/pagos/{id}/reembolsar` | Reembolsar (completado o disputado) | `pagos.reembolsar` |

### Políticas de cancelación (`/politicas-cancelacion`)

| Método | Ruta | Descripción |
|--------|------|-------------|
| GET    | `/politicas-cancelacion` | Listar políticas |
| GET    | `/politicas-cancelacion/{id}` | Obtener por ID |

### Configuración (`/configuracion`)

| Método | Ruta | Descripción | Permiso |
|--------|------|-------------|---------|
| GET    | `/configuracion` | Listar claves/valores | `configuracion.modificar` |
| PATCH  | `/configuracion/{clave}` | Actualizar valor | `configuracion.modificar` |

### Reportes (`/reportes`)

| Método | Ruta | Descripción |
|--------|------|-------------|
| GET    | `/reportes/estadisticas-reservas` | Estadísticas de reservas |
| GET    | `/reportes/ingresos` | Ingresos por período |
| GET    | `/reportes/ocupacion` | Ocupación |
| GET    | `/reportes/auditoria` | Log de auditoría |
| GET    | `/reportes/clientes` | Ranking de clientes |
| GET    | `/reportes/dashboard` | Resumen dashboard |

---

## 10. Referencias

- [FastAPI](https://fastapi.tiangolo.com/)
- [SQLAlchemy](https://docs.sqlalchemy.org/)
- [Pydantic](https://docs.pydantic.dev/)
- [PostgreSQL](https://www.postgresql.org/docs/)

---

# RoyalPalms API — Documentación de Endpoints

## Base URL
```
http://localhost:8000/api/v1
```

## Autenticación

Los endpoints que requieren autenticación usan **Bearer Token** en el header:
```
Authorization: Bearer {access_token}
```

El **refresh token** se envía en el body (JSON) en los endpoints `/auth/refresh` y `/auth/logout`; no va en el header.

---

## 1. Módulo de Autenticación (`/auth`)

### 1.1. Registrar Usuario
**POST** `/auth/register`

**Descripción:** Crea un nuevo usuario. Se le asigna automáticamente el rol **huésped**.

**Autenticación:** No requerida

**Request Body (application/json):**
```json
{
  "email": "usuario@example.com",
  "nombre": "Juan",
  "apellido": "Pérez",
  "telefono": "+505 1234-5678",
  "password": "contraseña_segura"
}
```

**Response 201:**
```json
{
  "id": 1,
  "email": "usuario@example.com",
  "nombre": "Juan",
  "apellido": "Pérez",
  "telefono": "+505 1234-5678",
  "activo": true,
  "fecha_creacion": "2024-01-25T12:00:00",
  "roles": [{"id": 4, "nombre": "Huésped"}]
}
```

**Errores:** `400` (email ya registrado), `422` (validación)

---

### 1.2. Iniciar Sesión
**POST** `/auth/login`

**Descripción:** Autentica al usuario y devuelve access token y refresh token.

**Autenticación:** No requerida

**Request Body:**
```json
{
  "email": "usuario@example.com",
  "password": "contraseña"
}
```

**Response 200:**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "expires_in": 1800
}
```

**Errores:** `401` (credenciales incorrectas), `403` (usuario inactivo o bloqueado por intentos), `422` (validación)

---

### 1.3. Refrescar Token
**POST** `/auth/refresh`

**Descripción:** Obtiene un nuevo access token usando el refresh token (sin volver a enviar contraseña).

**Autenticación:** No requerida (se envía el refresh token en el body)

**Request Body:**
```json
{
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

**Response 200:** Mismo formato que login (`access_token`, `token_type`, `refresh_token`, `expires_in`).

**Errores:** `401` (refresh token inválido o expirado)

---

### 1.4. Cerrar Sesión (Logout)
**POST** `/auth/logout`

**Descripción:** Revoca la sesión asociada al refresh token (cierre de sesión correcto).

**Autenticación:** No requerida

**Request Body:**
```json
{
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

**Response 200:**
```json
{
  "detail": "Sesión cerrada correctamente"
}
```

**Errores:** `401` si el token no es válido (opcional según implementación)

---

### 1.5. Obtener Usuario Actual
**GET** `/auth/me`

**Descripción:** Devuelve el usuario autenticado con sus roles.

**Autenticación:** Requerida (Bearer)

**Response 200:**
```json
{
  "id": 1,
  "email": "usuario@example.com",
  "nombre": "Juan",
  "apellido": "Pérez",
  "telefono": "+505 1234-5678",
  "activo": true,
  "fecha_creacion": "2024-01-25T12:00:00",
  "roles": [{"id": 4, "nombre": "Huésped"}]
}
```

**Errores:** `401` (token inválido o expirado)

---

### 1.6. Actualizar Mi Perfil
**PUT** `/auth/me`

**Descripción:** El usuario autenticado actualiza su nombre, apellido y/o teléfono (no email ni contraseña).

**Autenticación:** Requerida

**Request Body (campos opcionales):**
```json
{
  "nombre": "Juan",
  "apellido": "Pérez",
  "telefono": "+505 1234-5678"
}
```

**Response 200:** Usuario actualizado con roles (mismo formato que GET `/auth/me`).

**Errores:** `401` (no autenticado), `422` (validación)

---

### 1.7. Listar Usuarios
**GET** `/auth/usuarios`

**Descripción:** Lista todos los usuarios (paginado). Requiere permiso **usuarios.gestionar**.

**Autenticación:** Requerida + permiso `usuarios.gestionar`

**Query Parameters:**
- `Saltar` (integer, opcional): Registros a omitir (default: 0, ge: 0)
- `Limite` (integer, opcional): Máximo de registros (default: 100, ge: 1, le: 100)

**Response 200:** Array de usuarios con `id`, `email`, `nombre`, `apellido`, `telefono`, `activo`, `fecha_creacion`, `roles`.

**Errores:** `401` (no autenticado), `403` (sin permiso usuarios.gestionar)

---

### 1.8. Listar Roles
**GET** `/auth/roles`

**Descripción:** Lista los roles disponibles (id, nombre) para asignar a usuarios. Útil para formularios de administración.

**Autenticación:** No requerida

**Response 200:**
```json
[
  {"id": 1, "nombre": "Administrador"},
  {"id": 4, "nombre": "Huésped"}
]
```

---

### 1.9. Asignar Roles a Usuario
**PUT** `/auth/usuarios/{usuario_id}/roles`

**Descripción:** Asigna los roles indicados al usuario (reemplaza los actuales). Requiere permiso **usuarios.gestionar**.

**Autenticación:** Requerida + permiso `usuarios.gestionar`

**Path Parameters:** `usuario_id` (integer)

**Request Body:**
```json
{
  "rol_ids": [1, 4]
}
```

**Response 200:** Usuario actualizado con sus nuevos roles (mismo formato que GET `/auth/me`).

**Errores:** `401`, `403` (sin permiso), `404` (usuario no encontrado), `422` (validación)

---

## 1b. Tipos de Habitación (`/tipos-habitacion`)

Catálogo de tipos de habitación (Individual, Doble, Suite, etc.). Sin autenticación requerida.

### 1b.1. Listar Tipos
**GET** `/tipos-habitacion`

**Response 200:** Array de tipos con `id`, `codigo`, `nombre`, `descripcion`, `capacidad_maxima`, `precio_base`, `activo`, etc.

### 1b.2. Obtener Tipo por ID
**GET** `/tipos-habitacion/{tipo_id}`

**Path Parameters:** `tipo_id` (integer)

**Response 200:** Objeto tipo. **Errores:** `404` si no existe.

---

## 2. Módulo de Habitaciones (`/habitaciones`)

### 2.1. Crear Habitación
**POST** `/habitaciones`

**Descripción:** Crea una nueva habitación. Opcionalmente se puede subir una imagen a Supabase Storage. Requiere permiso **habitaciones.gestionar**.

**Autenticación:** Requerida + permiso `habitaciones.gestionar`

**Content-Type:** `multipart/form-data`

**Request Body (FormData):**
- `numero` (string, requerido): Número único de la habitación
- `tipo_habitacion_id` (integer, requerido): ID del tipo en `tipos_habitacion`
- `politica_cancelacion_id` (integer, opcional): ID de política de cancelación
- `descripcion` (string, opcional)
- `capacidad` (integer, requerido): Capacidad de huéspedes (mín. 1; no puede exceder la capacidad máxima del tipo)
- `precio_por_noche` (float, requerido)
- `estado` (string, opcional): default `"disponible"`
- `piso` (integer, opcional)
- `archivo` (file, opcional): Imagen (JPEG, PNG, WebP; ej. máx. 5MB)

**Response 201:** Objeto habitación con `id`, `numero`, `tipo_habitacion_id`, `tipo_nombre`, `politica_cancelacion_id`, `politica_nombre`, `descripcion`, `capacidad`, `precio_por_noche`, `estado`, `imagen_url`, `piso`, `fecha_creacion`, `fecha_actualizacion`.

**Errores:** `400` (número duplicado, capacidad excede tipo, archivo inválido), `401`, `403`, `404` (tipo no existe), `422`

---

### 2.2. Listar Habitaciones
**GET** `/habitaciones`

**Descripción:** Lista habitaciones con paginación.

**Autenticación:** No requerida

**Query Parameters:**
- `Saltar` (integer, opcional): default 0, ge 0
- `Limite` (integer, opcional): default 100, ge 1, le 100

**Response 200:** Array de habitaciones (incluyen `tipo_nombre`, `politica_nombre`).

---

### 2.3. Buscar Habitaciones Disponibles
**GET** `/habitaciones/buscar`

**Descripción:** Busca habitaciones disponibles en un rango de fechas (sin solapamiento con reservas no canceladas).

**Autenticación:** No requerida

**Query Parameters:**
- `FechaEntrada` (date, requerido): YYYY-MM-DD
- `FechaSalida` (date, requerido): YYYY-MM-DD
- `Capacidad` (integer, opcional, ge 1): Capacidad mínima
- `TipoHabitacionId` (integer, opcional): Filtrar por tipo

**Ejemplo:** `GET /habitaciones/buscar?FechaEntrada=2024-02-01&FechaSalida=2024-02-05&Capacidad=2`

**Response 200:** Array de habitaciones disponibles (mismo formato que listar).

**Errores:** `400` (fecha salida no posterior a entrada), `422`

---

### 2.4. Obtener Habitación por ID
**GET** `/habitaciones/{habitacion_id}`

**Descripción:** Devuelve una habitación por ID.

**Autenticación:** No requerida

**Path Parameters:** `habitacion_id` (integer)

**Response 200:** Objeto habitación con `tipo_nombre`, `politica_nombre`.

**Errores:** `404` (habitación no encontrada)

---

### 2.5. Actualizar Habitación
**PUT** `/habitaciones/{habitacion_id}`

**Descripción:** Actualiza una habitación. Si se envía `archivo`, se sube a Supabase y se actualiza `imagen_url`. Requiere permiso **habitaciones.gestionar**.

**Autenticación:** Requerida + permiso `habitaciones.gestionar`

**Content-Type:** `multipart/form-data`

**Path Parameters:** `habitacion_id` (integer)

**Request Body (FormData):**
- `tipo_habitacion_id` (integer, requerido)
- `politica_cancelacion_id` (integer, opcional)
- `descripcion` (string, opcional)
- `capacidad` (integer, requerido)
- `precio_por_noche` (float, requerido)
- `estado` (string, opcional): default `"disponible"`
- `archivo` (file, opcional)

**Response 200:** Habitación actualizada.

**Errores:** `400`, `401`, `403`, `404`, `422`

---

### 2.6. Eliminar Habitación
**DELETE** `/habitaciones/{habitacion_id}`

**Descripción:** Elimina la habitación. Solo permitido si no hay reservas activas (pendiente/confirmada); las reservas completadas/canceladas y sus transacciones se eliminan en cascada. Requiere permiso **habitaciones.gestionar**.

**Autenticación:** Requerida + permiso `habitaciones.gestionar`

**Path Parameters:** `habitacion_id` (integer)

**Response 200:** `{"message": "Habitación eliminada correctamente"}`

**Errores:** `400` (tiene reservas activas), `401`, `403`, `404`

---

### 2.7. Subir Imagen de Habitación
**POST** `/habitaciones/{habitacion_id}/imagen`

**Descripción:** Sube o reemplaza la imagen de la habitación en Supabase Storage. Requiere permiso **habitaciones.gestionar**.

**Autenticación:** Requerida + permiso `habitaciones.gestionar`

**Content-Type:** `multipart/form-data`

**Path Parameters:** `habitacion_id` (integer)

**Request Body:** `archivo` (file, requerido) — JPEG, PNG, WebP; tamaño máximo recomendado 5MB.

**Response 200:**
```json
{
  "message": "Imagen subida correctamente",
  "imagen_url": "https://...",
  "habitacion": { ... }
}
```

**Errores:** `400` (archivo no permitido), `401`, `403`, `404`, `500` (Supabase no configurado o error de subida)

---

## 3. Módulo de Reservas (`/reservas`)

### 3.1. Crear Reserva
**POST** `/reservas`

**Descripción:** Crea una nueva reserva para el usuario autenticado. El precio se calcula en BD (procedimiento almacenado) con desglose: subtotal, impuestos, descuentos, otros_cargos, precio_total, moneda.

**Autenticación:** Requerida

**Request Body (application/json):**
```json
{
  "habitacion_id": 1,
  "fecha_entrada": "2024-02-01",
  "fecha_salida": "2024-02-05",
  "numero_huespedes": 2,
  "notas": "Llegada tarde",
  "canal_reserva": "web",
  "politica_cancelacion_id": null
}
```

**Response 201:** Reserva con `id`, `usuario_id`, `habitacion_id`, `codigo_reserva`, `moneda`, `subtotal`, `impuestos`, `descuentos`, `otros_cargos`, `precio_total`, `precio_por_noche_snapshot`, `estado`, `numero_habitacion`, `nombre_usuario`, `fecha_creacion`, `fecha_actualizacion`, y opcionalmente `transacciones`.

**Errores:** `400` (habitación no disponible, fechas inválidas, capacidad excedida), `401`, `404`, `422`

---

### 3.2. Previsualizar Precio de Reserva
**POST** `/reservas/previsualizar-precio`

**Descripción:** Calcula y devuelve el desglose de precios (moneda, subtotal, impuestos, descuentos, otros_cargos, precio_total) **sin crear** la reserva. Útil para mostrar el total al usuario antes de confirmar.

**Autenticación:** Requerida

**Request Body:** Igual que crear reserva (`habitacion_id`, `fecha_entrada`, `fecha_salida`, `numero_huespedes`, `notas`, etc.).

**Response 200:**
```json
{
  "habitacion_id": 1,
  "fecha_entrada": "2024-02-01",
  "fecha_salida": "2024-02-05",
  "numero_huespedes": 2,
  "notas": null,
  "moneda": "USD",
  "subtotal": "300.00",
  "impuestos": "30.00",
  "descuentos": "0.00",
  "otros_cargos": "0.00",
  "precio_total": "330.00"
}
```

**Errores:** `400`, `401`, `404`, `422`

---

### 3.3. Listar Mis Reservas
**GET** `/reservas`

**Descripción:** Lista las reservas del usuario autenticado (paginado).

**Autenticación:** Requerida

**Query Parameters:** `Saltar` (default 0), `Limite` (default 100, ge 1, le 100)

**Response 200:** Array de reservas con desglose de precios, `numero_habitacion`, `nombre_usuario`, `transacciones` (opcional).

---

### 3.4. Listar Todas las Reservas
**GET** `/reservas/todas`

**Descripción:** Lista todas las reservas del sistema. Requiere permiso **reservas.ver_todas**.

**Autenticación:** Requerida + permiso `reservas.ver_todas`

**Query Parameters:** `Saltar`, `Limite`

**Response 200:** Array de reservas (mismo formato que 3.3).

**Errores:** `401`, `403`

---

### 3.5. Obtener Reserva por ID
**GET** `/reservas/{reserva_id}`

**Descripción:** Obtiene una reserva. El cliente solo puede ver las suyas; con permiso `reservas.ver_todas` puede ver cualquiera.

**Autenticación:** Requerida

**Path Parameters:** `reserva_id` (integer)

**Response 200:** Reserva con desglose de precios, `numero_habitacion`, `nombre_usuario`, `transacciones`.

**Errores:** `401`, `403`, `404`

---

### 3.6. Historial de Estados de una Reserva
**GET** `/reservas/{reserva_id}/historial-estados`

**Descripción:** Devuelve el historial de cambios de estado de la reserva (trazabilidad). Mismo criterio de acceso que ver la reserva.

**Autenticación:** Requerida

**Path Parameters:** `reserva_id` (integer)

**Response 200:** Array de objetos con `id`, `reserva_id`, `estado_anterior`, `estado_nuevo`, `motivo`, `cambiado_por`, `fecha_cambio`.

**Errores:** `401`, `403`, `404`

---

### 3.7. Actualizar Reserva
**PUT** `/reservas/{reserva_id}`

**Descripción:** Actualiza una reserva. Si se cambian `fecha_entrada` o `fecha_salida`, se recalcula el desglose de precios (subtotal, impuestos, precio_total). Cliente solo puede actualizar las suyas; admin o permiso puede actualizar cualquiera.

**Autenticación:** Requerida

**Path Parameters:** `reserva_id` (integer)

**Request Body (todos opcionales):**
```json
{
  "fecha_entrada": "2024-02-01",
  "fecha_salida": "2024-02-06",
  "numero_huespedes": 2,
  "estado": "pendiente",
  "notas": "Notas actualizadas"
}
```

**Response 200:** Reserva actualizada.

**Errores:** `400` (habitación no disponible en nuevas fechas), `401`, `403`, `404`, `422`

---

### 3.8. Cancelar Reserva
**POST** `/reservas/{reserva_id}/cancelar`

**Descripción:** Cancela la reserva. **No se puede cancelar** si el estado es **completada** o **no_show**. Si la reserva está pendiente o confirmada, los pagos (cargos) asociados pasan a estado **disputado**; el administrador puede gestionar reembolsos después. Cliente solo puede cancelar las suyas; admin/permiso cualquiera.

**Autenticación:** Requerida

**Path Parameters:** `reserva_id` (integer)

**Response 200:** Reserva con `estado: "cancelada"`.

**Errores:** `400` (ya cancelada, o es completada/no_show), `401`, `403`, `404`

---

## 3b. Políticas de cancelación (`/politicas-cancelacion`)

### 3b.1. Listar políticas de cancelación
**GET** `/politicas-cancelacion`

**Descripción:** Lista políticas de cancelación (para formularios de reserva y admin).

**Autenticación:** No requerida

**Query Parameters:**
- `SoloActivos` (boolean, default true): solo políticas activas
- `Saltar` (integer, default 0), `Limite` (integer, default 100, ge 1, le 100)

**Response 200:** Array de políticas (id, nombre, descripcion, horas_anticipacion, porcentaje_penalizacion, activa, etc.).

### 3b.2. Obtener política por ID
**GET** `/politicas-cancelacion/{politica_id}`

**Descripción:** Obtiene una política por ID.

**Path Parameters:** `politica_id` (integer)

**Response 200:** Objeto política. **Errores:** `404` si no existe.

---

## 3c. Configuración del hotel (`/configuracion`)

### 3c.1. Listar configuración
**GET** `/configuracion`

**Descripción:** Lista las claves de configuración del hotel (moneda, impuestos, intentos de login, etc.). Requiere permiso **configuracion.modificar**.

**Autenticación:** Requerida + permiso `configuracion.modificar`

**Query Parameters:** `Saltar` (default 0), `Limite` (default 500, ge 1, le 500)

**Response 200:** Array de items con `clave`, `valor`, `tipo`, `descripcion`, `modificable`, `fecha_actualizacion`.

### 3c.2. Actualizar valor de una clave
**PATCH** `/configuracion/{clave}`

**Descripción:** Actualiza el valor de una clave (solo si es modificable). Requiere permiso **configuracion.modificar**.

**Autenticación:** Requerida + permiso `configuracion.modificar`

**Path Parameters:** `clave` (string)

**Request Body:**
```json
{ "valor": "nuevo_valor" }
```

**Response 200:** Item de configuración actualizado. **Errores:** `400` (clave no modificable), `404` (clave no existe)

---

## 4. Módulo de Pagos — Transacciones (`/pagos`)

El módulo de pagos trabaja con **transacciones de pago**: una reserva puede tener varias transacciones (un cargo principal, reembolsos, ajustes, penalizaciones). Reglas: **un solo cargo total por reserva** (no pagos parciales); el monto del cargo debe coincidir con el pendiente; reembolsos generan una transacción tipo reembolso (monto negativo) y marcan el cargo original como reembolsado. Se pueden reembolsar transacciones en estado **completado** o **disputado**.

### 4.1. Crear Transacción (Cargo)
**POST** `/pagos`

**Descripción:** Crea una transacción de tipo **cargo** para una reserva. El usuario debe ser dueño de la reserva o tener permiso `pagos.procesar`. El monto debe ser el pendiente de la reserva (no se permiten pagos parciales).

**Autenticación:** Requerida (propietario de la reserva o permiso)

**Request Body (application/json):**
```json
{
  "reserva_id": 1,
  "tipo": "cargo",
  "monto": "330.00",
  "metodo_pago": "tarjeta_credito",
  "numero_transaccion": null,
  "referencia_externa": null,
  "pasarela_pago": null,
  "moneda": "USD",
  "notas": null
}
```

**Métodos de pago válidos:** `tarjeta_credito`, `tarjeta_debito`, `efectivo`, `transferencia`, `paypal`, `cripto`

**Response 201:** Transacción creada con `id`, `reserva_id`, `tipo`, `monto`, `metodo_pago`, `estado` (pendiente), `numero_transaccion`, `moneda`, `fecha_creacion`, etc.

**Errores:** `400` (ya existe cargo total, monto no coincide con pendiente, reglas de negocio), `401`, `403`, `404`, `422`

---

### 4.2. Listar Todas las Transacciones
**GET** `/pagos`

**Descripción:** Lista todas las transacciones de pago. Requiere permiso **pagos.procesar**.

**Autenticación:** Requerida + permiso `pagos.procesar`

**Query Parameters:** `Saltar` (default 0), `Limite` (default 100, ge 1, le 100)

**Response 200:** Array de transacciones (id, reserva_id, tipo, monto, metodo_pago, estado, numero_transaccion, moneda, fecha_pago, fecha_creacion, etc.).

---

### 4.3. Listar Transacciones por Reserva
**GET** `/pagos/reserva/{reserva_id}`

**Descripción:** Lista las transacciones asociadas a una reserva. El usuario debe ser dueño de la reserva o tener permiso `pagos.procesar`.

**Autenticación:** Requerida

**Path Parameters:** `reserva_id` (integer)

**Response 200:** Array de transacciones de esa reserva (cargos, reembolsos, etc.).

**Errores:** `401`, `403`, `404`

---

### 4.4. Obtener Transacción por ID
**GET** `/pagos/{transaccion_id}`

**Descripción:** Obtiene una transacción. Mismo criterio de acceso que por reserva (dueño o permiso pagos.procesar).

**Autenticación:** Requerida

**Path Parameters:** `transaccion_id` (integer)

**Response 200:** Objeto transacción con todos los campos.

**Errores:** `401`, `403`, `404`

---

### 4.5. Procesar Transacción
**POST** `/pagos/{transaccion_id}/procesar`

**Descripción:** Marca la transacción como **completado** y actualiza la reserva a **confirmada** si corresponde. Requiere permiso **pagos.procesar**.

**Autenticación:** Requerida + permiso `pagos.procesar`

**Path Parameters:** `transaccion_id` (integer)

**Response 200:** Transacción actualizada (estado completado, fecha_pago asignada).

**Errores:** `400` (ya procesada, tipo no es cargo, etc.), `401`, `403`, `404`

---

### 4.6. Actualizar Transacción
**PUT** `/pagos/{transaccion_id}`

**Descripción:** Actualiza estado, numero_transaccion, fecha_pago o notas. Requiere permiso **pagos.procesar**.

**Autenticación:** Requerida + permiso `pagos.procesar`

**Path Parameters:** `transaccion_id` (integer)

**Request Body (opcionales):**
```json
{
  "estado": "completado",
  "numero_transaccion": "REF-123",
  "fecha_pago": "2024-01-25T12:30:00",
  "notas": "Pagado con tarjeta"
}
```

**Response 200:** Transacción actualizada.

**Errores:** `401`, `403`, `404`, `422`

---

### 4.7. Reembolsar Transacción
**POST** `/pagos/{transaccion_id}/reembolsar`

**Descripción:** Reembolsa un cargo. Solo se puede reembolsar si el estado es **completado** o **disputado** (p. ej. tras cancelar una reserva los cargos pasan a disputado). Crea una nueva transacción tipo reembolso (monto negativo) y marca el cargo como **reembolsado**. La reserva asociada puede pasar a cancelada según lógica de negocio. Requiere permiso **pagos.reembolsar**.

**Autenticación:** Requerida + permiso `pagos.reembolsar`

**Path Parameters:** `transaccion_id` (integer)

**Response 200:** Transacción de reembolso creada y/o cargo actualizado.

**Errores:** `400` (ya reembolsado, tipo reembolso, estado no completado/disputado), `401`, `403`, `404`

---

## 5. Módulo de Reportes (`/reportes`)

Todos los endpoints de reportes requieren permiso **reportes.ver**.

### 5.1. Estadísticas de Reservas
**GET** `/reportes/estadisticas-reservas`

**Query Parameters:** `fecha_inicio` (date, opcional), `fecha_fin` (date, opcional)

**Response 200:** Totales por estado, ingresos, promedios en el período.

### 5.2. Ingresos por Período
**GET** `/reportes/ingresos`

**Query Parameters:** `fecha_inicio`, `fecha_fin`

**Response 200:** Total de ingresos y desglose por método de pago.

### 5.3. Ocupación
**GET** `/reportes/ocupacion`

**Query Parameters:** `fecha_inicio` (date, requerido), `fecha_fin` (date, requerido), `agrupar_por` ("habitacion" | "tipo", default "habitacion")

**Response 200:** Ocupación (noches, ingresos) por habitación o por tipo.

### 5.4. Log de Auditoría
**GET** `/reportes/auditoria`

**Query Parameters:** `fecha_desde`, `fecha_hasta`, `usuario_id`, `accion`, `tabla_afectada`, `Saltar`, `Limite`

**Response 200:** Lista de registros de auditoría con filtros aplicados.

### 5.5. Ranking de Clientes
**GET** `/reportes/clientes`

**Query Parameters:** `fecha_inicio`, `fecha_fin`, `orden` ("reservas" | "gastado", default "gastado"), `Limite` (default 50, ge 1, le 200)

**Response 200:** Lista de clientes ordenada por número de reservas o por total gastado.

### 5.6. Dashboard
**GET** `/reportes/dashboard`

**Query Parameters:** `fecha_inicio`, `fecha_fin`

**Response 200:** Resumen agregado para panel de control (estadísticas, ingresos, ocupación, etc.).

---

## Estados y valores

### Estados de Reserva
- `pendiente`: Creada, esperando pago
- `confirmada`: Pago completado
- `cancelada`: Cancelada
- `completada`: Check-out realizado
- `no_show`: No se presentó

### Tipos de Transacción
- `cargo`: Pago a favor del hotel (monto > 0)
- `reembolso`: Devolución (monto < 0)
- `ajuste`, `penalizacion`, etc. según catálogo

### Estados de Transacción/Pago
- `pendiente`, `completado`, `rechazado`, `reembolsado`, `en_proceso`, `disputado`

### Métodos de Pago
- `tarjeta_credito`, `tarjeta_debito`, `efectivo`, `transferencia`, `paypal`, `cripto`

---

## Códigos de Estado HTTP

- `200 OK`: Operación exitosa
- `201 Created`: Recurso creado
- `400 Bad Request`: Solicitud inválida o regla de negocio
- `401 Unauthorized`: No autenticado o token inválido
- `403 Forbidden`: Sin permiso para la operación
- `404 Not Found`: Recurso no encontrado
- `422 Unprocessable Entity`: Error de validación (Pydantic)

---

## Notas importantes

1. **JWT**: El access token expira según `ACCESS_TOKEN_EXPIRE_MINUTES`. Use `POST /auth/refresh` con el refresh token para obtener uno nuevo. Use `POST /auth/logout` para cerrar sesión.

2. **RBAC**: Los endpoints protegen por **permisos** (ej. `usuarios.gestionar`, `habitaciones.gestionar`, `reservas.ver_todas`, `pagos.procesar`, `pagos.reembolsar`, `configuracion.modificar`, `reportes.ver`), no solo por rol “administrador”.

3. **Paginación**: Los listados usan `Saltar` y `Limite` (no skip/limit).

4. **Fechas**: Formato ISO 8601 (YYYY-MM-DD). La fecha de salida debe ser posterior a la de entrada.

5. **Precios**: Reservas incluyen desglose enterprise: `moneda`, `subtotal`, `impuestos`, `descuentos`, `otros_cargos`, `precio_total`. Use `POST /reservas/previsualizar-precio` para mostrar el total antes de crear la reserva.

6. **Variables de entorno**: Ver `.env.example`. Obligatorias: `DATABASE_URL`, `SECRET_KEY`. Opcionales: `ALGORITHM`, `ACCESS_TOKEN_EXPIRE_MINUTES`, `API_V1_PREFIX`, `PROJECT_NAME`, `SUPABASE_*`, `POOL_SIZE`, `MAX_OVERFLOW`.

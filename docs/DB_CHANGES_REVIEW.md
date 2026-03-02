### Cambios técnicos aplicados tras la revisión de base de datos

Este documento resume los cambios realizados en la **base de datos** y su relación con el **backend** para responder a los comentarios del revisor.

---

### 1. Concurrencia y overbooking en reservas

**Problema detectado**  
Se usaba la función `fn_validar_no_solapamiento_reserva()` con un `EXISTS` para evitar solapamientos, pero sin bloqueo explícito sobre el recurso lógico. Con alta concurrencia, dos transacciones podían pasar el `EXISTS` y crear reservas solapadas para la misma habitación.

**Solución aplicada**  
Se añadió un bloqueo lógico por habitación usando `pg_advisory_xact_lock` dentro de la función:

- Fichero: `database_final.sql`
- Función modificada: `fn_validar_no_solapamiento_reserva`

Comportamiento:
- Antes de comprobar solapamientos, se ejecuta:
  - `PERFORM pg_advisory_xact_lock(NEW.habitacion_id);`
- Esto garantiza que, para una `habitacion_id` concreta, solo una transacción a la vez puede validar/insertar/actualizar reservas.  
- Combinado con el `EXISTS` sobre `reservas`, elimina la condición de carrera que permitía doble reserva en el mismo rango de fechas.

**Impacto en el backend**  
El backend ya utilizaba la tabla `reservas` y esta función vía trigger, por lo que **no fue necesario cambiar código Python**.  
El cambio es totalmente transparente para la API, pero mejora la robustez ante alta concurrencia.

---

### 2. Coherencia contable de montos en `transacciones_pago`

**Problema detectado**  
La tabla `transacciones_pago` tenía solo:

- `CHECK (monto != 0)`

pero no se forzaba que:

- CARGOS / DEPÓSITOS / AJUSTES / PENALIZACIONES fueran **monto positivo**, y  
- REEMBOLSOS fueran **monto negativo**.

Esto podía llevar a inconsistencias contables (por ejemplo, un reembolso con monto positivo).

**Solución aplicada (nivel SQL)**  

- Fichero: `database_final.sql`
- Tabla: `transacciones_pago`

Se añadió una nueva restricción:

```sql
CONSTRAINT chk_monto_tipo_coherente CHECK (
    (tipo IN ('cargo','deposito','ajuste','penalizacion') AND monto > 0)
    OR
    (tipo = 'reembolso' AND monto < 0)
),
```

La restricción existente `chk_monto_no_cero` se mantiene:

- `monto` nunca puede ser 0.

**Solución aplicada (nivel backend)**  
El backend ya estaba alineado con este modelo:

- Cargos (pagos normales) se crean con monto positivo.  
- Reembolsos se crean con monto negativo (`monto = -abs(original)`).

Además, recientemente se endureció la lógica de dominio:

- No se permiten pagos parciales: el cargo debe ser exactamente igual al pendiente de la reserva.
- Solo se puede tener un **cargo total** por reserva.
- Al reembolsar:
  - Se crea una transacción tipo `REEMBOLSO` con monto negativo.
  - El cargo original pasa a estado `REEMBOLSADO`.
  - La reserva se marca como `cancelada`.

Estos cambios en el servicio de pagos (`ServicioTransaccionPago`) ya cumplían las nuevas reglas de la base de datos, por lo que el añadido de la `CHECK` simplemente refuerza la coherencia a nivel SQL.

**Impacto en el backend y API**  
- No fue necesario cambiar la interfaz de la API.  
- Los cambios son internos al dominio de pagos (ya implementados) y a la base de datos.  
- Si algún flujo futuro intentara crear un reembolso positivo o un cargo negativo, fallará a nivel de BD con un error claro.

---

### 3. Fragilidad de `precio_total` en reservas → Modelo de precios enterprise

**Comentario del revisor**  
Se señaló que `reservas.precio_total` era “frágil” porque:

- No almacenaba desglose de impuestos, descuentos, moneda, tasa de cambio, etc.
- En un hotel enterprise real se modelan precio base, impuestos, cargos adicionales, descuentos, promociones y tarifas dinámicas.

**Solución aplicada (nuevo modelo enterprise)**  

Se rediseñó la tabla `reservas` y la lógica de creación/actualización de reservas para introducir un **desglose completo de precios**, manteniendo compatibilidad con el resto del sistema:

- Fichero: `database_final.sql`
- Tabla: `reservas`

Nuevas columnas:

- `moneda CHAR(3) NOT NULL DEFAULT 'USD'`
- `tasa_cambio NUMERIC(10,6) NOT NULL DEFAULT 1.0`
- `subtotal NUMERIC(12,2) NOT NULL` — importe base de la estancia (precio por noche * nº noches).
- `impuestos NUMERIC(12,2) NOT NULL DEFAULT 0`
- `descuentos NUMERIC(12,2) NOT NULL DEFAULT 0`
- `otros_cargos NUMERIC(12,2) NOT NULL DEFAULT 0`
- `precio_total NUMERIC(12,2) NOT NULL` — se mantiene, pero ahora se define como:
  - `precio_total = subtotal + otros_cargos + impuestos - descuentos`

Se añadió la `CHECK`:

```sql
CONSTRAINT chk_precio_total_desglose CHECK (
    precio_total = subtotal + otros_cargos + impuestos - descuentos
)
```

**Lógica de cálculo en `sp_crear_reserva`**

En el SP `sp_crear_reserva`:

- Se calcula `subtotal := precio_por_noche * (fecha_salida - fecha_entrada)`.
- Se lee la moneda por defecto desde `configuracion_hotel` (`hotel_moneda`), con fallback a `'USD'`.
- Se lee el porcentaje de impuesto desde `configuracion_hotel` (`impuesto_porcentaje`).
- Se calculan:
  - `impuestos := ROUND(subtotal * impuesto_pct / 100, 2)`
  - `descuentos := 0` (por ahora)
  - `otros_cargos := 0`
  - `precio_total := subtotal + otros_cargos + impuestos - descuentos`
- Se insertan todos estos valores en `reservas` junto con `moneda` y `tasa_cambio = 1.0`.

**Lógica de recálculo en el backend (cambios de fechas)**

En `ServicioReserva.ActualizarReserva`:

- Cuando cambian `fecha_entrada` o `fecha_salida`:
  - Se valida disponibilidad de la habitación con el nuevo rango.
  - Se recalcula:
    - `subtotal` en base al `precio_por_noche` de la habitación y nº de noches.
    - `moneda` e `impuestos` desde `configuracion_hotel` (claves `hotel_moneda` e `impuesto_porcentaje`).
    - `descuentos` y `otros_cargos` se conservan de la reserva existente.
    - `precio_total = subtotal + otros_cargos + impuestos - descuentos`.
  - Se actualizan todas estas columnas en el objeto `Reserva`.

**Vistas y reportes**

- `vista_reservas_completas` ahora expone:
  - `moneda`, `subtotal`, `impuestos`, `descuentos`, `otros_cargos`, además de `precio_total`.
- `sp_obtener_estadisticas_reservas` y `mv_estadisticas_mensuales` siguen usando `precio_total` para ingresos y promedios, que ahora es consistente con el desglose.

**Script de migración enterprise**

- Fichero: `database_migration_enterprise_pricing.sql`

Acciones principales:

1. `ALTER TABLE reservas` para añadir las nuevas columnas.
2. Inicializar datos existentes:
   - `subtotal := precio_total` (para reservas históricas).
   - `impuestos`, `descuentos`, `otros_cargos` a 0.
   - `moneda := 'USD'` y `tasa_cambio := 1.0` si estaban nulos.
3. Crear/actualizar la `CHECK` `chk_precio_total_desglose`.
4. Recrear `vista_reservas_completas` incluyendo el desglose.

**Impacto en el backend y la API**

- Modelo `Reserva` (SQLAlchemy) actualizado con los nuevos campos.
- `ReservaResponse` (Pydantic) ahora devuelve también:
  - `moneda`, `subtotal`, `impuestos`, `descuentos`, `otros_cargos`, además de `precio_total`.
- La API de creación de reservas (**inputs**) no cambia: el cliente sigue enviando solo habitación, fechas y nº de huéspedes; el backend calcula el desglose.

Con esto, el comentario de “precio_total frágil” queda resuelto con un **modelo de precios enterprise**, manteniendo la compatibilidad de la API y enriqueciendo tanto backend como reportes.

---

### 4. Auditoría verdaderamente inmutable

**Problema detectado**  
La tabla `auditoria` se describe como “inmutable”, pero:

- No existía restricción técnica que impidiera `UPDATE` o `DELETE` directos sobre la tabla.
- Sin RLS ni triggers de bloqueo, un usuario con permisos suficientes podía modificar registros de auditoría.

**Solución aplicada (nivel SQL)**  

- Fichero: `database_final.sql`
- Tabla: `auditoria`

Se añadieron:

```sql
CREATE OR REPLACE FUNCTION fn_bloquear_modificacion_auditoria()
RETURNS TRIGGER AS $$
BEGIN
    RAISE EXCEPTION 'La tabla de auditoría es inmutable: no se permiten UPDATE ni DELETE sobre auditoria'
        USING ERRCODE = 'P0100';
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_bloquear_modificacion_auditoria
    BEFORE UPDATE OR DELETE ON auditoria
    FOR EACH ROW EXECUTE FUNCTION fn_bloquear_modificacion_auditoria();
```

Efecto:
- Cualquier intento de `UPDATE` o `DELETE` sobre `auditoria` falla con un error explícito.
- La única vía para insertar registros sigue siendo la función `registrar_auditoria(...)` (que ya es `SECURITY DEFINER`).

**Impacto en el backend**  
- El backend no hace `UPDATE`/`DELETE` sobre `auditoria`, solo inserta mediante la función `registrar_auditoria`.  
- Por lo tanto, **no hay cambios necesarios en el código**; la protección es transparente.

---

### 5. Uso de ENUMs vs tablas catálogo

**Comentario del revisor**  
Se indicó que el uso de `ENUM` en PostgreSQL para:

- `estado_reserva`
- `metodo_pago`
- `estado_pago`
- `tipo_transaccion`

es más rígido que usar tablas catálogo, ya que cambiar un `ENUM` en producción implica migraciones cuidadosas.

**Decisión en esta iteración**  
- **No se eliminaron los ENUMs existentes** para evitar una migración masiva y cambios en el código del backend.  
- Se documenta que:
  - Para nuevas funcionalidades o tipos adicionales, la estrategia recomendada a futuro es introducir tablas catálogo y, eventualmente, migrar desde ENUMs a FKs.
  - El diseño actual es aceptable para el tamaño del proyecto y el alcance actual.

En el README de respuesta se explica esta decisión como un compromiso entre flexibilidad futura y estabilidad del sistema actual.

---

### 6. Script de migración para bases ya desplegadas

Se creó un script de migración separado:

- Fichero: `database_migration_review_fix.sql`

Que incluye:

1. `CREATE OR REPLACE FUNCTION fn_validar_no_solapamiento_reserva()`  
   - Añade `pg_advisory_xact_lock(NEW.habitacion_id)` para serializar reservas por habitación.

2. `ALTER TABLE transacciones_pago ...`  
   - Añade la `CHECK` `chk_monto_tipo_coherente` sin eliminar la `chk_monto_no_cero`.

3. Función y trigger para hacer inmutable la tabla `auditoria`:
   - `fn_bloquear_modificacion_auditoria`
   - `trg_bloquear_modificacion_auditoria`

Este script permite aplicar solo los cambios necesarios sobre una base de datos ya existente (por ejemplo, en producción) sin recrear todo el esquema.


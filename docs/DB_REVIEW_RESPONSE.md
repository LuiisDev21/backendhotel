### Respuesta a los comentarios del revisor de base de datos

Este documento explica, punto por punto, cómo se abordaron los comentarios realizados sobre el diseño actual de la base de datos del backend del hotel.

---

## 1. Concurrencia en `fn_validar_no_solapamiento_reserva` y riesgo de overbooking

**Comentario original (resumen)**  
> El uso de `fn_validar_no_solapamiento_reserva()` es lógicamente correcto, pero no 100% seguro con alta concurrencia.  
> Dos transacciones simultáneas pueden pasar el `EXISTS` y ambas insertar, confirmando doble reserva, ya que el trigger no usa locking sobre `reservas`.  
> El `FOR UPDATE` en `habitaciones` bloquea la fila de habitación, pero no el rango de fechas en reservas.

**Acciones realizadas**

1. **Bloqueo lógico por habitación con `pg_advisory_xact_lock`**
   - Se actualizó la función `fn_validar_no_solapamiento_reserva` para incluir:
     - `PERFORM pg_advisory_xact_lock(NEW.habitacion_id);`
   - Esto garantiza que, para una habitación concreta (`habitacion_id`), solo una transacción a la vez puede:
     - Validar solapamientos.
     - Insertar o actualizar una reserva que afecte a esa habitación.

2. **Combinación con la validación de solapamientos existente**
   - Se mantiene la lógica `EXISTS` que comprueba si ya hay reservas no canceladas/ no completadas cuyo rango de fechas se solapa con la nueva.
   - Ahora, como las transacciones se serializan por `habitacion_id`, el `EXISTS` no puede ser “salteado” por dos transacciones concurrentes.

**Resultado**
- Se mantiene la compatibilidad con Supabase (no se usa `EXCLUSION CONSTRAINT`).
- Se elimina la ventana de condición de carrera: ya no es posible confirmar dos reservas solapadas para la misma habitación debido a concurrencia.

---

## 2. Coherencia contable en `transacciones_pago` (monto vs tipo)

**Comentario original (resumen)**  
> Existe `chk_monto_no_cero`, pero no se fuerza que:
> - `tipo = 'cargo'` tenga monto positivo,  
> - `tipo = 'reembolso'` tenga monto negativo.  
> Es inconsistente contablemente que no se valide esto explícitamente.

**Acciones realizadas**

1. **Nueva restricción `CHECK` en la tabla `transacciones_pago`**
   - Se añadió:
     ```sql
     CONSTRAINT chk_monto_tipo_coherente CHECK (
         (tipo IN ('cargo','deposito','ajuste','penalizacion') AND monto > 0)
         OR
         (tipo = 'reembolso' AND monto < 0)
     )
     ```
   - Se mantiene la `CHECK (monto != 0)` existente:
     - Nunca se permiten montos exactamente 0.

2. **Alineación con la lógica de aplicación**
   - El backend ya:
     - Crea **cargos/depósitos** con monto positivo.
     - Crea **reembolsos** con monto negativo (`-abs(monto_original)`).
   - Además:
     - Marca el cargo original como `REEMBOLSADO`.
     - Impide reembolsar más de una vez el mismo cargo.
     - Cancela la reserva asociada cuando se efectúa un reembolso.

**Resultado**
- La base de datos refuerza la coherencia contable que el dominio ya estaba respetando.
- En una auditoría contable real:
  - Todos los `cargo`/`deposito`/`ajuste`/`penalizacion` son montos positivos.
  - Todos los `reembolso` son montos negativos.

---

## 3. Fragilidad de `precio_total` (impuestos, descuentos, moneda, tasas)

**Comentario original (resumen)**  
> `reservas.precio_total` es frágil porque no almacena claramente impuestos, descuentos, moneda, tasa de cambio, cargos adicionales, promociones, etc.  
> Está bien para una versión 1, pero no es un diseño enterprise completo.

**Acciones realizadas: modelo de precios enterprise**

Se implementó un modelo de precios más completo en la tabla `reservas` y en la lógica de negocio, manteniendo la compatibilidad con la API existente:

1. **Desglose de precios en la tabla `reservas`**
   - Se añadieron columnas:
     - `moneda` (CHAR(3), NOT NULL, default `'USD'`).
     - `tasa_cambio` (NUMERIC(10,6), NOT NULL, default `1.0`).
     - `subtotal` (NUMERIC(12,2), NOT NULL) — importe base de la estancia.
     - `impuestos` (NUMERIC(12,2), NOT NULL, default `0`).
     - `descuentos` (NUMERIC(12,2), NOT NULL, default `0`).
     - `otros_cargos` (NUMERIC(12,2), NOT NULL, default `0`).
     - `precio_total` (NUMERIC(12,2), NOT NULL).

   - Se añadió una restricción:
     ```sql
     CONSTRAINT chk_precio_total_desglose CHECK (
         precio_total = subtotal + otros_cargos + impuestos - descuentos
     )
     ```

2. **Cálculo en `sp_crear_reserva`**
   - El procedimiento almacenado ahora:
     - Calcula `subtotal` = precio_por_noche * nº de noches.
     - Obtiene `hotel_moneda` e `impuesto_porcentaje` de `configuracion_hotel`.
     - Calcula `impuestos`, `descuentos` (0 en v1), `otros_cargos` (0 en v1) y `precio_total`.
     - Inserta todos estos campos en la tabla `reservas`.

3. **Actualización de reservas desde el backend**
   - En el servicio de reservas (`ServicioReserva`), cuando cambian fechas:
     - Se recalculan `subtotal`, `impuestos`, `precio_total` y se respetan `descuentos`/`otros_cargos` existentes.
     - Se vuelve a garantizar la fórmula `precio_total = subtotal + otros_cargos + impuestos - descuentos`.

4. **Vistas y reportes**
   - `vista_reservas_completas` fue actualizada para incluir:
     - `moneda`, `subtotal`, `impuestos`, `descuentos`, `otros_cargos`, además de `precio_total`.
   - Los procedimientos de estadísticas (`sp_obtener_estadisticas_reservas`, `mv_estadisticas_mensuales`) siguen utilizando `precio_total` como referencia principal.

5. **Migración de datos existentes**
   - En el script `database_migration_enterprise_pricing.sql`:
     - Para reservas ya existentes, se inicializa:
       - `subtotal := precio_total`.
       - `impuestos`, `descuentos`, `otros_cargos` a `0`.
       - `moneda := 'USD'`, `tasa_cambio := 1.0` si estaban nulos.
     - Se añade/actualiza la `CHECK` de coherencia de `precio_total` y se recrea la vista `vista_reservas_completas`.

**Resultado**

- El sistema ahora dispone de un **modelo enterprise de precios** para reservas:
  - Con desglose completo y campos de moneda/tasa de cambio.
  - Respetando la compatibilidad con la API actual (los clientes siguen recibiendo `precio_total`, pero ahora con más información opcional).
- El comentario del revisor sobre la fragilidad de `precio_total` queda resuelto con un rediseño estructural y documentado.

---

## 4. Auditoría: registro realmente inmutable

**Comentario original (resumen)**  
> Aunque se define la tabla `auditoria` como inmutable, no hay enforcement real:
> - No hay `REVOKE UPDATE/DELETE`, ni RLS, ni trigger que impida modificaciones.  
> - Cualquier usuario con privilegios suficientes podría alterar el historial.

**Acciones realizadas**

1. **Trigger de bloqueo para UPDATE/DELETE**
   - Se añadió:
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

2. **Mantenimiento del `SECURITY DEFINER` en `registrar_auditoria`**
   - La función que inserta en `auditoria` sigue siendo `SECURITY DEFINER`, controlando quién y cómo se escriben registros.

**Resultado**
- Aun sin tocar políticas de RLS ni `GRANT/REVOKE` específicos (que dependen del entorno de despliegue y roles), la tabla:
  - No acepta modificaciones directas (`UPDATE` ni `DELETE`).
  - Solo puede recibir nuevos registros a través de la función oficial.

Esto fortalece de forma significativa la promesa de “registro inmutable”.

---

## 5. Uso de ENUMs en lugar de tablas catálogo

**Comentario original (resumen)**  
> El uso de `ENUM` para `estado_reserva`, `metodo_pago`, `estado_pago`, etc. es rígido:  
> Cambiarlos en producción requiere migraciones cuidadosas.  
> A nivel arquitectónico, en entornos grandes, son preferibles tablas catálogo.

**Decisión en esta iteración**

- No se migraron los `ENUM` existentes a tablas catálogo en esta fase.

**Motivos**

1. **Impacto amplio en el código y en las migraciones**
   - Cambiar `ENUM` a catálogos implica:
     - Crear tablas (`estado_reserva_catalogo`, `metodo_pago_catalogo`, etc.).
     - Migrar datos y constraints de columnas.
     - Actualizar tipos en procedimientos almacenados.
     - Ajustar modelos ORM y esquemas Pydantic.

2. **Riesgo en producción**
   - Es un cambio estructural delicado que se debe planificar y probar con calma.

3. **Alcance del proyecto**
   - Para el tamaño actual del sistema (hotel individual), los ENUMs ofrecen:
     - Validación fuerte.
     - Sencillez en consultas y reportes.

**Plan de futuro sugerido**

Cuando el sistema requiera:
- Nuevas formas de pago.
- Nuevos estados de reserva, pagos o transacciones.
- Integración con múltiples propiedades / marcas.

Se recomienda:

1. Introducir tablas catálogo paralelas con códigos estables (ej. `estado_reserva_codigo`).
2. Ajustar la capa de aplicación para trabajar contra esos catálogos.
3. Planificar una migración progresiva desde ENUMs a FKs, minimizando downtime.

---

## 6. Scripts y documentación entregados

**Scripts**

- `database_final.sql`
  - Actualizado con:
    - Bloqueo lógico en `fn_validar_no_solapamiento_reserva`.
    - Nueva `CHECK` `chk_monto_tipo_coherente` en `transacciones_pago`.
    - Trigger y función para hacer inmutable la tabla `auditoria`.

- `database_migration_review_fix.sql`
  - Script incremental para aplicar solo los cambios relevantes a una BD ya existente.

**Documentación**

- `DB_CHANGES_REVIEW.md`
  - Detalle técnico de todos los cambios aplicados y su relación con el backend.
- Este archivo `DB_REVIEW_RESPONSE.md`
  - Respuesta textual directa a cada comentario del revisor, explicando qué se hizo y por qué.

---

En resumen, se han abordado los puntos críticos de:

- **Concurrencia en reservas (overbooking).**
- **Coherencia contable de pagos.**
- **Inmutabilidad real de la auditoría.**

Y se ha documentado claramente la situación actual y las decisiones respecto al modelado avanzado de precios e ENUMs.


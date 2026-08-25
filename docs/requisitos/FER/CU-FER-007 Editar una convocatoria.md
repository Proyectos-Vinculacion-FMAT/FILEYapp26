---
estado: propuesta
version: "0.1"
tags:
  - tipo/caso-de-uso
  - dom/fer
  - tema/formularios
fecha: 2026-08-25
fecha_actualizacion: 2026-08-25
id: CU-FER-007
dominio: FER
responsable: Hugo Janssen
reglas_de_negocio: []
diagramas_relacionados: []
trazabilidad:
  ddr: []
---
# CU-FER-007 Editar una convocatoria

## Objetivo

Permitir al dueño de la feria corregir el nombre y las fechas anunciadas de una convocatoria, incluso mientras está
recibiendo registros, sin que eso invalide nada de lo ya recibido.

## Alcance

Core Ferias — panel de la feria. Edita **los datos de encuadre**: nombre y fechas. No cambia el
estado (eso es CU-FER-008) ni el tipo (nunca, ver E1), ni toca la configuración del módulo, que
vive en el panel de cada dominio.

## Actores

### Actor principal

- **Dueño de la feria** (fila en `AdminFeria` con `es_dueño = verdadero` para esta feria).

> [!important] Solo el dueño, no cualquier administrador
> Las convocatorias no son contenido corriente de la feria: definen **qué puertas están abiertas
> y hasta cuándo**, y de ellas cuelga el expediente entero de cada módulo. Por eso su
> administración queda reservada al dueño, junto con la de los accesos.
>
> Esto **enmienda** a [ADR-0004](<../../adr/0004-acceso-administrativo-por-feria.md>), que decía
> que lo único reservado al dueño era dar de alta y retirar administradores. Cualquier
> administrador **sí** puede consultar el catálogo (CU-FER-006) — sin eso no podría operar su
> propio módulo — y sigue pudiendo operar todo lo que cuelga de una convocatoria: dictaminar,
> revisar solicitudes, validar abonos.

## Disparador

Se corrige un nombre mal escrito, o se mueve la fecha de cierre anunciada porque el calendario
de la feria cambió.

## Precondiciones

- El actor tiene sesión activa **y es dueño de la feria** en la que opera.
- La feria no está `archivada`.
- La convocatoria existe en esta feria.

## Postcondiciones

### En éxito

- La convocatoria conserva su `id`, su `tipo` y su `estado`; cambian solo el nombre y/o las
  fechas.
- **Ningún `RegistroConvocatoria` se ve afectado.** Lo ya recibido sigue siendo válido.
- Queda una entrada `convocatoria_editada` en `BitacoraFER` con los valores **antes y después**.

### En fallo

- No cambia nada.

## Flujo principal

1. Desde el catálogo (CU-FER-006), el dueño elige "Editar" en una convocatoria.
2. El sistema presenta el formulario con los valores actuales. El **tipo se muestra pero no se
   puede modificar**.
3. El dueño cambia el nombre, la fecha de apertura y/o la de cierre.
4. Si la convocatoria ya tiene registros, el sistema **advierte** de cuántos hay antes de
   confirmar (ver A1).
5. El dueño confirma.
6. El sistema guarda los cambios y vuelve al catálogo.

## Flujos alternos

### A1. La convocatoria ya recibió registros

1. En el paso 4 existen `RegistroConvocatoria` para esta convocatoria.
2. El sistema muestra cuántos son y advierte de que **las fechas anunciadas cambiarán también
   para quien ya se registró**, porque no hay copia de las fechas dentro del registro.
3. El dueño confirma o cancela.
4. Si confirma, los cambios se aplican. **Nada de lo recibido se invalida**: mover la fecha de
   cierre hacia atrás no borra ni rechaza los registros que llegaron después de la fecha nueva.

> [!important] Adelantar la fecha de cierre no cierra la convocatoria
> Es la consecuencia de que `estado` mande sobre las fechas
> ([`Modelo de datos - Ferias`](<Modelo de datos - Ferias.md>) §3.3). Quien quiera
> **dejar de recibir registros** tiene que cerrarla (CU-FER-008), no mover la fecha. Si esto se
> deja implícito, alguien va a mover la fecha creyendo que cerró y va a seguir recibiendo
> solicitudes durante días.

### A2. Solo se corrige el nombre

1. El dueño cambia únicamente el nombre.
2. No hay advertencia del paso 4 aunque existan registros: el nombre no cambia ninguna regla.

## Flujos de excepción

### E1. Intento de cambiar el tipo

1. El tipo no es editable en el formulario, y una petición que lo intente **se rechaza en el
   servidor**.
2. El sistema explica que el tipo define de qué módulo cuelga la convocatoria y no puede
   cambiarse.

> [!important] Por qué el tipo es inmutable
> El tipo determina qué expediente cuelga de cada `RegistroConvocatoria`: solicitudes de
> actividad en `EVT`, aplicaciones a expositor en `STD`, solicitudes de visita en `VIS`.
> Cambiarlo dejaría registros apuntando a expedientes de un módulo que ya no le corresponde, y
> ninguna FK lo impediría porque el expediente cuelga del registro, no del tipo. Si hace falta
> otro tipo, se crea otra convocatoria (CU-FER-005).

### E2. Fechas incoherentes

1. La fecha de cierre es anterior o igual a la de apertura.
2. El sistema rechaza el guardado y lo señala en el campo.

### E3. La feria está archivada

1. El sistema rechaza la edición y ofrece el catálogo en solo lectura (CU-FER-006 E1).

### E4. Quien lo intenta no es el dueño de la feria

1. Un administrador de la feria —con acceso legítimo al contenido— intenta editar una convocatoria.
2. El sistema **rechaza la operación en el servidor**, no solo ocultando el botón.
3. El sistema explica que las convocatorias las administra el dueño de la feria, e indica quién
   es.

## Datos relevantes

### Entradas

- Nombre
- Fecha de apertura y fecha de cierre

### Salidas

- `Convocatoria` actualizada; `id`, `tipo` y `estado` intactos

> [!important] Esta es la acción que más justifica la bitácora
> Mover la fecha de cierre de una convocatoria abierta cambia lo que se anunció públicamente. Es
> exactamente el tipo de cambio que alguien discute después —"la convocatoria cerraba el 30"— y
> por eso `BitacoraFER` guarda **el valor anterior y el nuevo**, no solo que hubo un cambio: sin
> el valor de antes, la bitácora no responde la pregunta por la que se consulta. Ver
> [`Modelo de datos - Ferias`](<Modelo de datos - Ferias.md>) §3.5.

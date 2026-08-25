---
estado: propuesta
version: "0.1"
tags:
  - tipo/caso-de-uso
  - dom/fer
  - tema/permisos
fecha: 2026-08-25
fecha_actualizacion: 2026-08-25
id: CU-FER-009
dominio: FER
responsable: Hugo Janssen
reglas_de_negocio: []
diagramas_relacionados: []
trazabilidad:
  ddr: []
---
# CU-FER-009 Eliminar una convocatoria

## Objetivo

Permitir al dueño de la feria borrar una convocatoria **que nunca recibió registros**, para
deshacer un alta equivocada sin dejar basura en el catálogo.

## Alcance

Core Ferias — panel de la feria. Es un borrado **real**, no un archivado, y por eso está acotado
al único caso en que no destruye nada: una convocatoria sin un solo `RegistroConvocatoria`.

## Actores

### Actor principal

- **Dueño de la feria** (fila en `AdminFeria` con `es_dueño = verdadero` para esta feria).

> [!important] Solo el dueño, no cualquier administrador
> Igual que el alta (CU-FER-005), la edición (CU-FER-007) y la apertura (CU-FER-008). Aquí la
> razón es más evidente que en los otros tres: de una convocatoria cuelga el expediente entero
> de un módulo, y este es el único caso de uso del dominio que **borra**. Enmienda a
> [ADR-0004](<../../adr/0004-acceso-administrativo-por-feria.md>) — ver CU-FER-005.

## Disparador

Se creó una convocatoria del tipo equivocado, o con datos que no valen la pena corregir, y nadie
se ha registrado todavía.

## Precondiciones

- El actor tiene sesión activa **y es dueño de la feria** en la que opera.
- La feria no está `archivada`.
- La convocatoria **no tiene ningún `RegistroConvocatoria`** (ver E1).

## Postcondiciones

### En éxito

- La fila `Convocatoria` deja de existir.
- Si el tipo era `STD`, su `ConfiguracionSistema` se elimina con ella: sin convocatoria no
  configura nada.
- Queda una entrada `convocatoria_eliminada` en `BitacoraFER`, con los datos de lo borrado. Es el
  único borrado real del dominio: sin la bitácora, la convocatoria no dejaría ni el hueco.

### En fallo

- No se borra nada.

## Flujo principal

1. Desde el catálogo (CU-FER-006), el dueño elige "Eliminar" en una convocatoria cuyo conteo de
   registros es cero.
2. El sistema **vuelve a comprobar el conteo en el servidor**, no se fía del que pintó la lista.
3. El sistema pide confirmación explícita, diciendo que la acción **no se puede deshacer** y qué
   se borra con ella (la configuración del módulo, si la hay).
4. El dueño confirma.
5. El sistema borra la convocatoria y su configuración en una sola transacción, y vuelve al
   catálogo.

## Flujos alternos

### A1. La convocatoria está cerrada y nunca recibió nada

1. Una convocatoria `cerrada` con cero registros también se puede eliminar.
2. El flujo es idéntico. Que se haya llegado a abrir no cambia nada si no entró nadie: no hay
   dato de nadie que perder.

## Flujos de excepción

### E1. La convocatoria tiene registros

1. En el paso 2 existe al menos un `RegistroConvocatoria`.
2. El sistema **rechaza el borrado**, dice cuántos registros hay y ofrece **cerrarla**
   (CU-FER-008) como la acción que probablemente se buscaba.

> [!important] Es el límite que impide una pérdida de datos en cascada
> De un `RegistroConvocatoria` cuelga el expediente entero de cada módulo: en `STD`, la
> `Solicitud`, su `Editorial`, su `Reserva`, sus `Movimiento` y los comprobantes de pago
> adjuntos. Borrar la convocatoria de la que cuelga todo eso destruiría el historial de cobro de
> una edición con **una sola confirmación**.
>
> Por eso la comprobación se repite en el servidor (paso 2) y no se apoya solo en que el botón
> no aparezca: la lista pudo pintarse antes de que llegara el primer registro. Y por eso el
> borrado se acota a "cero registros" en lugar de resolverse con un borrado en cascada, que es
> la forma habitual de perder datos sin enterarse.

### E2. Quien lo intenta no es el dueño de la feria

1. Un administrador de la feria intenta eliminar una convocatoria.
2. El sistema **rechaza la operación en el servidor**, no solo ocultando el botón, y explica que
   las convocatorias las administra el dueño de la feria.

### E3. Carrera con un registro entrante

1. El conteo era cero al pintar la lista, pero entre el paso 2 y el paso 5 entra un registro.
2. El borrado **falla**: la restricción de integridad de `RegistroConvocatoria` hacia
   `Convocatoria` lo impide, sin borrado en cascada de por medio.
3. El sistema informa de que la convocatoria acaba de recibir su primer registro y ya no puede
   eliminarse.

> [!note] La integridad la pone la base de datos, no el orden de las comprobaciones
> El paso 2 evita el caso común; lo que evita el caso raro es que la FK **no borre en cascada**.
> Si algún día alguien la configura en cascada por comodidad, este caso de uso deja de proteger
> nada y el fallo será silencioso.

### E4. La feria está archivada

1. El sistema rechaza el borrado.

## Datos relevantes

### Entradas

- Convocatoria a eliminar
- Confirmación explícita

### Salidas

- `Convocatoria` eliminada; `ConfiguracionSistema` asociada eliminada si el tipo era `STD`
- El tipo vuelve a estar disponible para un alta nueva

> [!note] No hay papelera ni borrado lógico
> Se eligió el borrado real porque el caso permitido —cero registros— no tiene nada que
> conservar. Si en algún momento hiciera falta poder deshacer, la respuesta no es una papelera:
> es no borrar y cerrar la convocatoria, que es lo que ya hace CU-FER-008.
>
> Lo que sí queda es la entrada en `BitacoraFER`, que guarda `entidad_id` **aunque la fila ya no
> exista**: es un dato histórico, no una FK.

---
estado: propuesta
version: 0.1
tags:
  - requisitos
  - caso-de-uso
  - eventos
fecha: 2026-06-24
id: CU-EVE-026
dominio: EVE
reglas_de_negocio: []
---
# CU-EVE-026 Hacer un cambio de horario excepcional fuera de la ventana (con registro en bitácora y motivo)

## Objetivo

El administrador ejecuta un cambio de sala u horario de una actividad fuera de la ventana normal de ajustes —e incluso después de cerrado el programa— dejando registro del motivo y de quién lo autorizó en la bitácora, para mantener trazabilidad de las excepciones.

## Alcance

Módulo EVE — gobierno de cambios excepcionales. Aplica cuando ya venció `fecha_cierre_ajustes_proponente` o cuando el programa fue cerrado definitivamente (CU-EVE-027). La negociación con el proponente ocurre fuera del sistema (correo u otro medio); este caso de uso registra y aplica el cambio acordado.

## Actores

### Actor principal

- Administrador (Hipólito)

## Disparador

Tras acordar un cambio con el proponente fuera del sistema, el administrador necesita aplicarlo de manera excepcional.

## Precondiciones

- El administrador tiene sesión iniciada con permisos del módulo EVE.
- La actividad tiene una programación existente y la fecha actual es posterior a `fecha_cierre_ajustes_proponente`, o el programa ya está cerrado.

## Postcondiciones

### En éxito

- La programación de la actividad queda actualizada (sala, fecha y/o bloque) según lo acordado.
- Se crea un registro en `BitacoraEVE` con la acción, el detalle del cambio (de → a), el motivo y el administrador que lo ejecutó.

### En fallo

- La programación permanece sin cambios y no se registra nada en la bitácora.

## Flujo principal

1. El administrador abre la actividad cuyo horario debe cambiar de forma excepcional.
2. El sistema advierte que el cambio está fuera de la ventana de ajustes (o que el programa está cerrado) y que quedará registrado en la bitácora.
3. El administrador indica la nueva sala, fecha y/o bloque, y captura el motivo (campo obligatorio).
4. El sistema solicita doble verificación de la acción excepcional.
5. El administrador confirma.
6. El sistema aplica el cambio en la programación de la actividad.
7. El sistema crea el registro en `BitacoraEVE` (acción `cambio_horario_excepcional`, detalle de → a, motivo, administrador y marca de tiempo).
8. El sistema confirma al administrador que el cambio quedó aplicado y registrado.

## Flujos alternos

### A1. La actividad no estaba programada

1. En el paso 1, la actividad está en `sin_horario` (p. ej. tras una incomparecencia).
2. El administrador asigna por primera vez una programación de forma excepcional, capturando igualmente el motivo.
3. El flujo continúa en el paso 4.

## Flujos de excepción

### E1. Motivo faltante

1. En el paso 3, el administrador deja el motivo en blanco.
2. El sistema impide aplicar el cambio y resalta el motivo como obligatorio.
3. El administrador escribe el motivo y reintenta.

### E2. Conflicto con la nueva sala y bloque

1. En el paso 6, el sistema detecta que la nueva sala y bloque ya están ocupados por otra actividad.
2. El sistema advierte el conflicto; el administrador decide ajustar la nueva asignación o continuar bajo su criterio.

## Datos relevantes

### Entradas

- Identificador de la actividad o de su programación.
- Nueva sala, fecha y/o bloque.
- Motivo del cambio excepcional (obligatorio).

### Salidas

- Programación actualizada.
- Registro en `BitacoraEVE` con el detalle del cambio, el motivo y el autor.

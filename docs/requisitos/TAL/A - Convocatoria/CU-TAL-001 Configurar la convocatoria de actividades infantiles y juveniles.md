---
estado: aceptado
version: 0.2
tags:
  - requisitos
  - caso-de-uso
  - talleres
fecha: 2026-06-28
id: CU-TAL-001
dominio: TAL
reglas_de_negocio:
  - Solo puede haber una convocatoria de actividades infantiles/juveniles en estado `abierta` por edición de FILEY.
  - Solo el administrador del módulo TAL puede configurar o cerrar la convocatoria.
  - La duración de las actividades es fija (45–50 min); no se configuran bloques por categoría literaria o académica.
---
# CU-TAL-001 Configurar la convocatoria de actividades infantiles y juveniles

> Equivale a CU-EVT-001 pero para la convocatoria que administra Elvira.
> A diferencia de la convocatoria de Hipólito, las actividades tienen duración fija (45–50 min),
> admiten modalidad virtual y el público se segmenta por nivel escolar, no por categoría literaria.

## Objetivo

El administrador configura la convocatoria de actividades dirigidas a infancias y juventudes para una edición de FILEY —periodo de recepción, fecha límite, modalidades admitidas (presencial / virtual), espacios disponibles y cupos—, dejándola activa para que los talleristas puedan registrar sus propuestas.

## Alcance

Módulo de Talleres (TAL) — sección de configuración de convocatoria. Solo aplica a usuarios con permisos administrativos del módulo TAL (equipo de Elvira). No cubre la creación de la edición de la feria (`EdicionFeria`), ni la convocatoria del programa general (CU-EVT-001, Hipólito), ni la apertura del periodo de visitas escolares (proceso independiente).

## Actores

### Actor principal

- Administrador (Elvira / equipo de actividades infantiles y juveniles)

## Disparador

El administrador decide abrir la convocatoria de actividades infantiles/juveniles de una nueva edición de FILEY.

## Precondiciones

- El administrador tiene sesión iniciada con permisos del módulo TAL.
- Existe una `EdicionFeria` activa en el sistema.
- No hay una convocatoria de actividades infantiles/juveniles en estado `abierta` para la misma edición.

## Postcondiciones

### En éxito

- El registro `ParametrosConvocatoriaTAL` queda creado o actualizado con los parámetros configurados.
- La convocatoria queda en estado `abierta`, visible para los talleristas.
- Los talleristas pueden comenzar a registrar propuestas (CU-TAL-002).

### En fallo

- No se modifica la configuración existente. El sistema conserva los parámetros previos y devuelve al administrador al formulario con los errores indicados.

## Flujo principal

1. El administrador accede a la sección de configuración de convocatoria del módulo TAL.
2. El sistema presenta el formulario de configuración con los valores actuales (o en blanco si es primera configuración de la edición).
3. El administrador captura o actualiza el periodo de recepción: fecha de apertura y fecha de cierre.
4. El administrador selecciona las modalidades admitidas: Presencial, Virtual o ambas.
5. El administrador configura los espacios disponibles (salones, salas de cine u otros espacios del público infantil/juvenil) con su nombre y cupo.
6. El sistema valida que la fecha de apertura sea anterior a la de cierre y que haya al menos un espacio configurado.
7. El administrador confirma y guarda la configuración.
8. El sistema guarda el registro `ParametrosConvocatoriaTAL` y establece el estado de la convocatoria como `abierta`.
9. El sistema confirma al administrador que la convocatoria quedó activa y muestra el resumen de los parámetros guardados.

## Flujos alternos

### A1. Modificar una convocatoria ya abierta

1. En el paso 2, el sistema detecta que ya existe una configuración en estado `abierta` para la edición activa.
2. El sistema advierte al administrador que los cambios afectarán el periodo activo de inmediato.
3. El administrador confirma y continúa desde el paso 3.

### A2. Cerrar anticipadamente la convocatoria

1. El administrador accede a la configuración de una convocatoria en estado `abierta`.
2. El administrador selecciona la opción "Cerrar convocatoria".
3. El sistema establece el estado como `cerrada` y bloquea el registro de nuevas propuestas (CU-TAL-002) a partir de ese momento.
4. El sistema confirma al administrador el cierre.

## Flujos de excepción

### E1. Fechas inválidas

1. En el paso 6, el sistema detecta que la fecha de apertura es igual o posterior a la de cierre, o que alguna fecha es inválida.
2. El sistema resalta cada campo en error con un mensaje descriptivo.
3. La configuración no se guarda hasta que el administrador corrija.

### E2. Sin espacios configurados

1. En el paso 6, el sistema detecta que no hay ningún espacio con cupo configurado.
2. El sistema indica que se requiere al menos un espacio disponible para abrir la convocatoria.
3. La configuración no se guarda hasta que el administrador añada al menos un espacio.

## Datos relevantes

### Entradas

- Fecha de apertura de la convocatoria — obligatorio.
- Fecha de cierre de la convocatoria — obligatorio.
- Modalidades admitidas (selección múltiple: Presencial · Virtual; mínimo una) — obligatorio.
- Espacios disponibles: nombre del espacio y cupo por espacio — obligatorio (mínimo uno).

### Salidas

- `ParametrosConvocatoriaTAL` creado o actualizado.
- Convocatoria en estado `abierta`, habilitando el registro de propuestas (CU-TAL-002).

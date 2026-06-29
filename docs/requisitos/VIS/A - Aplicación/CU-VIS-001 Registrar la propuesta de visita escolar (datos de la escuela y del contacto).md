---
estado: propuesta
version: 0.01
tags:
  - tipo/caso-de-uso
  - dom/vis
fecha: 2026-06-24
id: CU-VIS-001
dominio: VIS
responsable: Nombre
issue_relacionado: PSD-XX
pr_relacionado: "#XX"
reglas_de_negocio:
  - RN-XXX-001
diagramas_relacionados:
  - BPMN-XXX-001
trazabilidad:
  ddr:
    - DDR-XX
---
# CU-VIS-001 Registrar la propuesta de visita escolar (datos de la escuela y del contacto)

## Objetivo

Permitir al Aplicante registrar su propuesta de visita escolar, capturando los datos de la escuela/institución, de su contacto, de su(s) representante(s) por grupo y la **cantidad de alumnos/visitantes** que asistirán, para participar en la convocatoria de visitas escolares.

> [!note] Dato obligatorio — cantidad de visitantes
> La **cantidad de alumnos/visitantes** que asistirán debe declararse explícitamente en la propuesta. Es el dato contra el que se valida el *Cupo* restante de cada actividad ([CU-VIS-011](<../C - Catálogo y reserva de talleres/CU-VIS-011 Validar que el cupo restante del taller cubra la cantidad de visitantes.md>)) y el que alimenta la numeralia de asistentes ([CU-VIS-015](<../D - Administración/CU-VIS-015 Consultar la lista de visitas escolares aceptadas, filtrable.md>)). Fuente: [Software para agendar escuelas](<../../../soporte/extraido/Software para agendar escuelas.md>) ("la cantidad de alumnos que reservarán su asistencia").

<!-- -->

> [!warning] Regla dura — máximo 105 alumnos por propuesta [RN-VIS-001]
> La **cantidad de alumnos/visitantes** declarada en **esta** propuesta de visita escolar no puede exceder **105**. Es un tope **por propuesta de registro**, no por escuela en general: como cada nivel educativo se registra como una propuesta independiente (ver nota de campos abajo), una escuela con varios niveles tiene un tope de 105 **por cada una** de esas propuestas, no 105 repartidos entre todas. El sistema debe rechazar el registro si la cantidad declarada supera ese tope. Resuelto en la Junta 3 con organizadores FILEY (ver [RSM - Junta 3 con organizadores FILEY](<../../../soporte/meetings/resumenes/RSM - Junta 3 con organizadores FILEY.md>)); consistente con el tope de reserva de talleres en [CU-VIS-012](<../C - Catálogo y reserva de talleres/CU-VIS-012 Reservar uno o varios talleres del catálogo para armar el itinerario de la visita.md>).

<!-- -->

> [!note] Campos del formulario (Junta 3 con organizadores FILEY)
> Confirmados en la junta de organizadores; ver [RSM - Junta 3 con organizadores FILEY](<../../../soporte/meetings/resumenes/RSM - Junta 3 con organizadores FILEY.md>).
>
> - **Datos de la escuela/institución:** nombre, clave de centro de trabajo (CCT), si es
>   **pública o privada** (con este dato FILEY evalúa internamente si apoya el transporte),
>   **ubicación** (Mérida / municipio cercano / otro estado de Yucatán o vecino), **turno**
>   (matutino/vespertino) y **nivel educativo** (primaria, secundaria, preparatoria; universidad
>   cuenta como público general).
> - **Un registro (propuesta) por nivel educativo:** si la escuela tiene grupos de varios
>   niveles educativos, debe enviar una propuesta independiente por cada nivel.
> - **Datos de contacto:** puede ser un maestro directo o un padre/madre de familia; se captura
>   su teléfono, el contacto de la persona y el correo de la escuela.
> - **Representante por grupo:** la visita se divide en grupos (cada grado tiene uno); es
>   **obligatorio** declarar un representante por cada grupo. La validación de que esa persona
>   exista/asista es responsabilidad interna de FILEY, no del sistema.
> - **Campo libre:** espacio para detalles que no caben en los campos anteriores (p. ej. alumnos
>   de más, niños con capacidades especiales).

<!-- -->

> [!note] Precisión con el formulario real (Elvira, 2026-06-29)
> Elvira compartió el Google Form real (ya operativo) y un ejemplo de
> [ficha escolar interna](<../../../soporte/extraido/Material%20para%20Registro%20de%20Actividades%20FILEY%202027/Ficha%20escolar.%20Secundaria%20_EDMUNDO%20VILLALVA%20RODRIGUEZ_.md>)
> que la coordinación llena a partir de esas respuestas. Precisa/agrega sobre la nota de Junta 3:
>
> - **Cargo del responsable:** campo nuevo, no contemplado antes — opciones **Director(a) /
>   Docente / Prefecto(a)**.
> - **Estado:** lista cerrada, no texto libre — **Yucatán / Campeche / Quintana Roo**.
> - **Municipio:** lista cerrada con libre — **Mérida, Tizimín, Cenotillo, Espita, Buctzotz,
>   Cansahcab, Otro** (campo de texto si elige "Otro").
> - **Nivel educativo:** agrega **Multigrado** a las opciones ya confirmadas (primaria,
>   secundaria, preparatoria, universidad).
> - **Nombre del director/a de la institución:** dato propio, distinto del responsable que
>   llena el registro (que puede ser un docente o prefecto, no necesariamente el director).
> - **Grupos:** hasta **3 grupos** por propuesta (opcionales, no obligatorios los tres), cada
>   uno con responsable, grado y cantidad de alumnos (máx. 35) — consistente con la nota de
>   "representante por grupo" de arriba; en la práctica una misma persona puede quedar como
>   responsable de los tres grupos (ver ejemplo de ficha).
> - **Folio y fecha de recepción:** los asigna FILEY al recibir el registro; no los llena el
>   Aplicante.
> - Escuelas que no encajan en el formulario (casos atípicos) contactan primero a Elvira, quien
>   las orienta sobre qué declarar.

## Alcance

Captura la propuesta de visita escolar de una institución para un único nivel educativo: escuelas con varios niveles envían una propuesta por nivel (ver nota de campos arriba). No valida todavía cupo de actividades (CU-VIS-011) ni arma el itinerario (CU-VIS-012); solo registra los datos de la escuela, su contacto, sus representantes por grupo y la cantidad de visitantes.

## Actores

### Actor principal

- Aplicante

### Actores secundarios

> [!note] Opcional
> Usar solo si participan actores de apoyo además del principal. Eliminar esta sección si no aplica.

## Disparador

Evento que inicia el caso de uso.

## Precondiciones

- Condición 1

## Postcondiciones

### En éxito

- Resultado esperado si el flujo termina correctamente

### En fallo

- Estado resultante si el flujo no puede completarse

## Flujo principal

1. El actor realiza la acción inicial.
2. El sistema valida la condición correspondiente.
3. El sistema ejecuta la acción principal.
4. El sistema confirma el resultado al actor.

## Flujos de excepción

### E1. Cantidad de visitantes excede el máximo permitido

1. El Aplicante declara una cantidad de alumnos/visitantes mayor a **105** para esta propuesta.
2. El sistema rechaza el registro y no permite guardarlo.
3. El sistema informa al Aplicante que el máximo por propuesta es de 105 alumnos, y que si la escuela tiene varios niveles educativos debe dividir su registro en una propuesta por nivel (ver nota de campos del formulario).

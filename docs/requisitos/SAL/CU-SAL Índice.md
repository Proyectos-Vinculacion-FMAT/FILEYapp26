---
estado: propuesta
version: 0.3
tags:
  - tipo/indice
  - dom/sal
fecha: 2026-06-24
---
# CU-SAL — Índice de casos de uso (Salas y salones)

Inventario de casos de uso del dominio **Salas y salones** (`SAL`): CRUD único de espacios
(salones y sus salas) y su consulta, en **una sola pantalla**. Homologado en la
[Junta 3 con Equipo de desarrollo](<../../soporte/meetings/resumenes/RSM - Junta 3 con Equipo de desarrollo.md>);
la redacción detallada (flujo principal, alternos y excepciones) sigue sujeta a revisión.
Cada CU enlaza a su archivo y, debajo, a la evidencia (junta o material de FILEY) que lo
sustenta.

**Actores:** Administrador.

> [!note]
> CRUD único de espacios, **compartido y visible** para todos los Administradores, sin
> distinción de panel (eventos o talleres). Un salón nace con una sala por defecto; agregar
> subdivisiones crea más salas. **No aplica a stands.**

## A. Salones

- [CU-SAL-001 Crear un salón (se genera su primera sala automáticamente)](<A - Salones/CU-SAL-001 Crear un salón (se genera su primera sala automáticamente).md>) — *Administrador*
  - Evidencia: énfasis en el actor acordado en [Junta 3 §5.2](<../../soporte/meetings/resumenes/RSM - Junta 3 con Equipo de desarrollo.md#52-sal>); glosario de *Salón*/*Sala* en [§2.6](<../../soporte/meetings/resumenes/RSM - Junta 3 con Equipo de desarrollo.md#26-salas-y-salones-sal>) ("un salón puede tener tantas salas como el administrador considere necesario").

- [CU-SAL-002 Editar los datos de un salón](<A - Salones/CU-SAL-002 Editar los datos de un salón.md>) — *Administrador*
  - Evidencia: [Junta 3 §5.2](<../../soporte/meetings/resumenes/RSM - Junta 3 con Equipo de desarrollo.md#52-sal>) y glosario de *Salón* en [§2.6](<../../soporte/meetings/resumenes/RSM - Junta 3 con Equipo de desarrollo.md#26-salas-y-salones-sal>).

- [CU-SAL-003 Eliminar un salón](<A - Salones/CU-SAL-003 Eliminar un salón.md>) — *Administrador*
  - Evidencia: [Junta 3 §5.2](<../../soporte/meetings/resumenes/RSM - Junta 3 con Equipo de desarrollo.md#52-sal>) y glosario de *Salón* en [§2.6](<../../soporte/meetings/resumenes/RSM - Junta 3 con Equipo de desarrollo.md#26-salas-y-salones-sal>).

## B. Salas

- [CU-SAL-004 Agregar una sala (subdivisión) a un salón](<B - Salas/CU-SAL-004 Agregar una sala (subdivisión) a un salón.md>) — *Administrador*
  - Evidencia: [Junta 3 §5.2](<../../soporte/meetings/resumenes/RSM - Junta 3 con Equipo de desarrollo.md#52-sal>) y glosario de *Sala* (subdivisión de un salón) en [§2.6](<../../soporte/meetings/resumenes/RSM - Junta 3 con Equipo de desarrollo.md#26-salas-y-salones-sal>); antecedente operativo en [Junta 2 con organizadores FILEY](<../../soporte/meetings/resumenes/RSM - Junta 2 con organizadores FILEY.md>), sección "Administración de salas y talleres" (Elvira subdivide una sala para que varios talleres la compartan).

- [CU-SAL-005 Editar una sala (aforo y disponibilidad)](<B - Salas/CU-SAL-005 Editar una sala (aforo y disponibilidad).md>) — *Administrador*
  - Evidencia: [Junta 3 §5.2](<../../soporte/meetings/resumenes/RSM - Junta 3 con Equipo de desarrollo.md#52-sal>) y glosario de *Sala* (aforo y horario de disponibilidad) en [§2.6](<../../soporte/meetings/resumenes/RSM - Junta 3 con Equipo de desarrollo.md#26-salas-y-salones-sal>); aforos concretos de ejemplo en [Junta 2 con organizadores FILEY — Espacios disponibles](<../../soporte/meetings/resumenes/RSM - Junta 2 con organizadores FILEY.md#espacios-disponibles>) (Ek Balam 35-40, salas de cine hasta 130).

- [CU-SAL-006 Eliminar una sala](<B - Salas/CU-SAL-006 Eliminar una sala.md>) — *Administrador*
  - Evidencia: [Junta 3 §5.2](<../../soporte/meetings/resumenes/RSM - Junta 3 con Equipo de desarrollo.md#52-sal>) y glosario de *Sala* en [§2.6](<../../soporte/meetings/resumenes/RSM - Junta 3 con Equipo de desarrollo.md#26-salas-y-salones-sal>).

## C. Consulta

- [CU-SAL-007 Consultar el catálogo compartido de salas y salones](<C - Consulta/CU-SAL-007 Consultar el catálogo compartido de salas y salones.md>) — *Administrador*
  - Evidencia: une a la antigua CU-SAL-008 según [Junta 3 §5.2](<../../soporte/meetings/resumenes/RSM - Junta 3 con Equipo de desarrollo.md#52-sal>) ("todo el CRUD vive en una sola pantalla"); la pregunta sobre catálogo compartido vs. separado venía abierta desde [Junta 2 con Equipo de desarrollo — Dudas que salieron](<../../soporte/meetings/resumenes/RSM - Junta 2 con Equipo de desarrollo.md#dudas-que-salieron-a-confirmar-con-el-cliente>) y se zanjó como compartido en Junta 3; depende además de la decisión pendiente [D2](<../../soporte/meetings/resumenes/RSM - Junta 3 con Equipo de desarrollo.md#d2--dominio-del-crud-de-bloques-de-horario-prg--sal>) sobre dónde vive el CRUD de bloques de horario.

---

> [!note] Pendientes por confirmar con el cliente
>
> - **Catálogo compartido vs. separado:** se mantiene como **único catálogo compartido**
>   entre Administradores, confirmado conceptualmente en Junta 3; la confirmación final con
>   el cliente sigue abierta.
> - **Aforos y nombres reales:** los espacios concretos y sus aforos aún deben confirmarse.
> - **Salas de cine:** queda por definir por dónde se canalizan y quién las registra (ver
>   [Junta 2 con Equipo de desarrollo — Dudas que salieron](<../../soporte/meetings/resumenes/RSM - Junta 2 con Equipo de desarrollo.md#dudas-que-salieron-a-confirmar-con-el-cliente>)).

<!-- -->

> [!question] Decisión pendiente — dominio del CRUD de bloques de horario
> Aún no se decide si el CRUD de **bloques de horario** vive en `SAL` (al crear/editar una
> sala) o en `PRG` (ver D2 en la
> [Junta 3 con Equipo de desarrollo](<../../soporte/meetings/resumenes/RSM - Junta 3 con Equipo de desarrollo.md#d2--dominio-del-crud-de-bloques-de-horario-prg--sal>)).
> Mientras no se resuelva, ningún CU de este dominio modela esa CRUD.

## Ajustes de la Junta 3 (homologación)

- **CU-SAL-008** (Consultar el detalle de una sala) se **une a CU-SAL-007**: todo el CRUD y
  la consulta de salas y salones viven en una sola pantalla, sin redirigir a pantallas
  distintas.
- Se deja de distinguir Administradores por nombre propio; el catálogo es compartido entre
  todos por igual.

La numeración de CUs es solo de conteo y no se reutiliza ni se recorre tras esta fusión.

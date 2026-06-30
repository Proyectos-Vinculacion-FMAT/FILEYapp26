---
estado: aceptado
version: 0.2
tags:
  - requisitos
  - caso-de-uso
  - talleres
  - visitas-escolares
fecha: 2026-06-28
id: CU-TAL-005
dominio: TAL
reglas_de_negocio:
  - El folio y la fecha de recepción los genera el sistema al enviar; el representante no los captura.
  - La clave de trabajo (SEP) es el identificador oficial de la institución educativa; es obligatoria.
  - Una solicitud puede incluir uno o más grupos; cada grupo es independiente en grado, responsable y cantidad de alumnos.
  - El envío de la solicitud no asigna actividades; la asignación la realiza Elvira en la fase de programación.
---
# CU-TAL-005 Registrar la solicitud de visita de una escuela o grupo de excursionistas

> Caso de uso completado con base en la ficha física "Registro para visitas escolares 2026" y
> el formulario en línea de FILEY (Google Forms). Da cobertura a RF-TAL-03.

## Objetivo

El representante escolar registra en el sistema la solicitud de visita de su institución a la FILEY, capturando los datos de contacto del responsable, los datos de la institución educativa y la información de los grupos que asistirán, dejando el registro disponible para que Elvira asigne actividades en la fase de programación.

## Alcance

Módulo TAL — formulario de registro de visita escolar. Aplica durante el periodo de convocatoria de visitas escolares (`abierta`). No cubre el alta de cuenta del representante (Core REG — CU-REG-001 / CU-REG-002), ni la consulta posterior del registro (CU-TAL-008, descartado: fuera de alcance del sistema). La asignación de actividades a los grupos queda en la fase de programación, fuera de este CU.

## Actores

### Actor principal

- Representante escolar (docente o personal administrativo responsable del trámite de inscripción de la institución)

## Disparador

El representante escolar decide registrar la visita de su institución a la FILEY y abre el formulario de solicitud.

## Precondiciones

- El representante tiene sesión iniciada (CU-REG-002).
- El periodo de registro de visitas escolares está en estado `abierta` (fecha actual dentro del periodo configurado).

## Postcondiciones

### En éxito

- Se crea un registro `VisitaEscolar` en estado `recibida`, con folio y fecha de recepción asignados por el sistema.
- Se crea un registro `GrupoVisita` por cada grupo declarado, vinculado a la `VisitaEscolar`.
- El representante recibe por correo la confirmación de recepción con su número de folio.

### En fallo

- No se crea ningún registro. El sistema conserva los datos capturados en el formulario para que el representante corrija y reintente.

## Flujo principal

1. El representante abre el formulario de registro de visita escolar.
2. El sistema precarga los datos del responsable (nombre completo, teléfono, correo) desde su perfil `Persona`.
3. El representante revisa y completa los datos del responsable si es necesario.
4. El representante captura los datos de la institución educativa: nombre, director(a), clave de trabajo (SEP), nivel académico, sector, turno, dirección, estado, municipio, teléfono de la institución y correo de la institución.
5. El representante captura los datos del primer grupo: nombre del responsable del grupo, grado y cantidad de alumnos.
6. El sistema valida en línea que los campos obligatorios estén completos.
7. El representante captura las observaciones generales de la visita (opcional) y envía el formulario.
8. El sistema realiza la validación final de campos obligatorios.
9. El sistema crea el registro `VisitaEscolar` en estado `recibida`, asigna folio y fecha de recepción.
10. El sistema crea un registro `GrupoVisita` por cada grupo declarado.
11. El sistema envía al representante un correo con el número de folio y la confirmación de recepción.
12. El sistema muestra la confirmación con el folio asignado y la opción de cerrar.

## Flujos alternos

### A1. El representante registra más de un grupo

1. En el paso 5, después de capturar el primer grupo, el representante selecciona "Agregar grupo".
2. El sistema presenta un bloque adicional de campos (nombre del responsable, grado, cantidad de alumnos).
3. El representante repite el proceso para cada grupo adicional que desea incluir.
4. El flujo continúa en el paso 6 del flujo principal.

## Flujos de excepción

### E1. Campos obligatorios faltantes

1. En el paso 8, el sistema detecta campos obligatorios sin completar.
2. El sistema resalta cada campo en error con un mensaje descriptivo.
3. El envío no procede hasta que el representante corrija y reintente.

### E2. Periodo de registro cerrado al momento del envío

1. En el paso 8, el sistema verifica que la fecha actual es posterior al cierre del periodo de visitas.
2. El sistema informa al representante que el periodo de registro ya cerró y no acepta el envío.
3. No se crea ningún registro.

## Datos relevantes

### Entradas

**Datos del responsable** (precargados desde el perfil `Persona`, editables):

- Nombre completo — obligatorio.
- Teléfono — obligatorio.
- Correo electrónico — obligatorio.

**Datos de la institución educativa:**

- Nombre de la institución — obligatorio.
- Director(a) — obligatorio.
- Clave de trabajo (clave SEP, ej. `31DES2001W`) — obligatorio.
- Nivel académico (selección: Preescolar · Primaria · Secundaria · Preparatoria · Universidad) — obligatorio.
- Sector (selección: Público · Privado) — obligatorio.
- Turno (selección: Matutino · Vespertino) — obligatorio.
- Dirección — obligatorio.
- Estado — obligatorio.
- Municipio — obligatorio.
- Teléfono de la institución — opcional.
- Correo de la institución — opcional.

**Por cada grupo** (mínimo 1):

- Nombre del responsable del grupo — obligatorio.
- Grado — obligatorio.
- Cantidad de alumnos — obligatorio (número entero positivo).

**Campo general:**

- Observaciones — opcional (texto libre; ej. disponibilidad de horario preferente).

### Salidas

- `VisitaEscolar` en estado `recibida` con folio y fecha de recepción.
- Uno o más registros `GrupoVisita` vinculados.
- Correo de confirmación al representante.

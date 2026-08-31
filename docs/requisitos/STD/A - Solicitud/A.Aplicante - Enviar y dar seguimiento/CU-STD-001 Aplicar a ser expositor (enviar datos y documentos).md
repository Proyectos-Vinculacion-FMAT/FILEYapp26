---
estado: propuesta
version: 0.1
tags:
  - tipo/caso-de-uso
  - dom/std
fecha: 2026-06-19
id: CU-STD-001
dominio: STD
reglas_de_negocio:
  - RN-16
  - RN-17
---
# CU-STD-001 Aplicar a ser expositor (enviar datos y documentos)

## Objetivo

La editorial envía su solicitud para participar como expositor, con sus datos y los documentos requeridos, para que el administrador la revise y, en su caso, quede habilitada para reservar stands.

## Alcance

Componente de Stands — módulo de Solicitud. Aplica a la etapa de convocatoria, con el aplicante ya autenticado. No cubre el alta de la cuenta ni la autenticación.

## Actores

### Actor principal

- Aplicante (editorial / entidad expositora)

## Disparador

El aplicante decide participar en la feria y abre el formulario de solicitud.

## Precondiciones

- El aplicante tiene sesión iniciada.
- La convocatoria de stands a la que aplica está `abierta`.
- La persona no tiene una solicitud **en juego** en **esta** convocatoria (RN-22): se admite como mucho una en `pendiente`, `cambios_solicitados` o `aceptada`. Si la previa tiene cambios solicitados, se reedita la misma (CU-STD-002); si fue rechazada, se crea una nueva con la misma editorial; si ya fue aceptada, no hay nada que volver a enviar y el siguiente paso es elegir espacios (CU-STD-009).

## Postcondiciones

### En éxito

- Se crea una solicitud en estado `pendiente`, asociada a la editorial y al registro de la persona en esta convocatoria, con su fecha de envío y con la **fotografía** de los datos enviados (RN-22).
- Los datos de la editorial, sus sellos y los documentos adjuntos quedan almacenados.
- La solicitud queda en la cola de revisión del administrador.

### En fallo

- No se crea ni envía la solicitud; el sistema conserva lo capturado para que el aplicante corrija y reintente.

## Flujo principal

1. El aplicante abre el formulario de solicitud.
2. El aplicante captura los datos de la editorial: domicilio, contactos (director general, comercial, editorial y de promoción), giro, responsable y nombre del antepecho del stand, materiales, temáticas y sellos editoriales que representa.
3. El aplicante adjunta los documentos requeridos: constancia de situación fiscal y lista de títulos.
4. El aplicante envía la solicitud.
5. El sistema valida que los campos obligatorios y los documentos requeridos estén completos.
6. El sistema crea el registro de la persona en esta convocatoria si aún no existe, y registra la solicitud en estado `pendiente` con su fecha de envío, asociándola a la editorial y a ese registro.
7. El sistema confirma al aplicante que su solicitud fue enviada y se encuentra en revisión.

## Flujos alternos

### A1. La editorial representa a dos o más editoriales

1. En el paso 3, el aplicante declara que representa a dos o más editoriales.
2. El sistema solicita adjuntar, por cada editorial representada, una carta **con membrete del representado** y **firma de un ejecutivo facultado**, donde se autorice exhibir y comercializar su fondo editorial en la FILEY de forma exclusiva (RN-17).
3. El aplicante adjunta las cartas y el flujo continúa en el paso 4.

> [!note] Origen
> Este flujo alterno deriva de la Convocatoria de Expositores FILEY 2026, que exige —en caso de representar dos o más editoriales— una carta con membrete del representado y firma de un ejecutivo facultado autorizando la exhibición y comercialización exclusiva de su fondo editorial, para evitar la duplicidad de fondos en stands distintos. Formalizado en RN-17.

## Flujos de excepción

### E1. Información o documentos obligatorios faltantes

1. En el paso 5 el sistema detecta campos obligatorios o documentos requeridos sin completar.
2. El sistema señala lo que falta y no envía la solicitud.
3. El aplicante completa la información y reintenta el envío.

### E2. Ya existe una solicitud para la editorial/cuenta

1. En el paso 6 el sistema detecta que la persona ya tiene una solicitud **en juego** en esta convocatoria.
2. El sistema impide crear una nueva y avisa al aplicante.
3. Si la solicitud previa tiene cambios solicitados, el sistema lo dirige a editarla y reenviarla (CU-STD-002). Si ya fue **aceptada**, se lo dice y lo manda a elegir espacios: no está bloqueado, está un paso más adelante. Si fue rechazada, **no bloquea**: permite crear la nueva (RN-22).

> [!note] Una solicitud en juego **por convocatoria**, no por editorial
> Hasta el 2026-08-27 esto decía "una solicitud por editorial/cuenta". Con varias convocatorias
> de stands en la misma feria, la misma editorial puede tener una solicitud viva en cada una.

## Datos relevantes

### Entradas

- Datos de la editorial y sus contactos.
- Sellos editoriales, materiales y temáticas.
- Documentos: constancia de situación fiscal, lista de títulos y, en su caso, carta(s) de representación.

### Salidas

- Solicitud en estado `pendiente` con acuse de envío al aplicante.

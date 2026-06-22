---
estado: propuesta
version: 0.1
tags:
  - requisitos
  - caso-de-uso
  - stands
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

Componente de Stands — módulo de Aplicación. Aplica a la etapa de convocatoria, con el usuario ya autenticado. No cubre el alta de la cuenta ni la autenticación.

## Actores

### Actor principal

- Usuario (editorial / entidad expositora)

## Disparador

El usuario decide participar en la feria y abre el formulario de aplicación.

## Precondiciones

- El usuario tiene sesión iniciada.
- El evento está en periodo de convocatoria abierto.
- La editorial/cuenta no tiene una aplicación previa activa (se permite una sola aplicación en proceso por editorial/cuenta; si la previa tiene cambios solicitados, se reedita la misma; si fue rechazada definitivamente, se permite crear una nueva).

## Postcondiciones

### En éxito

- Se crea una aplicación en estado `pendiente`, asociada a la editorial y al evento, con su fecha de envío.
- Los datos de la editorial, sus sellos y los documentos adjuntos quedan almacenados.
- La aplicación queda en la cola de revisión del administrador.

### En fallo

- No se crea ni envía la aplicación; el sistema conserva lo capturado para que el usuario corrija y reintente.

## Flujo principal

1. El usuario abre el formulario de aplicación.
2. El usuario captura los datos de la editorial: domicilio, contactos (director general, comercial, editorial y de promoción), giro, responsable y nombre del antepecho del stand, materiales, temáticas y sellos editoriales que representa.
3. El usuario adjunta los documentos requeridos: constancia de situación fiscal y lista de títulos.
4. El usuario envía la aplicación.
5. El sistema valida que los campos obligatorios y los documentos requeridos estén completos.
6. El sistema registra la aplicación en estado `pendiente`, con su fecha de envío, asociándola a la editorial y al evento.
7. El sistema confirma al usuario que su aplicación fue enviada y se encuentra en revisión.

## Flujos alternos

### A1. La editorial representa a dos o más editoriales

1. En el paso 3, el usuario declara que representa a dos o más editoriales.
2. El sistema solicita adjuntar, por cada editorial representada, una carta **con membrete del representado** y **firma de un ejecutivo facultado**, donde se autorice exhibir y comercializar su fondo editorial en la FILEY de forma exclusiva (RN-17).
3. El usuario adjunta las cartas y el flujo continúa en el paso 4.

> [!note] Origen
> Este flujo alterno deriva de la Convocatoria de Expositores FILEY 2026, que exige —en caso de representar dos o más editoriales— una carta con membrete del representado y firma de un ejecutivo facultado autorizando la exhibición y comercialización exclusiva de su fondo editorial, para evitar la duplicidad de fondos en stands distintos. Formalizado en RN-17.

## Flujos de excepción

### E1. Información o documentos obligatorios faltantes

1. En el paso 5 el sistema detecta campos obligatorios o documentos requeridos sin completar.
2. El sistema señala lo que falta y no envía la aplicación.
3. El usuario completa la información y reintenta el envío.

### E2. Ya existe una aplicación para la editorial/cuenta

1. En el paso 6 el sistema detecta que la editorial/cuenta ya tiene una aplicación registrada.
2. El sistema impide crear una nueva y avisa al usuario.
3. Si la aplicación previa tiene cambios solicitados, el sistema lo dirige a editarla y reenviarla (CU-STD-002). Si la aplicación previa fue rechazada, el sistema permite continuar con la creación de la nueva solicitud.

## Datos relevantes

### Entradas

- Datos de la editorial y sus contactos.
- Sellos editoriales, materiales y temáticas.
- Documentos: constancia de situación fiscal, lista de títulos y, en su caso, carta(s) de representación.

### Salidas

- Aplicación en estado `pendiente` con acuse de envío al usuario.

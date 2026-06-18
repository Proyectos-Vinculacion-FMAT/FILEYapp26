---
tags:
  - juntas
  - cliente
  - descubrimiento
  - eventos
  - talleres
  - salones
  - salas
  - formularios
  - permisos
estado: final
version: "1.1"
fecha: 2026-06-17
Asistentes:
  - "Organizador general: Hipólito"
  - "Asistente: Laura"
  - "Organizadora de Talleres: Elvira"
  - "Equipo de desarrollo: Profesor Edgar Cambranes"
  - "Equipo de desarrollo: Isaac Ortiz"
---
# Junta 2 con organizadores FILEY

## Contexto

Segunda junta de descubrimiento, enfocada en el manejo de espacios (salas y salones), horarios de actividades, talleres y visitas escolares.

## Espacios disponibles

FILEY opera dos sistemas de espacios independientes, administrados por personas distintas:

- **Sistema de Hipólito (programa principal):** 3 salones, más espacios dentro de la sala de exposición con nombres literarios — Uxmal, Dzibilchaltún y Chichén Itzá.
- **Sistema de Elvira (talleres, zona Ek Balam):** la zona Ek Balam se subdivide con mamparas en varios espacios para talleres (capacidad 35-40 personas, lotes para niños), más **dos salas de cine** (lunes a viernes en la mañana, hasta 130 personas cada una, actividades de 2 horas con horario máximo de préstamo) y la biblioteca.
- En casos excepcionales se podría permitir sobrecupo en cines o salones, pero se maneja con discreción y cuidado.

## Administración de salas y talleres

- La organizadora de talleres (Elvira) administra sus salas según le convenga: puede asignar varios talleres a una misma sala o subdividir una sala para que varios talleres la compartan.
- En general se reciben alrededor de 300 propuestas de talleres y se aceptan alrededor de 250.
- La mayoría de los talleres son de sesión única. Algunos talleristas repiten 2-3 veces si tienen disponibilidad amplia y Elvira necesita llenar horarios vacíos. Las editoriales (o autores) que ofrecen un taller como parte de su contrato de stand pueden llegar a tener 10-15 sesiones. Elvira decide la repetición a discreción, según disponibilidad y necesidad de llenar huecos en el programa.

## Horarios y bloques de actividades

- El programa maestro de Hipólito usa bloques de **1 hora (o 1h15)** como unidad base del calendario. Dentro de cada bloque, la actividad real ocupa **45-50 minutos**; el resto es margen de transición entre actividades, que no aparece explícito en el programa impreso.
- Excepción: los eventos masivos reciben un bloque de **2 horas** para su preparación dentro del salón.
- Las actividades en salas de cine duran **2 horas**.
- El horario muerto (receso) de referencia para el sistema es el de Hipólito: **de 2pm a 4pm**. (Elvira maneja un receso propio de su programa de talleres, de 1pm a 3pm, pero se usa el de Hipólito como referencia general del sistema.)

## Visitas escolares

- Al día se reciben entre **3,000 y 3,500 niños** solo por visitas escolares.
- Las actividades deben cubrir las necesidades de aforo y nivel educativo de cada escuela (algunas requieren aforo de 50 personas, otras de 300; los niveles van de primaria a secundaria, etc.).
- Si una escuela no logra entrar a una actividad, puede asistir al área de exhibición. También, por acuerdo mutuo entre el tallerista y la escuela, puede asistir a un taller si cumple los requisitos de aforo y nivel educativo.

## Tipos de eventos

- Los eventos de Hipólito (conversatorio, conferencias, charlas, mesas redondas, presentaciones, lectura y firma de libros, presentación de revistas) son distintos de los talleres escolares.
- Existen presentaciones de "Jóvenes con" para nivel preparatoria.
- Los eventos artísticos **no son administrados por el equipo de Hipólito**: el área artística organiza su propia cartelera de forma independiente y le entrega a Hipólito una lista preliminar ya organizada. Hipólito únicamente la captura en el sistema para fines de **contabilidad/control interno**, sin gestionar su aprobación ni su programación de horario.
- Hipólito puede marcar sus eventos como aptos para nivel juvenil, para que aparezcan en el catálogo de opciones de excursión escolar (siempre que cumplan aforo, horario, día y nivel educativo recomendado).

## Flujo de aprobación y notificaciones

- Hipólito revisa las propuestas de forma continua conforme llegan (semana a semana), no solo hasta el cierre de la convocatoria.
- El sistema debe mostrarle un contador de propuestas aceptadas, rechazadas y espacios disponibles restantes, para que sepa cuánto margen le queda mientras revisa.
- Notificación en dos fases:
  1. Al terminar su revisión, Hipólito envía en un solo lote todas las notificaciones de aceptado/rechazado (no una por una).
  2. Más adelante, cuando ya tiene armado el programa, se envía una segunda notificación con fecha, sala y horario asignado; el registrante debe confirmar su disponibilidad.
- El sistema debe dejar constancia de que la notificación fue enviada (bitácora), para que Hipólito pueda deslindarse de responsabilidad si alguien dice que no la recibió.
- Los registrantes aceptados tienen una ventana de tiempo con fecha de cierre fija (por ejemplo, del 3 al 30 de noviembre) para modificar ellos mismos los datos de su propia actividad — no la fecha/horario, que la asigna FILEY. Al cerrarse la ventana, el sistema bloquea cualquier cambio.
- Se solicitan dos cuentas de correo distintas para las notificaciones automatizadas: una para eventos/talleres y otra para visitas escolares, para que Elvira no mezcle ambos flujos en su bandeja.

## Identidad, acceso y permisos

- Se necesita un identificador único de persona compartido entre el módulo de Hipólito y el de Elvira, ya que un mismo tallerista, autor o editorial puede participar en ambos sistemas (por ejemplo, presentar un libro con Hipólito y dar un taller con Elvira). Se propuso usar la combinación de **teléfono + correo electrónico**, ya que el nombre no es confiable (variaciones de acentos, errores de captura).
- Autenticación propuesta sin contraseña: el usuario ingresa su correo (o teléfono) y recibe un **código de acceso de un solo uso** en cada inicio de sesión. Esto evita que la gente olvide su contraseña y termine creando registros duplicados con otro correo.
- Permisos administrativos en dos niveles, similar a Google Drive: **solo lectura vs. edición**. Por ejemplo, la maestra/directora necesitaría solo poder consultar la información, no modificarla.
- Ya existe un sistema de registro de visitantes anterior a este proyecto, que capturaba nombre, correo, procedencia y edad (por año de nacimiento). Puede servir de referencia para el nuevo módulo de visitantes.

## Plan de trabajo y siguientes pasos

- División del equipo de desarrollo: Hugo trabajará el módulo de expositores/stands; Juan Manuel e Isaac trabajarán el módulo de programación/eventos.
- Meta: tener un prototipo visual (elementos tangibles) antes de fin de junio de 2026.
- Julio: ajustes y refinamiento del prototipo con el equipo de desarrollo.
- Meta de lanzamiento: mediados de agosto de 2026, antes de que abra la convocatoria de Hipólito.
- El equipo de desarrollo validará primero internamente con el equipo operativo (Hipólito, Elvira) antes de presentar avances a niveles directivos (la maestra, Javier).

## Pendientes por definir

- Política de registro de escuelas: limitar el registro a un solo tipo de actividad por escuela (para evitar, por ejemplo, que una escuela se registre a todas las funciones de cine).
- El registro de presentación de libros podría incluir la opción de subir portada, foto del autor y sinopsis del libro.

## Necesidades del sistema

- Organizar y visualizar las propuestas de eventos enviadas, para poder aprobarlas o rechazarlas, y después acomodarlas en un horario de actividades a lo largo de la feria (ver "Flujo de aprobación y notificaciones").
- Minimizar la carga de la organizadora de talleres al asignar un taller a una escuela: Elvira identificó esto como su necesidad principal — quiere pasar la responsabilidad de elegir el taller a la escuela o su representante (validando que coincidan aforo y nivel educativo).
- Enviar correos de confirmación a las escuelas registradas, en varios momentos antes de la feria.
- Exportar el programa maestro a Excel, Word o PDF: es un deseo del cliente. Hoy Hipólito hace manualmente la "pulida final" del programa cuando termina de organizar la cartelera, antes de pasarla a su editor (quien hace el diseño/maquetación del programa impreso); el sistema debe generar ese archivo exportable para apoyar ese paso, que seguirá siendo manual en la parte de diseño.
- Registrar internamente los eventos artísticos (ver "Tipos de eventos") solo para fines de contabilidad, sin gestionar su aprobación ni programación.

## Preguntas a definir

- ¿Qué eventos de Hipólito suelen ser aptos para nivel juvenil?
- ¿Quién decide si un evento es apto para escuelas: Hipólito o el registrado?
- ¿Cuántos espacios exactos administra Elvira en Ek Balam, incluyendo los nombres de las subdivisiones con mamparas?
- ¿Qué información mínima debe capturarse de la lista preliminar de eventos artísticos para registrarla en el sistema?
- ¿El identificador único entre los módulos de Hipólito y Elvira debe ser teléfono, correo o la combinación de ambos? ¿Qué pasa si hay discrepancia entre los dos registros de una misma persona?

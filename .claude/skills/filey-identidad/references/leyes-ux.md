# Leyes de UX aplicadas a FILEY

Destilado de <https://www.userinterface.wiki/laws-of-ux>. Solo se conservan las leyes que
**cortan una decisión real** en este proyecto, cada una atada a un componente y a una
comprobación. Una ley sin regla operativa no entra en este archivo.

Las cinco primeras están enunciadas en la fuente citada. Las cinco siguientes son canon
establecido de Laws of UX (Yablonski) y se incluyen porque los flujos de FILEY las tocan de
forma directa.

---

## Del sitio fuente

### Fitts — el tiempo para alcanzar un objetivo depende de su tamaño y distancia

**Regla FILEY.** La acción primaria de cada pantalla es el elemento interactivo más grande y
está al final del flujo de lectura. Las acciones destructivas (rechazar propuesta, quitar
taller del itinerario, eliminar programación) **nunca** van adyacentes a la confirmatoria:
van separadas, o en otro nivel visual (`.btn-ghost` frente a `.btn-primary`).
Áreas de click chicas (íconos de tabla, botones prev/next de día) se amplían con padding
invisible, no agrandando el ícono.

**Dónde.** Botonera de formularios, barra de dictamen del admin, filas de tabla.
**Verificación.** Altura ≥40px en la acción primaria; nunca primaria y destructiva contiguas.

### Hick — el tiempo de decisión crece con el número y complejidad de opciones

La fuente es explícita en la magnitud: pasar de 2 a 4 opciones se nota; de 8 a 16 duele.

**Regla FILEY.** Máximo ~7 opciones visibles simultáneamente. El registro de una propuesta
no se presenta como 25 campos seguidos: se revela por secciones (divulgación progresiva).
Los filtros del admin muestran los tres de uso diario; el resto va tras "más filtros".

**Dónde.** Formulario de propuesta, catálogo de talleres, filtros de listados admin.
**Verificación.** Contar opciones/campos visibles por pantalla y por sección.

### Miller — ~7±2 elementos en memoria de trabajo; agrupar no es opcional

**Regla FILEY.** Los formularios largos se parten en bloques con encabezado numerado
(el patrón bento del prototipo). Los datos se muestran **formateados**, no crudos:
`EVT-024` y no `24`; `9 mar · 11:30–12:45` y no `2027-03-09T11:30:00`;
`38 / 40 lugares` y no `38`.

**Dónde.** Formularios de propuesta y de visita, fichas de detalle, tablas de seguimiento.
**Verificación.** Ninguna sección con más de 9 campos; ninguna fecha u hora sin formatear.

### Doherty — la productividad se dispara si ni el sistema ni la persona esperan

Umbral citado: **400 ms**. Por debajo se percibe instantáneo.

**Regla FILEY.** Ninguna acción queda sin respuesta visible. Si el servidor puede tardar
(subir constancia, notificar en lote, generar PDF), se muestra indicador de progreso o
estado optimista, y el botón se deshabilita para evitar doble envío.

**Dónde.** Envío de formularios, filtros que recargan listados, notificación en lote.
**Verificación.** Toda acción de red tiene estado de carga y bloqueo de reenvío.

### Postel — sé conservador al emitir, liberal al recibir

**Regla FILEY.** Los datos de contacto llegan de escuelas y ponentes en formatos
inconsistentes. Se aceptan teléfonos con espacios, guiones y paréntesis; correos con
mayúsculas y espacios al borde; nombres de escuela con acentuación variable. Se **normaliza
al guardar**, no se rechaza al escribir. La validación dispara al salir del campo, nunca
en cada tecla.

**Dónde.** Registro de cuenta, ficha de escuela, datos de contacto del ponente.
**Verificación.** El formulario normaliza en vez de rechazar; no hay error mientras se teclea.

---

## Canon adicional aplicable

### Jakob — la gente espera que tu sitio funcione como los que ya conoce

**Regla FILEY.** No se inventan patrones cuando existe uno convencional: el login va con
correo + código, los listados admin con filtros arriba y tabla abajo, el estado con badge.
Los usuarios (docentes, ponentes, expositores) no son usuarios frecuentes: entran pocas veces
al año. La familiaridad pesa más que la originalidad.

**Verificación.** Ningún patrón nuevo donde ya existe uno en el prototipo.

### Proximidad (Gestalt) — lo cercano se percibe como relacionado

**Regla FILEY.** El espacio comunica agrupación: mayor separación **entre** bloques que
**dentro** de un bloque. Una etiqueta va pegada a su campo, no equidistante entre dos.

**Verificación.** Separación entre secciones > separación entre campos de una sección.

### Zeigarnik — las tareas incompletas se recuerdan mejor

**Regla FILEY.** Todo flujo de varios pasos muestra dónde está la persona y qué falta
(la barra de pasos del prototipo). El estado "propuesta en borrador" o "faltan documentos"
se muestra siempre que se entra, no solo al abandonar.

**Verificación.** Todo flujo multipaso tiene indicador de progreso persistente.

### Peak-end — se recuerda el punto máximo y el final

**Regla FILEY.** La confirmación de envío es la pantalla más cuidada del flujo: folio
visible, qué sigue, cuándo esperar respuesta. El final de un flujo nunca es un redirect
silencioso al inicio.

**Verificación.** Todo flujo termina en pantalla de confirmación con folio y siguiente paso.

### Estética-usabilidad — lo que se ve mejor se percibe como más usable

**Regla FILEY.** Es la razón por la que la consistencia de tokens no es cosmética: una
pantalla con radios, sombras y colores fuera del sistema se percibe como más difícil,
aunque funcione igual. También es la trampa: no compensa un flujo mal diseñado.

**Verificación.** `./prototipo/scripts/check-ui.sh` en verde.

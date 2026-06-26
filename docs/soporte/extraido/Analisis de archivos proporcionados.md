---
tags:
  - tipo/analisis
  - tema/alcance
  - dom/std
  - dom/vis
tipo: analisis
descripcion: Qué pide cada documento entregado por FILEY y qué roces tiene con lo documentado (juntas y casos de uso).
fecha: 2026-06-21
fecha_actualizacion: 2026-06-22
fuentes_contrastadas:
  - "docs/soporte/meetings/resumenes/ (juntas FILEY y equipo; Junta 1 ya con transcripción)"
  - "docs/soporte/notas/Propuesta de CUs hologado.md"
  - "docs/requisitos/STD/ (casos de uso de Stands)"
---
# Análisis de los archivos proporcionados por FILEY

## Propósito y contexto

FILEY entregó este paquete de documentos **antes de la primera junta** (ver
[motivo de entrega](<../documentos proporcionados por FILEY/motivo de entrega.md>)). No son
especificaciones: son **(a) su propia propuesta de lo que necesitan** y cómo imaginan la
herramienta, y **(b) documentos de ejemplo que ya usan** en su operación manual actual.

Por eso son la **fuente primaria** del problema, y este análisis los contrasta en dos pasos:

1. **Contra las juntas con FILEY** (`RSM - Junta * con organizadores FILEY`) — son *sus
   palabras contra sí mismas*: ¿lo que escribieron antes coincide con lo que dijeron en
   reunión?, ¿evolucionó o se contradijo?
2. **Contra el equipo de desarrollo** (`RSM - Junta * con Equipo de desarrollo` y
   [Propuesta de CUs homologado](<../notas/Propuesta de CUs homologado.md>)) — que son
   una *abstracción* de lo que el equipo entendió de esas necesidades. Aquí salen los
   **roces**: lo que el cliente pidió y aún no está modelado, o que el equipo acotó/descartó.

> Convención: en este documento, **"roce"** = tensión, contradicción o hueco entre lo que
> el documento pide y lo documentado. No implica error; marca algo a confirmar o decidir.
> Los marcadores `[hh:mm:ss]` y `Lxxx` remiten a la transcripción de la Junta 1, vía su resumen.

## Inventario por intención

| Documento (fuente)                                    | Tipo                                           | Intención                                                                 |
| ----------------------------------------------------- | ---------------------------------------------- | ------------------------------------------------------------------------- |
| `Detalles para el Registro en Linea 2027.pdf`         | Propuesta/recomendaciones                      | Cómo construir el registro en línea: cronograma, flujo y pantallas.       |
| `Software para agendar escuelas.docx`                 | Propuesta de necesidad                         | Módulo de **visitas escolares** (la escuela elige su taller).             |
| `Convocatoria para Actividades FILEY 2027.pdf`        | Documento operativo                            | Bases públicas del registro de actividades de Contenidos.                 |
| `Registro de propuestas FILEY 2027.pdf`               | Modelo de formulario (**versión actualizada**) | Campos del formulario de registro, **condicional por tipo de actividad**. |
| `Convocatoria Expositores 2026.pdf`                   | Documento operativo                            | Bases de stands: precios, anticipos, descuentos, pagos.                   |
| `Registro-para-Expositores-FILEY-2026.pdf` *(imagen)* | Modelo de formulario                           | Ficha de registro de expositor.                                           |
| `Base Registro de Propuestas FILEY 2027.xlsx`         | Ejemplo de datos                               | Modelo de la **base de datos** de propuestas (salida del registro).       |
| `Programación General FILEY 2027.xlsx`                | Ejemplo de datos                               | **Programa maestro** (calendario por sala). Salida deseada.               |
| `Programa General FILEY 2026.pdf`                     | Ejemplo de salida                              | Programa impreso (maquetable). Formato de exportación deseado.            |
| `ACTIVIDADES ARTES VISUALES 2026.xlsx`                | Ejemplo de datos                               | Rubros propios de **Artes Visuales** (registro interno).                  |
| `MUESTRA TALLERES  Supermicrobios.pdf` *(imagen)*     | Ejemplo lleno                                  | Una ficha de **registro de taller** ya capturada.                         |
| `Información general talleres FILEY.pdf` *(imagen)*   | Documento operativo                            | Información general de talleres (no extraíble; requiere OCR).             |
| `Plano FILEY 2026 Salón Chichén Itzá.pdf` *(imagen)*  | Plano                                          | Mapa del *showfloor* de stands.                                           |

---

## 1. Contraste contra las juntas con FILEY (ellos vs. ellos)

### 1.1 Stands — consistente con la convocatoria; varios porcentajes aún en disputa

La [Convocatoria Expositores 2026](<Material para Registro de Actividades FILEY 2027/Convocatoria Expositores 2026.md>)
coincide con la [Junta 1](<../meetings/resumenes/RSM - Junta 1 con organizadores FILEY.md>) —ahora
respaldada por su transcripción— en lo esencial: stand 3×2 = 6 m² a **$15,000**, **$2,500/m²**
(precio que *"no cambia"*) `[00:05:06]`, **10% de pronto pago** `[01:16:02]`, factura opcional con
datos fiscales `[00:59:12]`, y asignación respetando a expositores previos.

- **Métodos de pago — confirmado (resuelve R2):** no se acepta **efectivo**; sólo **transferencia
  o cheque** depositado a la cuenta del patronato `[00:10:48]` `[00:12:36]`, por políticas
  antilavado (la UADY es donataria y todo pago debe ser rastreable) `[00:11:04–00:11:59]`. La
  convocatoria pública decía *"transferencia, depósito o cheque"*; lo que se descarta es el
  **efectivo**, no el cheque.
- **Descuento local — porcentaje en disputa (R9):** el descuento local existe, pero su porcentaje se
  citó de forma **inconsistente dentro de la misma junta**: **15%** `[00:48:17]`, **"hasta 20%"**
  `L581` y **"+5%"** `L605`; además **no se decidió si se acumula** con el pronto pago (posturas
  encontradas de Hipólito, Edgar y Gilberto) `[00:47:39–00:50:40]`. El 15% que cita `CU-STD-005` es
  sólo **una** de esas cifras. La convocatoria pública 2026 sólo menciona el 10% de pronto pago, no el local.
- **Anticipo del 50% — ahora en discusión (R10):** la convocatoria fija *"50%"*, pero en la junta el
  monto del primer pago quedó **sin cerrar**: Gilberto pide mínimo 50% `[00:22:00–00:22:28]`;
  Hipólito/Isaac hablan de 15–20% y 3–4 pagos `[00:27:25]`; Edgar propone que el sistema **acepte
  tantos pagos como quieran** y lleve la cuenta `[00:27:57–00:29:13]`. → Tomar el "50%" del documento como tentativo.
- **Roce de fechas/edición:** la convocatoria es del ciclo **2026** (edición XIV, feria 14–22 marzo 2026);
  los documentos de Contenidos son **2027** (edición XV, 13–21 marzo 2027). El material mezcla años
  de ejemplo: cuidado al tomar fechas/precios como vigentes.

### 1.2 Visitas escolares — el documento y la junta se refuerzan

[Software para agendar escuelas](<Software para agendar escuelas.md>) pide que **la escuela
visualice los talleres disponibles con su cupo, elija el de su agrado, y reciba un correo de
confirmación**, con candados (un tipo de actividad por escuela; preferencia de un mismo día;
límite de 105 alumnos; "cupo lleno" al saturarse).

Esto coincide **exactamente** con lo que Elvira identificó en la
[Junta 2 con organizadores](<../meetings/resumenes/RSM - Junta 2 con organizadores FILEY.md>)
como su **necesidad principal**: *pasar la responsabilidad de elegir el taller a la escuela*,
validando aforo y nivel educativo, y enviar correos de confirmación. → **Consistente y reforzado.**

### 1.3 Cronograma y flujo de registro — consistente

[Detalles para el Registro en Linea 2027](<Material para Registro de Actividades FILEY 2027/Detalles para el Registro en Linea 2027.md>)
fija el cronograma 2027 (lanzamiento 10 ago; cierre 2 oct 16:00; aviso de seleccionados 13 nov;
ajustes 7 dic 16:00; asignación de hora/sala 22 ene; constancias 26 abr). La Junta 2 describe
el **mecanismo** equivalente: ventana de modificación con fecha de cierre fija, segunda
notificación con sala/horario, candado al cierre. El documento aporta las **fechas concretas**;
la junta, el comportamiento. → **Consistente.**

### 1.4 Eventos artísticos / Artes Visuales — consistente

El [motivo de entrega](<../documentos proporcionados por FILEY/motivo de entrega.md>) aclara que
Artes Visuales, Cinematográficas y Escénicas **no tienen convocatoria abierta**: su registro es
**interno**. La Junta 2 lo confirma: los artísticos no los administra Hipólito; sólo los **captura
para contabilidad/control interno**. El `ACTIVIDADES ARTES VISUALES 2026.xlsx` es justo el modelo
de rubros propios de ese registro interno.

---

## 2. Contraste contra el equipo de desarrollo (abstracción → roces)

Referencia: [Propuesta de CUs homologado](<../notas/Propuesta de CUs homologado.md>) y
[Junta 2 con Equipo de desarrollo](<../meetings/resumenes/RSM - Junta 2 con Equipo de desarrollo.md>).

### 2.1 ⚠️ Roce principal: visitas escolares marcadas "fuera de scope"

La Propuesta de CUs dice: *"Visita escolar queda fuera del scope actual (**registro especulativo,
sin formulario real aún**); no se propone por ahora."* Y la Junta 2 del equipo **descartó** la
"actualización de la visita escolar por la propia escuela" por considerarla un supuesto no acordado.

Pero:

- El cliente **sí entregó por escrito** el comportamiento deseado (`Software para agendar escuelas.docx`).
- Elvira lo confirmó en junta como su **necesidad #1**.

Hay que **distinguir dos formularios distintos**, que el equipo mezcló:

1. **Registro de taller** (el tallerista propone un taller) — *sí* existe y opera hoy vía un
   **Google Forms + autocrat**; la [muestra Supermicrobios](<MUESTRA TALLERES Supermicrobios.md>)
   es una ficha **de un taller** generada por ese flujo. Está modelado como `EVT`.
2. **Visita escolar** (la escuela reserva un taller ya aceptado) — es lo que pide el `.docx`, lo
   más valioso para Elvira. **Aquí sí aplica "sin formulario real aún":** el formato que existe es
   una **propuesta de la propia Elvira**, y queda **pendiente confirmar si es el oficial** o sólo
   una idea suya. El Google Forms anterior **no** cubre esta reserva escolar.

→ **Recomendación:** reclasificar la visita escolar de "especulativa" a "diferida con fuente
documental (el `.docx`)", y dejar como pendiente confirmar con FILEY el formulario oficial de Elvira.

### 2.2 Registro condicional por tipo — alineado; el catálogo canónico es de 8

El [Registro de propuestas FILEY 2027](<Material para Registro de Actividades FILEY 2027/Registro de propuestas FILEY 2027.md>)
define un formulario **condicional por tipo** (Conversatorio, Conferencia, Charla, Mesa redonda,
Presentación de libro/revista, Lectura de obra, **Encuentro**), cada uno con sus campos y adjuntos
(semblanza PDF, sinopsis PDF, foto/portada JPG/PNG). Esto está cubierto por `CU-REG-003`
(enrutamiento condicional) y `CU-EVT-001`.

- **Catálogo canónico = 8 tipos.** Este documento llegó **después** del paquete inicial, enviado
  por FILEY como **"actualizado"**, e incorpora el octavo tipo (**Encuentro**). Por lo tanto **es la
  lista canónica**. La [Convocatoria 2027](<Material para Registro de Actividades FILEY 2027/Convocatoria para Actividades FILEY 2027.md>)
  lista sólo 7 (le falta "Encuentro") porque es una versión anterior; esa discrepancia es de
  versión, no una pregunta abierta. La duda que el equipo anotó en la Junta 2 **ya está resuelta** por este documento.
- **Constancia de participación:** el formulario la pide como sí/no por propuesta; la Junta 2 del equipo
  tiene abierta la duda de cómo se manejan constancias en actividades **grupales** (paneles, mesas). Coincide.

### 2.3 Vínculo base de datos ↔ programa maestro — hueco de edición manual

`Detalles…` pide que la base de propuestas y el programa maestro estén **vinculados**, pero que el
coordinador **pueda meter información directamente en el calendario sin romper el vínculo**. Los
`CU-PRG-*` modelan asignar/editar/quitar actividades **aprobadas**, pero **no** contemplan que el
coordinador agregue al calendario entradas que **no** provienen de una propuesta aprobada (p. ej.
los artísticos capturados sólo para control, o ajustes manuales de "pulida final"). → **Hueco a cubrir.**

La exportación del programa (`CU-PRG-011`) sí cubre el deseo de sacar Excel/Word/PDF; el
[Programa General 2026](<Material para Registro de Actividades FILEY 2027/Programa General FILEY 2026.md>)
y la `Programación General 2027.xlsx` son los **formatos de salida modelo** a replicar.

### 2.4 Registro interno de artísticos — necesidad sin CU dedicado

La Junta 2 lo lista como necesidad ("registrar internamente los artísticos para contabilidad"), pero
la Propuesta de CUs **no** tiene un caso de uso explícito para ese registro interno con los **rubros
propios** de Artes Visuales (`ACTIVIDADES ARTES VISUALES 2026.xlsx`). Además, el motivo de entrega
avisa que **Escénicas (~50)** y **Cinematográficas (~20)** quedaron **pendientes de integrar**. → **Gap conocido.**

### 2.5 Usuarios y autenticación — diferencia de prioridad, no de fondo

`Detalles…` recomienda que los interesados **creen su usuario** al inicio. La Junta 2 del equipo acordó
**"omitir por ahora el registro de usuario base"** (se separa después de los registros por actividad), y
la Junta 2 con FILEY propuso **login sin contraseña (código de un solo uso)**. No hay contradicción de
fondo; es una decisión de **secuencia/priorización** que conviene dejar explícita.

### 2.6 Cobro/contabilidad — la Junta 1 (verificada) agrega detalle que aún no se modela

La transcripción de la Junta 1 detalla necesidades contables que los documentos sólo insinúan y que
conviene cruzar con los `CU-STD-*`: **bitácora por expositor** tipo mayor (acumula pagos, adeudo,
pendientes de validar) `[00:54:02–00:55:37]`, **carga + validación manual de comprobantes** PNG/PDF/JPG
con múltiples pagos `[00:56:12]`, **recordatorios automáticos** de pago `[00:27:57]`, y **estados de
stand por color** (blanco/verde/azul) con bloqueo por operador `[00:32:19]`. La **pasarela de pago**
queda **fuera de esta edición** (será manual) `[00:15:20]`. → Verificar que el módulo de Stands cubra
bitácora, comprobantes múltiples y recordatorios.

---

## 3. Tabla de roces y pendientes

| #   | Roce / pendiente                                                                                                         | Origen documental                                                 | Estado en lo documentado                                  | Acción sugerida                                                                 |
| --- | ------------------------------------------------------------------------------------------------------------------------ | ----------------------------------------------------------------- | --------------------------------------------------------- | ------------------------------------------------------------------------------- |
| R1  | Visita escolar marcada "especulativa / sin formulario"                                                                   | `Software para agendar escuelas.docx`                             | Fuera de scope (Propuesta CUs); descartada en Junta 2 dev | Reclasificar a "diferida con fuente"; confirmar el formulario oficial de Elvira |
| R2  | Métodos de pago: transferencia o cheque, **sin efectivo** (antilavado) — **resuelto y verificado por transcripción**     | Convocatoria Expositores 2026 + Junta 1 `[00:10:48]` `[00:12:36]` | CU-STD asume comprobante; método no fijado                | Fijar método = transferencia/cheque (sin efectivo)                              |
| R3  | Catálogo de tipos: canónicamente **8** (incluye "Encuentro"); la convocatoria lista 7                                    | Registro de propuestas (actualizado) vs. Convocatoria             | Duda ya **resuelta**: 8 es canónico                       | Usar el Registro actualizado (8 tipos) como fuente                              |
| R4  | Constancias en actividades grupales                                                                                      | Registro de propuestas (campo sí/no)                              | Duda abierta en Junta 2 dev                               | Definir regla para paneles/mesas                                                |
| R5  | Edición manual del calendario sin romper el vínculo                                                                      | Detalles para el Registro                                         | No cubierto por CU-PRG-*                                  | Añadir CU de entrada manual al programa                                         |
| R6  | Registro interno de artísticos con rubros propios                                                                        | ACTIVIDADES ARTES VISUALES.xlsx + motivo de entrega               | Necesidad sin CU dedicado                                 | Definir CU de registro interno (contabilidad)                                   |
| R7  | Escénicas (~50) y Cinematográficas (~20) sin integrar                                                                    | motivo de entrega                                                 | No documentado                                            | Planear fase posterior                                                          |
| R8  | "Crear usuario" al inicio vs. "omitir usuario base por ahora"                                                            | Detalles vs. Junta 2 dev                                          | Decisión de secuencia                                     | Documentar orden de implementación                                              |
| R9  | Descuento local: existe, pero **% en disputa** (15% / "hasta 20%" / "+5%") y **acumulación con pronto pago sin decidir** | Junta 1 FILEY `[00:47:39–00:50:40]` vs. Convocatoria / CU-STD-005 | CU-STD-005 fija 15% (sólo una de las cifras)              | Decidir % definitivo y si se acumula con pronto pago                            |
| R10 | Anticipo de reserva: la convocatoria fija **50%**, pero en Junta 1 el monto/№ de pagos quedó **sin cerrar**              | Convocatoria Expositores 2026 vs. Junta 1 `[00:22:00–00:29:13]`   | CU-STD modela abonos; % no fijado                         | Definir anticipo mínimo y si se topa el número de pagos                         |
| R11 | Bitácora contable, comprobantes múltiples y recordatorios de pago                                                        | Junta 1 FILEY (verificada) `[00:54:02–00:55:37]`                  | Parcial en CU-STD                                         | Verificar cobertura en el módulo de Stands                                      |

---

## 4. Cobertura: qué documento alimenta qué

| Documento proporcionado                         | ¿Reflejado hoy?   | Dónde                          |
| ----------------------------------------------- | ----------------- | ------------------------------ |
| Convocatoria Expositores + ficha expositor      | ✅ Sí             | `CU-STD-001..035` (Stands)     |
| Registro de propuestas (condicional por tipo)   | ✅ Parcial        | `CU-REG-*`, `CU-EVT-*`         |
| Detalles para el Registro (cronograma/flujo)    | ✅ Parcial        | `CU-EVT-012/013`, `CU-PRG-008` |
| Programación/Programa General (salida)          | ✅ Parcial        | `CU-PRG-011` (exportación)     |
| Software para agendar escuelas (visita escolar) | ❌ Fuera de scope | — (ver R1)                     |
| ACTIVIDADES ARTES VISUALES (registro interno)   | ❌ Sin CU         | — (ver R6)                     |
| Escénicas / Cinematográficas                    | ❌ No documentado | — (ver R7)                     |

---

## 5. Lectura rápida (TL;DR)

- Los documentos de **stands y de registro de actividades de Contenidos** ya están razonablemente
  reflejados en los casos de uso; sirven sobre todo para **confirmar campos, precios y fechas**.
- El roce de mayor valor es **R1**: la **visita escolar** es la necesidad #1 del cliente (Elvira),
  está documentada por escrito y el equipo la dejó fuera de scope por considerarla especulativa.
  Conviene corregir esa premisa (y, aparte, confirmar si el formulario de reserva escolar de Elvira
  es el oficial).
- El catálogo de tipos de actividad (**R3**) ya está resuelto: son **8**, según el Registro de
  propuestas actualizado.
- **La transcripción verificada de la Junta 1** cierra **R2** (pagos: transferencia/cheque, sin
  efectivo) pero **abre/afina** **R9** (% del descuento local en disputa), **R10** (anticipo no
  cerrado) y **R11** (contabilidad: bitácora, comprobantes múltiples, recordatorios).
- Hay **huecos claros** en: registro interno de artísticos (R6), escénicas/cine (R7) y edición manual
  del programa (R5).

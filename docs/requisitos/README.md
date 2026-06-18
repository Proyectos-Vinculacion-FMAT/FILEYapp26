---
estado: propuesta
version: 0.3
tags:
  - requisitos
  - dominios
  - alcance
fecha: 2026-06-18
---
# README — Dominios y necesidades del cliente

Resumen de cómo se divide el sistema **FILEY** en dominios y qué información guarda cada uno. Sirve como índice y referencia de alcance para los requisitos funcionales (`RF-DOM-NN`).

## Enfoque

El sistema se organiza por **dominios verticales**. Cada dominio tiene **uno o varios tipos de registro**, y cada tipo de registro es un **modelo de datos**: define qué información se guarda de quien solicita ese servicio.

Los RFs se centran en ese modelo de datos: **por dominio y por tipo de registro, qué información se captura y conserva**.

> [!important]
> El **alcance de la primera entrega (agosto)** es el **registro de solicitantes**: capturar los datos de quienes exponen, dan talleres, rentan stands o agendan excursiones escolares. Es lo primero que ocurre, previo a la feria. Los demás dominios están planeados a futuro y se documentan aquí como referencia, no como compromiso de esta entrega.

## Propiedades compartidas (no son dominios)

Estas características aparecen en todos los registros, pero **se infieren** como propiedades comunes; **no** se modelan como un dominio transversal:

- **Solicitud / registro:** el acto de llenar un formulario para solicitar un servicio (rentar, exponer, impartir, agendar).
- **Datos de contacto:** la identidad mínima de quien solicita (nombre y medio de contacto).
- **Tipo de participante:** quién puede participar — asociaciones civiles, comunidad-UADY, editoriales, instituciones culturales, universidades públicas y privadas, y otras instituciones.

> [!note]
> Se manejan como propiedad compartida —y no como dominio— porque ya hay clientes reales con necesidades aisladas por dominio, y cada una se expresa fácilmente como una historia de usuario propia. Organizar por dominio mantiene esas necesidades concretas y separadas.

## Mapa de dominios

### Dominios prioritarios — primera entrega (agosto)

| Código | Dominio | Dueño | Tipos de registro |
| ------ | ------- | ----- | ----------------- |
| `STD` | Stands | Junta 1 | Arrendatario de stand (único) |
| `EVE` | Eventos generales | Hipólito | Conversatorio · Conferencia · Charla · Mesa redonda · Presentación de libro · Presentación de revista · Lectura de obra · Taller anexado |
| `TAL` | Talleres | Elvira | Tallerista · Escuelas o excursionistas |

> [!note]
> `EVE` es el dominio con más variantes y funciona como **calendario maestro**: además de sus formatos propios, integra los talleres que Elvira organiza en `TAL`.

> [!note]
> El dominio `STD` abarca, además del registro del arrendatario, el **proceso de reserva, pago y confirmación** de stands. Sus artefactos viven en `STD/`: índice de casos de uso (`CU-STD Índice.md`), modelo de datos (`Modelo de datos - Stands.md`) y proceso de alto nivel (`Proceso de alto nivel - Stands.md`).

### Dominios futuros — no prioritarios

Ordenados por la prioridad esperada después de la primera entrega:

| Orden | Código | Dominio | Necesidad que cubre | Condición |
| ----- | ------ | ------- | ------------------- | --------- |
| 1 | `PAG` | Pagos | Confirmar el cobro asociado a un registro aprobado. | Sujeto a decisión del cliente. |
| 2 | `ACC` | Acceso y verificación | Verificar la entrada de visitantes a la feria (QR u otro). | Mecanismo por definir. |
| 3 | `VIS` | Contabilidad de visitantes | Contar a los visitantes registrados. | Va al final. |
| 4 | `REP` | Reportes | Generar reportes a partir de los datos. | Secundario. |

## Organización de los requisitos

Los RFs **se dividen por dominio**: cada dominio tiene su propia carpeta y dentro viven sus requisitos (`RF-DOM-NN.md`). Esto mantiene separadas las necesidades concretas de cada dueño y facilita ubicar y versionar cada conjunto.

```text
requisitos/
├── README.md
├── RF-DOMINIO Template.md
├── EVE/   → RF-EVE-NN  (eventos generales · calendario maestro)
├── STD/   → RF-STD-NN  (stands; incluye índice de CU, modelo de datos y proceso de alto nivel)
└── TAL/   → RF-TAL-NN  (talleres: talleristas y visitas escolares)
```

> [!note]
> Cada carpeta de dominio agrupa solo sus requisitos. Crear una carpeta nueva al abrir un dominio adicional (p. ej. `PAG/`, `ACC/`) siguiendo la misma convención `RF-DOM-NN`.

## Relación entre dominios

- Elvira organiza los talleres en `TAL`; al cerrarlos, Hipólito los **anexa al calendario maestro** de `EVE`. Por eso `EVE` "hereda" los talleres como entradas de calendario, aunque su modelo de datos viva en `TAL`.

## Pendientes por validar

- Cómo se anexa un taller de `TAL` al calendario maestro de `EVE`.
- Si los pagos entran en alcance y bajo qué condiciones (decisión del cliente).
- Si el flujo de **reserva, pago y confirmación** de `STD` entra en la primera entrega (agosto) o se difiere: hoy excede el alcance de "registro de solicitantes" y se traslapa con el dominio futuro `PAG`.
- Si la contabilidad de visitantes y los reportes entran en alcance posterior.

> [!note]
> El detalle de qué información guarda cada tipo de registro **no vive aquí**: es responsabilidad de cada RF (`RF-DOM-NN`) y sus artefactos relacionados.

---
estado: aceptada
version: "1.0"
tags:
  - tipo/adr
  - dom/std
  - tema/arquitectura
  - tema/frontend
fecha: 2026-08-29
id: ADR-0008
responsable: Hugo Janssen
supersede:
reemplazado_por:
---
# ADR-0008. El showfloor lo dibuja Godot en el navegador, y con eso se retira la regla del «sin JavaScript»

## Estado

`Aceptado` — 2026-08-29. Formaliza una intención que ya existía —el componente de mapa lleva
meses construido y exportado— y que **la regla 6 contradecía por escrito**.

## Contexto

`CU-STD-009` y `CU-STD-032` piden un plano del recinto que se recorre con zoom y desplazamiento,
sobre el que se pulsa un espacio para ver su detalle. El componente que lo hace existe desde
antes que este monolito: `event-stand-map`, un proyecto de Godot exportado a WASM que se embebe
en un `<iframe>` y habla con la página por `postMessage`. Su contrato está escrito
(`docs/bridge_protocol.md`), sus estados ya son los del dominio —`disponible` / `reservado` /
`ocupado`, renombrados el 2026-08-27— y su build está exportado.

**El plan de `STD` lo daba por decidido**: la fase 3 dice literalmente *"vendorizar el build de
Godot y escribir el popover de detalle del stand en `filey.css`"*, y `CU-STD.csv` marca
`Embedded Godot View` en las dos vistas de mapa.

Lo que faltaba era la consecuencia. La regla 6 de `CLAUDE.md` decía:

> **Toda pantalla funciona sin JavaScript**, y **nada se carga de un CDN**.

Un canvas de WASM no funciona sin JavaScript de ninguna manera. Las dos frases iban juntas y
solo una sigue siendo cierta.

> [!note] Cómo se descubrió la contradicción
> Construyendo la fase 3 sin releer el plan, se hizo un mapa en **SVG servido por el
> servidor** — que satisfacía la regla 6 y no era lo acordado. El error de proceso está anotado
> aquí porque es el que importa: la regla escrita y el plan escrito decían cosas distintas, y
> nadie lo había notado porque ninguna pantalla las había puesto a las dos a prueba a la vez.

## Decisión

**El showfloor lo dibuja `event-stand-map` en el navegador, y JavaScript pasa a ser un requisito
del sistema.** La regla 6 se parte en dos:

1. **Se retira** «toda pantalla funciona sin JavaScript».
2. **Se conserva** «nada se carga de un CDN», que es independiente y sigue vigente por las
   mismas razones (control de versión, disponibilidad, privacidad). El build de Godot, con sus
   39 MB, **vive en el repositorio** como cualquier otro estático.

El reparto de responsabilidades es el del contrato del componente:

| Godot | Django |
| --- | --- |
| Dibuja el mapa, hace zoom y desplaza, detecta el clic | Sirve el JSON del mapa (`CU-STD-037`, `038`) |
| Reporta `openStand` con la caja en pantalla del espacio | Pinta el detalle y el «añadir a mi selección» |
| Mantiene el contorno de selección | Le dice cuándo se cerró el detalle (`clearSelection`) |

## Consecuencias

### Lo que se gana

- **El recorte de `RN-09` se queda en el servidor y no puede filtrarse.** El contrato lo exige:
  el mapa nunca decide qué esconder, recibe `ocupado` para los dos estados cuando quien mira es
  un aplicante. Un fallo del servidor no puede colarse por el canvas porque el canvas no tiene
  el dato.
- **Un solo renderizador para los dos públicos**, con dos cargas distintas.
- **No hacen falta cabeceras COOP/COEP**: el export es de un solo hilo.

### Lo que se paga

- **El sistema deja de funcionar sin JavaScript.** No solo el mapa: al retirar la regla, el
  resto de pantallas dejan de tener esa garantía como requisito. Las que hoy funcionan sin él
  —que son casi todas— **siguen haciéndolo**, y conviene que sigan: es accesibilidad barata
  mientras nadie tenga que pelearse con ella. Lo que cambia es que ya no bloquea.
- **39 MB de WASM en el repositorio**, y con ellos el riesgo que el plan nombra: el
  almacenamiento estático con manifiesto reescribe las URLs dentro del JS al hacer
  `collectstatic`, e `index.js` referencia el `.wasm` por nombre. Hay que **excluir ese
  directorio del manifiesto** o el mapa deja de cargar **solo en producción**.
- **El mapa tarda en arrancar.** La página enseña su propio velo hasta que llega `ready`; el
  arranque de Godot queda debajo y no se ve.

### Lo que se tira

El mapa en SVG servido por el servidor: su trazado de contornos, su CSS y sus pruebas de dibujo.
**No se tira lo que había debajo** — los modelos, el importador, el recorte de `RN-09` y el
detalle del espacio siguen valiendo, porque el contrato deja el detalle en manos de la página.

## Alternativas descartadas

**Mantener el SVG como alternativa sin JavaScript.** Serían dos renderizadores del mismo mapa
que hay que mantener a la par; el día que diverjan, el que se quede atrás es el que casi nadie
mira, y nadie se entera. La regla que lo justificaba ya no está.

**Dibujar el mapa en el servidor y quedarse ahí.** Es lo que se construyó por error. Funciona
para ver, y no para lo que el caso de uso pide: recorrer un recinto de 167 × 59 m con zoom
buscando un espacio. Con 151 cajas en pantalla, sin zoom no se leen los números.

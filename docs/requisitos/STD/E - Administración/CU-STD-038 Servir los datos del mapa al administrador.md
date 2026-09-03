---
estado: propuesta
version: "1.0"
tags:
  - tipo/caso-de-uso
  - dom/std
  - tema/mapa
fecha: 2026-08-27
id: CU-STD-038
dominio: STD
responsable: Hugo Janssen
reglas_de_negocio:
  - RN-10
  - RN-18
  - RN-19
  - RN-20
---
# CU-STD-038 Servir los datos del mapa al administrador

> [!note] Es el gemelo de CU-STD-037, y son dos a propósito
> El aplicante y el administrador piden el mismo mapa y **reciben cosas distintas**: uno ve dos
> estados y el otro tres, más quién reservó cada espacio y cuánto debe. Resolverlo con un `if`
> dentro de un solo caso de uso escondería que hay dos contratos, y el modo de fallo de
> confundirlos —enseñarle a un aplicante quién tiene apartado un stand— no da ningún síntoma.
> Ver [CU-STD-037](<../B - Reserva/CU-STD-037 Servir los datos del mapa al aplicante.md>).

## Objetivo

Entregar al componente de mapa los datos completos y sin censura del showfloor de una
convocatoria, para que el administrador opere el mapa (CU-STD-032) y corrija espacios
(CU-STD-033).

## Alcance

Componente de Stands — módulo de Administración. Es la fuente de datos de la vista A8 (mapa
completo) y de A9 (editar espacio). No cubre el dibujo ni la edición en sí.

## Actores

### Actor principal

- Administrador de la feria (con acceso a esta feria).

### Actor secundario

- Componente de mapa (`event-stand-map`).

## Disparador

El administrador abre el mapa completo del panel y el componente emite su petición de datos.

## Precondiciones

- El actor administra esta feria.
- La convocatoria tiene un mapa configurado (RN-19).

## Postcondiciones

### En éxito

- El componente recibe la retícula, los stands y las decoraciones de **esta convocatoria**.
- Cada stand viaja con su **estado real**: `disponible`, `reservado` u `ocupado` (RN-10, RN-18).
- Quien administra alcanza, para cada stand reservado, quién lo tiene y el saldo pendiente de
  esa reserva (RN-18) — **no en este JSON**; ver la nota de abajo.

> [!important] Construido el 2026-08-29 · lo de la reserva no viaja en el mapa
> `apps/stands/servicios/mapa_json.py::para_el_canvas` con `con_detalle=True` entrega los tres
> estados sin colapsar, y **eso es todo lo que distingue este caso de uso de CU-STD-037**. La
> editorial, el estado de la reserva y su saldo **no van en el JSON**: los sirve
> `views.detalle_stand`, que es la vista del panel lateral del paso 4 de
> [CU-STD-032](<CU-STD-032 Visualizar el mapa completo (con quién reservó y saldo pendiente).md>),
> y los trae solo si quien pregunta administra.
>
> **Por qué así.** El canvas no dibuja nada con esos datos —no pinta el nombre de la editorial
> sobre el espacio, ni colorea por saldo—, así que mandarlos en la carga inicial sería enviar
> 151 nombres y 151 importes a un cliente que no los usa, en la petición que ya es la más
> pesada de la pantalla. Y como el recorte de `RN-09` se juega en este mismo archivo, cuanto
> menos viaje por aquí menos superficie hay donde equivocarse: el modal se pide de uno en uno y
> pasa por su propia comprobación.
>
> Los pasos 5 y 6 de abajo se conservan porque describen bien **qué tiene que poder saber** el
> administrador; lo que cambia es por qué puerta. Si algún día el componente quiere pintar la
> ocupación por editorial, este caso de uso es el que hay que ampliar y el `con_detalle` de
> `para_el_canvas` es donde entra.

### En fallo

- No se entregan datos; el panel informa la causa.

## Flujo principal

1. El componente de mapa solicita los datos del mapa.
2. El sistema comprueba que quien pide administra esta feria.
3. El sistema toma la retícula de la convocatoria y sus stands (RN-19).
4. El sistema calcula el precio de cada stand (RN-01) con el `costo_m2` de esta convocatoria.
5. El sistema entrega el estado **real** de cada stand, **sin colapsar** (RN-18).
6. Para cada stand que pertenece a una reserva, el sistema pone a disposición la editorial que
   la tiene, el estado de esa reserva y su saldo pendiente — por la vista de detalle del
   espacio, no en esta carga (ver la nota de las postcondiciones).
7. El sistema entrega la retícula, los stands y las decoraciones.
8. El componente dibuja el mapa.

## Flujos alternos

### A1. El administrador entra en modo edición

1. El administrador activa el modo de edición del mapa (CU-STD-033).
2. El sistema entrega los mismos datos; lo que cambia es el modo en que arranca el componente.
3. Lo que el componente devuelva al guardar se atiende en CU-STD-033.

## Flujos de excepción

### E1. Quien pide no administra esta feria

1. En el paso 2 la comprobación falla.
2. El sistema no entrega datos y responde con un rechazo de acceso.
3. **No se degrada a la versión del aplicante.** Un administrador de otra feria no es un
   aplicante de ésta: darle el mapa recortado en vez de un rechazo escondería el error.

### E2. La convocatoria no tiene mapa configurado

1. En el paso 3, la convocatoria no tiene retícula ni stands.
2. El sistema lo informa y ofrece crearlo (CU-STD-033).

## Datos relevantes

### Entradas

- La convocatoria en curso.
- La identidad del administrador.

### Salidas

- Retícula del mapa: tamaño de celda, columnas, filas y metros por celda.
- Stands: clave, etiqueta, zona, forma en la retícula, metros cuadrados, precio calculado, qué
  incluye y **estado real**.
- Decoraciones.
- Por stand reservado —**servido aparte**, al abrir el espacio—: editorial, estado de la
  reserva y saldo pendiente.

## Reglas de negocio aplicables

- **RN-10:** los tres estados de un stand, aquí sin colapsar.
- **RN-18:** transparencia administrativa — es la regla que este caso de uso ejerce.
- **RN-19:** el mapa es de la convocatoria.
- **RN-20:** los estados que viajan son los del dominio.

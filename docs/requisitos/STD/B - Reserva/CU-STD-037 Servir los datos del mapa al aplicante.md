---
estado: propuesta
version: "1.0"
tags:
  - tipo/caso-de-uso
  - dom/std
  - tema/mapa
fecha: 2026-08-27
id: CU-STD-037
dominio: STD
responsable: Hugo Janssen
reglas_de_negocio:
  - RN-09
  - RN-10
  - RN-16
  - RN-19
  - RN-20
---
# CU-STD-037 Servir los datos del mapa al aplicante

> [!note] Por qué esto es un caso de uso y no un detalle de CU-STD-009
> El componente de mapa **pide sus datos**: al arrancar manda un mensaje `getMapData` y espera
> el JSON de vuelta. Ese intercambio es una operación con actor, precondiciones y una regla de
> negocio que se cumple o se incumple —RN-09— y es **el único punto donde el sistema decide qué
> le enseña a quién**. Dejarlo dentro de "visualizar el mapa" lo convertía en un detalle de
> implementación, y no lo es: es donde vive la censura.
>
> Su gemelo administrativo es [CU-STD-038](<../E - Administración/CU-STD-038 Servir los datos del mapa al administrador.md>).
> Son dos casos de uso y no uno con un `if` porque devuelven **cosas distintas** y equivocarse
> filtra información (RN-18).

## Objetivo

Entregar al componente de mapa los datos del showfloor de una convocatoria, ya recortados a lo
que un aplicante puede saber, para que el mapa los dibuje.

## Alcance

Componente de Stands — módulo de Reserva. Es la fuente de datos de la vista U2 (CU-STD-009) y
del detalle de un stand (CU-STD-010). No cubre el dibujo del mapa ni la interacción, que son del
componente.

## Actores

### Actor principal

- Aplicante (editorial / entidad expositora)

### Actor secundario

- Componente de mapa (`event-stand-map`), que es quien pide los datos.

## Disparador

El aplicante abre la vista del mapa y el componente emite su petición de datos.

## Precondiciones

- El aplicante tiene sesión iniciada.
- La editorial tiene una solicitud `aceptada` **en esta convocatoria** (RN-16).
- La convocatoria tiene un mapa configurado (RN-19).

## Postcondiciones

### En éxito

- El componente recibe la retícula, los stands y las decoraciones de **esta convocatoria**.
- Cada stand viaja con su estado ya colapsado según RN-09: `disponible` u `ocupado`. **Ningún
  stand viaja como `reservado`.**
- Ningún dato de quién reservó qué sale del servidor.

### En fallo

- No se entregan datos; el componente muestra su estado de error y la vista informa la causa.

## Flujo principal

1. El componente de mapa solicita los datos del mapa.
2. El sistema comprueba que el aplicante está habilitado para esta convocatoria (RN-16).
3. El sistema toma la retícula de la convocatoria y sus stands (RN-19).
4. El sistema calcula, para cada stand, su precio (RN-01) a partir de sus metros cuadrados y del
   `costo_m2` de la configuración de **esta** convocatoria.
5. El sistema **colapsa el estado** de cada stand: `Reservado` y `Ocupado` se entregan ambos
   como `ocupado` (RN-09). `Disponible` viaja tal cual.
6. El sistema entrega la retícula, los stands y las decoraciones del mapa.
7. El componente dibuja el mapa.

> [!important] El recorte va en la consulta, no en la respuesta ni en la pantalla
> El estado real y la identidad de quien reservó **no deben llegar al navegador**, ni siquiera
> en campos que la pantalla no pinte. Si viajaran, cualquiera con las herramientas de desarrollo
> abiertas vería qué editorial tiene apartado qué espacio.

## Flujos alternos

### A1. La convocatoria está cerrada

1. En el paso 2, la convocatoria ya no admite registros.
2. El sistema **sí entrega el mapa**: consultarlo sigue teniendo sentido para quien ya tiene una
   reserva en curso (CU-STD-013).
3. Los stands se entregan igual, pero la vista no ofrece agregarlos al carrito.

## Flujos de excepción

### E1. El aplicante no está habilitado

1. En el paso 2, la editorial no tiene una solicitud `aceptada` en esta convocatoria (RN-16).
2. El sistema no entrega datos e informa que hace falta una solicitud aceptada.

### E2. La convocatoria no tiene mapa configurado

1. En el paso 3, la convocatoria no tiene retícula ni stands (RN-19).
2. El sistema informa que el mapa no está disponible todavía.
3. Es la situación normal de una convocatoria recién creada: no es un error del aplicante.

## Datos relevantes

### Entradas

- La convocatoria en curso.
- La identidad del aplicante (para RN-16).

### Salidas

- Retícula del mapa: tamaño de celda, columnas, filas y metros por celda.
- Stands: clave, etiqueta, zona, forma en la retícula, metros cuadrados, precio calculado, qué
  incluye y estado **colapsado** (`disponible` / `ocupado`).
- Decoraciones: escenarios, servicios y rótulos del recinto.

## Reglas de negocio aplicables

- **RN-09:** el aplicante ve `ocupado` donde hay `Reservado`; el colapso ocurre aquí.
- **RN-10:** los tres estados de un stand.
- **RN-16:** solo con solicitud aceptada.
- **RN-19:** el mapa es de la convocatoria, no de la feria.
- **RN-20:** los estados que viajan son los del dominio.

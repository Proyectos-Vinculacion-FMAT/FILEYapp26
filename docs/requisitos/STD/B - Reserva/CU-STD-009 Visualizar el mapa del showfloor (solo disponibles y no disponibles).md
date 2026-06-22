---
estado: propuesta
version: 0.1
tags:
  - requisitos
  - caso-de-uso
  - stands
fecha: 2026-06-19
id: CU-STD-009
dominio: STD
reglas_de_negocio:
  - RN-09
  - RN-10
  - RN-16
---
# CU-STD-009 Visualizar el mapa del showfloor (solo disponibles y no disponibles)

## Objetivo

La editorial visualiza el mapa del showfloor para identificar qué stands puede reservar, distinguiendo únicamente los espacios disponibles de los no disponibles.

## Alcance

Componente de Stands — módulo de Reserva. Vista del usuario. El usuario no distingue Reservado de Ocupado: ambos se presentan como "no disponible" (RN-09). El detalle de cada stand se cubre en CU-STD-010.

## Actores

### Actor principal

- Usuario (editorial / entidad expositora)

## Disparador

El usuario, ya habilitado para reservar, abre el mapa del showfloor.

## Precondiciones

- El usuario tiene sesión iniciada.
- La editorial tiene una aplicación `aceptada` (habilitada para reservar, RN-16).
- El evento tiene un mapa de stands configurado.

## Postcondiciones

### En éxito

- Se muestra el mapa del evento con cada stand marcado como **disponible** o **no disponible**.

### En fallo

- No se muestra el mapa; se informa la causa (sin habilitación o sin mapa configurado).

## Flujo principal

1. El usuario abre el mapa del showfloor.
2. El sistema muestra los stands del evento, indicando para cada uno si está **disponible** o **no disponible** (los estados Reservado y Ocupado se presentan como "no disponible", RN-09).
3. El usuario navega el mapa (desplazamiento/zoom) para explorar los espacios.
4. El usuario selecciona un stand disponible para consultar su detalle (CU-STD-010).

## Flujos alternos

> [!note] Opcional
> Sin flujos alternos relevantes.

## Flujos de excepción

### E1. El usuario no está habilitado para reservar

1. En el paso 1 el sistema detecta que la editorial no tiene una aplicación `aceptada` (RN-16).
2. El sistema no muestra el mapa e informa que debe contar con una aplicación aceptada.

### E2. El evento no tiene mapa configurado

1. En el paso 2 el evento aún no tiene stands configurados en el mapa.
2. El sistema informa que el mapa no está disponible por el momento.

## Datos relevantes

### Entradas

- Evento vigente.

### Salidas

- Mapa del showfloor con la disponibilidad de cada stand.

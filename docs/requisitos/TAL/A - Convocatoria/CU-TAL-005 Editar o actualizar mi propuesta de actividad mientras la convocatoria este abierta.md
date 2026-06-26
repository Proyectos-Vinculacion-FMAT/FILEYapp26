---
estado: propuesta
version: 0.1
tags:
  - requisitos
  - caso-de-uso
  - talleres
fecha: 2026-06-25
id: CU-TAL-005
dominio: TAL
reglas_de_negocio: []
---
# CU-TAL-005 Editar o actualizar mi propuesta de actividad mientras la convocatoria esté abierta

> Borrador inicial (título y descripción). Da cobertura a RF-TAL-02.
> **Diferencia clave con EVT:** en la convocatoria infantil/juvenil **no hay dictamen ni
> solicitud de cambios del administrador** (no existe el flujo de revisión de Hipólito). Por
> eso la edición es **autogestionada**: la inicia el propio tallerista, no una observación del
> administrador. (No equivale a CU-EVT-004.)

## Objetivo

El tallerista consulta y modifica los datos de una propuesta que ya registró —para corregir un error o actualizar información— mientras la convocatoria siga abierta, manteniendo el registro vigente sin tener que crear una propuesta nueva.

## Alcance

Módulo de Talleres (TAL) — edición autogestionada de una propuesta propia. Solo aplica a propuestas de la cuenta con sesión activa y mientras la convocatoria esté `abierta` (antes de la fecha límite). No cubre el primer registro (CU-TAL-002 / CU-TAL-003) ni el registro de visitas escolares (CU-TAL-008).

## Actores

### Actor principal

- Tallerista

## Disparador

El tallerista detecta un error o necesita actualizar los datos de una propuesta que ya envió.

## Notas / diferencias respecto a EVT

- No existe estado `cambios_solicitados` ni mensaje del administrador: la edición es por iniciativa propia.
- Una vez cerrada la convocatoria, la propuesta queda fija (no editable).

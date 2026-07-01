---
estado: propuesta
version: 0.1
tags:
  - caso-de-uso
  - autenticacion
  - core-registros
  - admin
  - navegacion
fecha: 2026-06-30
id: CU-REG-006
dominio: CORE-REG
responsable: Juan Manuel Hernandez Miranda
reglas_de_negocio: []
diagramas_relacionados: []
trazabilidad:
  ddr: []
---
# CU-REG-006 Consultar los módulos administrables y entrar a un panel

> [!note] Por qué vive en REG (Core Registros) y no en EVT
> Esta pantalla es el **punto de entrada transversal** posterior al login administrativo: le
> muestra al administrador **todos** los módulos que puede gestionar (Eventos, Infantil/Juvenil,
> Stands), no solo uno. Por eso no pertenece a `EVT` (que es específico de eventos) sino al Core
> Registros, que el propio `CU-REG Índice.md` define como "la puerta de entrada a cualquier
> módulo del sistema". Se coloca en la raíz de `docs/requisitos/REG/` junto a CU-REG-001…005,
> siguiendo la convención de REG (dominio sin subcarpetas). Es la contraparte con pantalla del
> flujo A1 de CU-REG-003 (selección de módulo cuando hay más de un `RolPermiso`).

## Objetivo

Tras autenticarse, el usuario administrativo con permisos en más de un módulo visualiza los módulos que puede administrar y elige a cuál panel entrar. Reutiliza visualmente la misma pantalla de "convocatorias" que ven los usuarios externos, pero cada tarjeta lleva al **panel administrativo** del módulo, no al portal público.

## Alcance

Core Registros — navegación posterior al login del panel administrativo. No cubre la autenticación (CU-REG-003) ni las funciones internas de cada panel (`EVT`/`TAL`/`STD`). No aplica a usuarios externos.

## Actores

### Actor principal

- Usuario administrativo (con uno o varios `RolPermiso`). Caso típico del prototipo: **Hipólito como administrador general** (`modulo = *`), que puede entrar a los tres módulos.

## Disparador

El sistema termina CU-REG-003 y la cuenta tiene más de un `RolPermiso`, o el administrador ya dentro de un panel decide cambiar de módulo.

## Precondiciones

- El usuario tiene sesión administrativa activa (CU-REG-003).
- La cuenta tiene al menos un `RolPermiso` registrado.

## Postcondiciones

### En éxito

- El sistema abre el panel del módulo elegido y fija ese módulo como contexto activo de la sesión.

### En fallo

- El usuario permanece en la pantalla de selección sin entrar a ningún panel.

## Flujo principal

1. El sistema muestra las tarjetas de los módulos administrables por la cuenta (según sus `RolPermiso`): Eventos, Infantil/Juvenil, Stands.
2. El administrador selecciona un módulo.
3. El sistema abre el panel administrativo de ese módulo (para EVE: la lista de propuestas del panel de Hipólito).

## Flujos alternos

### A1. La cuenta administra un solo módulo

1. En el paso 1, el sistema detecta que la cuenta tiene un único `RolPermiso`.
2. El sistema **omite** esta pantalla y entra directamente al panel de ese módulo (esta selección solo tiene sentido con dos o más módulos).

### A2. Módulos a los que no se tiene permiso

1. La cuenta no tiene `RolPermiso = *`, sino permisos sobre módulos específicos.
2. El sistema muestra únicamente las tarjetas de los módulos permitidos (o muestra los demás deshabilitados, como referencia visual). Decisión de presentación, no de acceso: los módulos sin permiso nunca son navegables.

## Flujos de excepción

### E1. Sesión sin RolPermiso

1. La cuenta perdió sus `RolPermiso` o la sesión expiró.
2. El sistema redirige al login administrativo (CU-REG-003) sin mostrar módulos.

## Datos relevantes

### Entradas

- Selección del módulo por parte del administrador.

### Salidas

- Contexto de módulo activo fijado en la sesión.
- Panel administrativo del módulo elegido, abierto.

> [!note] Nota de prototipo (maqueta de la vista del administrador — EVT)
> En la maqueta, Hipólito se presenta como **administrador general** (`modulo = *`) y ve las
> tres tarjetas, pero **solo el panel de Eventos está construido**. Las tarjetas de
> Infantil/Juvenil y de Stands se muestran visibles pero **no navegables** (etiqueta
> "Próximamente" / deshabilitadas), porque esta primera maqueta modela exclusivamente la vista
> del administrador del módulo de Eventos.

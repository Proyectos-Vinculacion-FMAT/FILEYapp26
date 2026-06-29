---
estado: propuesta
version: 0.1
tags:
  - tipo/caso-de-uso
  - dom/std
fecha: 2026-06-22
id: CU-STD-030
modulo: E. Administración
actor_principal: Administrador
requisitos_relacionados: []
dependencias:
  - CU-STD-031
---
# CU-STD-030 Consultar la lista de expositores con solicitud aceptada

## Descripción

El administrador consulta un catálogo de todas las entidades expositoras (editoriales) que han superado el filtro de solicitud y están habilitadas para operar dentro del evento.

## Actores

- **Actor principal:** Administrador (coordinador del showfloor)

## Precondiciones

- El administrador tiene sesión iniciada.

## Disparador

El administrador selecciona la opción de "Expositores" en el menú principal (vista A6).

## Flujo principal

1. El administrador ingresa a la vista de Expositores.
2. El sistema recupera los perfiles de todas las entidades `Editorial` cuya `Solicitud` al evento en curso se encuentre en estado `aceptada`.
3. El sistema muestra una tabla o listado con columnas clave: Razón Social / Nombre Comercial, RFC, Nombre del Contacto, Teléfono y Correo.
4. El administrador utiliza los controles de búsqueda (por nombre, RFC o correo) para localizar a un expositor en particular.
5. El administrador selecciona un expositor para consultar su ficha técnica y operativa (CU-STD-031).
6. El caso de uso termina.

## Flujos alternativos

> [!note] Opcional
> Sin flujos alternos.

## Excepciones

### E1. Lista vacía
1. En el paso 2, el sistema detecta que no hay expositores con solicitud aceptada para este evento.
2. El sistema muestra un mensaje indicando que no se encontraron expositores y sugiere revisar la bandeja de solicitudes (A1).

## Postcondiciones

- **Éxito:** El administrador visualiza de forma rápida la cartera de clientes vigentes.
- **Fallo:** No aplica.

## Reglas de negocio relacionadas

- **RN-16:** Solo los expositores con solicitud aceptada se consideran participantes activos habilitados para apartar espacios.

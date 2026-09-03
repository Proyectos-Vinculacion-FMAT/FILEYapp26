---
estado: propuesta
version: 0.1
tags:
  - tipo/caso-de-uso
  - dom/std
fecha: 2026-06-22
id: CU-STD-031
modulo: E. Administración
actor_principal: Administrador
requisitos_relacionados: []
dependencias:
  - CU-STD-029
---
# CU-STD-031 Ver el detalle de un expositor (reservas, documentos, datos de empresa y contacto)

## Descripción

El administrador visualiza el expediente integral de un expositor (Editorial), lo que incluye su información fiscal, de contacto, documentos adjuntos (como la constancia fiscal) y un acceso rápido a la reserva que tenga activa.

## Actores

- **Actor principal:** Administrador (coordinador del showfloor)

## Precondiciones

- El administrador tiene sesión iniciada.
- El administrador ha seleccionado un expositor desde la lista (CU-STD-030).

## Disparador

Selección de un expositor en el listado para ver su detalle (vista A7).

## Flujo principal

1. El sistema muestra la ficha completa de la entidad `Editorial`.
2. El sistema despliega la información fiscal: Razón social, RFC, y enlace para descargar el `Documento` de Constancia de Situación Fiscal.
3. El sistema muestra los datos comerciales y sellos (`SelloEditorial`).
4. El sistema despliega la información de contacto operativo y legal.
5. El sistema muestra una sección con las `Reserva` de este expositor en esta feria —**una por convocatoria** a la que haya aplicado— con su estado, total y stands.
6. Si la editorial tiene una reserva, el administrador puede seleccionarla para ser redirigido a la gestión de esa reserva en particular (CU-STD-029).
7. El administrador finaliza su consulta y regresa a la lista.

## Flujos alternativos

> [!note] Opcional
> Sin flujos alternos.

## Excepciones

### E1. Expositor inexistente
1. El enlace o ID buscado es inválido.
2. El sistema responde **404**, con la navegación del panel intacta para volver a la lista.

> [!note] Igual que `CU-STD-029` E1
> Un 404 y no una redirección con aviso, por la misma razón: ver la nota de aquel caso de uso.

## Postcondiciones

- **Éxito:** El administrador se informa de todos los datos necesarios para facturación o atención a clientes.
- **Fallo:** No aplica.

## Reglas de negocio relacionadas

- Ninguna adicional aplicable a la consulta de información estática.

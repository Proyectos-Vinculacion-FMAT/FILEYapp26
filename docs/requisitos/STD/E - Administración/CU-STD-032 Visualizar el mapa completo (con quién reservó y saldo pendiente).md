---
estado: propuesta
version: 0.1
tags:
  - tipo/caso-de-uso
  - dom/std
fecha: 2026-06-22
id: CU-STD-032
modulo: E. Administración
actor_principal: Administrador
requisitos_relacionados: []
dependencias:
  - CU-STD-029
---
# CU-STD-032 Visualizar el mapa completo (con quién reservó y saldo pendiente)

## Descripción

El administrador visualiza el mapa interactivo del showfloor sin restricciones. A diferencia del aplicante final, el administrador puede ver la ocupación real, identificar qué editorial tiene cada stand, consultar rápidamente sus saldos pendientes y navegar directo a la gestión de sus reservas.

## Actores

- **Actor principal:** Administrador (coordinador del showfloor)

## Precondiciones

- El administrador tiene sesión iniciada.
- Existe un mapa configurado para el evento.

## Disparador

El administrador ingresa a la sección "Mapa" del menú principal (vista A8).

## Flujo principal

1. El administrador abre la vista del mapa interactivo.
2. El sistema despliega todos los stands y su estado actual (`Disponible`, `Reservado`, `Ocupado`).
3. El administrador selecciona un stand que se encuentre en estado `Reservado` u `Ocupado`.
4. El sistema despliega un panel flotante o lateral de consulta rápida que indica: 
   - Clave y dimensiones del stand.
   - Nombre Comercial de la `Editorial` que lo posee.
   - Estado de la `Reserva` (`Por confirmar`, `Confirmada` o `Pagada`).
   - Saldo pendiente de la reserva.
5. Desde ese panel, el administrador selecciona "Ver detalle de la reserva".
6. El sistema lo redirige a la vista de gestión completa de esa reserva en particular (CU-STD-029).
7. El caso de uso termina.

## Flujos alternativos

### A1. Consultar un stand disponible

1. En el paso 3, el administrador hace clic en un stand `Disponible`.
2. El sistema muestra únicamente la clave, dimensiones y el costo base. No muestra información de editorial al estar libre.

## Excepciones

> [!note] Opcional
> Sin excepciones relevantes.

## Postcondiciones

- **Éxito:** El administrador obtiene una perspectiva geográfica e informada de la ocupación del evento.
- **Fallo:** No aplica.

## Reglas de negocio relacionadas

- **RN-08:** Transparencia administrativa: el admin ve sin censura la propiedad de los stands en el mapa.

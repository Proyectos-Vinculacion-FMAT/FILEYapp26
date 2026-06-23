---
estado: propuesta
version: 0.1
tags:
  - caso-de-uso
  - autenticacion
  - core-registros
fecha: 2026-06-22
id: CU-REG-004
dominio: CORE-REG
responsable: Juan Manuel Hernandez Miranda
reglas_de_negocio: []
diagramas_relacionados: []
trazabilidad:
  ddr: []
---
# CU-REG-004 Cerrar sesión

## Objetivo

Terminar la sesión activa del usuario (externo o administrativo), invalidando el JWT en uso y dejando el sistema en estado no autenticado.

## Alcance

Core Registros. Aplica a cualquier usuario autenticado, independientemente del módulo o del mecanismo con que inició sesión (OTP o contraseña).

## Actores

### Actor principal

- Cualquier usuario autenticado (externo o administrativo)

## Disparador

El usuario presiona el botón "Cerrar sesión" desde cualquier pantalla del sistema.

## Precondiciones

- El usuario tiene una sesión activa (JWT válido en el cliente).

## Postcondiciones

### En éxito

- El JWT queda invalidado (añadido a la lista de tokens revocados o eliminado del almacenamiento del cliente).
- El usuario es redirigido a la pantalla de inicio de acceso correspondiente (portal público o panel admin, según desde dónde cerró sesión).
- Cualquier intento posterior de usar el JWT invalidado es rechazado con error 401.

### En fallo

- Si el servidor no puede procesar la revocación (error de red), el cliente elimina el token localmente de igual forma. El token expirará por su tiempo natural.

## Flujo principal

1. El usuario presiona "Cerrar sesión".
2. El cliente envía la solicitud de cierre al servidor con el JWT actual.
3. El servidor registra el JWT en la lista de tokens revocados (hasta su fecha de expiración natural).
4. El servidor responde con confirmación.
5. El cliente elimina el JWT de su almacenamiento local.
6. El sistema redirige al usuario a la pantalla de inicio de acceso.

## Flujos de excepción

### E1. Error de red al comunicar el cierre al servidor

1. El cliente no puede alcanzar al servidor.
2. El cliente elimina el JWT de su almacenamiento local de todas formas.
3. El sistema redirige al usuario a la pantalla de inicio de acceso.
4. El JWT quedará válido en el servidor hasta su expiración natural — riesgo aceptable dado que los JWTs tienen vida corta.

## Datos relevantes

### Entradas

- JWT de sesión activo (en cabecera de la solicitud)

### Salidas

- JWT añadido a la lista de revocados en el servidor
- Redirección a pantalla de acceso

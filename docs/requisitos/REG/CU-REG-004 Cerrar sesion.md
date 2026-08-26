---
estado: aprobado
version: 0.4
tags:
  - caso-de-uso
  - autenticacion
  - core-registros
fecha: 2026-06-22
fecha_actualizacion: 2026-08-21
id: CU-REG-004
dominio: CORE-REG
responsable: Juan Manuel Hernandez Miranda
reglas_de_negocio: []
diagramas_relacionados: []
trazabilidad:
  ddr: []
---
# CU-REG-004 Cerrar sesión

> [!important] Actualización 2026-08-21 — este CU describía un problema que ya no existe
> La v0.3 describía el cierre de sesión sobre un par de tokens JWT: revocar el *refresh token*
> en una lista de revocados, borrar ambos del almacenamiento del navegador, y **aceptar que el
> *access token* siguiera siendo válido hasta una hora después**. Esa contrapartida estaba
> registrada como "decisión pendiente" con dos salidas posibles, ninguna buena.
>
> Con la migración al monolito ([ADR-0002](<../../adr/0002-migracion-de-registro-al-monolito.md>))
> el problema desapareció por completo: la sesión vive en el servidor, así que cerrarla es
> **inmediato y total**. No hay lista de revocados que mantener, ni credencial que siga sirviendo
> después de cerrar, ni decisión pendiente que tomar.

## Objetivo

Terminar la sesión activa del usuario (externo o administrativo), dejando el sistema en estado no
autenticado de forma inmediata.

## Alcance

Core Registros. Aplica a cualquier usuario autenticado, sea aplicante (externo) o administrativo.
Todos inician sesión por OTP por correo (CU-REG-002 / CU-REG-003), por lo que el cierre de sesión
es idéntico para todos.

## Actores

### Actor principal

- Cualquier usuario autenticado (externo o administrativo)

## Disparador

El usuario presiona el botón "Cerrar sesión" desde cualquier pantalla del sistema.

## Precondiciones

- El usuario tiene una sesión activa.

## Postcondiciones

### En éxito

- **La sesión deja de existir en el servidor.** Cualquier petición posterior con esa cookie es
  tratada como no autenticada.
- El navegador recibe una cookie caducada, de modo que tampoco conserva el identificador.
- Se descarta el **contexto de feria** de la sesión: quien vuelva a entrar elegirá feria de nuevo
  (CU-FER-002).
- El usuario es redirigido a la pantalla de acceso correspondiente (portal público o acceso
  administrativo, según desde dónde cerró sesión).

### En fallo

- Ver E1: no hay un caso de fallo que deje al usuario dentro.

## Flujo principal

1. El usuario presiona "Cerrar sesión".
2. El sistema elimina la sesión del servidor y caduca la cookie del navegador.
3. El sistema redirige al usuario a la pantalla de acceso que le corresponde.

> [!note] Por qué cerrar sesión es una acción que modifica, no un enlace
> La petición de cierre se envía como **POST protegido contra CSRF**, no como un enlace. Un
> enlace `GET` puede dispararlo cualquier página de terceros —o un precargador del navegador—
> sacando al usuario de su sesión sin que lo pidiera. Es una molestia pequeña, pero gratuita de
> evitar.

## Flujos de excepción

### E1. Error de red al comunicar el cierre al servidor

1. El navegador no alcanza al servidor.
2. La sesión **sigue abierta en el servidor**, porque nunca llegó la orden de cerrarla, y
   caducará por su tiempo natural.
3. El usuario ve el error y puede reintentar. A diferencia de la v0.3, aquí no hay nada que el
   cliente pueda "borrar localmente" para dar el cierre por bueno: la sesión no vive en el
   cliente.

> [!warning] Riesgo real de este caso, y cómo se acota
> Si alguien cierra sesión en una computadora compartida y el cierre falla por red, la sesión
> sigue viva hasta caducar. Lo que lo acota es la **duración de la sesión** (12 horas de
> inactividad) y que el cierre se pueda reintentar. Si el equipo decidiera acortar ese plazo,
> este es el caso que lo justificaría.

## Datos relevantes

### Entradas

- La cookie de sesión, que acompaña automáticamente a la petición de cierre.

### Salidas

- Sesión eliminada del servidor.
- Cookie de sesión caducada en el navegador.
- Redirección a la pantalla de acceso.

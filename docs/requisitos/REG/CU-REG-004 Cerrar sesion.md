---
estado: aprobado
version: 0.3
tags:
  - caso-de-uso
  - autenticacion
  - core-registros
fecha: 2026-06-22
fecha_actualizacion: 2026-08-05
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

Core Registros. Aplica a cualquier usuario autenticado, sea aplicante (externo) o administrativo. Todos inician sesión por OTP por correo (CU-REG-002 / CU-REG-003), por lo que el cierre de sesión es idéntico para todos: invalidar el JWT de la sesión activa.

## Actores

### Actor principal

- Cualquier usuario autenticado (externo o administrativo)

## Disparador

El usuario presiona el botón "Cerrar sesión" desde cualquier pantalla del sistema.

## Precondiciones

- El usuario tiene una sesión activa (JWT válido en el cliente).

## Postcondiciones

### En éxito

- El **token de renovación** queda revocado en el servidor: la sesión ya no se puede prolongar.
- El cliente elimina de su almacenamiento tanto el token de acceso como el de renovación.
- El usuario es redirigido a la pantalla de inicio de acceso correspondiente (portal público o panel admin, según desde dónde cerró sesión).
- Cualquier intento posterior de renovar la sesión con el token revocado es rechazado.

> [!warning] Precisión importante — el token de acceso no se revoca al instante
> La sesión usa **dos** tokens: uno de **acceso** (de vida corta, el que acompaña cada petición)
> y uno de **renovación** (de vida más larga, el que permite obtener accesos nuevos). Cerrar
> sesión revoca el de **renovación**; el de **acceso** que ya estaba emitido **sigue siendo
> válido hasta que caduca por sí solo** — actualmente hasta **1 hora**.
>
> En la práctica esto no afecta a la persona que cierra sesión (su navegador ya borró el token),
> pero sí importa en un caso concreto: si alguien copió el token de acceso antes del cierre,
> conserva acceso durante esa hora. Es la contrapartida conocida de este tipo de sesiones, que
> no consultan la base de datos en cada petición.
>
> **Decisión pendiente:** si se considera demasiado tiempo, hay dos salidas — acortar la vida
> del token de acceso (más renovaciones, más carga) o verificar revocaciones en cada petición
> (más seguro, más consultas). No se ha decidido; hoy rige 1 hora.

### En fallo

- Si el servidor no puede procesar la revocación (error de red), el cliente elimina el token localmente de igual forma. El token expirará por su tiempo natural.

## Flujo principal

1. El usuario presiona "Cerrar sesión".
2. El cliente envía la solicitud de cierre al servidor, incluyendo su **token de renovación**.
3. El servidor registra ese token en la lista de revocados (hasta su fecha de expiración natural).
4. El servidor responde con confirmación. **Si el token ya era inválido o estaba expirado, responde igualmente con éxito**: el objetivo —que no sirva— ya se cumple, y fallar aquí solo dejaría al usuario atrapado en una sesión que quiere abandonar.
5. El cliente elimina de su almacenamiento local ambos tokens (acceso y renovación).
6. El sistema redirige al usuario a la pantalla de inicio de acceso.

## Flujos de excepción

### E1. Error de red al comunicar el cierre al servidor

1. El cliente no puede alcanzar al servidor.
2. El cliente elimina sus tokens del almacenamiento local de todas formas.
3. El sistema redirige al usuario a la pantalla de inicio de acceso.
4. El token de renovación quedará válido en el servidor hasta su expiración natural. Riesgo acotado: nadie más lo tiene, porque el cliente ya lo borró.

## Datos relevantes

### Entradas

- Token de renovación de la sesión activa
- Token de acceso (autentica la propia petición de cierre)

### Salidas

- Token de renovación añadido a la lista de revocados en el servidor
- Almacenamiento local del cliente limpio
- Redirección a pantalla de acceso

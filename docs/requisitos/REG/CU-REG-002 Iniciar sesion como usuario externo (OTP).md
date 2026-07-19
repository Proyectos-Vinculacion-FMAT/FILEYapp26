---
estado: aceptado
version: 0.1
tags:
  - caso-de-uso
  - autenticacion
  - core-registros
  - otp
fecha: 2026-06-22
id: CU-REG-002
dominio: CORE-REG
responsable: Juan Manuel Hernandez Miranda
reglas_de_negocio: []
diagramas_relacionados: []
trazabilidad:
  ddr: []
---
# CU-REG-002 Iniciar sesión como usuario externo (OTP por correo)

## Objetivo

Autenticar a un usuario externo (proponente, tallerista, representante escolar) mediante un código de un solo uso enviado a su correo, sin necesidad de contraseña. El usuario obtiene una sesión activa para operar en el módulo que le corresponde.

## Alcance

Core Registros. Aplica a todos los usuarios con cuenta en `Persona` que no tienen `RolPermiso` administrativo. No aplica a usuarios administrativos (ver CU-REG-003).

## Actores

### Actor principal

- Usuario externo (proponente, tallerista o representante escolar con cuenta registrada)

### Actores secundarios

- Sistema de correo (Resend desde dominio filey.org) — envía el OTP.

## Disparador

El usuario ingresa su correo en la pantalla de acceso y el sistema lo reconoce como cuenta existente sin rol administrativo.

## Precondiciones

- El correo ingresado existe en `Persona` con `estado = activa`.
- La cuenta no tiene `RolPermiso` con `modulo` distinto de público (en ese caso aplica CU-REG-003).

## Postcondiciones

### En éxito

- Se crea una entrada en `SesionOTP` con `usado = true` (quemado al validar).
- El sistema emite un JWT de sesión con `persona_id` y el módulo al que pertenece.
- El usuario queda autenticado y es redirigido a su panel (ej. lista de propuestas en EVE, panel de tallerista en TAL).

### En fallo

- No se emite ningún JWT. El usuario permanece sin sesión.
- El OTP queda invalidado si fue el último intento permitido.

## Flujo principal

1. El usuario ingresa su correo en la pantalla de acceso.
2. El sistema reconoce el correo como cuenta existente sin rol administrativo.
3. El sistema genera un código OTP de 6 dígitos aleatorios.
4. El sistema almacena el OTP hasheado en `SesionOTP` con `expira_en = ahora + 15 minutos`, `usado = false`, `canal = correo`.
5. El sistema envía el código al correo del usuario desde `noreply@filey.org`.
6. El sistema muestra una pantalla con un campo para ingresar el código de 6 dígitos e indica que tiene 15 minutos para usarlo.
7. El usuario ingresa el código recibido.
8. El sistema valida: (a) el código coincide con el hash almacenado, (b) `expira_en` no ha pasado, (c) `usado = false`.
9. El sistema marca el OTP como `usado = true`.
10. El sistema emite un JWT de sesión firmado con `persona_id`, rol y expiración de sesión.
11. El sistema redirige al usuario a su panel principal.

## Flujos alternos

### A1. El usuario no recibió el código (reenvío)

1. Tras 60 segundos de espera, el sistema habilita el botón "Reenviar código".
2. El usuario solicita reenvío.
3. El sistema invalida el OTP anterior (`usado = true`) y genera uno nuevo desde el paso 3 del flujo principal.

### A2. Sesión iniciada desde CU-REG-001 (cuenta recién creada)

1. CU-REG-001 ya verificó el correo — el sistema entra directamente en el paso 3 sin repetir el paso 1-2.

## Flujos de excepción

### E1. Código incorrecto

1. En el paso 8, el código no coincide con el hash almacenado.
2. El sistema muestra el número de intentos restantes (máximo 3 por OTP emitido).
3. Si hay intentos restantes, el usuario puede volver a ingresar el código.
4. Al agotar los 3 intentos, el OTP queda invalidado y el sistema obliga a solicitar uno nuevo (A1).

### E2. Código expirado

1. En el paso 8, `expira_en` ya pasó.
2. El sistema informa la expiración y ofrece directamente el botón "Enviar nuevo código".
3. El flujo retoma desde A1.

### E3. Fallo en el envío del correo

1. En el paso 5, el servicio de correo devuelve error.
2. El sistema no muestra la pantalla de código; informa al usuario que el correo no pudo enviarse y le pide intentar de nuevo en unos minutos.
3. No se crea ningún registro `SesionOTP` si el envío falló antes de almacenarlo, o se invalida si ya se almacenó.

### E4. se ingresa mas de 5 veces incorrectamente el codigo

1. en el paso 7, el usuario ingresa mas de 5 veces el codigo incorrectamante
2. el sistema le avisa al usuario que ya no puede intentar con ese codigo, por lo que tiene que generar uno nuevo
3. y se le reenvia un codigo nuevo para que lo vuelva a intentar 

### E5. presiana el boton reenviar 

1. en el paso 6, cuando el usuario esta en la pantalla de OTP, debe tener la opportuindad de apretar el boton de reenviar
2. luego de que aprete reenviar las contraseñas que se hayan mandado anteriormente por correo no seran validas
3. cuando el boton sea apretado, tendra un cool-down de 30 segundos para que se pueda enviar de nuevo el codigo

## Datos relevantes

### Entradas

- Correo electrónico (pantalla inicial)
- Código OTP de 6 dígitos (pantalla de verificación)

### Salidas

- JWT de sesión (persona_id, módulo, expiración)
- Registro `SesionOTP` actualizado (`usado = true`)

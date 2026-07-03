---
estado: aceptado
version: 0.2
tags:
  - caso-de-uso
  - autenticacion
  - core-registros
  - admin
  - otp
fecha: 2026-06-22
fecha_actualizacion: 2026-06-30
id: CU-REG-003
dominio: CORE-REG
responsable: Juan Manuel Hernandez Miranda
reglas_de_negocio: []
diagramas_relacionados: []
trazabilidad:
  ddr: []
---
# CU-REG-003 Iniciar sesión como usuario administrativo (OTP por correo)

> [!important] Cambio de decisión (2026-06-30) — el admin ahora entra con OTP, no con contraseña
> En la versión 0.1 este CU definía el acceso administrativo mediante **correo + contraseña**.
> El equipo decidió **unificar el acceso administrativo con el de usuarios externos usando OTP
> por correo**, para simplificar la implementación y no mantener dos mecanismos de
> autenticación distintos. Ya no hay contraseñas para administradores: entran con el mismo
> código de un solo uso que los usuarios externos (ver CU-REG-002). La diferencia entre ambos
> perfiles pasa a ser únicamente el `RolPermiso` de la cuenta, no el mecanismo de login.
>
> Consecuencias en otros CUs (pendientes de homologar): CU-REG-005 ya no envía un enlace para
> "establecer contraseña" — provisionar una cuenta administrativa se reduce a crear la
> `Persona` (si no existe) y su `RolPermiso`; a partir de ahí la persona entra por OTP.

## Objetivo

Autenticar a un usuario con rol administrativo (Hipólito, Elvira, administrador general) mediante un código de un solo uso (OTP) enviado a su correo, otorgando una sesión con permisos acotados a su(s) módulo(s). Se usa el mismo mecanismo que para usuarios externos (CU-REG-002); lo que distingue a un administrador es tener al menos un `RolPermiso` registrado.

## Alcance

Core Registros — panel de administración. Aplica únicamente a cuentas con `RolPermiso` registrado (`nivel = edicion` o `nivel = lectura`). El mecanismo de autenticación es idéntico al de CU-REG-002 (OTP); la diferencia está en el destino tras iniciar sesión (panel administrativo en lugar del portal público) y en la selección de módulo cuando la cuenta administra más de uno (CU-REG-006).

## Actores

### Actor principal

- Usuario administrativo (Hipólito — EVE, Elvira — TAL, Administrador general — todos los módulos)

### Actores secundarios

- Sistema de correo (Resend desde dominio filey.org) — envía el OTP.

## Disparador

El usuario accede a la URL del panel de administración (ruta diferenciada del portal público, ej. `/admin`, o el enlace "Acceso administrativo") e ingresa su correo.

## Precondiciones

- El usuario tiene una cuenta en `Persona` con al menos un `RolPermiso` registrado.

## Postcondiciones

### En éxito

- Se crea una entrada en `SesionOTP` con `usado = true` (quemado al validar).
- El sistema emite un JWT de sesión con `persona_id` y el/los `modulo`/`nivel` de sus `RolPermiso`.
- El usuario es redirigido:
  - Si tiene un solo `RolPermiso`: directamente al panel de ese módulo.
    - `modulo = EVE` → panel de Hipólito (gestión de propuestas, programa general).
    - `modulo = TAL` → panel de Elvira (talleres y visitas escolares).
    - `modulo = EVE, nivel = lectura` → panel de solo lectura (para supervisores).
  - Si tiene más de un `RolPermiso` (ej. administrador general con `modulo = *`): a la pantalla de selección de módulo (CU-REG-006) para elegir a qué panel entrar.

### En fallo

- No se emite ningún JWT. El usuario permanece sin sesión en el panel de administración.
- El OTP queda invalidado si fue el último intento permitido.

## Flujo principal

1. El usuario accede a la URL del panel de administración (o al enlace "Acceso administrativo").
2. El sistema muestra la pantalla de acceso e ingresa su correo.
3. El sistema verifica que el correo existe en `Persona` y tiene al menos un `RolPermiso`.
4. El sistema genera un código OTP de 6 dígitos aleatorios y lo almacena hasheado en `SesionOTP` con `expira_en = ahora + 15 minutos`, `usado = false`, `canal = correo`.
5. El sistema envía el código al correo del usuario desde `noreply@filey.org`.
6. El sistema muestra la pantalla para ingresar el código de 6 dígitos e indica que tiene 15 minutos para usarlo.
7. El usuario ingresa el código recibido.
8. El sistema valida: (a) el código coincide con el hash almacenado, (b) `expira_en` no ha pasado, (c) `usado = false`.
9. El sistema marca el OTP como `usado = true`.
10. El sistema emite un JWT de sesión firmado con `persona_id`, el/los `modulo`/`nivel` de sus `RolPermiso` y expiración de sesión.
11. El sistema registra la fecha/hora de último acceso en `Persona`.
12. El sistema redirige: al panel del módulo si tiene uno solo, o a la selección de módulo (CU-REG-006) si tiene varios.

## Flujos alternos

### A1. Usuario con permisos en múltiples módulos

1. En el paso 12, el sistema detecta más de un `RolPermiso` para la persona (caso típico: administrador general con `modulo = *`).
2. El sistema deriva a la pantalla de selección de módulo (CU-REG-006): "¿A qué sección deseas entrar?".
3. El usuario selecciona el módulo y el sistema abre el panel correspondiente.

### A2. El usuario no recibió el código (reenvío)

1. Tras 60 segundos de espera, el sistema habilita el botón "Reenviar código".
2. El usuario solicita reenvío.
3. El sistema invalida el OTP anterior (`usado = true`) y genera uno nuevo desde el paso 4 del flujo principal.

## Flujos de excepción

### E1. Código incorrecto

1. En el paso 8, el código no coincide con el hash almacenado.
2. El sistema muestra el número de intentos restantes (máximo 3 por OTP emitido).
3. Si hay intentos restantes, el usuario puede volver a ingresar el código.
4. Al agotar los 3 intentos, el OTP queda invalidado y el sistema obliga a solicitar uno nuevo (A2).

### E2. Código expirado

1. En el paso 8, `expira_en` ya pasó.
2. El sistema informa la expiración y ofrece el botón "Enviar nuevo código".
3. El flujo retoma desde A2.

### E3. Cuenta sin RolPermiso administrativo

1. El correo existe en `Persona` pero no tiene ningún `RolPermiso` registrado.
2. El sistema no otorga acceso al panel administrativo y trata la cuenta como usuario externo (CU-REG-002), redirigiéndola al portal público.

### E4. Fallo en el envío del correo

1. En el paso 5, el servicio de correo devuelve error.
2. El sistema no muestra la pantalla de código; informa que el correo no pudo enviarse y pide intentar de nuevo en unos minutos.
3. No se crea ningún registro `SesionOTP` si el envío falló antes de almacenarlo, o se invalida si ya se almacenó.

## Datos relevantes

### Entradas

- Correo electrónico (pantalla inicial)
- Código OTP de 6 dígitos (pantalla de verificación)

### Salidas

- JWT de sesión (persona_id, modulo(s), nivel, expiración)
- Registro `SesionOTP` actualizado (`usado = true`)
- Actualización de último acceso en `Persona`

> [!note]
> La creación de cuentas administrativas y la asignación de `RolPermiso` no forman parte de
> este CU (ver CU-REG-005). Con el cambio a OTP, provisionar una cuenta administrativa ya no
> implica establecer contraseña: basta con que exista la `Persona` y su `RolPermiso` para que
> la persona pueda iniciar sesión por OTP.

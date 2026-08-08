---
estado: aceptado
version: 0.3
tags:
  - caso-de-uso
  - autenticacion
  - core-registros
  - admin
  - otp
fecha: 2026-06-22
fecha_actualizacion: 2026-08-05
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
> Consecuencias en otros CUs (ya homologadas): CU-REG-005 ya no envía un enlace para
> "establecer contraseña" — provisionar una cuenta administrativa se reduce a crear la
> `Persona` (si no existe) y su `RolPermiso`; a partir de ahí la persona entra por OTP.

> [!important] Cambio 2026-08-05 — el acceso administrativo ya no revela quién es administrador
> Saber **qué correos son administradores** es el dato que un atacante más quiere: le permite
> dirigir phishing o fuerza bruta contra las cuentas con más poder del sistema. En la v0.2, este
> CU respondía "no estás registrado como administrador" (E3), lo que convertía la pantalla de
> acceso en una herramienta para averiguar esa lista a razón de un correo por intento.
>
> A partir de esta versión, el acceso administrativo responde **exactamente igual** en los tres
> casos —administrador real, participante sin permisos y correo inexistente— en cuerpo, código
> de respuesta y **tiempo de respuesta**. Quien no sea administrador simplemente nunca recibe
> el código. **E3 queda derogado** (ver abajo).
>
> Este CU hereda además todo lo definido en CU-REG-002 sobre límites de emisión, intentos y
> envío en segundo plano (A1, E1, E6, E7 de aquel CU).

## Objetivo

Autenticar a un usuario con rol administrativo (Hipólito, Elvira, administrador general) mediante un código de un solo uso (OTP) enviado a su correo, otorgando una sesión con permisos acotados a su(s) módulo(s). Se usa el mismo mecanismo que para usuarios externos (CU-REG-002); lo que distingue a un administrador es tener al menos un `RolPermiso` registrado.

## Alcance

Core Registros — panel de administración. Aplica únicamente a cuentas con `RolPermiso` registrado (`nivel = edicion` o `nivel = lectura`). El mecanismo de autenticación es idéntico al de CU-REG-002 (OTP); la diferencia está en el destino tras iniciar sesión (panel administrativo en lugar del portal público) y en la selección de módulo cuando la cuenta administra más de uno (CU-REG-006).

## Actores

### Actor principal

- Usuario administrativo (Hipólito — EVT, Elvira — TAL, Administrador general — todos los módulos)

### Actores secundarios

- **Sistema de correo** — envía el OTP. Mismo servicio y mismas condiciones que CU-REG-002 (remitente del dominio de la feria; envío en segundo plano).

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
    - `modulo = EVT` → panel de Hipólito (gestión de propuestas, programa general).
    - `modulo = TAL` → panel de Elvira (talleres infantiles/juveniles).
    - `modulo = VIS` → panel de visitas escolares.
    - `modulo = STD` → panel de stands.
    - `nivel = lectura` → el mismo panel, sin capacidad de modificar (supervisores).
  - Si tiene más de un `RolPermiso` (ej. administrador general con `modulo = *`): a la pantalla de selección de módulo (CU-REG-006) para elegir a qué panel entrar.

### En fallo

- No se emite ningún JWT. El usuario permanece sin sesión en el panel de administración.
- El OTP queda invalidado si fue el último intento permitido.

## Flujo principal

1. El usuario accede a la URL del panel de administración (o al enlace "Acceso administrativo").
2. El sistema muestra la pantalla de acceso y el usuario ingresa su correo.
3. El sistema comprueba **internamente** si el correo existe en `Persona` y tiene al menos un `RolPermiso`. **El resultado de esta comprobación nunca se refleja en la respuesta** (ver A3).
4. El sistema comprueba los límites de emisión de la cuenta (cool-down y tope por ventana, según A1/E6 de CU-REG-002).
5. El sistema genera un código OTP de 6 dígitos, invalida los anteriores de esa cuenta y lo almacena hasheado en `SesionOTP` con `expira_en = ahora + 15 minutos`, `usado = false`, `canal = correo`.
6. El sistema despacha el correo **en segundo plano** desde el buzón del dominio de la feria, y responde de inmediato.
7. El sistema muestra la pantalla para ingresar el código de 6 dígitos e indica que tiene 15 minutos para usarlo, advirtiendo que el código llegará **solo si el correo corresponde a una cuenta administrativa**.
8. El usuario ingresa el código recibido.
9. El sistema valida: (a) el código coincide con el hash almacenado, (b) `expira_en` no ha pasado, (c) `usado = false`, (d) **la cuenta sigue teniendo al menos un `RolPermiso`**.
10. El sistema marca el OTP como `usado = true`.
11. El sistema emite un JWT de sesión ligado a `persona_id`. Igual que en CU-REG-002, **el JWT no lleva dentro el módulo ni el nivel**: cada petición al panel revalida los `RolPermiso` contra la base de datos.
12. El sistema registra la fecha/hora de último acceso en `Persona`.
13. El sistema redirige: al panel del módulo si tiene uno solo, o a la selección de módulo (CU-REG-006) si tiene varios.

> [!important] La autorización vive en el servidor, no en la pantalla
> El hecho de tener un JWT válido **no** da acceso al panel administrativo: un participante que
> obtenga un código válido por el flujo público no puede usarlo para entrar al panel, porque el
> servidor revalida `RolPermiso` en cada consulta. Las validaciones del navegador son solo
> comodidad visual.

## Flujos alternos

### A1. Usuario con permisos en múltiples módulos

1. En el paso 12, el sistema detecta más de un `RolPermiso` para la persona (caso típico: administrador general con `modulo = *`).
2. El sistema deriva a la pantalla de selección de módulo (CU-REG-006): "¿A qué sección deseas entrar?".
3. El usuario selecciona el módulo y el sistema abre el panel correspondiente.

### A2. El usuario no recibió el código (reenvío)

1. Tras 60 segundos de espera, el sistema habilita el botón "Reenviar código".
2. El usuario solicita reenvío.
3. El sistema invalida el OTP anterior (`usado = true`) y genera uno nuevo desde el paso 5 del flujo principal.
4. Aplican íntegros el cool-down y los topes definidos en CU-REG-002 (A1, E6), incluida la advertencia sobre volver a entrar antes de 60 s tras cerrar sesión.

### A3. El correo no corresponde a una cuenta administrativa (respuesta uniforme)

1. En el paso 3, el correo no existe en `Persona`, o existe pero no tiene ningún `RolPermiso`.
2. El sistema **no crea ningún registro y no envía ningún correo**, pero responde exactamente igual que en el flujo principal: mismo mensaje, mismo código de respuesta y mismo tiempo de respuesta.
3. El sistema simula el comportamiento observable de un OTP real —cool-down, topes de emisión, conteo de intentos y expiración— de modo que un atacante que sondee la pantalla no pueda distinguir este camino del real. **Ningún código introducido aquí puede acertar jamás.**
4. La persona ve la pantalla de código y nunca recibe nada.

> [!note] Por qué también se iguala el tiempo
> Aunque el mensaje sea idéntico, el camino real tarda más (hashear el código, escribir en base
> de datos, contactar al servidor de correo). Esa diferencia de milisegundos bastaba para
> distinguir a un administrador. Por eso ambos caminos se retienen hasta un mínimo común y el
> envío del correo se sacó de la respuesta.

## Flujos de excepción

### E1. Código incorrecto

1. En el paso 9, el código no coincide con el hash almacenado.
2. El sistema muestra el número de intentos restantes (máximo 3 por OTP emitido).
3. Si hay intentos restantes, el usuario puede volver a ingresar el código.
4. Al agotar los 3 intentos, el OTP queda invalidado y el sistema obliga a solicitar uno nuevo (A2).
5. La respuesta es idéntica a la que recibe un correo no administrativo en A3.

### E2. Código expirado

1. En el paso 9, `expira_en` ya pasó.
2. El sistema informa la expiración y ofrece el botón "Enviar nuevo código".
3. El flujo retoma desde A2.

### E3. ~~Cuenta sin RolPermiso administrativo~~ — DEROGADO

> [!caution] Derogado el 2026-08-05 — publicaba la lista de administradores
> La v0.2 exigía informar que la cuenta no es administrativa y redirigir al portal público. Ese
> mensaje era exactamente el oráculo que permitía enumerar administradores: bastaba probar
> correos y ver cuál *no* recibía el aviso. **Ahora rige A3: la respuesta es indistinguible y
> la persona simplemente nunca recibe el código.**
>
> **Costo asumido en experiencia de uso:** alguien que se equivoque de pantalla (un participante
> que entra por `/admin/acceso`) no recibe ninguna pista de su error — verá la pantalla de
> código y esperará un correo que no llega. Se aceptó a cambio de no publicar qué cuentas son
> administrativas. La pantalla lo advierte con un texto genérico ("si este correo corresponde a
> una cuenta administrativa, recibirás un código").

### E4. Fallo en el envío del correo

1. En el paso 6, el servicio de correo devuelve error. Como el envío ocurre en segundo plano, el fallo se detecta después de responder.
2. El sistema invalida el código recién emitido: no queda ningún OTP utilizable.
3. El administrador ve la pantalla de código y, al no recibir nada, usa "Enviar nuevo código". El motivo del fallo queda en la bitácora del servidor. Idéntico a E3 de CU-REG-002.

### E5. Demasiadas solicitudes o intentos fallidos

1. Aplican íntegros E6 y E7 de CU-REG-002 (tope de 5 emisiones por 15 min; bloqueo tras 10 fallos en 15 min).
2. Las respuestas de bloqueo son también idénticas entre el camino real y el de A3, para no reintroducir la distinción por comportamiento.

## Datos relevantes

### Entradas

- Correo electrónico (pantalla inicial)
- Código OTP de 6 dígitos (pantalla de verificación)

### Salidas

- JWT de sesión (`persona_id`, expiración). Los módulos y niveles **no** viajan en el token: se consultan por petición.
- Registro `SesionOTP` actualizado (`usado = true`)
- Actualización de último acceso en `Persona`

## Requisito de despliegue

El comportamiento uniforme de A3 se sostiene sobre un estado temporal (el que simula cool-down,
topes e intentos de los correos no administrativos). En producción, con **varios procesos
atendiendo peticiones**, ese estado debe vivir en un almacén **compartido** entre todos ellos. Si
cada proceso guarda el suyo, las respuestas dejan de ser consistentes y la diferencia vuelve a
delatar quién es administrador.

> [!note]
> La creación de cuentas administrativas y la asignación de `RolPermiso` no forman parte de
> este CU (ver CU-REG-005). Con el cambio a OTP, provisionar una cuenta administrativa ya no
> implica establecer contraseña: basta con que exista la `Persona` y su `RolPermiso` para que
> la persona pueda iniciar sesión por OTP.

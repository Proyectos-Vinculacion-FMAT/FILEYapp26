---
estado: aceptado
version: 0.4
tags:
  - caso-de-uso
  - autenticacion
  - core-registros
  - admin
  - otp
fecha: 2026-06-22
fecha_actualizacion: 2026-08-21
id: CU-REG-003
dominio: CORE-REG
responsable: Juan Manuel Hernandez Miranda
reglas_de_negocio: []
diagramas_relacionados: []
trazabilidad:
  ddr: []
---
# CU-REG-003 Iniciar sesión como usuario administrativo (OTP por correo)

> [!important] Cambio de decisión (2026-06-30) — el admin entra con OTP, no con contraseña
> En la versión 0.1 este CU definía el acceso administrativo mediante **correo + contraseña**.
> El equipo unificó el acceso administrativo con el de usuarios externos usando OTP por correo,
> para no mantener dos mecanismos de autenticación distintos. Ya no hay contraseñas para
> administradores. La diferencia entre ambos perfiles es únicamente **qué puede hacer la cuenta**,
> no cómo entra.

<!-- -->

> [!important] Cambio 2026-08-21 — tres correcciones a la vez
> Esta versión corrige tres cosas que la v0.3 daba por ciertas y ya no lo eran:
>
> | Qué | v0.3 | v0.4 |
> | --- | --- | --- |
> | Qué se emite al autenticar | Un **JWT** con *access* y *refresh token* | **Sesión de Django** con cookie `HttpOnly` (ver [ADR-0002](<../../adr/0002-migracion-de-registro-al-monolito.md>)) |
> | Qué define a un administrador | Tener al menos un `RolPermiso` (módulo + nivel) | **Administrar al menos una feria** (`AdminFeria`, ver [ADR-0004](<../../adr/0004-acceso-administrativo-por-feria.md>)) |
> | Correo que no es administrativo | Respuesta **indistinguible** del caso real; nunca llegaba el código (A3, con señuelo) | Se responde **"Correo incorrecto."** si la cuenta no existe; si existe, el flujo continúa igual que en el portal público y el permiso se comprueba **después** del código (nuevas A3 y E3) |
>
> El tercer cambio revierte una decisión de seguridad del 2026-08-05. **La razón por la que
> revertirlo no reabre el agujero está explicada en A3** — no es un descuido, es que el agujero
> se tapa en otro punto del flujo.

## Objetivo

Autenticar a un usuario con acceso administrativo mediante un código de un solo uso (OTP)
enviado a su correo, y llevarlo al panel de la feria que administra. Se usa el mismo mecanismo
que para usuarios externos (CU-REG-002); lo que distingue a un administrador es **administrar al
menos una feria**.

## Alcance

Core Registros — acceso al panel de administración. Aplica a cuentas con al menos una fila en
`AdminFeria`, sean dueñas de la feria o no. El mecanismo de autenticación es idéntico al de
CU-REG-002; la diferencia está en el destino tras iniciar sesión (panel de una feria en lugar
del portal público) y en la selección de feria cuando la cuenta administra más de una
(CU-FER-002).

## Actores

### Actor principal

- Usuario administrativo: dueño o administrador de al menos una feria.

### Actores secundarios

- **Sistema de correo** — envía el OTP. Mismo servicio y mismas condiciones que CU-REG-002
  (remitente del dominio de la feria; envío en segundo plano).

## Disparador

El usuario accede a la URL del panel de administración (o al enlace "Acceso administrativo") e
ingresa su correo.

## Precondiciones

- El usuario tiene una cuenta en `Persona` con estado `activa`.
- Para **entrar** (no para recibir el código): al menos una fila en `AdminFeria`.

## Postcondiciones

### En éxito

- La entrada en `SesionOTP` queda con `usado = true` (quemada al validar).
- El sistema **abre una sesión de servidor** ligada a `persona_id`, con cookie `HttpOnly`. **La
  sesión no lleva dentro qué ferias administra**: se consulta `AdminFeria` en cada petición, para
  que retirar un acceso (CU-FER-004) surta efecto de inmediato.
- Se registra el último acceso en `Persona`.
- El usuario es redirigido:
  - Si administra **una** feria: directamente al panel de esa feria.
  - Si administra **varias**: a la pantalla de selección de feria (CU-FER-002).

### En fallo

- No se abre ninguna sesión. El usuario permanece sin autenticar.
- El OTP queda invalidado si fue el último intento permitido.

## Flujo principal

1. El usuario accede a la URL del panel de administración (o al enlace "Acceso administrativo").
2. El sistema muestra la pantalla de acceso y el usuario ingresa su correo.
3. El sistema comprueba que el correo corresponde a una **cuenta existente y activa**. Si no
   existe, sigue por A3. **En este paso no se comprueba si la cuenta administra alguna feria.**
4. El sistema comprueba los límites de emisión de la cuenta (cool-down y tope por ventana, según
   A1/E6 de CU-REG-002).
5. El sistema genera un código OTP de 6 dígitos, invalida los anteriores de esa cuenta y lo
   almacena hasheado en `SesionOTP` con `expira_en = ahora + 15 minutos`, `usado = false`,
   `canal = correo`.
6. El sistema despacha el correo **en segundo plano** desde el buzón del dominio de la feria, y
   responde de inmediato.
7. El sistema muestra la pantalla para ingresar el código de 6 dígitos e indica que tiene 15
   minutos para usarlo.
8. El usuario ingresa el código recibido.
9. El sistema valida: (a) el código coincide con el hash almacenado, (b) `expira_en` no ha
   pasado, (c) `usado = false`.
10. El sistema marca el OTP como `usado = true`.
11. El sistema comprueba que la cuenta **administra al menos una feria**. Si no, sigue por E3.
12. El sistema abre la sesión, rotando el identificador de sesión, y registra el último acceso.
13. El sistema redirige: al panel de la feria si administra una sola, o a la selección de feria
    (CU-FER-002) si administra varias.

> [!important] La autorización vive en el servidor, y se revisa en cada petición
> Tener sesión válida **no** da acceso al panel: cada petición a una pantalla administrativa
> revalida `AdminFeria` contra la base de datos, para esa feria concreta. Un participante que
> obtenga una sesión legítima por el flujo público no puede usarla para entrar a ningún panel, y
> a quien se le retire el acceso deja de entrar en su siguiente petición, sin esperar a que
> caduque nada. Las validaciones del navegador son solo comodidad visual.

## Flujos alternos

### A1. Usuario con acceso a varias ferias

1. En el paso 13 el sistema detecta más de una fila en `AdminFeria`.
2. El sistema deriva a la pantalla de selección de feria (CU-FER-002).
3. El usuario elige la feria y el sistema abre su panel.

### A2. El usuario no recibió el código (reenvío)

1. Tras 60 segundos de espera, el sistema habilita el botón "Reenviar código".
2. El usuario solicita reenvío.
3. El sistema invalida el OTP anterior (`usado = true`) y genera uno nuevo desde el paso 5.
4. Aplican íntegros el cool-down y los topes definidos en CU-REG-002 (A1, E6), incluida la
   advertencia sobre volver a entrar antes de 60 s tras cerrar sesión.

### A3. El correo no corresponde a ninguna cuenta

1. En el paso 3 el correo no existe en `Persona`, o existe con estado `inactiva`.
2. El sistema **no emite ni envía nada** y responde **"Correo incorrecto."**, dejando al usuario
   en la misma pantalla para que corrija.
3. El flujo no avanza a la pantalla de código.

> [!important] Por qué esto **no** reabre la enumeración de administradores
> Entre el 2026-08-05 y el 2026-08-21 este CU exigía que el acceso administrativo respondiera
> igual ante cualquier correo, con un señuelo que simulaba el comportamiento de un OTP real. El
> objetivo era correcto —**saber qué correos son administradores es el dato que un atacante más
> quiere**, porque le permite dirigir phishing o fuerza bruta contra las cuentas con más poder—,
> pero el mecanismo era más caro de lo necesario y producía una experiencia de uso mala de
> verdad: quien se equivocaba de pantalla, o de correo, veía la pantalla de código y esperaba
> indefinidamente un correo que nunca iba a llegar.
>
> Lo que hace segura esta versión es **dónde se comprueba el permiso**: ya no en el paso del
> correo, sino en el paso 11, **después** de acertar el código. Con eso:
>
> - Esta pantalla revela únicamente **si un correo tiene cuenta** — exactamente lo mismo que ya
>   revela, por diseño, el acceso público al bifurcar entre "entrar" y "registrarse" (CU-REG-001).
>   No es información nueva: quien quiera sondearla ya podía hacerlo en la otra pantalla.
> - Esta pantalla **no revela quién es administrador**. Para averiguarlo hay que superar el OTP,
>   es decir, **hay que poder leer el correo de esa persona**. Quien ya controla un buzón no
>   necesita esta pantalla para saber qué permisos tiene esa cuenta.
>
> En otras palabras: el oráculo de la v0.2 permitía enumerar administradores **a razón de un
> correo por intento y sin poseer ninguna cuenta**. Esta versión no, y a cambio recupera un
> mensaje de error que la persona entiende.

## Flujos de excepción

### E1. Código incorrecto

1. En el paso 9, el código no coincide con el hash almacenado.
2. El sistema muestra el número de intentos restantes (máximo 3 por OTP emitido).
3. Si hay intentos restantes, el usuario puede volver a ingresar el código.
4. Al agotar los 3 intentos, el OTP queda invalidado y el sistema obliga a solicitar uno nuevo
   (A2).

### E2. Código expirado

1. En el paso 9, `expira_en` ya pasó.
2. El sistema informa la expiración y ofrece el botón "Enviar nuevo código".
3. El flujo retoma desde A2.

### E3. La cuenta existe y el código es correcto, pero no administra ninguna feria

1. En el paso 11, la cuenta no tiene ninguna fila en `AdminFeria` — nunca la tuvo, o se la
   retiraron (CU-FER-004) entre la emisión del código y su verificación.
2. El sistema **no abre sesión administrativa**. Informa a la persona de que su cuenta no
   administra ninguna feria y le ofrece ir al **portal de participante**, que sí le corresponde.
3. El OTP ya quedó quemado en el paso 10 y no se reutiliza.

> [!note] Este mensaje sí puede ser explícito, y es la diferencia con A3
> Aquí la persona ya demostró ser dueña del buzón: decirle qué permisos tiene su propia cuenta no
> le revela nada que no pudiera averiguar de otras formas. Es justamente el caso que la v0.2
> intentaba ocultar y que, al ocultarlo, dejaba a un participante despistado esperando un correo
> que no llegaría nunca. La regla general: **antes del OTP, lo mínimo; después del OTP, la
> verdad.**

### E4. Fallo en el envío del correo

1. En el paso 6, el servicio de correo devuelve error. Como el envío ocurre en segundo plano, el
   fallo se detecta después de responder.
2. El sistema invalida el código recién emitido: no queda ningún OTP utilizable.
3. La persona ve la pantalla de código y, al no recibir nada, usa "Enviar nuevo código". El
   motivo del fallo queda en la bitácora del servidor. Idéntico a E3 de CU-REG-002.

### E5. Demasiadas solicitudes o intentos fallidos

1. Aplican íntegros E6 y E7 de CU-REG-002 (tope de 5 emisiones por 15 min; bloqueo tras 10 fallos
   en 15 min).

### E6. ~~Cuenta sin RolPermiso administrativo~~ — DEROGADO (2026-08-05), sustituido por E3

> [!caution] Historia de esta excepción, para no volver a recorrerla
> Fue **E3 en la v0.2**: informaba que la cuenta no era administrativa **en la pantalla del
> correo**, antes del OTP. Eso era un oráculo de enumeración y se derogó el 2026-08-05 en favor
> de la respuesta uniforme con señuelo. El 2026-08-21 el aviso vuelve, pero **movido después del
> OTP** (E3 de esta versión), que es lo que lo hace inofensivo. Si alguien propone volver a
> ponerlo antes del código, esto es lo que hay que releer.

## Datos relevantes

### Entradas

- Correo electrónico (pantalla inicial)
- Código OTP de 6 dígitos (pantalla de verificación)

### Salidas

- Sesión de servidor abierta (`persona_id`), con cookie `HttpOnly`. Las ferias que administra
  **no** viajan en la sesión: se consultan por petición.
- Registro `SesionOTP` actualizado (`usado = true`)
- Actualización de último acceso en `Persona`

## Requisito de despliegue

El límite de peticiones por IP que protege esta pantalla se apoya en un contador en caché. En
producción, con **varios procesos atendiendo peticiones**, ese contador debe vivir en un almacén
**compartido** entre todos ellos (Redis/Memcached). Si cada proceso lleva el suyo, el límite real
se multiplica por el número de procesos y deja de frenar lo que pretende.

> [!note]
> La creación de ferias y el alta de sus administradores no forman parte de este CU: ver
> [CU-FER-001](<../FER/CU-FER-001 Crear una feria y designar a su dueño.md>) y
> [CU-FER-003](<../FER/CU-FER-003 Dar de alta un administrador en mi feria.md>). Provisionar un
> acceso administrativo no implica establecer contraseña: basta con que exista la `Persona` y su
> fila en `AdminFeria` para que la persona entre por OTP.

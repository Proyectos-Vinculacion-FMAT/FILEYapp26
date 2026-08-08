---
estado: aceptado
version: 0.3
tags:
  - caso-de-uso
  - autenticacion
  - core-registros
  - otp
fecha: 2026-06-22
fecha_actualizacion: 2026-08-05
id: CU-REG-002
dominio: CORE-REG
responsable: Juan Manuel Hernandez Miranda
reglas_de_negocio: []
diagramas_relacionados: []
trazabilidad:
  ddr: []
---
# CU-REG-002 Iniciar sesión como usuario externo (OTP por correo)

> [!important] Actualización 2026-08-05 — se resolvieron dos contradicciones internas de la v0.1
> La v0.1 se contradecía a sí misma en dos puntos, y la implementación tuvo que elegir:
>
> | Punto | v0.1 decía | Queda en |
> | --- | --- | --- |
> | Intentos por código | **3** (E1) vs **5** (E4) | **3 intentos** (E1). E4 queda derogado. |
> | Cool-down de reenvío | **60 s** (A1) vs **30 s** (E5) | **60 s** (A1). E5 queda derogado. |
>
> Además se documentan aquí las **defensas contra abuso** añadidas en la auditoría de
> seguridad del 2026-08-02 (E6, E7), que la v0.1 no contemplaba.

## Objetivo

Autenticar a un usuario externo (proponente, tallerista, representante escolar) mediante un código de un solo uso enviado a su correo, sin necesidad de contraseña. El usuario obtiene una sesión activa para operar en el módulo que le corresponde.

## Alcance

Core Registros. Cubre el acceso por el **portal público**, con independencia de los permisos de la cuenta. El acceso al **panel administrativo** se cubre en CU-REG-003.

> [!note] Qué distingue este CU de CU-REG-003: la puerta, no la persona
> Lo que separa ambos casos de uso es **por dónde entra la persona**, no quién es. Una cuenta con
> `RolPermiso` puede iniciar sesión por el portal público con este CU —y es lo correcto cuando
> Hipólito o Elvira entran a presentar una propuesta propia, no a administrar—; simplemente
> llega al portal de convocatorias, no al panel. El caso de una persona que es a la vez
> proponente y administradora está previsto en CU-REG-005 A1.

## Actores

### Actor principal

- Usuario externo (proponente, tallerista o representante escolar con cuenta registrada)

### Actores secundarios

- **Sistema de correo** — envía el OTP. El proveedor concreto es una decisión de
  infraestructura, no de este CU: hoy es **SMTP autenticado** (cuenta de correo institucional;
  en desarrollo, una cuenta Gmail temporal) y está previsto migrar a un proveedor transaccional
  antes del despliegue real. El CU solo exige que el remitente sea un buzón **del dominio que
  la feria controla**, para no fallar SPF/DMARC y caer en spam.

> [!warning] Requisito de remitente (aprendido en producción de pruebas)
> Enviar como un dominio que no se controla (p. ej. `noreply@filey.org` usando una cuenta
> Gmail) hace que el correo se reescriba o se rechace. El remitente debe coincidir con la
> cuenta autenticada del proveedor.

## Disparador

El usuario ingresa su correo en la pantalla de acceso del portal público y el sistema lo reconoce como cuenta existente.

## Precondiciones

- El correo ingresado existe en `Persona` con `estado = activa`.
- El acceso se realiza desde el portal público (para el panel administrativo, ver CU-REG-003).

## Postcondiciones

### En éxito

- La entrada en `SesionOTP` queda con `usado = true` (quemada al validar).
- El sistema emite un JWT de sesión ligado a `persona_id`. **El JWT no lleva dentro el módulo ni el rol**: los permisos se resuelven contra `RolPermiso` en cada petición, para que revocar un permiso surta efecto sin esperar a que caduque el token.
- El usuario queda autenticado y es redirigido al portal de convocatorias (EVT, TAL, STD, VIS).
- Se actualiza el último acceso en `Persona`.

### En fallo

- No se emite ningún JWT. El usuario permanece sin sesión.
- El OTP queda invalidado si fue el último intento permitido.

## Flujo principal

1. El usuario ingresa su correo en la pantalla de acceso.
2. El sistema reconoce el correo como cuenta existente y activa. Si no existe, el flujo deriva a CU-REG-001 (registro).
3. El sistema comprueba los límites de emisión de la cuenta (cool-down de 60 s y tope por ventana; ver A1, E6). Si alguno está activo, no genera código y sigue por la excepción correspondiente.
4. El sistema genera un código OTP de 6 dígitos aleatorios.
5. El sistema **invalida los códigos anteriores de esa cuenta** que sigan vigentes y almacena el nuevo OTP hasheado en `SesionOTP` con `expira_en = ahora + 15 minutos`, `usado = false`, `canal = correo`. Solo un código está vigente a la vez.
6. El sistema **despacha el correo en segundo plano** (fuera de la respuesta) desde el buzón del dominio de la feria, y responde de inmediato.
7. El sistema muestra una pantalla con un campo para ingresar el código de 6 dígitos e indica que tiene 15 minutos para usarlo.
8. El usuario ingresa el código recibido.
9. El sistema valida: (a) el código coincide con el hash almacenado, (b) `expira_en` no ha pasado, (c) `usado = false`.
10. El sistema marca el OTP como `usado = true`.
11. El sistema emite un JWT de sesión firmado con `persona_id` y expiración de sesión, y registra el último acceso en `Persona`.
12. El sistema redirige al usuario al portal de convocatorias, donde elige el módulo en el que quiere participar.

> [!note] Por qué el correo sale en segundo plano (cambio 2026-08-02)
> Hablar con el servidor de correo tardaba ~2.8 s **dentro** de la respuesta HTTP. Eso hacía
> lento el login y, en el flujo administrativo (CU-REG-003), delataba por tiempo quién es
> administrador. La consecuencia visible es que el usuario ya no recibe un error inmediato si
> el envío falla — ver E3.

## Flujos alternos

### A1. El usuario no recibió el código (reenvío) — cool-down de 60 s

1. Tras 60 segundos de espera, el sistema habilita el botón "Reenviar código".
2. El usuario solicita reenvío.
3. El sistema invalida el OTP anterior (`usado = true`) y genera uno nuevo desde el paso 4 del flujo principal.
4. Si el usuario solicita un código antes de cumplirse los 60 s, el sistema no emite nada e informa cuántos segundos faltan.

> [!important] El cool-down de 60 s aplica a **toda** emisión, no solo al botón "Reenviar"
> Se mide desde la **última emisión** de esa cuenta, sea de un login nuevo o de un reenvío.
> Sin esto, cualquiera que supiera el correo de una persona podía pedirle códigos en bucle:
> como cada código nuevo invalida el anterior, la víctima nunca lograba usar el suyo (DoS de
> login) y además recibía una avalancha de correos (mail bombing). Ver la auditoría del
> 2026-08-02.
>
> **Efecto secundario conocido (decisión abierta):** el cool-down se mide por tiempo y **no
> distingue** si el código anterior ya se usó con éxito. Una persona que inicia sesión, cierra
> sesión y quiere volver a entrar antes de 60 s recibe la espera aunque no haya hecho nada
> anómalo. Está **pendiente de decidir** si un código ya verificado con éxito debe dejar de
> contar para el cool-down.

### A2. Sesión iniciada desde CU-REG-001 (cuenta recién creada)

1. CU-REG-001 ya verificó el correo — el sistema entra directamente en el paso 4 sin repetir los pasos 1-2.
2. Al ser la **primera** emisión de la cuenta, no aplica el cool-down de A1.

## Flujos de excepción

### E1. Código incorrecto — máximo 3 intentos por código

1. En el paso 9, el código no coincide con el hash almacenado.
2. El sistema incrementa el contador de intentos y muestra cuántos quedan (**máximo 3 por OTP emitido**).
3. Si hay intentos restantes, el usuario puede volver a ingresar el código.
4. Al agotar los 3 intentos, el OTP queda invalidado y el sistema obliga a solicitar uno nuevo (A1). **El sistema no reenvía nada por su cuenta**: la persona debe pedirlo, respetando el cool-down.

> [!note] El conteo de intentos se serializa
> Dos peticiones simultáneas con el mismo código podían gastar más de 3 intentos (carrera
> confirmada con prueba de concepto el 2026-08-02). La verificación se ejecuta bajo bloqueo de
> la fila del OTP, así que el límite ya no se puede burlar con concurrencia.

### E2. Código expirado

1. En el paso 9, `expira_en` ya pasó.
2. El sistema informa la expiración y ofrece directamente el botón "Enviar nuevo código".
3. El flujo retoma desde A1 (sujeto al cool-down).

### E3. Fallo en el envío del correo

1. En el paso 6, el servicio de correo devuelve error. Como el envío ocurre **en segundo plano**, el fallo se detecta después de haber respondido al usuario.
2. El sistema **invalida el código recién emitido** (`usado = true`): la garantía de fondo se mantiene — un envío fallido nunca deja un OTP utilizable.
3. El usuario **sí ve la pantalla de código** (a diferencia de la v0.1) y, al no recibir nada, usa "Enviar nuevo código". El motivo real del fallo queda registrado en la bitácora del servidor.

> [!warning] Cambio respecto a la v0.1
> La v0.1 exigía "no mostrar la pantalla de código" y avisar del fallo en el momento. Con el
> envío en segundo plano eso ya no es posible: cuando se sabe que falló, la respuesta ya salió.
> Se conserva lo esencial (ningún OTP utilizable queda vivo) y se sacrifica el aviso inmediato.

### E4. ~~Se ingresa más de 5 veces incorrectamente el código~~ — DEROGADO

> [!caution] Derogado el 2026-08-05 — contradecía a E1
> Este flujo fijaba el límite en **5 intentos** mientras E1 lo fijaba en **3**, y además decía
> que el sistema *reenvía automáticamente* un código nuevo, lo que choca con el cool-down de A1
> y habilitaría mail bombing. **Rige E1: 3 intentos y reenvío solicitado por la persona.**
> El caso de fallos repetidos *a lo largo de varios códigos* se cubre ahora en E7.

### E5. ~~Cool-down de 30 segundos al reenviar~~ — DEROGADO

> [!caution] Derogado el 2026-08-05 — contradecía a A1
> Este flujo fijaba el cool-down en **30 s** mientras A1 lo fijaba en **60 s**. **Rige A1: 60
> segundos.** Lo que sí se conserva de E5 es su regla de invalidación, ya incorporada al paso 5
> del flujo principal: al emitir un código nuevo, los anteriores dejan de ser válidos.

### E6. Demasiadas solicitudes de código para la misma cuenta

1. La cuenta ya recibió **5 códigos en los últimos 15 minutos**.
2. El sistema no emite ni envía nada e informa que hubo demasiadas solicitudes, indicando cuánto falta para poder reintentar.
3. El bloqueo se libera solo, conforme las emisiones antiguas salen de la ventana de 15 minutos.

*Motivo: cortar el mail bombing sostenido, que el cool-down de 60 s por sí solo no impide.*

### E7. Demasiados intentos fallidos acumulados (bloqueo temporal de la cuenta)

1. La cuenta acumula **10 intentos fallidos en 15 minutos**, sumando todos los códigos emitidos en esa ventana.
2. El sistema bloquea la verificación durante 15 minutos e informa a la persona que espere antes de volver a intentar.
3. Un inicio de sesión exitoso reinicia el contador.

*Motivo: E1 acota los intentos por código, pero sin este límite un atacante podía pedir código
tras código y seguir probando indefinidamente desde muchas direcciones distintas.*

> [!note] Límite adicional por dirección IP
> Con independencia de E6 y E7, el sistema limita las peticiones por IP (identificación 20/min;
> emisión y verificación 10/min). E6 y E7 actúan **por cuenta** porque el límite por IP no
> frena a un atacante repartido entre muchas direcciones.

## Datos relevantes

### Entradas

- Correo electrónico (pantalla inicial)
- Código OTP de 6 dígitos (pantalla de verificación)

### Salidas

- JWT de sesión (`persona_id`, expiración). Se entregan un *access token* de vida corta y un *refresh token* para renovarlo.
- Registro `SesionOTP` actualizado (`usado = true`)
- Último acceso actualizado en `Persona`

## Parámetros configurables

Valores vigentes; se ajustan por configuración, sin tocar el código.

| Parámetro | Valor | Origen |
| --- | --- | --- |
| Longitud del código | 6 dígitos | Flujo principal |
| Vigencia del código | 15 min | Flujo principal, paso 5 |
| Intentos por código | 3 | E1 |
| Cool-down entre emisiones | 60 s | A1 |
| Emisiones máximas por cuenta | 5 por 15 min | E6 |
| Fallos que disparan el bloqueo | 10 por 15 min | E7 |
| Duración del bloqueo | 15 min | E7 |

---
estado: propuesta
version: 0.3
tags:
  - casos-de-uso
  - autenticacion
  - core-registros
fecha: 2026-06-22
fecha_actualizacion: 2026-08-21
---
# CU-REG — Índice de casos de uso (Core Registros — Autenticación e Identidad)

Inventario de casos de uso del **Core Registros**: creación de cuenta, inicio de sesión y cierre de sesión. Estos CUs son transversales — son la puerta de entrada a cualquier módulo del sistema FILEY (EVT, TAL, STD, VIS).

> [!important] Nomenclatura de módulos — se usa `EVT`, no `EVE`
> Las versiones anteriores de estos documentos alternaban entre `EVE` y `EVT` para el módulo de
> Actividades FILEY (Eventos). **El identificador correcto es `EVT`**, que es el que usan tanto
> el resto de la documentación de requisitos como la implementación. Los cuatro módulos son
> `EVT`, `TAL`, `STD` y `VIS`.

<!-- -->

> [!important] Actualización 2026-08-21 — el acceso administrativo se mudó a `FER`
> `REG` ya **no** define quién es administrador. Con
> [ADR-0004](<../../adr/0004-acceso-administrativo-por-feria.md>), el acceso administrativo se
> otorga **por feria** (`AdminFeria`) y lo administra el dueño de cada feria; `RolPermiso` —con
> sus módulos, sus niveles y su comodín `*`— queda derogado.
>
> El reparto queda así: **`REG` responde *quién eres*; [`FER`](<../FER/CU-FER Índice.md>)
> responde *en qué feria estás y qué puedes hacer ahí*.** La cuenta es global y no pertenece a
> ninguna feria.
>
> En consecuencia: **CU-REG-005 queda reemplazado** por CU-FER-003, y **CU-REG-006 se partió en
> dos** (primero feria, en CU-FER-002; luego módulo, en CU-REG-006). CU-REG-003 sigue vivo: el
> mecanismo de login no cambia, solo qué se comprueba y a dónde lleva.

**Actores:**

- **Usuario externo** — proponente, tallerista o representante escolar que accede esporádicamente (una vez al año).
- **Usuario administrativo** — Hipólito (EVT), Elvira (TAL), administrador general; acceden con frecuencia diaria durante meses.

> [!important] Autenticación unificada por OTP (actualizado 2026-06-30)
> **Todos** los usuarios —externos y administrativos— inician sesión con **OTP por correo**
> (sin contraseña). El equipo unificó el mecanismo para simplificar la implementación (ver
> CU-REG-003, cambio de decisión). Lo que distingue a un administrador no es el mecanismo de
> login sino **administrar al menos una feria** (`AdminFeria`).
>
> - En la v0.1, los usuarios administrativos usaban **usuario + contraseña**; esa decisión
>   quedó **derogada**.

<!-- -->

> [!note]
> Las entidades que soportan estos CUs son `Persona` y `SesionOTP`, definidas en
> [`Modelo de datos - Registros`](<Modelo de datos - Registros.md>). El acceso administrativo lo
> define `AdminFeria`, en
> [`FER/Modelo de datos - Ferias`](<../FER/Modelo de datos - Ferias.md>).

---

## Casos de uso

- **CU-REG-001** Registrar nueva cuenta de usuario externo — *Usuario externo*
- **CU-REG-002** Iniciar sesión como usuario externo (OTP por correo) — *Usuario externo*
- **CU-REG-003** Iniciar sesión como usuario administrativo (OTP por correo) — *Usuario administrativo*
- **CU-REG-004** Cerrar sesión — *Cualquier usuario autenticado*
- ~~**CU-REG-005** Crear cuenta de usuario administrativo y asignar permisos de módulo~~ — **reemplazado por [CU-FER-003](<../FER/CU-FER-003 Dar de alta un administrador en mi feria.md>)**
- **CU-REG-006** Consultar los módulos de una feria y entrar a un panel — *Usuario administrativo* (antes cubría también la selección de feria; ver [CU-FER-002](<../FER/CU-FER-002 Consultar mis ferias y entrar a una.md>))

---

## Artefactos relacionados

- [`Modelo de datos - Registros`](<Modelo de datos - Registros.md>) — `Persona` y `SesionOTP`.
- [`Mecanismo de sesión y control de acceso`](<Mecanismo de sesion y control de acceso.md>) — qué
  ocurre **después** del OTP: la cookie de sesión, qué manda el navegador en cada petición, quién
  decide si pasa, y los huecos conocidos de lo que rodea a ese mecanismo.

---

## Relación con otros dominios

| Dominio                       | Cuándo llega aquí                                                                                |
| ----------------------------- | ------------------------------------------------------------------------------------------------ |
| EVT                           | Antes de CU-EVT-002 (enviar propuesta): el proponente debe estar autenticado.                    |
| STD                           | Antes de CU-STD-001 (aplicar como expositor): el representante editorial debe estar autenticado. |
| TAL                           | Antes del registro de tallerista: el tallerista debe estar autenticado.                          |
| VIS                           | Antes de CU-VIS-001 (registrar visita escolar): el representante escolar debe estar autenticado. |
| Panel admin (EVT/TAL/STD/VIS) | Todo acceso administrativo requiere CU-REG-003 previo.                                           |

---

## Decisiones pendientes

- [x] ¿Correo y teléfono son **ambos obligatorios** al registrarse, o basta con el correo? **Resuelto (2026-08-05):** ambos obligatorios para usuarios externos (CU-REG-001 E1). En el alta administrativa el teléfono es opcional (CU-REG-005).
- [x] ¿Qué pasa si dos registros tienen el mismo correo pero distinto teléfono? **Resuelto:** el correo es la identidad única de la cuenta, así que ese caso no puede darse — el segundo registro se reconoce como cuenta existente (CU-REG-001 A1). El caso inverso (mismo teléfono, distinto correo) sí se bloquea (CU-REG-001 E2).
- [x] ¿Los usuarios administrativos también usan OTP o siempre contraseña? **Resuelto (2026-06-30):** OTP para todos; se derogó la contraseña para admins (ver CU-REG-003).
- [x] Homologar CU-REG-005 al nuevo esquema OTP: al provisionar una cuenta administrativa ya no se envía enlace para "establecer contraseña"; basta crear la `Persona` y su `RolPermiso`. **Resuelto (2026-07-22):** CU-REG-005 actualizado — sin contraseña ni enlace de activación; el OTP se emite en el login (CU-REG-003).

### Abiertas tras la revisión del 2026-08-05

- [ ] **Cool-down tras un inicio de sesión exitoso.** El cool-down de 60 s se mide por tiempo y no distingue si el código anterior ya se usó bien: quien cierra sesión y vuelve a entrar antes de 60 s recibe la espera. ¿Se exceptúan los códigos ya verificados? (CU-REG-002 A1)
- [x] ~~**Vida del token de acceso tras cerrar sesión.**~~ **Sin objeto (2026-08-21):** ya no hay tokens. La sesión vive en el servidor y cerrarla es inmediato y total (CU-REG-004 v0.4, [ADR-0002](<../../adr/0002-migracion-de-registro-al-monolito.md>)).
- [ ] **Pantalla de gestión de accesos administrativos.** Sigue abierta, pero se mudó: ahora es la pantalla de [CU-FER-003](<../FER/CU-FER-003 Dar de alta un administrador en mi feria.md>), y quien la usa es el **dueño de cada feria**, no el equipo técnico. Mientras no exista, ningún dueño puede ejercer la responsabilidad que ADR-0004 le asigna.
- [x] ~~**Salto directo al panel con un solo módulo.**~~ **Sin objeto (2026-08-21):** dentro de una feria todos los módulos son accesibles, así que no hay caso de "un solo módulo". El salto que **sí** hace falta es el de una sola **feria** — ver [CU-FER-002](<../FER/CU-FER-002 Consultar mis ferias y entrar a una.md>) A1, donde es requisito desde el principio.
- [ ] **Precondición de convocatoria activa en CU-REG-001.** No implementada; decidir si se exige de verdad.
- [x] ~~**Proveedor de correo definitivo.**~~ **Resuelto de hecho (2026-08-12):** el envío se hace por **Resend**, no por SMTP. Queda por confirmar el remitente definitivo del dominio que la feria controla, que es lo que exige CU-REG-002 para no fallar SPF/DMARC.

### Abiertas tras el cambio de diseño del 2026-08-21

- [ ] **Transferencia de propiedad de una feria.** Un dueño que deja el proyecto bloquea el alta de administradores en su feria. Ver [`FER/CU-FER Índice`](<../FER/CU-FER Índice.md>).
- [ ] **Nivel de solo lectura.** ADR-0004 lo elimina; confirmar con el cliente que no hace falta un supervisor que solo observe.
- [ ] **Cómo elige feria un participante.** `FER` resuelve la navegación del administrador; falta la del aplicante.

> [!note] Riesgo aceptado a propósito
> Tanto el flujo público como el administrativo revelan **si un correo tiene cuenta**, porque es
> la experiencia de uso aprobada del prototipo y evita dejar a alguien esperando un correo que no
> va a llegar. Lo que ninguno de los dos revela es **quién es administrador**: eso solo se sabe
> después de acertar el OTP, es decir, teniendo acceso al buzón de esa persona. El razonamiento
> completo está en CU-REG-003 A3.

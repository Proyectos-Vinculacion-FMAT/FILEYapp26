---
estado: propuesta
version: 0.2
tags:
  - casos-de-uso
  - autenticacion
  - core-registros
fecha: 2026-06-22
fecha_actualizacion: 2026-08-05
---
# CU-REG — Índice de casos de uso (Core Registros — Autenticación e Identidad)

Inventario de casos de uso del **Core Registros**: creación de cuenta, inicio de sesión y cierre de sesión. Estos CUs son transversales — son la puerta de entrada a cualquier módulo del sistema FILEY (EVT, TAL, STD, VIS).

> [!important] Nomenclatura de módulos — se usa `EVT`, no `EVE`
> Las versiones anteriores de estos documentos alternaban entre `EVE` y `EVT` para el módulo de
> Actividades FILEY (Eventos). **El identificador correcto es `EVT`**, que es el que usan tanto
> el resto de la documentación de requisitos como la implementación. Los cuatro módulos
> administrables son `EVT`, `TAL`, `STD` y `VIS`, más el comodín `*` (administrador general).

**Actores:**

- **Usuario externo** — proponente, tallerista o representante escolar que accede esporádicamente (una vez al año).
- **Usuario administrativo** — Hipólito (EVT), Elvira (TAL), administrador general; acceden con frecuencia diaria durante meses.

> [!important] Autenticación unificada por OTP (actualizado 2026-06-30)
> **Todos** los usuarios —externos y administrativos— inician sesión con **OTP por correo**
> (sin contraseña). El equipo unificó el mecanismo para simplificar la implementación (ver
> CU-REG-003, cambio de decisión). Lo que distingue a un administrador no es el mecanismo de
> login sino tener al menos un `RolPermiso` registrado.
>
> - En la v0.1, los usuarios administrativos usaban **usuario + contraseña**; esa decisión
>   quedó **derogada**.

<!-- -->

> [!note]
> Las entidades que soportan estos CUs (`Persona`, `SesionOTP`, `RolPermiso`) están definidas en `CORES/Definicion de Cores.md` — Core 1 Registros.

---

## Casos de uso

- **CU-REG-001** Registrar nueva cuenta de usuario externo — *Usuario externo*
- **CU-REG-002** Iniciar sesión como usuario externo (OTP por correo) — *Usuario externo*
- **CU-REG-003** Iniciar sesión como usuario administrativo (OTP por correo) — *Usuario administrativo*
- **CU-REG-004** Cerrar sesión — *Cualquier usuario autenticado*
- **CU-REG-005** Crear cuenta de usuario administrativo y asignar permisos de módulo — *Administrador general*
- **CU-REG-006** Consultar los módulos administrables y entrar a un panel — *Usuario administrativo*

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
- [ ] **Vida del token de acceso tras cerrar sesión.** Cerrar sesión revoca la renovación, pero el token de acceso ya emitido sigue válido hasta 1 hora. ¿Se acorta, se verifica revocación por petición, o se acepta? (CU-REG-004)
- [ ] **Pantalla de gestión de usuarios administrativos.** CU-REG-005 está implementado sin interfaz (comando en el servidor); ningún cliente puede dar de alta administradores por sí mismo. ¿Entra en alcance y cuándo?
- [ ] **Salto directo al panel con un solo módulo.** A1 de CU-REG-006 no está implementado: hoy todos pasan por la pantalla de selección.
- [ ] **Precondición de convocatoria activa en CU-REG-001.** No implementada; decidir si se exige de verdad.
- [ ] **Proveedor de correo definitivo.** Hoy es SMTP con una cuenta temporal. Decidir entre cuenta institucional por SMTP o proveedor transaccional antes del despliegue (afecta a CU-REG-002, 003 y 005).

> [!note] Riesgo aceptado a propósito
> El flujo **público** sí revela si un correo tiene cuenta o no (responde "nueva" o "existente"),
> porque es la experiencia de uso aprobada del prototipo. Solo el flujo **administrativo** oculta
> esa información (CU-REG-003 A3), porque ahí el dato revelado —quién es administrador— es el que
> tiene valor para un atacante.

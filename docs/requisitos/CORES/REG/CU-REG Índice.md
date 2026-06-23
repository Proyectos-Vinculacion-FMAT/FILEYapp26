---
estado: propuesta
version: 0.1
tags:
  - casos-de-uso
  - autenticacion
  - core-registros
fecha: 2026-06-22
---
# CU-REG — Índice de casos de uso (Core Registros — Autenticación e Identidad)

Inventario de casos de uso del **Core Registros**: creación de cuenta, inicio de sesión y cierre de sesión. Estos CUs son transversales — son la puerta de entrada a cualquier módulo del sistema FILEY (STD, EVE, TAL).

**Actores:**
- **Usuario externo** — proponente, tallerista o representante escolar que accede esporádicamente (una vez al año).
- **Usuario administrativo** — Hipólito (EVE), Elvira (TAL), administrador general; acceden con frecuencia diaria durante meses.

> [!important]
> Existen **dos mecanismos de autenticación** según el tipo de actor:
> - **OTP por correo** (sin contraseña) → usuarios externos. Acordado en Junta 2.
> - **Usuario + contraseña** (sesión persistente) → usuarios administrativos. La frecuencia de acceso hace inviable el OTP para este perfil.

> [!note]
> Las entidades que soportan estos CUs (`Persona`, `SesionOTP`, `RolPermiso`) están definidas en `CORES/Definicion de Cores.md` — Core 1 Registros.

---

## Casos de uso

- **CU-REG-001** Registrar nueva cuenta de usuario externo — *Usuario externo*
- **CU-REG-002** Iniciar sesión como usuario externo (OTP por correo) — *Usuario externo*
- **CU-REG-003** Iniciar sesión como usuario administrativo (usuario + contraseña) — *Usuario administrativo*
- **CU-REG-004** Cerrar sesión — *Cualquier usuario autenticado*
- **CU-REG-005** Crear cuenta de usuario administrativo y asignar permisos de módulo — *Administrador general*

---

## Relación con otros dominios

| Dominio | Cuándo llega aquí |
|---------|-------------------|
| EVE | Antes de CU-EVE-002 (enviar propuesta): el proponente debe estar autenticado. |
| STD | Antes de CU-STD-001 (aplicar como expositor): el representante editorial debe estar autenticado. |
| TAL | Antes del registro de tallerista o de visita escolar: el tallerista/representante escolar debe estar autenticado. |
| Panel admin (EVE/TAL/STD) | Todo acceso administrativo requiere CU-REG-003 previo. |

---

## Decisiones pendientes

- [ ] ¿Correo y teléfono son **ambos obligatorios** al registrarse, o basta con el correo? (Pendiente de la junta del lunes 22-Jun — ver `Definicion de Cores.md`)
- [ ] ¿Qué pasa si dos registros tienen el mismo correo pero distinto teléfono? (Posible duplicado de escuela registrándose varias veces — ver `Definicion de Cores.md`)
- [ ] ¿Los usuarios administrativos también usan OTP o siempre contraseña? **Propuesta actual:** contraseña para admins. Confirmar con Hipólito y Elvira.

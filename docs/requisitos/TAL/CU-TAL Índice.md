---
estado: propuesta
version: 0.1
tags:
  - casos-de-uso
  - talleres
fecha: 2026-06-25
---
# CU-TAL — Índice de casos de uso (Actividades infantiles y juveniles)

Inventario de casos de uso del dominio **Talleres** (`TAL`): la convocatoria de **actividades dirigidas a infancias y juventudes** que administra **Elvira**, paralela —pero distinta— a la convocatoria del programa general (Hipólito, dominio `EVT`).

**Actores:** Tallerista (persona/institución que propone una actividad infantil/juvenil) · Representante escolar (escuela o grupo de excursionistas) · Administrador (Elvira y su equipo) · Sistema.

> [!note] Alcance de este índice
> Por ahora cubre únicamente la **fase de registro** (A · Convocatoria): el llenado y envío de
> propuestas, su seguimiento y el registro de visitas escolares. La programación de salas y la
> publicación **no** forman parte de este alcance (dependen de los Cores de Programación/Salas
> y del equipo correspondiente).

> [!important] Sin revisión propuesta-por-propuesta
> A diferencia de la convocatoria de Hipólito (EVT, fase B · Revisión y Selección), la
> convocatoria infantil/juvenil **no tiene un proceso de dictamen dentro del sistema**
> (aceptar / solicitar cambios / rechazar por propuesta). La propuesta se **registra** y la
> **confirmación de participación** la comunica la coordinación por correo (en diciembre). Por
> eso no hay CU de revisión aquí, y la edición de propuestas (CU-TAL-005) es autogestionada.

> [!note] Identidad y registro de cuenta
> El alta de cuenta y el acceso (OTP) del tallerista y del representante escolar dependen del
> Core Registros: ver `REG/CU-REG Índice.md` — CU-REG-001 y CU-REG-002.

## Flujo de alto nivel (registro)

```
REG: Registro de cuenta / acceso (OTP)
         ↓
TAL: Elige convocatoria infantil/juvenil → Captura propuesta → Envía → Da seguimiento
```

---

## A. Convocatoria (registro)

Cubre la apertura del periodo y todo lo que hace el tallerista (y la escuela) mientras la convocatoria está abierta.

- CU-TAL-001 Configurar la convocatoria de actividades infantiles y juveniles (periodo, modalidades y cupos) — *Administrador (Elvira)*
- CU-TAL-002 Capturar y registrar los datos de la propuesta de actividad infantil/juvenil (llenado del formulario) — *Tallerista*
- CU-TAL-003 Enviar la propuesta de actividad infantil/juvenil (acción de envío) — *Tallerista*
- CU-TAL-004 Registrar múltiples propuestas desde una misma cuenta sin recapturar datos del responsable — *Tallerista*
- CU-TAL-005 Editar o actualizar mi propuesta de actividad mientras la convocatoria esté abierta (autogestionada) — *Tallerista*
- CU-TAL-006 Consultar mis propuestas de actividad y revisar su estado actual — *Tallerista*
- CU-TAL-007 Registrar la solicitud de visita de una escuela o grupo de excursionistas — *Representante escolar*
- CU-TAL-008 Consultar y actualizar el registro de una visita escolar — *Representante escolar*

---

## Diferencias clave respecto a EVT (Hipólito)

El registro de propuestas de Elvira **no es igual** al de Hipólito. Principales diferencias capturadas en los CU:

| Aspecto | EVT (Hipólito) | TAL (Elvira) |
|--------|----------------|--------------|
| Público objetivo | General (literario / académico) | Infancias y juventudes, por nivel escolar |
| Tipos de actividad | Conversatorio, Conferencia, Presentación de libro/revista, etc. | Taller, Cuentacuento, Plática para jóvenes, Presentación para niños/jóvenes, Obra teatral, Proyección en cines |
| Categorización | `literaria` / `academica` × `uady` / `externo` | Por nivel escolar y turno |
| Duración | Variable (bloques estándar) | Fija, 45–50 min |
| Modalidad | Presencial | Presencial o virtual |
| Adjuntos | PDF/imágenes obligatorios | Sin adjuntos (texto/selección) |
| Revisión de propuestas | Dictamen por propuesta: aceptar / solicitar cambios / rechazar (fase B) | **Sin dictamen en sistema**; confirmación por correo (diciembre) |
| Edición de propuesta | En respuesta a solicitud de cambios del admin (CU-EVT-004) | Autogestionada por el tallerista (CU-TAL-005) |
| Registro de visitas escolares | No aplica | Sí (CU-TAL-007 / CU-TAL-008) |

---

## Artefactos relacionados

- `RF-TAL-01 … RF-TAL-04` — requisitos funcionales origen de estos casos de uso.
- `EVT/CU-EVE Índice.md` — convocatoria del programa general (Hipólito), de referencia estructural.
- `REG/CU-REG Índice.md` — alta de cuenta y autenticación de talleristas y representantes escolares.

## Mapa CU → RF (trazabilidad inicial)

| CU | RF origen |
|----|-----------|
| CU-TAL-002, CU-TAL-003, CU-TAL-004, CU-TAL-005, CU-TAL-006 | RF-TAL-01, RF-TAL-02 |
| CU-TAL-007 | RF-TAL-03 |
| CU-TAL-008 | RF-TAL-04 |

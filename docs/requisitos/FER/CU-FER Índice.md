---
estado: propuesta
version: "0.1"
tags:
  - tipo/indice
  - dom/fer
  - tema/permisos
  - tema/arquitectura
fecha: 2026-08-21
fecha_actualizacion: 2026-08-21
---
# CU-FER — Índice de casos de uso (Core Ferias)

Inventario de casos de uso del **Core Ferias**: crear una edición de la feria, entrar a ella y
administrar quién tiene acceso. Junto con `REG`, es una de las dos capas **globales** del
sistema — todo lo demás (`EVT`, `TAL`, `STD`, `VIS`, `PRG`, `SAL`) ocurre **dentro** de una
feria.

> [!important] La división que ordena todo el sistema
> **`REG` responde *quién eres*; `FER` responde *en qué feria estás y qué puedes hacer ahí*.**
> La cuenta es global y no pertenece a ninguna feria: la misma `Persona`, con el mismo correo y
> el mismo OTP, puede administrar FILEY 2027 y ser participante en FILEY 2028. Lo que se separa
> por feria es el contenido, nunca la identidad.

**Actores:**

- **Operador de la plataforma** — el equipo técnico. Crea ferias y designa a su dueño. No es un
  rol dentro de ninguna feria (CU-FER-001).
- **Dueño de la feria** — una persona por feria. Puede todo lo de la feria **y además** dar de
  alta y retirar a sus administradores (CU-FER-003, CU-FER-004).
- **Administrador de la feria** — puede todo el contenido de la feria; **no** puede administrar
  accesos.

---

## Casos de uso

- **CU-FER-001** Crear una feria y designar a su dueño — *Operador de la plataforma*
- **CU-FER-002** Consultar las ferias que administro y entrar a una — *Usuario administrativo*
- **CU-FER-003** Dar de alta un administrador en mi feria — *Dueño de la feria*
- **CU-FER-004** Retirar el acceso de un administrador de mi feria — *Dueño de la feria*

---

## Artefactos del dominio

- [`Modelo de datos - Ferias`](<Modelo de datos - Ferias.md>) — `Feria` y `AdminFeria`, y qué
  vive en el schema global frente a qué vive en el de cada feria.
- [ADR-0003](<../../adr/0003-una-feria-por-schema.md>) — por qué cada feria tiene su propio
  schema y cómo Django resuelve cuál usar en cada petición.
- [ADR-0004](<../../adr/0004-acceso-administrativo-por-feria.md>) — por qué el permiso es por
  feria y no por módulo, y qué se pierde con esa decisión.

---

## Qué cambia en lo ya escrito

Este dominio no se añade en el vacío: reemplaza el modelo de permisos con el que se construyó
`REG`. Lo afectado, y en qué estado queda:

| Documento | Qué le pasa |
| --- | --- |
| `REG/CU-REG-005` | **Reemplazado por CU-FER-003.** El alta ya no asigna módulo y nivel sobre el sistema, sino acceso a una feria, y solo la ejecuta el dueño de esa feria. |
| `REG/CU-REG-006` | **Reformulado.** Lo que se elige tras entrar ya no son módulos sueltos: primero se elige feria (CU-FER-002) y luego módulo dentro de ella. |
| `REG/CU-REG-003` | **Corregido.** Lo que comprueba el acceso administrativo ya no es "¿tiene algún `RolPermiso`?" sino "¿administra alguna feria?". |
| `REG/Modelo de datos - Registros` | `RolPermiso` queda derogado; la pregunta abierta sobre `admin(usuario, feria)` queda cerrada aquí. |
| `TAL/Modelo de datos - Talleres` | **Pendiente de corregir.** Lleva `edicion_id` en cuatro tablas, una dentro de su clave primaria compuesta. Con ADR-0003 ninguna tabla de dominio guarda identificador de edición. |
| `PRG/Modelo de datos - Programación` | **Pendiente de corregir.** `Notificacion.disparada_por` apunta a `Cuenta`, una entidad que ya no existe: debe ser `Persona` (`REG`). |
| `VIS/Modelo de datos - Visitas escolares` | **Pendiente de corregir.** `aplicante_id` y `revisado_por` apuntan a `Cuenta`: deben ser `Persona` (`REG`). |
| `STD/Modelo de datos - Stands` | **Corregido (v2.0, 2026-08-21).** Extrajo `Cuenta` → `Persona` (`REG`) y `Evento` → `Feria` (`FER`), y retiró `evento_id` de solicitudes, stands y reservas. `edicion` y `sede` se incorporaron a `Feria`. |
| `EVT/Modelo de datos - Eventos` | **Sin cambios.** Su v3.0 ya asume una instancia por edición y que ninguna tabla guarda identificador de edición: ADR-0003 lo confirma. |

---

## Relación con otros dominios

| Dominio | Cómo depende de `FER` |
| --- | --- |
| `REG` | Ninguna: `REG` es global e independiente. `FER` depende de `REG` (necesita `Persona`), no al revés. |
| `EVT`, `TAL`, `STD`, `VIS` | Sus convocatorias, propuestas y actividades viven **dentro** del schema de una feria. No referencian a `Feria`: la feria es el contexto de la conexión, no una columna. |
| `PRG`, `SAL` | Igual: el programa y el catálogo de salas son de la feria en la que se está. |

---

## Pendientes por validar

- **Transferencia de propiedad de una feria.** Con exactamente un dueño y solo él pudiendo
  administrar accesos, una feria cuyo dueño deja el proyecto queda bloqueada. Hoy la salida es
  que el operador de la plataforma reasigne la propiedad por comando. Falta decidir si se
  formaliza como caso de uso ejecutable por el propio dueño (CU-FER-005) — es lo que quitaría
  la dependencia del equipo técnico. Ver `Modelo de datos - Ferias` §6 y CU-FER-004 E2.
- **Cómo elige la feria un participante.** `FER` define quién administra una feria; falta
  precisar cómo llega el **aplicante** a la feria en la que quiere proponer: si basta el prefijo
  de URL o hace falta una portada que liste las ferias con convocatoria abierta. Hoy el
  participante llega a `/convocatorias` sin feria de por medio.
- **Qué pasa al archivar una feria.** El estado `archivada` está definido, pero no el
  procedimiento: si el schema se conserva en línea, se vuelca a un respaldo, o queda accesible
  en solo lectura desde el panel.
- **Nivel de solo lectura.** ADR-0004 lo elimina a sabiendas (no hay supervisor que solo
  observe). Conviene confirmarlo con el cliente antes de que haya administradores operando: si
  lo pide de vuelta, se recupera con columnas en `AdminFeria` y un ADR que reemplace al 0004.

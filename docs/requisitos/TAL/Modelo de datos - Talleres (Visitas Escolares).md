---
estado: propuesta
version: 0.1
tags:
  - modelo-de-datos
  - talleres
  - visitas-escolares
fecha: 2026-06-28
---
# Modelo de datos — Talleres / Visitas Escolares

> Cubre únicamente las entidades de **visitas escolares** (CU-TAL-007).
> Las entidades de propuestas de talleristas (RF-TAL-01/02) se documentarán en una sección separada.
> Fuente primaria: ficha física "Registro para visitas escolares 2026" y formulario Google Forms de FILEY.

---

## 1. Entidades

### VisitaEscolar

Registro principal de la solicitud de visita de una institución educativa a la FILEY.

| Atributo             | Tipo          | Restricciones                             | Notas |
|----------------------|---------------|-------------------------------------------|-------|
| `id`                 | UUID          | PK                                        | |
| `folio`              | String        | Único, generado por sistema               | Ej. `VIS-2026-001` |
| `fecha_recepcion`    | DateTime      | Generado por sistema al enviar            | |
| `estado`             | Enum          | `recibida` \| `confirmada` \| `cancelada` | Estado inicial: `recibida` |
| `observaciones`      | Text          | Opcional                                  | Texto libre; ej. preferencia de horario |
| `id_responsable`     | FK → Persona  | Obligatorio                               | Core REG — quien hace el trámite |
| `id_edicion`         | FK → EdicionFeria | Obligatorio                           | Core compartido |

### InstitucionEducativa

Datos de la institución que registra la visita. Embebidos en `VisitaEscolar` para MVP (no entidad separada aún, dado que no hay reutilización entre ediciones confirmada).

| Atributo               | Tipo    | Restricciones | Notas |
|------------------------|---------|---------------|-------|
| `nombre_institucion`   | String  | Obligatorio   | |
| `director`             | String  | Obligatorio   | |
| `clave_trabajo`        | String  | Obligatorio   | Clave SEP — identificador oficial de la institución educativa en México |
| `nivel_academico`      | Enum    | Obligatorio   | `preescolar` \| `primaria` \| `secundaria` \| `preparatoria` \| `universidad` |
| `sector`               | Enum    | Obligatorio   | `publico` \| `privado` |
| `turno`                | Enum    | Obligatorio   | `matutino` \| `vespertino` |
| `direccion`            | String  | Opcional      | |
| `estado_republica`     | String  | Obligatorio   | |
| `municipio`            | String  | Obligatorio   | |
| `telefono_institucion` | String  | Opcional      | |
| `correo_institucion`   | String  | Opcional      | |

> **Nota:** La `clave_trabajo` (ej. `31DES2001W`) es el identificador oficial del INEGI/SEP para instituciones educativas en México. Puede usarse en el futuro como clave de deduplicación si se crea una entidad `InstitucionEducativa` separada y reutilizable entre ediciones.

### GrupoVisita

Un grupo de alumnos que asistirá dentro de la misma visita. Una `VisitaEscolar` tiene al menos un `GrupoVisita`.

| Atributo              | Tipo              | Restricciones          | Notas |
|-----------------------|-------------------|------------------------|-------|
| `id`                  | UUID              | PK                     | |
| `id_visita`           | FK → VisitaEscolar | Obligatorio            | |
| `nombre_responsable`  | String            | Obligatorio            | Docente o adulto responsable del grupo durante la visita |
| `grado`               | String            | Obligatorio            | Ej. "Segundo", "Tercero de primaria" |
| `cantidad_alumnos`    | Integer           | Obligatorio, > 0       | Alumnos del grupo (capacidad de sala: ~35 por grupo en Ek Balam) |

---

## 2. Relaciones

```
Persona (Core REG)
    └──< VisitaEscolar (1:N — un responsable puede registrar varias visitas en distintas ediciones)
              ├── [InstitucionEducativa embebida]
              └──< GrupoVisita (1:N — al menos 1 grupo por visita)

EdicionFeria (Core compartido)
    └──< VisitaEscolar
```

---

## 3. Notas de diseño

- **Capacidad por sala:** El Salón Ek Balam aloja ~35 personas por sala (subdivisiones con mamparas). Los grupos de la ficha real son de 35 alumnos cada uno. El sistema no valida esto automáticamente en el registro, pero Elvira lo considera al asignar actividades.
- **Total de alumnos:** Se calcula sumando `cantidad_alumnos` de todos los `GrupoVisita` de la visita. No es un campo almacenado.
- **Turno:** El turno de la institución (matutino/vespertino) condiciona qué bloques de actividad son asignables por Elvira; no se valida en el registro, se usa en programación.
- **Nivel académico ↔ Público de actividad:** El programa muestra actividades con etiqueta `Público` (primaria, secundaria, prepa, general). El `nivel_academico` de la institución es el criterio de compatibilidad que Elvira usa para asignar grupos a actividades. No se valida en el registro.

---

## 4. Temas abiertos

- Confirmar si `InstitucionEducativa` debe ser una entidad separada y reutilizable entre ediciones (requeriría deduplicación por `clave_trabajo`), o si se mantiene embebida en `VisitaEscolar`.
- Definir qué datos mínimos recibe Elvira en el panel de administración para asignar actividades a los grupos (fase de programación, fuera de alcance del registro).
- Confirmar si el estado `confirmada` se asigna cuando Elvira envía la carta de confirmación, o en otro momento.

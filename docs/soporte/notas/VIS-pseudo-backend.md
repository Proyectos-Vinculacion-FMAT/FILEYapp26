# Pseudo-backend JSON para VIS

## Contexto

Los prototipos HTML de FILEY son estáticos: cada página trae sus propios datos de ejemplo
hardcodeados, y navegar de una pantalla a otra pierde cualquier cambio (los README de los
módulos lo dicen explícitamente: "no guarda ni envía datos"). Esto genera inconsistencia en la
demo — reservar un taller en `reservar.html` no aparece en `itinerario.html` ni en el panel de
admin. Este documento define un pseudo-backend con **JSON como base de datos** para el dominio
`VIS` (Visitas escolares), persistido en `localStorage` durante la demo, sin API real ni build
step. EVT y REG quedan fuera de esta iteración.

## Alcance

- Consistencia de datos en el happy path de **VIS únicamente**, aplicante y administrador.
- Datos semilla reproducibles para iniciar/reiniciar la demo.
- Sin dictamen (Aceptar/Solicitud de cambios/Rechazar): ya estaba fuera del alcance de la
  maqueta VIS (README, CU-VIS-006/007/008). Los registros de escuela no tienen estado de
  revisión, son simplemente editables.
- El catálogo de talleres modela un único día: **14 de marzo de 2027**.
- El catálogo de talleres sigue siendo semilla propia de VIS (no se modela `TAL` como dominio
  aparte).

## Datos: archivos semilla

Un archivo JSON por registro, agrupados por tipo:

```text
prototipo/common/db/VIS/semillas/
  escuelas/
    vis-2027-001.json   ← Benito Juárez García (única visible del lado aplicante)
    vis-2027-008.json   ← Instituto Modelo
    vis-2027-046.json   ← Ermilo Abreu Gómez
  talleres/
    2027-03-14.json     ← catálogo del único día modelado (nombrado por fecha para poder
                           agregar más días después sin cambiar el patrón)
```

Cada JSON de escuela es autocontenido: institución, responsable, grupos y su propio array de
**reservas embebido** (no existe una colección `vis_reservas` aparte — el itinerario de una
escuela es literalmente el array `reservas` de su registro).

```json
// vis-2027-001.json (forma aproximada)
{
  "id": "vis-2027-001",
  "folio": "VIS-2027-001",
  "institucion": { "nombre": "Benito Juárez García", "cct": "31DPR0681L", "...": "..." },
  "responsable": { "nombre": "Isaac Alejandro Ortiz Zaldivar", "cargo": "Docente", "...": "..." },
  "nivel_educativo": "Primaria",
  "campo_libre": "",
  "grupos": [
    { "id": "g1", "nombre_responsable": "Erick Matos Pantoja", "grado": "6°", "cantidad_alumnos": 35 },
    { "id": "g2", "nombre_responsable": "Juan López Salvador", "grado": "4°", "cantidad_alumnos": 35 },
    { "id": "g3", "nombre_responsable": "Enrique Segoviano Ruiz", "grado": "5°", "cantidad_alumnos": 20 }
  ],
  "reservas": [
    { "id": "r1", "grupo_id": "g1", "taller_id": "...", "cantidad_alumnos": 35, "fecha_reserva": "..." },
    { "id": "r2", "grupo_id": "g3", "taller_id": "...", "cantidad_alumnos": 20, "fecha_reserva": "..." },
    { "id": "r3", "grupo_id": "g1", "taller_id": "...", "cantidad_alumnos": 35, "fecha_reserva": "..." }
  ]
}
```

`talleres/2027-03-14.json` es un array plano: `[{ id, turno, sala, horario, titulo, nivel, base }, …]`
— mismo layout salas×bloques que hoy vive hardcodeado como `GRID`/`SALAS`/`TIMES` en
`prototipo/VIS/app.js`, movido a datos semilla.

Los 3 registros de escuela migran tal cual de las filas ya hardcodeadas en
`admin-propuestas.html` (folio, institución, grupos y reservaciones existentes), con un solo
ajuste: las reservaciones de **Instituto Modelo (008)** se recorren del 17 al **14 de marzo**,
para que todo el sistema module un único día. **Ermilo Abreu Gómez (046)** nace sin reservas
(sus reservaciones "fueron canceladas por la coordinación" en el ejemplo original).

`db.js` hace `fetch()` de los 4 archivos en paralelo al cargar, arma un objeto en memoria y lo
copia a `localStorage` (el JSON "temporal" de la corrida de demo) en el primer uso. La semilla
original nunca se muta. `FileyDB.reset()` repite el `fetch` y sobrescribe el JSON temporal, para
reiniciar la demo sin tocar los archivos originales.

## Reglas de negocio

- **Cupo compartido**: el cupo restante de un taller = `base` − suma de `cantidad_alumnos` de
  las reservas de **todas** las escuelas cuyo `reservas[].taller_id` apunte a ese taller (se
  recorren las 3 escuelas semilla, es trivial a esta escala).
- **Badges por escuela**: las badges de grupo en el grid solo listan los grupos de la escuela
  que se está viendo/editando en ese momento — no se mezclan grupos de otras escuelas.
- **Solo Benito Juárez (VIS-2027-001) es visible del lado aplicante**: no hay login ni selector
  de escuela, así que el flujo aplicante siempre opera sobre ese registro fijo. Las otras 2
  escuelas semilla existen solo para poblar la lista del panel admin.
- **Grado por nivel educativo**: al registrar/editar un grupo, el campo "Grado" pasa de texto
  libre a un `select` cuyas opciones dependen del `nivel_educativo` de la escuela:
  - Preescolar → 3 grados
  - Primaria → 6 grados
  - Secundaria → 3 grados
  - Preparatoria → 3 grados
  - Universidad o Multigrado → se mantiene como campo de texto libre (no hay catálogo fijo de
    grados para estos niveles).
- **Reserva en conflicto de horario = mover, no bloquear**: si un grupo ya tiene una reserva en
  un bloque horario y el usuario intenta asignarlo a otro taller en ese mismo bloque, el sistema
  debe quitar automáticamente la reserva anterior de ese grupo y dejarlo en la más reciente (hoy
  la interfaz simplemente bloquea el intento y no hace nada).

## Flujo por pantalla

**Lado escuela (aplicante)** — todo opera sobre el registro de Benito Juárez:

- `formulario-vis.html`: los campos hoy precargados se leen del JSON semilla en vez de estar
  hardcodeados en el HTML; siguen viéndose igual (no se alarga la demo) pero son editables,
  incluido el campo de detalles adicionales. Enviar hace `insert`/`update` sobre el registro.
- `reservar.html`: el grid se pinta desde el catálogo semilla. Reservar agrega una entrada al
  array `reservas` de Benito Juárez; el cupo se recalcula sumando reservas reales de las 3
  escuelas, y las badges reflejan los grupos de esta escuela.
- `itinerario.html`: se genera leyendo `reservas` del registro de Benito Juárez (unido con el
  catálogo para mostrar título/sala/horario) — ya no lista ítems hardcodeados.

**Lado administrador** — único lugar donde se ven las 3 escuelas semilla:

- `admin-propuestas.html`: filas generadas desde las 3 escuelas, ordenadas por folio, indicando
  si cada una ya tiene talleres reservados.
- `admin-escuela-edit.html`: carga los datos actuales de la escuela seleccionada para
  actualizarlos; guardar hace `update` sobre ese registro.
- `admin-reservar.html` / `itinerario-admin.html`: mismo flujo que el lado escuela pero para la
  escuela seleccionada desde la lista, leyendo/escribiendo su propio array `reservas`.
- Los botones ya existentes "Cancelar todas las reservaciones" / "Cancelar reservaciones G*"
  quitan esas entradas del array `reservas`, igual que `[data-itin-remove]` en
  `itinerario.html`/`itinerario-admin.html` — es la misma acción de "quitar reserva".

## Cómo probar en desarrollo

Los JSON semilla se cargan con `fetch()`, que falla si el HTML se abre directo por `file://`
(CORS). Para desarrollo, levantar `scripts/preview-vis.sh` (sirve `prototipo/` por HTTP local,
sin dejar nada en el repo) y probar contra `http://localhost:8080/...`. En producción esto no es
un problema: el prototipo se publica en GitHub Pages, que ya sirve por HTTP real.

## Orden de implementación

1. Los 4 archivos semilla + `common/db.js` (fetch, copia a `localStorage`, API
   get/list/insert/update/reset).
2. Arreglos de proto previos: select de grado dependiente de nivel educativo; mover (no
   bloquear) una reserva en conflicto de horario.
3. Lado escuela: formulario → reservar → itinerario, contra el JSON temporal.
4. Lado admin: lista (3 escuelas por folio) → editar escuela → reservar/itinerario admin.

## Verificación

- Enviar el formulario sin tocar los placeholders y confirmar que la escuela aparece en la
  lista admin con esos mismos datos.
- Reservar un taller del lado escuela y confirmar que el cupo baja, la reserva aparece en
  `itinerario.html`, y el admin ve la misma reserva al entrar a esa escuela.
- Editar/reservar desde el admin y confirmar que se refleja igual del lado escuela.
- Repetir con las otras 2 escuelas solo desde el admin, confirmando que el cupo se comparte
  entre las 3 pero grupos/itinerario no se mezclan.
- Intentar reservar un mismo grupo en dos talleres del mismo bloque horario y confirmar que se
  mueve la reserva en vez de bloquearse.
- Cambiar el nivel educativo de una escuela y confirmar que las opciones de grado disponibles
  cambian según el nivel (o quedan como texto libre en universidad/multigrado).
- `FileyDB.reset()` debe devolver las 3 escuelas, el catálogo y las reservas a su estado
  semilla original.

# Resumen de reunión — FILEY | 23 de junio de 2026

**Duración:** ~3 horas | **Asistentes:** equipo técnico + Hipólito (contenidos) + Elvira (talleres/VIDA)
**Fuente:** Transcripción automática CraftNote

---

## 1. CORE REG — Registro y autenticación

### Registro de usuario externo (aplicante)

- Formulario único de registro con campos: nombre completo, correo electrónico, teléfono, dependencia, cargo, ciudad, estado
- Autenticación por **OTP enviado al correo** (sin contraseña permanente)
- El correo es la llave de identidad del usuario

### Registro y autenticación de usuario administrativo

- Registro manual por admin superior (Hipólito o Elvira no se auto-registran)
- Autenticación: **usuario + contraseña**
- Se consideró Firebase para gestión de credenciales admin; no se cerró la decisión

### Pantalla de inicio post-login (aplicante)

- El usuario ve un panel con las convocatorias disponibles como botones (habilitados/deshabilitados según fechas)
- Tipos visibles: Contenidos, Talleres, Visitas escolares, Stands

---

## 2. CORE EVE — Convocatoria y Propuestas

### Configuración de convocatoria (admin)

- Campos: fecha de apertura, fecha de cierre, adjuntar PDF con bases
- **El cierre automático al vencer la fecha se absorbe en este mismo CU** → CU-EVE-005 (cierre automático) queda redundante o se elimina
- Se puede abrir/cerrar manualmente también

### Tipos de actividades y formularios

| Módulo           | Responsable | Tipos de actividad                                                                                                                      |
| ----------------- | ----------- | --------------------------------------------------------------------------------------------------------------------------------------- |
| Contenidos        | Hipólito   | Conversatorio, conferencia, charla, mesa redonda, presentación de libro, presentación de revista, lectura de obra, encuentro          |
| Talleres / VIDA   | Elvira      | Cuenta cuentos, plática para jóvenes, presentación de libros para niños/jóvenes, obra, presentación teatral, proyección en cines |
| Visitas escolares | Elvira      | Aforo máximo 105 personas (múltiplos de 35); el formulario ya existe                                                                  |
| Stands            | TBD         | —                                                                                                                                      |

### Registro de propuesta de actividad (aplicante)

- El aplicante elige el tipo de actividad → el formulario muestra los campos específicos correspondientes
- Campos comunes a todos los formularios + campos específicos por tipo
- Una vez enviada, **la propuesta es inmutable** (solo admin puede solicitar cambios)
- El aplicante puede tener múltiples propuestas registradas (bajo el mismo correo)
- Vista "mis solicitudes" con estado de cada una

### Estados de una propuesta

```
Enviada → En revisión  →  Aceptada
                      →  Solicitud de cambios  →  (aplicante edita y reenvía)
                      →  Rechazada
```

- **En revisión**: estado inicial automático al enviar
- **Solicitud de cambios**: reabre el formulario al aplicante con observaciones del admin; al reenviar vuelve a "en revisión"
- **Rechazada**: decisión definitiva; libera el espacio si había reserva
- **Notificación por correo** al cambiar estado (hardcoded en primera versión)

### Revisión por el admin (Hipólito / Elvira)

- Vista de lista de solicitudes con filtros por estado/tipo
- Detalle de cada solicitud (read-only del contenido)
- Acciones: Aceptar / Solicitar cambios / Rechazar
- El admin puede añadir observaciones al solicitar cambios
- Hipólito puede editar campos por curaduría (a definir exacto)

---

## 3. Programación de actividades

### CRUD de espacios (Salones y Salas)

- Estructura: **Salón** → contiene una o varias **Salas**
- Al crear un salón se genera automáticamente una sala por defecto
- Cada sala tiene: nombre, aforo, horarios disponibles

### Asignación de actividades aceptadas

- Una vez aceptada una propuesta, el admin (Hipólito o Elvira) asigna: sala, fecha, hora de inicio y fin
- Vista tipo **calendario / Excel** (eje X = días, eje Y = salones/salas)
- Bloques fijos de tiempo de **1h15m**
- Sin movimiento automático de bloques
- Si hay choque de horario → advertencia pero no bloqueo automático
- Una actividad puede programarse **más de una vez** (ej. taller que se repite)

### Visibilidad cruzada

- Hipólito ve la programación de Elvira en **solo lectura** y viceversa
- Ambos comparten las mismas salas/salones

### Exportación

- Vista general exportable a **Excel, Word y PDF**
- URL pública para que asistentes consulten la programación sin login (pendiente de definir)

### Notificación al aplicante

- Cuando se asigna horario, el aplicante recibe notificación con los datos
- El aplicante puede **confirmar o cancelar** su participación (se mencionó pero no se cerró el flujo)

---

## 4. Terminología acordada

| Término acordado                            | Alternativas descartadas             |
| -------------------------------------------- | ------------------------------------ |
| **Aplicante**                          | Proponente, registrante, solicitante |
| **Registro de propuesta de actividad** | Envío de propuesta, postulación    |
| **Solicitud de cambios**               | Rechazado con cambios, revisión     |
| **Salón / Sala**                      | Espacio, venue                       |

---

## 5. Tareas pendientes — ordenadas por prioridad

### Urgentes (antes del fin de semana 27-Jun)

- [X] **Hacer push** del trabajo de Juan al repositorio (tenía zip sin subir)
- [X] **Ajustar CU-EVE-001** (configurar convocatoria) para que absorba el cierre automático
- [X] **Marcar CU-EVE-005** como redundante o eliminar (el cierre automático ya está en CU-EVE-001)
- [X] **Actualizar terminología** en todos los CUs ya redactados: usar "aplicante" en lugar de otras variantes

### Esta semana (antes del 30-Jun)

- [X] Revisar los **5 formularios existentes** (Hipólito + Elvira + visitas escolares + stands) para identificar y alinear los **campos comunes** de registro de propuesta
- [X] Redactar los **CU-EVE de registro de propuesta** de actividad (flujo del aplicante: registrar → ver lista → ver detalle con estado)
- [X] Redactar los **CU-EVE de revisión/selección** (flujo del admin: ver lista → revisar → aceptar/solicitar cambios/rechazar + notificación)
- [X] Clarificar con Hipólito cómo hace actualmente la programación (¿Excel propio?) para no romper su flujo actual
- [X] Preguntar a Hipólito si quiere manejar notificación del **preliminar de programación** (antes de asignar definitivamente)

### Para agosto (módulo REG listo para producción)

- [ ] Confirmar decisión sobre **Firebase vs alternativa** para gestión de credenciales admin
- [ ] Mapear el flujo de **"eventos EBT"** (no estaba en la documentación al momento de la reunión)
- [ ] Definir si **visitas escolares** queda con Elvira o se maneja como módulo separado
- [ ] Definir flujo de **confirmación/cancelación del aplicante** tras recibir horario asignado

### Pendientes de diseño (septiembre-octubre)

- [ ] **Catálogo de actividades para escuelas** (pendiente de diseño completo; no implementar aún)
- [ ] **URL pública** de programación (consulta sin login)
- [ ] Coordinación Hipólito/Elvira para acceso compartido a salas (read-only cross-module)
- [ ] Vista del **programa publicado** (catálogo final exportable/publicable)

---

## 6. Decisiones que quedaron abiertas

1. ¿Firebase o solución propia para autenticación admin?
2. ¿El aplicante ve todas sus solicitudes juntas o separadas por módulo/convocatoria?
3. ¿Hipólito puede editar campos de una propuesta durante la curaduría, o solo acepta/rechaza?
4. ¿La fecha deseada la indica el aplicante en el formulario o la asigna directamente Hipólito?
5. ¿Confirmación/cancelación del aplicante es obligatoria o solo informativa?
6. Granularidad de roles admin: ¿Hipólito y Elvira tienen acceso total o limitado a su módulo?

---

*Documento generado a partir de la transcripción de la reunión del 23 de junio de 2026.*

---

## 7. Aclaraciones de Hipólito — respuestas recibidas el 27-Jun-2026

Preguntas surgidas del análisis de los CUs de EVT; respondidas por escrito.

### 7.1 "Público al que va dirigido" — tipo de campo

**Pregunta:** ¿El campo "público al que va dirigido" es texto libre o tiene opciones predefinidas?

**Respuesta:** Selección múltiple. Las opciones son:
- Público en general
- Académico
- Estudiantil
- Infantil
- Familias

**Impacto:** Campo actualizado en CU-EVT-002 (Datos relevantes → Entradas).

---

### 7.2 Distribución del catálogo/programa al público

**Pregunta:** ¿Hipólito envía catálogos al público general una vez que tiene la programación lista?

**Respuesta:** No se envía al público general. El programa es para trabajo interno. La información detallada se usa para elaborar el programa impreso/digital (trabajo de diseño editorial, no de distribución directa desde el sistema).

**Impacto:** Confirma que las funciones de exportación (A6) y publicación (A5) son herramientas de uso interno/editorial, no de distribución masiva. La cartelera pública (V1, V2) es un canal separado y complementario.

---

### 7.3 RFH-18 — Ventana de ajustes: ¿el proponente puede pedir cambios?

**Pregunta:** ¿El periodo de ajustes del RFH-18 aplica a todos los tipos de actividad? ¿El proponente puede solicitar cambios de horario?

**Respuesta:** Los proponentes **no tienen opción de pedir cambios de horario**. Solo el coordinador (Hipólito) puede hacer cambios de horario, salón y, excepcionalmente, de fecha (en ese caso coordinando con el involucrado). La "ventana de ajustes" es del coordinador, no del proponente.

**Impacto:**
- RFH-18 reescrito para reflejar que la ventana es del coordinador, no del proponente.
- Vista P4 ("Mi horario asignado") actualizada: se eliminó la acción "Solicitar cambio"; el proponente solo puede confirmar asistencia o indicar incomparecencia.
- Tema abierto del Modelo de datos sobre RFH-18 cerrado.

---

### 7.4 Ejemplar físico — ¿qué pasa si el proponente no lo envía?

**Pregunta:** ¿Qué ocurre si el proponente que presentará un libro/revista no envía el ejemplar físico?

**Respuesta:** No hay consecuencia en el sistema. El aviso de envío sirve para presionar al solicitante — el ejemplar físico le ayuda a Hipólito a revisar mejor la propuesta. El solicitante no debe saber que la omisión no tiene consecuencias.

**Impacto:**
- CU-EVT-010 actualizado: el objetivo y el alcance ahora especifican que la marcación es un registro de control interno **no bloqueante**, y se añadieron las reglas de negocio correspondientes.
- El texto del formulario (CU-EVT-002, flujo alterno A1) permanece sin cambios: debe seguir mostrando la instrucción de envío de ejemplar para mantener la presión.

---
estado: propuesta
version: "0.1"
tags:
  - tipo/plan-de-pruebas
  - dom/reg
  - dom/fer
  - dom/evt
  - dom/tal
  - dom/std
  - dom/vis
  - dom/prg
  - dom/sal
  - tema/usabilidad
  - tema/usuarios
fecha: 2026-09-02
---
# Matriz de pruebas de usabilidad — FILEY 2027

Qué se prueba con personas, con quién, contra qué caso de uso y con qué criterio se declara
aprobado. Cada fila nace de un `CU-DOM-NNN` de [`requisitos/`](<../requisitos/README.md>) y se
verifica contra las [leyes de UX del proyecto](<../../.claude/skills/filey-identidad/references/leyes-ux.md>).

**Fuentes:** los índices de casos de uso de los ocho dominios, los mapas de flujo del prototipo
([REG](<../../prototipo/mapas/REG.md>) · [EVT](<../../prototipo/mapas/EVT.md>) ·
[VIS](<../../prototipo/mapas/VIS.md>)) y las reglas de identidad/UX del skill `filey-identidad`.

> [!important] El dato que decide todo el diseño de estas pruebas
> **Nadie usa FILEY dos veces seguidas.** Un docente agenda su visita una vez al año; un ponente
> manda propuesta una vez al año; un expositor renta stand una vez al año. No hay curva de
> aprendizaje que amortice un mal flujo: **cada sesión es la primera sesión**. Por eso lo que se
> mide aquí es *éxito sin ayuda a la primera*, no velocidad de usuario experto — y por eso la
> ley de Jakob (parecerse a lo que ya conocen) pesa más que cualquier originalidad.

<!-- -->

> [!note] Dos excepciones a lo anterior
> Los **administradores** (Hipólito en `EVT`, Elvira en `TAL`/`VIS`, Gilberto en `STD`) sí son
> usuarios frecuentes durante seis a ocho semanas al año, y en modo ráfaga: dictaminan decenas
> de propuestas seguidas. Sus pruebas se miden distinto — importa el **costo por repetición**
> (clics y confirmaciones por propuesta), no el descubrimiento.

---

## 1. Perfiles de participante

| ID | Perfil | Quién es en la vida real | Frecuencia de uso | Contexto de uso probable |
| --- | --- | --- | --- | --- |
| **P1** | Proponente `EVT` | Ponente, editorial, académico UADY o externo | 1 vez/año | Escritorio, con el PDF de la convocatoria abierto al lado |
| **P2** | Tallerista `TAL` | Quien propone actividad infantil/juvenil | 1 vez/año | Escritorio o tableta |
| **P3** | Responsable escolar `VIS` | Docente, prefecto(a), director(a) o padre/madre de familia | 1 vez/año | **Móvil frecuente**, a veces en horario de clase |
| **P4** | Expositor `STD` | Editorial o empresa que renta stand | 1 vez/año | Escritorio, con documentos fiscales a la mano |
| **P5** | Administrador de módulo | Hipólito (`EVT`), Elvira (`TAL`/`VIS`), Gilberto (`STD`) | Diario en temporada | Escritorio, sesiones largas, **imprime listados** |
| **P6** | Dueño de la feria | Coordinación general de FILEY | Semanal en temporada | Escritorio |
| **P7** | Operador de la plataforma | Equipo técnico (UADY/FMAT) | Al abrir cada edición | Terminal + `/django-admin/` |

> [!warning] P3 es el perfil de mayor riesgo del sistema
> Es el único que combina las tres condiciones malas a la vez: **formulario más largo**
> (escuela + contacto + hasta 3 grupos), **regla dura no obvia** (105 alumnos por propuesta, una
> propuesta por nivel educativo — ver [CU-VIS-001](<../requisitos/VIS/A - Aplicación/CU-VIS-001 Registrar la propuesta de visita escolar (datos de la escuela y del contacto).md>))
> y **uso desde el teléfono**. Si solo hay presupuesto para una ronda, se prueba P3.

---

## 2. Método

### 2.1 Muestra

Cinco participantes por perfil y por ronda. Es el punto en el que se detecta ~85% de los
problemas de usabilidad de un flujo; más participantes en la misma ronda repiten hallazgos en
vez de descubrir nuevos. Vale más **tres rondas de cinco** que una de quince.

| Ronda | Qué se prueba | Sobre qué | Perfiles | Cuándo |
| --- | --- | --- | --- | --- |
| **R1** | `REG` + `FER` — acceso, elección de edición, catálogo, accesos y convocatorias | **Django, ya construido** | P1, P3, P5, P6, P7 | Ya se puede correr |
| **R2** | `EVT` + `VIS` — propuesta, seguimiento, dictamen, itinerario | **Prototipo estático** | P1, P3, P5 | Antes de portar a Django |
| **R3** | `STD`, `TAL`, `PRG`, `SAL` | Prototipo o Django según avance | P2, P4, P5 | Conforme se construyan |
| **T** | Transversales (sin JS, impresión, móvil, teclado, tono) | Donde exista la pantalla | Todos | En cada ronda, como capa extra |

> [!tip] La ronda 2 se corre sobre el prototipo, y eso es una ventaja, no un parche
> `prototipo/` es la **especificación visual** del proyecto: un hallazgo ahí se arregla editando
> HTML, no migraciones. Probar antes de portar a Django es lo que hace barato el rediseño.

### 2.2 Sesión

Sesión de **60 minutos**, moderada, con pensar en voz alta:

1. **5 min** — consentimiento, contexto, aviso de que se prueba el sistema y no a la persona.
2. **5 min** — preguntas de contexto (¿cómo lo hace hoy? ¿en qué dispositivo?).
3. **40 min** — 4 a 6 tareas de la matriz, en el orden en que ocurrirían de verdad.
4. **10 min** — cuestionario SUS + preguntas abiertas.

Reglas del moderador: no se guía, no se nombra el botón, no se contesta "¿le doy aquí?" hasta que
la persona ya lo intentó. **Ninguna tarea se lee con el vocabulario de la interfaz** — si la
tarea dice "dictamina", se mide si encontró el botón "Dictaminar", no si sabe leer.

### 2.3 Métricas por tarea

| Métrica | Cómo se mide | Umbral por defecto |
| --- | --- | --- |
| **Éxito** | Completó / completó con ayuda / no completó | Ver columna de cada fila (85–95%) |
| **Tiempo en tarea** | Del inicio de la tarea a la confirmación en pantalla | Ver columna; **calibrar tras el piloto** |
| **Errores** | Acciones que alejan del objetivo y hay que deshacer | ≤1 por tarea crítica |
| **Peticiones de ayuda** | Veces que pregunta al moderador | 0 en tareas críticas |
| **SEQ** | *Single Ease Question*, 1–7, al terminar cada tarea | ≥5.5 |
| **SUS** | Al final de la sesión, 10 ítems | ≥68 aceptable · **≥75 objetivo** |

> [!warning] Los tiempos objetivo de la matriz son hipótesis, no compromisos
> Están estimados a partir de la complejidad declarada en los `CU-DOM.csv` y del número de campos
> de cada formulario. **Se recalibran con el piloto** (un participante por perfil, cuyos datos no
> entran al análisis). Un objetivo que falla en el piloto se ajusta; uno que falla en la ronda es
> un hallazgo.

### 2.4 Severidad de los hallazgos

| Nivel | Significado | Qué dispara |
| --- | --- | --- |
| **0** | No es problema de usabilidad | Se archiva |
| **1** | Cosmético | Se arregla si sobra tiempo |
| **2** | Menor — molesta, no bloquea | Backlog priorizado |
| **3** | Mayor — impide o retrasa la tarea | **Se arregla antes de la siguiente ronda** |
| **4** | Catastrófico — la tarea no se completa, o se completa mal sin que la persona lo note | **Bloquea el despliegue del módulo** |

El nivel 4 incluye un caso propio de este sistema: **completar la tarea creyendo algo falso.**
Un dueño que "cierra" una convocatoria adelantando su fecha (PU-FER-07), o una escuela que cree
tener cupo garantizado cuando no lo reservó (PU-VIS-05), terminaron el flujo sin error visible y
con un daño real. Se cuenta como fallo aunque la pantalla diga que todo salió bien.

---

## 3. Matriz — Ronda 1: `REG` + `FER` (lo ya construido en Django)

Cubre lo que hoy corre en `filey/`: acceso por OTP, alta de cuenta, elección de edición, catálogo
de convocatorias y el panel de accesos de una feria. Ver
[`CU-REG Índice`](<../requisitos/REG/CU-REG Índice.md>) y
[`CU-FER Índice`](<../requisitos/FER/CU-FER Índice.md>).

| ID | Perfil | Tarea que se le pide | CU | Aprueba si… | Objetivo | Ley · Prio |
| --- | --- | --- | --- | --- | --- | --- |
| **PU-REG-01** | P1 · P3 | "Es tu primera vez aquí. Entra y llega a la lista de convocatorias." | CU-REG-001 · 002 | Llega al catálogo sin ayuda y sin retroceder más de una vez | 3 min · 90% | Jakob · Zeigarnik — **Crítica** |
| **PU-REG-02** | P1 | "Volviste seis meses después. Entra con el correo que ya habías usado." | CU-REG-002 | **No busca contraseña** ni intenta registrarse otra vez | 90 s · 95% | Jakob — **Crítica** |
| **PU-REG-03** | P3 | "No te llegó el código. Consíguelo de nuevo." | CU-REG-002 A1 | Encuentra *Reenviar* y entiende por qué está deshabilitado 60 s | 60 s · 85% | Doherty · tono — Alta |
| **PU-REG-04** | P1 | "Teclea mal el código dos veces y luego entra." | CU-REG-002 E1 | Entiende cuántos intentos quedan (de 3) y qué pasa al agotarlos | 2 min · 85% | Postel · tono — Alta |
| **PU-REG-05** | P5 | "Entra como administrador de tu módulo." | CU-REG-003 | Distingue el acceso admin del de participante sin preguntar | 2 min · 90% | Hick — **Crítica** |
| **PU-REG-06** | P5 | "Cierra tu sesión y comprueba que quedó cerrada." | CU-REG-004 | Encuentra *Salir* en la barra superior a la primera | 45 s · 95% | Jakob — Media |
| **PU-FER-01** | P1 · P3 | "Elige la edición en la que vas a participar." | CU-FER-010 | Reconoce que elige **edición**, no módulo | 60 s · 90% | Hick — Alta |
| **PU-FER-02** | P5 | "Entra a FILEY 2027; administras dos ediciones." | CU-FER-002 | No confunde edición con módulo y sabe en cuál quedó | 60 s · 90% | Miller · acento — Alta |
| **PU-FER-03** | P1 · P3 | "Dinos cuáles convocatorias están abiertas hoy y cuál te toca a ti." | CU-FER-006 | Lee *abierta/cerrada* **por texto**, no deduciéndolo del color | 90 s · 90% | Color+texto · Hick — **Crítica** |
| **PU-FER-04** | P6 | "Da acceso de administrador a alguien de tu equipo." | CU-FER-003 | Alta correcta a la primera; entiende que el acceso es **por feria** | 2.5 min · 90% | Jakob — Alta |
| **PU-FER-05** | P6 | "Retira el acceso de un administrador que ya no colabora." | CU-FER-004 | No retira al equivocado; la confirmación dice **a quién** y con qué efecto | 2 min · 95% | Fitts — **Crítica** |
| **PU-FER-06** | P6 | "Da de alta la convocatoria de Eventos con sus fechas." | CU-FER-005 | Distingue fechas **anunciadas** del **estado** de la convocatoria | 4 min · 85% | Miller — Alta |
| **PU-FER-07** | P6 | "Cierra hoy la convocatoria de Eventos, antes de su fecha de cierre." | CU-FER-008 · 007 | **Usa el control de estado, no la fecha.** Adelantar la fecha no cierra nada | 2 min · 90% | Comprensión — **Crítica** |
| **PU-FER-08** | P6 | "Elimina una convocatoria creada por error." | CU-FER-009 | Entiende qué se lleva por delante antes de confirmar | 90 s · 95% | Fitts · tono — Alta |
| **PU-FER-09** | P7 | "Crea la edición 2028, designa a su dueño y haz que los participantes la vean." | CU-FER-001 · 010 | Descubre solo que nace `en_preparacion` y la activa | 5 min · 80% | Visibilidad del estado — Alta |

> [!danger] Tres trampas conocidas que estas pruebas existen para medir
> No son hipótesis: están documentadas como riesgo en el propio repositorio, y cada una produce
> una tarea "completada" con daño real.
>
> - **PU-FER-07 — fecha ≠ estado.** `CU-FER-008` es explícito: *"adelantar la fecha de cierre no
>   cierra nada"*. Si el dueño mueve la fecha creyendo que cerró, `EVT`/`STD`/`VIS` **siguen
>   aceptando registros**. Severidad 4 si ocurre.
> - **PU-FER-09 — la feria nace invisible.** Una edición recién creada está `en_preparacion` y el
>   participante solo ve las `activa`. Como la pantalla de elegir feria se salta cuando hay una
>   sola, el síntoma no es "falta una tarjeta": es *"no hay ninguna edición abierta"*.
> - **PU-FER-03 — estado solo por color.** Los organizadores **imprimen** los listados: un estado
>   que solo se distingue por color desaparece en blanco y negro (ver PU-TRV-02).

---

## 4. Matriz — Ronda 2: `EVT` + `VIS` (prototipo)

Los dos dominios con pantallas maquetadas y el par crítico aplicante/administrador completo.
Ver [`CU-EVT Índice`](<../requisitos/EVT/CU-EVT Índice.md>) y
[`CU-VIS Índice`](<../requisitos/VIS/CU-VIS Índice.md>).

### 4.1 `EVT` — proponente (P1)

| ID | Tarea que se le pide | CU | Aprueba si… | Objetivo | Ley · Prio |
| --- | --- | --- | --- | --- | --- |
| **PU-EVT-01** | "Averigua si tu actividad cabe en esta convocatoria y cuándo cierra." | CU-EVT-001 | Encuentra tipo admitido y fecha límite **sin abrir el PDF** | 2 min · 85% | Hick — Alta |
| **PU-EVT-02** | "Registra una charla con un ponente y su adjunto." | CU-EVT-002 | Termina sin abandonar ni perder lo capturado | 12 min · 85% | Hick · Miller · Zeigarnik — **Crítica** |
| **PU-EVT-03** | "Registra una presentación de libro." | CU-EVT-002 A1 | **Menciona por su cuenta** que debe enviar el ejemplar físico | 15 min · 80% | Divulgación progresiva — **Crítica** |
| **PU-EVT-04** | "Envía con un campo obligatorio vacío y corrígelo." | CU-EVT-002 E | No pierde datos y localiza el campo señalado a la primera | 2 min · 90% | Postel · tono — **Crítica** |
| **PU-EVT-05** | "Dinos en qué va tu propuesta y cuál es su folio." | CU-EVT-003 | Lee estado y folio sin interpretarlos mal | 60 s · 95% | Peak-end · Miller — Alta |
| **PU-EVT-06** | "Te pidieron cambios. Averigua cuáles y reenvía." | CU-EVT-004 | Encuentra el comentario del administrador **antes** de editar | 6 min · 85% | Zeigarnik — **Crítica** |
| **PU-EVT-07** | "Descarga tu constancia de participación." | CU-EVT-005 | La localiza sin recorrer todo el panel | 90 s · 90% | Jakob — Media |

### 4.2 `EVT` — administrador (P5)

| ID | Tarea que se le pide | CU | Aprueba si… | Objetivo | Ley · Prio |
| --- | --- | --- | --- | --- | --- |
| **PU-EVT-08** | "Encuentra las propuestas pendientes de literatura de esta semana." | CU-EVT-007 · 011 | **Usa los filtros** en vez de recorrer la lista | 2 min · 90% | Hick (3 filtros visibles) — Alta |
| **PU-EVT-09** | "Revisa esta propuesta y acéptala con su categoría." | CU-EVT-008 · 009 | Dictamina la propuesta correcta y entiende que se crea la Actividad | 5 min · 90% | Fitts — **Crítica** |
| **PU-EVT-10** | "Pide cambios a una propuesta y rechaza otra." | CU-EVT-009 | **No confunde rechazar con pedir cambios**; no están contiguos | 5 min · 90% | Fitts · tono — **Crítica** |
| **PU-EVT-11** | "Notifica el resultado a las 40 propuestas ya dictaminadas." | CU-EVT-010 | Sabe a quiénes va **antes** de enviar y ve progreso al enviar | 4 min · 85% | Doherty — **Crítica** |
| **PU-EVT-12** | "Marca que ya llegó el ejemplar físico de esta propuesta." | CU-EVT-012 | Encuentra el control en lista o detalle | 60 s · 90% | Fitts — Media |
| **PU-EVT-13** | "Configura fechas y cupos de la convocatoria del próximo año." | CU-EVT-001 | Termina sin campos ambiguos ni pedir ayuda | 8 min · 80% | Miller — Alta |
| **PU-EVT-14** | "Genera la ficha PDF de una actividad para el programa." | CU-EVT-006 | Obtiene el PDF y sabe qué contiene | 90 s · 90% | Doherty — Media |

### 4.3 `VIS` — escuela (P3) y administración (P5)

| ID | Perfil | Tarea que se le pide | CU | Aprueba si… | Objetivo | Ley · Prio |
| --- | --- | --- | --- | --- | --- | --- |
| **PU-VIS-01** | P3 | "Registra tu escuela con tres grupos de secundaria." | CU-VIS-001 | Completa escuela + contacto + 3 grupos sin abandonar | 15 min · 85% | Hick · Miller · Zeigarnik — **Crítica** |
| **PU-VIS-02** | P3 | "Tu escuela lleva 130 alumnos, de primaria y de secundaria. Regístrala." | CU-VIS-001 E1 | Descubre el tope de **105 por propuesta** y que va **una propuesta por nivel** | 8 min · 75% | Regla dura · tono — **Crítica** |
| **PU-VIS-03** | P3 | "Cambiaron los números. Corrige tu propuesta ya enviada." | CU-VIS-002 | Encuentra la edición y sabe si sigue dentro de la ventana | 4 min · 85% | Zeigarnik — Alta |
| **PU-VIS-04** | P3 | "Dinos si tu visita ya fue aceptada y qué sigue." | CU-VIS-003 | Lee estado y siguiente paso sin ayuda | 60 s · 95% | Peak-end — Alta |
| **PU-VIS-05** | P3 | "Arma tu itinerario: tres talleres de tu nivel el 14 de marzo." | CU-VIS-010 · 011 · 012 | Filtra por nivel/día/turno y entiende el **cupo restante** | 10 min · 80% | Hick · Miller — **Crítica** |
| **PU-VIS-06** | P3 | "Quita un taller del itinerario y confirma que liberó el cupo." | CU-VIS-013 · 014 | Entiende que el cupo liberado puede no volver a estar | 3 min · 90% | Fitts · tono — Alta |
| **PU-VIS-07** | P5 | "Revisa las propuestas del día y dictamina tres." | CU-VIS-004 → 008 | Dictamen inline **sin perder el lugar** en la lista | 8 min · 85% | Hick · Fitts — **Crítica** |
| **PU-VIS-08** | P5 | "Una escuela llamó por teléfono: dala de alta y reserva por ella." | CU-VIS-016 · 010–012 | Completa alta manual + reserva en una sola sesión | 12 min · 80% | Jakob — Alta |
| **PU-VIS-09** | P5 | "Quita a esta escuela de un taller sobrevendido." | CU-VIS-015 · 016 · 017 | No quita a la escuela equivocada; ve el efecto en el cupo | 3 min · 90% | Fitts — Alta |

> [!warning] Dos brechas ya detectadas que la ronda 2 debe confirmar con usuarios
> - El [mapa de flujo de VIS](<../../prototipo/mapas/VIS.md>) marca la **brecha C1+C4**: el
>   catálogo de `reservar.html` **no filtra por nivel educativo**, que es justo lo que pide
>   CU-VIS-010. PU-VIS-05 mide cuánto cuesta eso en la práctica.
> - `PU-VIS-02` es la tarea con el objetivo de éxito más bajo de toda la matriz (**75%**) a
>   propósito: hoy la regla de "una propuesta por nivel" solo existe como texto de excepción
>   (`E1`). Si el resultado real ronda ese número, el arreglo no es un mensaje mejor, es un
>   formulario que pregunte el nivel **antes** de pedir los 30 campos restantes.

---

## 5. Matriz — Ronda 3: `STD`, `TAL`, `PRG`, `SAL`

Dominios documentados pero sin pantalla construida (salvo el tablero de programación, maquetado
dentro del panel de `EVT`). Estas filas se corren **conforme cada módulo tenga pantalla**; hasta
entonces sirven como criterio de diseño, no como prueba pendiente.

### 5.1 `STD` — expositor (P4) y administración (P5)

| ID | Perfil | Tarea que se le pide | CU | Aprueba si… | Objetivo | Ley · Prio |
| --- | --- | --- | --- | --- | --- | --- |
| **PU-STD-01** | P4 | "Aplica como expositor con los documentos de tu empresa." | CU-STD-001 | Sube todos los documentos requeridos sin abandonar | 15 min · 85% | Hick · Miller — **Crítica** |
| **PU-STD-02** | P4 | "Te pidieron cambios en tu solicitud. Corrígela y reenvía." | CU-STD-002 · 003 | Encuentra qué le pidieron y reenvía | 6 min · 85% | Zeigarnik — Alta |
| **PU-STD-03** | P4 | "Encuentra en el mapa un stand de esquina disponible." | CU-STD-009 · 010 | Distingue disponible de no disponible **sin depender del color** | 5 min · 85% | Color+texto · a11y — **Crítica** |
| **PU-STD-04** | P4 | "Aparta dos stands contiguos y resérvalos." | CU-STD-011 · 012 | Entiende que **el carrito no es reserva** hasta confirmar | 5 min · 85% | Zeigarnik · Peak-end — **Crítica** |
| **PU-STD-05** | P4 | "Dinos cuánto debes y para cuándo." | CU-STD-013 · 017 | Lee total / abonado / pendiente / descuento sin equivocarse | 2 min · 90% | Miller (formateo) — **Crítica** |
| **PU-STD-06** | P4 | "Paga el 50% y registra tu comprobante." | CU-STD-015 · 016 | Encuentra los datos bancarios y sube el comprobante | 6 min · 85% | Jakob · Doherty — **Crítica** |
| **PU-STD-07** | P4 | "Te llegó un aviso de posible cancelación. Resuélvelo." | CU-STD-014 · 025 | Entiende el plazo y **qué acción evita** la cancelación | 4 min · 85% | Zeigarnik · tono — **Crítica** |
| **PU-STD-12** | P5 | "Revisa las solicitudes del día: acepta una, pide cambios a otra, rechaza una tercera." | CU-STD-004 → 008 | No confunde rechazar con pedir cambios; el aplicante recibe el motivo | 8 min · 90% | Fitts · tono — **Crítica** |
| **PU-STD-08** | P5 | "Valida un pago, registra un abono manual y aplica un descuento." | CU-STD-018 · 019 · 020 | Registra el motivo del descuento; no confunde validar con registrar | 8 min · 85% | Hick · trazabilidad — Alta |
| **PU-STD-09** | P5 | "Resuelve dos reservas vencidas: prorroga una, cancela otra." | CU-STD-035 · 036 | No cancela la equivocada; la nueva fecha queda explícita | 6 min · 90% | Fitts — **Crítica** |
| **PU-STD-10** | P5 | "Configura precio por m², plazos y descuento por pronto pago." | CU-STD-034 | Termina sin ambigüedad sobre qué parámetro afecta a qué | 10 min · 80% | Miller — Alta |
| **PU-STD-11** | P5 | "Dinos quién reservó el stand B-14 y cuánto debe." | CU-STD-032 · 028–031 | Llega del mapa al expediente del expositor | 3 min · 85% | Jakob — Alta |

### 5.2 `TAL` — tallerista (P2) y administración (P5)

| ID | Perfil | Tarea que se le pide | CU | Aprueba si… | Objetivo | Ley · Prio |
| --- | --- | --- | --- | --- | --- | --- |
| **PU-TAL-01** | P2 | "Registra tu taller infantil con su público meta y modalidad." | CU-TAL-002 | Completa el formulario y entiende el cupo que ofrece | 10 min · 85% | Hick · Miller — **Crítica** |
| **PU-TAL-02** | P2 | "Revisa el estado de tu propuesta y corrígela si te pidieron cambios." | CU-TAL-003 · 004 | Encuentra el comentario y reenvía | 5 min · 85% | Zeigarnik — Alta |
| **PU-TAL-03** | P5 | "Dictamina las propuestas de talleres del día." | CU-TAL-007 → 009 | Usa los contadores por estado para priorizar | 8 min · 85% | Hick — Alta |
| **PU-TAL-04** | P2 | "Descarga tu constancia." | CU-TAL-005 | La localiza y entiende que en `TAL` es obligatoria | 90 s · 90% | Peak-end — Media |

### 5.3 `PRG` y `SAL` — administración (P5) y público

| ID | Perfil | Tarea que se le pide | CU | Aprueba si… | Objetivo | Ley · Prio |
| --- | --- | --- | --- | --- | --- | --- |
| **PU-PRG-01** | P5 | "Programa esta actividad aceptada en sala y horario." | CU-PRG-002 | Ve el **choque de horario antes de guardar**, no después | 5 min · 85% | Fitts · Doherty — **Crítica** |
| **PU-PRG-02** | P5 | "Mueve una actividad de sala y elimina otra programación." | CU-PRG-003 · 004 | **No cree haber eliminado la actividad** al eliminar su programación | 4 min · 90% | Fitts · tono — **Crítica** |
| **PU-PRG-03** | P5 | "Programa un taller que se repite 4 veces en la semana." | CU-PRG-002 A1 (TAL) | Entiende el bloque de 1:00 y el selector de repetición | 6 min · 80% | Miller — Alta |
| **PU-PRG-04** | P1 · P2 | "Confirma que asistirás al horario que te asignaron." | CU-PRG-008 · 009 | Llega desde el correo y completa la confirmación | 3 min · 90% | Zeigarnik · Peak-end — **Crítica** |
| **PU-PRG-05** | Público | "Encuentra a qué hora es la actividad X, desde tu teléfono." | CU-PRG-010 | La encuentra en móvil sin zoom ni scroll horizontal | 2 min · 90% | Jakob · responsive — Alta |
| **PU-PRG-06** | P5 | "Exporta el programa para revisarlo con tu equipo." | CU-PRG-011 | Obtiene el archivo y sabe qué trae | 90 s · 90% | Doherty — Media |
| **PU-SAL-01** | P5 | "Da de alta el salón Uxmal con sus cuatro salas." | CU-SAL-001 · 004 · 007 | Entiende que el salón **nace con una sala automática** | 6 min · 85% | Hick (CRUD inline) — Alta |
| **PU-SAL-02** | P5 | "Corrige el aforo de una sala a 80 personas y el nombre del salón." | CU-SAL-002 · 005 | Edita la sala correcta sin salir de la pantalla única | 2 min · 90% | Fitts — Alta |
| **PU-SAL-03** | P5 | "Elimina un salón que ya tiene actividades programadas." | CU-SAL-003 · 006 | Entiende **por qué el sistema no lo deja** y qué hacer | 3 min · 90% | Prevención de error — **Crítica** |

---

## 6. Matriz — transversales (T)

Se corren **en cada ronda**, montadas sobre las tareas que ya se están probando. No necesitan
participantes propios salvo donde se indica.

| ID | Perfil | Qué se hace | Cubre | Aprueba si… | Ley · Prio |
| --- | --- | --- | --- | --- | --- |
| **PU-TRV-01** | Todos | Repetir la tarea crítica del perfil **con JavaScript desactivado** | Regla 6 de `CLAUDE.md` | Completa la tarea; ninguna acción queda muerta | Degradación elegante — **Crítica** |
| **PU-TRV-02** | P5 | Imprimir el listado **en blanco y negro** y preguntar el estado de cada fila | CU-EVT-007 · CU-VIS-004 · CU-STD-028 | Lee el estado sin color, a 95% | Color+texto — **Crítica** |
| **PU-TRV-03** | P3 | Correr PU-VIS-01 completa **desde el teléfono** | CU-VIS-001 | Sin scroll horizontal; ningún objetivo de toque bajo 40 px | Fitts · responsive — **Crítica** |
| **PU-TRV-04** | Todos | Recorrer el formulario **solo con teclado**, y con lector de pantalla | CU-REG-001 · CU-EVT-002 · CU-VIS-001 | Foco visible, orden lógico, errores anunciados; contraste AA | WCAG AA — **Crítica** |
| **PU-TRV-05** | Todos | Sin leer el título: "¿en qué módulo y en qué edición estás?" | Transversal | Acierta por el acento de dominio y la barra superior | Acento · Jakob — Alta |
| **PU-TRV-06** | Todos | Observación del moderador: ¿alguna acción se quedó sin respuesta? | Transversal | Toda acción responde <400 ms o muestra indicador; sin doble envío | Doherty — **Crítica** |
| **PU-TRV-07** | Todos | Mostrar un mensaje de error fuera de contexto: "¿qué harías?" | Transversal | Explica la acción correctiva con sus palabras | Tono de UI — Alta |

> [!note] PU-TRV-01 no es una prueba técnica, es una prueba de usuario
> Que la pantalla *funcione* sin JS lo verifica una prueba automática. Lo que mide PU-TRV-01 es
> si **se siente igual de completa**: filtros que ahora exigen un botón "Aplicar", modales que se
> vuelven páginas, confirmaciones que cambian de sitio. El criterio es que la persona termine sin
> notar que está en un modo degradado.

---

## 7. Cobertura y huecos

| Dominio | CU documentados | CU con escenario | Cobertura | Qué queda fuera y por qué |
| --- | --- | --- | --- | --- |
| `REG` | 6 | 5 | 83% | CU-REG-005 está **derogado** por CU-FER-003; CU-REG-006 quedó **reformulado** y se prueba como PU-FER-02 (ver `CU-FER Índice`) |
| `FER` | 10 | 10 | 100% | — |
| `EVT` | 12 | 12 | 100% | — |
| `VIS` | 17 | 16 | 94% | Solo queda fuera CU-VIS-009 (notificar resultado), de actor **Sistema** |
| `TAL` | 10 | 7 | 70% | CU-TAL-001, 006 y 010 son espejo exacto de `EVT`: se prueban una vez, en `EVT` |
| `STD` | 36 | 29 | 81% | Los 6 CU de **Sistema** (021, 022, 023, 024, 026, 027) no tienen interfaz: se verifican por su **efecto** en PU-STD-05/07. CU-STD-033 está marcado *WILL NOT DO* |
| `PRG` | 8 (+8 variantes TAL) | 8 | 100% | CU-PRG-001 no es pantalla propia: vive en el listado que ya prueba PU-EVT-08. Las variantes `(TAL)` se cubren con PU-PRG-03 en vez de duplicar seis escenarios |
| `SAL` | 7 | 7 | 100% | — |

> [!important] Qué NO cubre esta matriz, a propósito
> - **Casos de uso de actor "Sistema"** (notificaciones automáticas, vencimientos, descuento por
>   pronto pago). No tienen interacción que observar; se prueban por su efecto en la pantalla del
>   humano que los recibe — la notificación se evalúa en PU-STD-07 y PU-PRG-04, no por sí sola.
> - **Corrección funcional.** Que el cupo se descuente bien es materia de `pytest`
>   (`apps/<dom>/pruebas/`), no de una sesión con personas. Aquí solo se mide si la persona
>   **entiende** lo que el sistema hizo.
> - **Rendimiento**, salvo el umbral percibido de 400 ms de PU-TRV-06.

---

## 8. Evaluación heurística (paso previo, sin usuarios)

Antes de gastar una sesión con una persona real, dos evaluadores del equipo recorren el flujo con
esta rúbrica. Barata, y saca los problemas de nivel 1–2 que si no se comen el tiempo de la sesión.

| # | Heurística | Comprobación concreta en FILEY |
| --- | --- | --- |
| 1 | Visibilidad del estado | ¿Se ve en qué edición, módulo y paso estoy? ¿Toda acción confirma? |
| 2 | Correspondencia con el mundo real | ¿"Dictaminar" y "convocatoria" sí son palabras del dominio? ¿Aparece jerga interna (`CU-EVT-009`, `en_preparacion`) en pantalla? |
| 3 | Control y libertad | ¿Puedo salir de un formulario largo sin perderlo todo? |
| 4 | Consistencia | ¿Mismo patrón de listado+filtros en `EVT`, `VIS`, `STD`? ¿Tokens del sistema (`./scripts/check-ui.sh` en verde)? |
| 5 | Prevención de errores | ¿El tope de 105 se avisa **antes** de llenar 30 campos? ¿Se puede borrar un salón con actividades? |
| 6 | Reconocer antes que recordar | ¿El folio y el estado están a la vista, o hay que recordarlos del correo? |
| 7 | Flexibilidad | ¿Filtros de uso diario visibles, resto tras "más filtros"? |
| 8 | Diseño minimalista | ¿≤7 opciones simultáneas? ¿≤9 campos por sección? |
| 9 | Recuperación de errores | ¿El mensaje dice qué pasó, por qué y qué hacer, en el tono de la §7 de `filey-identidad`? |
| 10 | Ayuda y documentación | ¿Se puede completar sin abrir el PDF de la convocatoria? |

---

## 9. Cómo se registra un hallazgo

```text
ID:          H-R1-003
Escenario:   PU-FER-07
Participante: P6-02
Severidad:   4 (catastrófico — completó creyendo algo falso)
Qué pasó:    Adelantó la fecha de cierre y dio por cerrada la convocatoria.
             La convocatoria siguió abierta.
Frecuencia:  3 de 5 participantes
CU afectado: CU-FER-008
Ley:         Visibilidad del estado del sistema
Propuesta:   Separar visualmente fechas (informativas) del interruptor de estado,
             y que la pantalla diga "abierta / cerrada" como estado, no como fecha.
```

Al cierre de cada ronda: tabla de hallazgos ordenada por `severidad × frecuencia`, tasas de
éxito por tarea, SUS por perfil, y la decisión explícita de qué se arregla antes de la siguiente
ronda. Los hallazgos de severidad 3 y 4 se enlazan al `CU` que corrigen; si cambian una regla de
negocio, van a un ADR, no a esta matriz.

---

## 10. Pendientes de esta matriz

- **Calibrar los tiempos objetivo** con un piloto de un participante por perfil. Hoy son
  estimaciones derivadas de la complejidad declarada en los `CU-DOM.csv`.
- **Reclutamiento de P3 y P4.** Depende de que FILEY comparta contactos de escuelas y expositores
  de la edición anterior; sin ellos la ronda 2 se corre con participantes sustitutos y el
  resultado vale menos.
- **Datos de prueba.** Ninguna sesión debe usar datos reales de escuelas o de personas. Hace
  falta un `seed` de demo por feria (ya existe la vía: `manage.py alta_feria`).
- **Convocatorias de `FER` (PU-FER-06/07/08)** aún no tienen CRUD construido; esas tres filas
  quedan bloqueadas hasta que exista la pantalla.
- **Definir si `SUS` se aplica también a P5/P6**, que evalúan una herramienta de trabajo diario y
  no un trámite anual: sus puntajes no son comparables con los de P1–P4.

Ver también: [Mapa de etiquetas](<../MAPA-DE-ETIQUETAS.md>) ·
[README de requisitos](<../requisitos/README.md>) · [`PU-Matriz.csv`](<PU-Matriz.csv>)

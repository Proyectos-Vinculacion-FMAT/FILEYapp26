/* =========================================================
   FILEY 2027 — Prototipo: campos dinámicos del formulario de propuesta
   Genera los campos específicos según el tipo de actividad elegido.
   (Sólo demostrativo — no envía datos.)

   Lo que manda aquí es `docs/requisitos/EVT/Modelo de datos - Eventos.md`
   §2.7 y su `erDiagram - Captura de solicitudes.mmd`:

   · Cada persona de una actividad tiene su propio nombre Y su propia
     semblanza (`nombre_participante_N` / `semblanza_participante_N`). La
     semblanza es **texto**, no un PDF adjunto: es contenido, no un anexo.
   · Cuántas personas caben lo dice la tabla del tipo — hay tantas columnas
     `nombre_*_N` como personas admite. De ahí sale `max` en TIPOS.
   · Los `name` de cada campo son los de esas columnas, a propósito: leyendo
     el formulario se ve contra qué se va a guardar.
   · Sí siguen siendo archivos las fotografías y portadas, que son lo único
     que `RouterDocumentos` (§2.8) enruta.
   ========================================================= */

// Topes de captura. La UI los enseña y el `maxlength` los impone; en el
// monolito los repite la validación del formulario de Django.
const MAX = {
  semblanza: 2000,
  sinopsis: 2000,
  sinopsisPub: 4000  // sinopsis de libro o de revista, que piden más espacio
};

/* ---- Texto de ejemplo — SOLO del prototipo --------------------------------
   Existe para recorrer el happy path en una demo sin teclear treinta campos,
   y para que la captura en cascada se vea desbloqueada de entrada en vez de
   obligar a escribir un nombre antes de poder enseñar la semblanza.

   **No existe en Django**: allá el formulario nace vacío, que es lo que tiene
   que ver quien de verdad va a proponer una actividad. Si algún día hace falta
   apagarlo aquí, basta con vaciar este objeto. */
const MUESTRA = {
  titulo: "El mar que nos habita",
  organiza: "Editorial La Nave",
  moderador: "Ana Pech Uc",
  editorial: "Editorial La Nave",
  sinopsis:
    "Una conversación sobre la memoria del puerto de Progreso y sobre cómo el " +
    "mar ordena la vida de quienes viven de él. Se leerán fragmentos de la obra " +
    "y se abrirá una ronda de preguntas con el público.",
  personas: {
    participante: [
      { nombre: "Elena Poniatowska", semblanza: "Escritora y periodista. Premio Cervantes 2013." },
      { nombre: "Juan Villoro", semblanza: "Narrador y cronista. Autor de «El testigo»." }
    ],
    autor: [
      { nombre: "Elena Poniatowska", semblanza: "Escritora y periodista. Premio Cervantes 2013." }
    ],
    editor: [
      { nombre: "Ana Pech Uc", semblanza: "Editora de Cuadernos del Mayab desde 2019." }
    ],
    presentador: [
      { nombre: "Jorge Cortés Ancona", semblanza: "Crítico literario y ensayista yucateco." }
    ]
  }
};

/* La lista de ejemplo se busca por `muestra` y no por `clave` porque en
   libro y revista los presentadores son `participante` en el modelo —esas
   son sus columnas— pero no pueden salir con el nombre del autor. */
function muestraDe(cfg, indice) {
  const lista = MUESTRA.personas[cfg.muestra || cfg.clave] || [];
  return lista[indice - 1] || null;
}

// ---- Bloques reutilizables -------------------------------------------------
const F = {
  text(label, req, hint, valor) {
    return `<div class="field"><label>${label} ${tag(req)} ${hintHtml(hint)}</label>
      <input type="text" placeholder="" value="${valor || ""}"></div>`;
  },
  textarea(label, req, max, name, valor) {
    const tope = max ? ` maxlength="${max}"` : "";
    const pista = max ? `máx. ${max} caracteres` : "";
    const texto = valor || "";
    const contador = max
      ? `<p class="evt-contador"><span data-cuenta>${texto.length}</span> / ${max}</p>`
      : "";
    return `<div class="field"><label>${label} ${tag(req)} ${hintHtml(pista)}</label>
      <textarea rows="5"${tope}${name ? ` name="${name}"` : ""}>${texto}</textarea>${contador}</div>`;
  },
  select(label, req, opts) {
    const o = opts.map(v => `<option>${v}</option>`).join("");
    return `<div class="field"><label>${label} ${tag(req)}</label>
      <select><option value="" disabled selected>Selecciona…</option>${o}</select></div>`;
  },
  /* Una casilla suelta, para una pregunta cuya respuesta por omisión es
     la inofensiva: sin marcar ya es «no», así que no hay nada obligatorio
     que contestar ni asterisco que poner. */
  check(label, name) {
    return `<div class="field">
      <label class="evt-check"><input type="checkbox"${name ? ` name="${name}"` : ""}> ${label}</label>
    </div>`;
  },
  radioSiNo(label, req) {
    return `<div class="field"><label>${label} ${tag(req)}</label>
      <div class="radio-row">
        <label><input type="radio" name="r${rid()}"> Sí</label>
        <label><input type="radio" name="r${rid()}"> No</label>
      </div></div>`;
  },
  /* El control nativo dice «Examinar…» en el idioma del navegador, no en
     el de la página, y no cuenta qué se adjuntó. Se esconde dentro del
     rótulo —sigue recibiendo el foco— y lo que se ve es este bloque, que
     al cargar un archivo se queda en verde con su nombre. */
  file(label, req, hint) {
    return `<div class="field"><label>${label} ${tag(req)} ${hintHtml(hint)}</label>
      <label class="file-mock" data-adjunto>
        <input type="file">
        <div class="ico">📎</div>
        <div class="txt"><strong data-adjunto-nombre>Adjuntar archivo</strong><small>${hint || "Formato permitido"}</small></div>
      </label></div>`;
  },
  aviso(txt) {
    return `<div class="note note-warn"><div class="ico">📦</div>
      <div><strong>Envío de ejemplar físico.</strong> ${txt}</div></div>`;
  },

  /* Lista de personas de la actividad. Arranca con una sola —lo mínimo que
     la actividad exige— y crece de una en una hasta `max`. Ver personaHtml. */
  personas(cfg) {
    return `<div class="field">
      <label>${cfg.etiqueta} ${tag(cfg.req)} ${hintHtml(cfg.hint || `hasta ${cfg.max}`)}</label>
      <div data-personas
           data-clave="${cfg.clave}"
           data-singular="${cfg.singular}"
           data-max="${cfg.max}"
           data-req="${cfg.req ? 1 : 0}"
           data-semblanza="${cfg.semblanza ? 1 : 0}"
           data-participa="${cfg.participa ? 1 : 0}">
        <div data-lista>${personaHtml(cfg, 1)}</div>
        <button type="button" class="evt-agregar" data-agregar disabled>+ Agregar ${cfg.singular.toLowerCase()}</button>
        <p class="evt-bloqueo" data-bloqueo-agregar></p>
        <p class="evt-bloqueo" data-aviso-personas hidden></p>
      </div>
    </div>`;
  }
};

function tag(req) {
  return req ? `<span class="req">*</span>` : `<span class="opt">(opcional)</span>`;
}
function hintHtml(h) { return h ? `<span class="hint">— ${h}</span>` : ""; }
let _rid = 0; function rid() { return ++_rid; }

/* Una persona: su nombre, su semblanza y —solo en libro y revista— la casilla
   de si estará presente en la actividad (`autor_N_participa` /
   `editor_N_participa`). Solo la primera es obligatoria y solo de la segunda
   en adelante se puede quitar. */
function personaHtml(cfg, indice) {
  const obligatoria = cfg.req && indice === 1;
  const ejemplo = muestraDe(cfg, indice);
  const participa = cfg.participa
    ? `<label class="evt-check">
         <input type="checkbox" name="${cfg.clave}_${indice}_participa">
         Participará en la actividad
       </label>`
    : "";
  const quitar = indice > 1
    ? `<button type="button" class="evt-persona__quitar" data-quitar>Quitar</button>`
    : "";
  /* La semblanza no se escribe antes que el nombre: se pinta apagada y con
     un aviso al pie, no solo con el cursor en «prohibido». */
  const textoSemblanza = ejemplo ? ejemplo.semblanza : "";
  const semblanza = cfg.semblanza
    ? `<div class="field" data-semblanza>
         <label>Semblanza ${tag(obligatoria)} <span class="hint">— máx. ${MAX.semblanza} caracteres</span></label>
         <textarea rows="5" maxlength="${MAX.semblanza}" name="semblanza_${cfg.clave}_${indice}">${textoSemblanza}</textarea>
         <p class="evt-contador"><span data-cuenta>${textoSemblanza.length}</span> / ${MAX.semblanza}</p>
         <p class="evt-bloqueo" data-bloqueo>Escribe primero el nombre.</p>
       </div>`
    : "";

  return `<div class="evt-persona" data-persona>
    <div class="evt-persona__head">
      <span class="evt-persona__n" data-numero>${cfg.singular} ${indice}</span>
      ${participa}
      ${quitar}
    </div>
    <div class="field">
      <label>Nombre ${tag(obligatoria)}</label>
      <input type="text" name="nombre_${cfg.clave}_${indice}" value="${ejemplo ? ejemplo.nombre : ""}">
    </div>
    ${semblanza}
  </div>`;
}

/* Lee la configuración de vuelta del DOM, para poder añadir personas después
   de haber pintado la sección. */
function cfgDe(caja) {
  return {
    clave: caja.dataset.clave,
    singular: caja.dataset.singular,
    max: +caja.dataset.max,
    req: caja.dataset.req === "1",
    semblanza: caja.dataset.semblanza === "1",
    participa: caja.dataset.participa === "1"
  };
}

/* Pone o quita el asterisco de obligatorio de un campo, en vivo.

   Suelta porque la usan dos reglas: la semblanza que deja de ser opcional
   en cuanto su nombre tiene algo escrito, y el presentador que hace falta
   cuando nadie de la publicación asiste. */
function marcarObligatorio(campo, obligatorio) {
  if (!campo) return;
  const contenedor = campo.closest(".field");
  const marca = contenedor && contenedor.querySelector("label .req, label .opt");
  if (!marca) return;
  marca.className = obligatorio ? "req" : "opt";
  marca.textContent = obligatorio ? "*" : "(opcional)";
}

/* Tras agregar o quitar, los índices tienen que volver a ser 1..n seguidos:
   son los que nombran las columnas de la tabla del tipo, y un hueco dejaría
   `nombre_autor_3` con `nombre_autor_2` vacío. */
function renumerar(caja) {
  const cfg = cfgDe(caja);
  const personas = caja.querySelectorAll("[data-persona]");
  personas.forEach((persona, i) => {
    const n = i + 1;
    persona.querySelector("[data-numero]").textContent = `${cfg.singular} ${n}`;
    const nombre = persona.querySelector(`input[name^="nombre_${cfg.clave}_"]`);
    if (nombre) nombre.name = `nombre_${cfg.clave}_${n}`;
    const semblanza = persona.querySelector(`textarea[name^="semblanza_${cfg.clave}_"]`);
    if (semblanza) semblanza.name = `semblanza_${cfg.clave}_${n}`;
    const participa = persona.querySelector(`input[name$="_participa"]`);
    if (participa) participa.name = `${cfg.clave}_${n}_participa`;
  });
  actualizarPuerta(caja);
}

/* Captura en cascada: la semblanza se abre cuando su nombre tiene algo escrito,
   y solo se puede agregar a la siguiente persona cuando las que ya están
   quedaron completas. Así no se acumulan bloques a medias, que en el modelo
   serían columnas `nombre_*_N` con hueco.

   Cada bloqueo se ve —campo o botón apagado— y además se explica en texto: un
   control gris sin motivo se lee como una avería, no como un paso pendiente. */
function actualizarPuerta(caja) {
  const cfg = cfgDe(caja);
  const personas = Array.from(caja.querySelectorAll("[data-persona]"));
  let completas = true;

  personas.forEach(persona => {
    const nombre = persona.querySelector('input[type="text"]');
    const conNombre = nombre.value.trim() !== "";
    if (!conNombre) completas = false;

    const bloque = persona.querySelector("[data-semblanza]");
    if (!bloque) return;
    const area = bloque.querySelector("textarea");
    /* No se borra lo ya escrito al vaciar el nombre: se apaga y se conserva. */
    area.disabled = !conNombre;
    bloque.querySelector("[data-bloqueo]").hidden = conNombre;
    /* Y en cuanto hay nombre, su semblanza deja de ser opcional: media
       persona no se puede mandar a un comité. */
    marcarObligatorio(area, conNombre);
    if (area.value.trim() === "") completas = false;
  });

  const boton = caja.querySelector("[data-agregar]");
  const aviso = caja.querySelector("[data-bloqueo-agregar]");
  const lleno = personas.length >= cfg.max;

  boton.hidden = lleno;
  boton.disabled = !completas;
  aviso.hidden = lleno || completas;
  aviso.textContent = cfg.semblanza
    ? "Completa el nombre y la semblanza para agregar el siguiente."
    : "Completa el nombre para agregar el siguiente.";
}

// Selección múltiple: público al que va dirigido
function publicoCheckboxes() {
  const opciones = ["Público en general", "Académico", "Estudiantil", "Infantil", "Familias"];
  const chips = opciones.map(op =>
    `<label class="check-chip">
      <input type="checkbox" name="publico" value="${op.toLowerCase().replace(/ /g,'-')}">
      <span class="chip">${op}</span>
    </label>`
  ).join("");
  return `<div class="field">
    <label>Público al que va dirigido <span class="req">*</span>
      <span class="opt" style="font-weight:400">&nbsp;(puedes elegir más de uno)</span>
    </label>
    <div class="check-chips">${chips}</div>
  </div>`;
}

/* El orden de captura, y es el mismo en Django (`campos_tipo.html`):
   título, moderador, organiza, público, lo propio del tipo, constancia,
   sinopsis, adjuntos, ejemplar físico y comentarios.

   Los adjuntos van al final aunque el diagrama del modelo los sitúe
   antes: adjuntar es lo último que se hace, y así su sitio no cambia de
   un tipo a otro. */
function comunesActividad({ etiqueta, singular, max }) {
  return [
    F.text("Título de la actividad", true, null, MUESTRA.titulo),
    F.text("Moderador/a", false, "uno como máximo", MUESTRA.moderador),
    F.text("Organiza", true, null, MUESTRA.organiza),
    publicoCheckboxes(),
    F.personas({ clave: "participante", etiqueta, singular, max, req: true, semblanza: true }),
    F.check("Necesito constancia de participación"),
    F.textarea("Sinopsis de la actividad", true, MAX.sinopsis, "sinopsis", MUESTRA.sinopsis),
    F.textarea("Comentarios u observaciones", false)
  ].join("");
}

// ---- Definición por tipo ---------------------------------------------------
// El `max` de cada lista sale de cuántas columnas `nombre_*_N` tiene su tabla
// en el modelo de datos (§2.7); no es un número elegido aquí.
const TIPOS = {
  "Conversatorio":  () => comunesActividad({ etiqueta: "Participantes", singular: "Participante", max: 3 }),
  "Mesa redonda":   () => comunesActividad({ etiqueta: "Participantes", singular: "Participante", max: 3 }),
  "Lectura de obra":() => comunesActividad({ etiqueta: "Quién imparte", singular: "Participante", max: 2 }),
  "Encuentro":      () => comunesActividad({ etiqueta: "Quién imparte", singular: "Participante", max: 2 }),
  "Conferencia":    () => comunesActividad({ etiqueta: "Quién imparte", singular: "Participante", max: 2 }),
  "Charla":         () => comunesActividad({ etiqueta: "Quién imparte", singular: "Participante", max: 2 }),

  "Presentación de libro": () => [
    F.text("Título de la actividad", true, null, MUESTRA.titulo),
    F.text("Moderador/a", false, "uno como máximo", MUESTRA.moderador),
    F.text("Organiza", true, null, MUESTRA.organiza),
    publicoCheckboxes(),
    // Lo propio del tipo, en el orden de `Actividad_PresentacionLibro`.
    F.text("Título de la publicación", true, null, MUESTRA.titulo),
    F.select("El proponente es", true, ["Autor/a", "Editor/a", "Antologador/a", "Compilador/a", "Coordinador/a"]),
    F.personas({
      clave: "autor", etiqueta: "Autores", singular: "Autor/a", max: 5,
      req: true, semblanza: true, participa: true,
      hint: "nombre igual a la portada del libro; marca quiénes estarán presentes"
    }),
    F.personas({
      clave: "participante", muestra: "presentador",
      etiqueta: "Presentadores", singular: "Presentador/a", max: 2,
      req: false, semblanza: true
    }),
    F.text("Editorial", true, "si es publicación independiente, anótelo", MUESTRA.editorial),
    F.check("Necesito constancia de participación"),
    F.textarea("Sinopsis del libro", true, MAX.sinopsisPub, "sinopsis", MUESTRA.sinopsis),
    F.file("Fotografía del autor/a en alta resolución", true, "JPG o PNG"),
    F.file("Portada del libro en alta resolución", true, "JPG o PDF"),
    F.aviso("Enviar un ejemplar de la obra a: Oficinas FILEY (Salones 42 y 43), UAA “Elvia Carrillo Puerto-UADY”, Calle 33A x 20, Tanlum, C.P. 97210, Mérida, Yucatán. Atención: Coordinación General de Contenidos."),
    F.textarea("Comentarios u observaciones", false)
  ].join(""),

  "Presentación de revista": () => [
    F.text("Título de la actividad", true, null, MUESTRA.titulo),
    F.text("Moderador/a", false, "uno como máximo", MUESTRA.moderador),
    F.text("Organiza", true, null, MUESTRA.organiza),
    publicoCheckboxes(),
    // Lo propio del tipo, en el orden de `Actividad_PresentacionRevista`.
    F.text("Título de la publicación", true, null, "Cuadernos del Mayab"),
    F.select("El proponente es", true, ["Autor/a", "Editor/a", "Antologador/a", "Compilador/a", "Coordinador/a"]),
    F.personas({
      clave: "editor", etiqueta: "Editores", singular: "Editor/a", max: 2,
      req: true, semblanza: true, participa: true,
      hint: "marca quiénes estarán presentes en la actividad"
    }),
    F.personas({
      clave: "participante", muestra: "presentador",
      etiqueta: "Presentadores", singular: "Presentador/a", max: 2,
      req: false, semblanza: true
    }),
    F.text("Editorial", true, "responsable de la revista", MUESTRA.editorial),
    F.check("Necesito constancia de participación"),
    F.textarea("Sinopsis de la revista", true, MAX.sinopsisPub, "sinopsis", MUESTRA.sinopsis),
    F.file("Portada de la revista en alta resolución", true, "JPG o PDF"),
    F.aviso("Enviar un ejemplar de la revista a: Oficinas FILEY (Salones 42 y 43), UAA “Elvia Carrillo Puerto-UADY”, Calle 33A x 20, Tanlum, C.P. 97210, Mérida, Yucatán. Atención: Coordinación General de Contenidos."),
    F.textarea("Comentarios u observaciones", false)
  ].join("")
};

// ---- Render ----------------------------------------------------------------
document.addEventListener("DOMContentLoaded", () => {
  const grid = document.getElementById("tipo-grid");
  const container = document.getElementById("campos-tipo");
  const section = document.getElementById("section-campos");
  const heading = document.getElementById("tipo-elegido");
  if (!grid) return;

  grid.addEventListener("click", (e) => {
    const btn = e.target.closest(".tipo-opt");
    if (!btn) return;
    grid.querySelectorAll(".tipo-opt").forEach(b => b.classList.remove("is-active"));
    btn.classList.add("is-active");
    const tipo = btn.dataset.tipo;
    _rid = 0;
    container.innerHTML = TIPOS[tipo] ? TIPOS[tipo]() : "";
    container.querySelectorAll("[data-personas]").forEach(renumerar);
    refrescarPresentadores();
    if (heading) heading.textContent = tipo;
    section.style.display = "block";
    section.scrollIntoView({ behavior: "smooth", block: "start" });
  });

  /* Agregar y quitar personas. Delegado en el contenedor porque su contenido
     se vuelve a generar entero cada vez que se cambia de tipo de actividad. */
  container.addEventListener("click", (e) => {
    const agregar = e.target.closest("[data-agregar]");
    if (agregar) {
      const caja = agregar.closest("[data-personas]");
      const cfg = cfgDe(caja);
      const lista = caja.querySelector("[data-lista]");
      if (lista.children.length >= cfg.max) return;
      lista.insertAdjacentHTML("beforeend", personaHtml(cfg, lista.children.length + 1));
      renumerar(caja);
      return;
    }

    const quitar = e.target.closest("[data-quitar]");
    if (quitar) {
      const caja = quitar.closest("[data-personas]");
      quitar.closest("[data-persona]").remove();
      renumerar(caja);
    }
  });

  /* El adjunto cargado se ve: el bloque se queda en verde con el nombre
     del archivo. Es la única confirmación que hay de que entró. */
  container.addEventListener("change", (e) => {
    const campo = e.target;
    if (campo.type !== "file") return;
    const caja = campo.closest("[data-adjunto]");
    if (!caja) return;
    const archivo = campo.files && campo.files[0];
    caja.classList.toggle("is-cargado", !!archivo);
    const rotulo = caja.querySelector("[data-adjunto-nombre]");
    if (rotulo) rotulo.textContent = archivo ? archivo.name : "Adjuntar archivo";
  });

  /* Quién sostiene una presentación: un autor —o editor— que asista, o un
     presentador. Basta con uno de los dos, así que mientras nadie de la
     publicación esté marcado, el primer presentador pasa a ser obligatorio.

     En Django esto vive dos veces —aquí y en `exigir_presentador`— y por
     el mismo motivo: pedirle al servidor que repinte la sección con cada
     clic vaciaría los campos de archivo. */
  function listasDe() {
    const todas = Array.from(container.querySelectorAll("[data-personas]"));
    return {
      publicacion: todas.filter(c => c.querySelector("input[name$=_participa]")),
      presentadores: todas.filter(c => !c.querySelector("input[name$=_participa]"))[0]
    };
  }

  function alguienAsiste(cajas) {
    return cajas.some(caja =>
      Array.from(caja.querySelectorAll("[data-persona]")).some(fila => {
        const casilla = fila.querySelector("input[name$=_participa]");
        const nombre = fila.querySelector('input[type="text"]');
        return casilla && casilla.checked && nombre && nombre.value.trim() !== "";
      })
    );
  }

  function refrescarPresentadores() {
    const listas = listasDe();
    if (!listas.publicacion.length || !listas.presentadores) return;

    const hacenFalta = !alguienAsiste(listas.publicacion);
    const primera = listas.presentadores.querySelector("[data-persona]");
    if (!primera) return;

    marcarObligatorio(primera.querySelector('input[type="text"]'), hacenFalta);
    marcarObligatorio(primera.querySelector("textarea"), hacenFalta);

    const aviso = listas.presentadores.querySelector("[data-aviso-personas]");
    if (aviso) {
      aviso.hidden = !hacenFalta;
      aviso.textContent =
        "Nadie de la publicación está marcado como que asiste, así que hace " +
        "falta al menos un presentador: la actividad no puede quedarse sin " +
        "nadie delante.";
    }
  }

  container.addEventListener("change", refrescarPresentadores);

  container.addEventListener("input", (e) => {
    /* Contador de caracteres de semblanzas y sinopsis. */
    const area = e.target;
    if (area.tagName === "TEXTAREA" && area.maxLength > 0) {
      const contador = area.parentNode.querySelector(".evt-contador");
      if (contador) {
        contador.querySelector("[data-cuenta]").textContent = area.value.length;
        contador.classList.toggle("is-tope", area.value.length >= area.maxLength);
      }
    }

    /* La puerta: escribir el nombre abre su semblanza, y completar las dos
       habilita el botón de agregar. Se revisa al teclear —no al salir del
       campo— porque no es una validación que reprocha, es un candado que se
       abre: el aviso tiene que irse en cuanto deja de ser cierto. */
    const caja = e.target.closest("[data-personas]");
    if (caja) actualizarPuerta(caja);

    /* Y quién sostiene la presentación, que depende del nombre además de
       la casilla. */
    refrescarPresentadores();
  });
});

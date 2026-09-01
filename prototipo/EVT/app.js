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

// ---- Bloques reutilizables -------------------------------------------------
const F = {
  text(label, req, hint) {
    return `<div class="field"><label>${label} ${tag(req)} ${hintHtml(hint)}</label>
      <input type="text" placeholder=""></div>`;
  },
  textarea(label, req, max, name) {
    const tope = max ? ` maxlength="${max}"` : "";
    const pista = max ? `máx. ${max} caracteres` : "";
    const contador = max
      ? `<p class="evt-contador"><span data-cuenta>0</span> / ${max}</p>`
      : "";
    return `<div class="field"><label>${label} ${tag(req)} ${hintHtml(pista)}</label>
      <textarea${tope}${name ? ` name="${name}"` : ""}></textarea>${contador}</div>`;
  },
  select(label, req, opts) {
    const o = opts.map(v => `<option>${v}</option>`).join("");
    return `<div class="field"><label>${label} ${tag(req)}</label>
      <select><option value="" disabled selected>Selecciona…</option>${o}</select></div>`;
  },
  radioSiNo(label, req) {
    return `<div class="field"><label>${label} ${tag(req)}</label>
      <div class="radio-row">
        <label><input type="radio" name="r${rid()}"> Sí</label>
        <label><input type="radio" name="r${rid()}"> No</label>
      </div></div>`;
  },
  file(label, req, hint) {
    return `<div class="field"><label>${label} ${tag(req)} ${hintHtml(hint)}</label>
      <div class="file-mock">
        <div class="ico">📎</div>
        <div class="txt"><strong>Adjuntar archivo</strong><small>${hint || "Formato permitido"}</small></div>
      </div></div>`;
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
  const participa = cfg.participa
    ? `<label class="evt-check">
         <input type="checkbox" name="${cfg.clave}_${indice}_participa" checked>
         Participará en la actividad
       </label>`
    : "";
  const quitar = indice > 1
    ? `<button type="button" class="evt-persona__quitar" data-quitar>Quitar</button>`
    : "";
  /* La semblanza no se escribe antes que el nombre: se pinta apagada y con
     un aviso al pie, no solo con el cursor en «prohibido». */
  const semblanza = cfg.semblanza
    ? `<div class="field" data-semblanza>
         <label>Semblanza ${tag(obligatoria)} <span class="hint">— máx. ${MAX.semblanza} caracteres</span></label>
         <textarea maxlength="${MAX.semblanza}" name="semblanza_${cfg.clave}_${indice}" disabled></textarea>
         <p class="evt-contador"><span data-cuenta>0</span> / ${MAX.semblanza}</p>
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
      <input type="text" name="nombre_${cfg.clave}_${indice}">
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

// Campos comunes al final de casi todos los tipos
function comunesActividad({ etiqueta, singular, max }) {
  return [
    F.text("Título de la actividad", true),
    F.personas({ clave: "participante", etiqueta, singular, max, req: true, semblanza: true }),
    F.text("Moderador/a", false, "uno como máximo"),
    F.text("Organiza", true),
    publicoCheckboxes(),
    F.radioSiNo("¿Requiere constancia de participación?", true),
    F.textarea("Sinopsis de la actividad", true, MAX.sinopsis, "sinopsis"),
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
    F.text("Título de la actividad", true),
    F.text("Organiza", true),
    F.text("Título de la publicación", true),
    F.select("El proponente es", true, ["Autor/a", "Editor/a", "Antologador/a", "Compilador/a", "Coordinador/a"]),
    F.personas({
      clave: "autor", etiqueta: "Autores", singular: "Autor/a", max: 5,
      req: true, semblanza: true, participa: true,
      hint: "nombre igual a la portada del libro; marca quiénes estarán presentes"
    }),
    F.personas({
      clave: "participante", etiqueta: "Presentadores", singular: "Presentador/a", max: 2,
      req: false, semblanza: true
    }),
    F.text("Moderador/a", false, "uno como máximo"),
    F.text("Editorial", true, "si es publicación independiente, anótelo"),
    publicoCheckboxes(),
    F.radioSiNo("¿Requiere constancia de participación?", true),
    F.textarea("Sinopsis del libro", true, MAX.sinopsisPub, "sinopsis"),
    F.file("Fotografía del autor/a en alta resolución", true, "JPG o PNG"),
    F.file("Portada del libro en alta resolución", true, "JPG o PDF"),
    F.aviso("Enviar un ejemplar de la obra a: Oficinas FILEY (Salones 42 y 43), UAA “Elvia Carrillo Puerto-UADY”, Calle 33A x 20, Tanlum, C.P. 97210, Mérida, Yucatán. Atención: Coordinación General de Contenidos."),
    F.textarea("Comentarios u observaciones", false)
  ].join(""),

  "Presentación de revista": () => [
    F.text("Título de la actividad", true),
    F.text("Organiza", true),
    F.text("Título de la publicación", true),
    F.select("El proponente es", true, ["Autor/a", "Editor/a", "Antologador/a", "Compilador/a", "Coordinador/a"]),
    F.personas({
      clave: "editor", etiqueta: "Editores", singular: "Editor/a", max: 2,
      req: true, semblanza: true, participa: true,
      hint: "marca quiénes estarán presentes en la actividad"
    }),
    F.personas({
      clave: "participante", etiqueta: "Presentadores", singular: "Presentador/a", max: 2,
      req: false, semblanza: true
    }),
    F.text("Moderador/a", false, "uno como máximo"),
    F.text("Editorial", true, "responsable de la revista"),
    publicoCheckboxes(),
    F.radioSiNo("¿Requiere constancia de participación?", true),
    F.textarea("Sinopsis de la revista", true, MAX.sinopsisPub, "sinopsis"),
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

    /* Y la puerta: escribir el nombre abre su semblanza, y completar las dos
       habilita el botón de agregar. Se revisa al teclear —no al salir del
       campo— porque no es una validación que reprocha, es un candado que se
       abre: el aviso tiene que irse en cuanto deja de ser cierto. */
    const caja = e.target.closest("[data-personas]");
    if (caja) actualizarPuerta(caja);
  });
});

/* =========================================================
   FILEY 2027 — Prototipo: campos dinámicos del formulario de propuesta
   Genera los campos específicos según el tipo de actividad elegido.
   (Sólo demostrativo — no envía datos.)
   ========================================================= */

// ---- Bloques reutilizables -------------------------------------------------
const F = {
  text(label, req, hint) {
    return `<div class="field"><label>${label} ${tag(req)} ${hintHtml(hint)}</label>
      <input type="text" placeholder=""></div>`;
  },
  multi(label, n, req, hint) {
    let rows = "";
    for (let i = 1; i <= n; i++) rows += `<input type="text" placeholder="Nombre ${i}">`;
    return `<div class="field"><label>${label} ${tag(req)} ${hintHtml(hint || `máx. ${n}`)}</label>
      <div class="multi-input">${rows}</div></div>`;
  },
  textarea(label, req, hint) {
    return `<div class="field"><label>${label} ${tag(req)} ${hintHtml(hint)}</label>
      <textarea placeholder=""></textarea></div>`;
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
  }
};

function tag(req) {
  return req ? `<span class="req">*</span>` : `<span class="opt">(opcional)</span>`;
}
function hintHtml(h) { return h ? `<span class="hint">— ${h}</span>` : ""; }
let _rid = 0; function rid() { return ++_rid; }

// Campos comunes al final de casi todos los tipos
function comunesActividad({ participantesLabel, participantesN, participantesReq, sinopsisPalabras = 500 }) {
  return [
    F.text("Título de la actividad", true),
    F.multi(participantesLabel, participantesN, participantesReq),
    F.multi("Moderador/a", 1, false, "máx. 1, opcional"),
    F.text("Organiza", true),
    F.text("Público al que va dirigido", true),
    F.radioSiNo("¿Requiere constancia de participación?", true),
    F.file("Semblanzas de los participantes (PDF)", true, "máx. 500 palabras por participante"),
    F.file("Sinopsis de la actividad (PDF)", true, `máx. ${sinopsisPalabras} palabras`),
    F.textarea("Comentarios u observaciones", false)
  ].join("");
}

// ---- Definición por tipo ---------------------------------------------------
const TIPOS = {
  "Conversatorio": () => comunesActividad({ participantesLabel: "Nombre de los participantes", participantesN: 3, participantesReq: false }),
  "Mesa redonda": () => comunesActividad({ participantesLabel: "Nombre de los participantes", participantesN: 3, participantesReq: true }),
  "Lectura de obra": () => comunesActividad({ participantesLabel: "Nombre de los participantes", participantesN: 3, participantesReq: false }),
  "Encuentro": () => comunesActividad({ participantesLabel: "Nombre de los participantes", participantesN: 3, participantesReq: false }),
  "Conferencia": () => comunesActividad({ participantesLabel: "Nombre de quien imparte", participantesN: 2, participantesReq: true }),
  "Charla": () => comunesActividad({ participantesLabel: "Nombre de quien imparte", participantesN: 2, participantesReq: true }),

  "Presentación de libro": () => [
    F.text("Título de la publicación", true),
    F.select("El proponente es", true, ["Autor/a", "Editor/a", "Antologador/a", "Compilador/a", "Coordinador/a"]),
    F.multi("Nombre(s) igual a la portada del libro", 5, true),
    F.radioSiNo("¿El autor participará en la actividad?", true),
    F.text("Si no todos participan, nombres de quienes sí estarán presentes", false, "condicional"),
    F.multi("Nombre de los presentadores", 2, false, "máx. 2, opcional"),
    F.multi("Moderador/a", 1, false, "máx. 1, opcional"),
    F.text("Editorial", true, "si es publicación independiente, anótelo"),
    F.text("Público al que va dirigido", true),
    F.radioSiNo("¿Requiere constancia de participación?", true),
    F.file("Semblanza del autor/a (PDF)", true, "máx. 500 palabras c/u"),
    F.file("Sinopsis del libro (PDF)", true, "máx. 800 palabras"),
    F.file("Fotografía del autor/a en alta resolución", true, "JPG o PNG"),
    F.file("Portada del libro en alta resolución", true, "JPG o PDF"),
    F.aviso("Enviar un ejemplar de la obra a: Oficinas FILEY (Salones 42 y 43), UAA “Elvia Carrillo Puerto-UADY”, Calle 33A x 20, Tanlum, C.P. 97210, Mérida, Yucatán. Atención: Coordinación General de Contenidos."),
    F.textarea("Comentarios u observaciones", false)
  ].join(""),

  "Presentación de revista": () => [
    F.text("Título de la publicación", true),
    F.multi("Nombre del editor/a", 2, true),
    F.radioSiNo("¿El editor/a participará en la actividad?", true),
    F.text("Si no todos participan, nombres de quienes sí estarán presentes", false, "condicional"),
    F.multi("Nombre de los presentadores", 2, false, "máx. 2, opcional"),
    F.multi("Moderador/a", 1, false, "máx. 1, opcional"),
    F.text("Organiza", true),
    F.text("Público al que va dirigido", true),
    F.radioSiNo("¿Requiere constancia de participación?", true),
    F.file("Semblanza del editor/a (PDF)", true, "máx. 500 palabras c/u"),
    F.file("Sinopsis de la revista (PDF)", true, "máx. 800 palabras"),
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
    if (heading) heading.textContent = tipo;
    section.style.display = "block";
    section.scrollIntoView({ behavior: "smooth", block: "start" });
  });
});

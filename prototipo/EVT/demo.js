/* =========================================================
   FILEY 2027 — Prototipo EVT · Motor de demostración
   ---------------------------------------------------------
   Da continuidad al flujo de la presentación usando el ejemplo
   "El mar que nos habita" (folio EVE-2027-0042). El estado se
   guarda en localStorage para que el hilo se mantenga al pasar
   de una pantalla a otra (proponente ↔ administrador):

     · Proponente envía la propuesta  → aparece en "Mis propuestas".
     · Admin la revisa y la ACEPTA    → cambia de estado en ambos lados.
     · Admin la coloca en el horario  → queda programada.

   Es solo demostrativo (no hay backend). Incluye toasts y un
   botón flotante "Reiniciar demo" para volver a correr el guion.
   ========================================================= */
(function () {
  "use strict";

  var KEY = "filey_evt_demo_v1";

  var DEFAULT = {
    // "El mar que nos habita" — EVE-2027-0042 (Editorial La Nave)
    emqnhEnviada: false,     // el proponente ya envió la propuesta
    emqnhEstado: "pendiente", // pendiente | aceptada
    emqnhProgramada: false,   // colocada en el tablero de horario
    emqnhHorario: null,       // { dia, bloque, sala }
    ejemplarRecibido: false,  // control interno del admin
    loteNotificado: false     // se envió el lote de resultados
  };

  function read() {
    try {
      var raw = localStorage.getItem(KEY);
      if (!raw) return Object.assign({}, DEFAULT);
      return Object.assign({}, DEFAULT, JSON.parse(raw));
    } catch (e) {
      return Object.assign({}, DEFAULT);
    }
  }

  function write(state) {
    try { localStorage.setItem(KEY, JSON.stringify(state)); } catch (e) {}
  }

  var FileyDemo = {
    get: function () { return read(); },
    set: function (patch) {
      var s = read();
      Object.assign(s, patch || {});
      write(s);
      return s;
    },
    reset: function () {
      try { localStorage.removeItem(KEY); } catch (e) {}
    },

    /* ---- Atajos del guion ---- */
    enviarPropuesta: function () {
      this.set({ emqnhEnviada: true, emqnhEstado: "pendiente" });
    },
    aceptarPropuesta: function () {
      this.set({ emqnhEnviada: true, emqnhEstado: "aceptada" });
    },
    programar: function (horario) {
      this.set({ emqnhProgramada: true, emqnhHorario: horario || null });
    },

    /* ---- Toast ---- */
    toast: function (msg, type) {
      injectStyles();
      var host = document.getElementById("filey-toast-host");
      if (!host) {
        host = document.createElement("div");
        host.id = "filey-toast-host";
        document.body.appendChild(host);
      }
      var t = document.createElement("div");
      t.className = "filey-toast" + (type ? " is-" + type : "");
      t.innerHTML = '<span class="ic">' + (type === "ok" ? "✓" : type === "warn" ? "⚠️" : "ℹ️") +
        "</span><span>" + msg + "</span>";
      host.appendChild(t);
      // forzar transición
      requestAnimationFrame(function () { t.classList.add("show"); });
      setTimeout(function () {
        t.classList.remove("show");
        setTimeout(function () { if (t.parentNode) t.parentNode.removeChild(t); }, 300);
      }, 3200);
    }
  };

  /* ---- Estilos inyectados (toast + botón reiniciar) ---- */
  function injectStyles() {
    if (document.getElementById("filey-demo-css")) return;
    var css = document.createElement("style");
    css.id = "filey-demo-css";
    css.textContent = [
      "#filey-toast-host{position:fixed;right:18px;bottom:18px;z-index:9999;display:flex;flex-direction:column;gap:10px;max-width:min(92vw,380px)}",
      ".filey-toast{display:flex;align-items:flex-start;gap:10px;background:var(--color-azul-institucional,#01457C);color:#fff;",
      "padding:12px 15px;border-radius:10px;box-shadow:0 18px 50px rgba(16,36,64,.28);font-size:14px;line-height:1.35;",
      "font-family:var(--font-filey,sans-serif);opacity:0;transform:translateY(12px);transition:opacity .25s ease,transform .25s ease}",
      ".filey-toast.show{opacity:1;transform:translateY(0)}",
      ".filey-toast.is-ok{background:var(--ok-600,#1d8a4e)}",
      ".filey-toast.is-warn{background:var(--warn-600,#b8860b)}",
      ".filey-toast .ic{font-size:15px;line-height:1.35}",
      "#filey-demo-reset{position:fixed;left:14px;bottom:14px;z-index:9998;display:inline-flex;align-items:center;gap:7px;",
      "background:rgba(255,255,255,.92);color:#6b7686;border:1px solid #e2e7ee;border-radius:999px;padding:6px 13px;",
      "font-size:12.5px;font-weight:600;font-family:var(--font-filey,sans-serif);cursor:pointer;box-shadow:0 4px 14px rgba(16,36,64,.12);",
      "backdrop-filter:saturate(1.2) blur(2px);transition:all .15s ease}",
      "#filey-demo-reset:hover{color:#01457C;border-color:#c8d0db;box-shadow:0 6px 18px rgba(16,36,64,.18)}",
      "#filey-demo-reset .dot{width:7px;height:7px;border-radius:50%;background:#c99213;display:inline-block}"
    ].join("");
    document.head.appendChild(css);
  }

  /* ---- Botón flotante para reiniciar el guion de la demo ---- */
  function injectReset() {
    if (document.getElementById("filey-demo-reset")) return;
    var b = document.createElement("button");
    b.id = "filey-demo-reset";
    b.type = "button";
    b.title = "Vuelve el prototipo al inicio del guion (El mar que nos habita)";
    b.innerHTML = '<span class="dot"></span> Reiniciar demo';
    b.addEventListener("click", function () {
      FileyDemo.reset();
      FileyDemo.toast("Demo reiniciada. El guion vuelve al inicio.", "ok");
      setTimeout(function () { location.reload(); }, 650);
    });
    document.body.appendChild(b);
  }

  window.FileyDemo = FileyDemo;

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", function () { injectStyles(); injectReset(); });
  } else {
    injectStyles(); injectReset();
  }
})();

/* =========================================================
   FILEY 2027 — Pseudo-backend para VIS (Visitas escolares)
   JSON como "base de datos", persistido en localStorage.

   - Semilla de fábrica: archivos en common/db/VIS/semillas/ (nunca se mutan).
   - Al primer uso se copian a localStorage (el estado "temporal" de la demo).
   - Todas las lecturas/escrituras de la sesión van contra esa copia.
   - FileyDB.reset() vuelve a copiar la semilla — reinicia la demo.

   Se carga con <script src=".../common/db.js"> ANTES de app.js. Como usa
   fetch(), las páginas deben servirse por HTTP (scripts/preview-vis.sh o
   GitHub Pages); abrir por file:// falla por CORS.
   ========================================================= */
(function () {
  'use strict';

  var STORAGE_KEY = 'filey_vis_v2'; // v2: agrega config de convocatoria + demanda por día

  // Base de los archivos semilla, relativa a la ubicación de este db.js
  // (no a la página que lo incluye), para que funcione desde aplicantes/ y
  // administradores/ por igual.
  var DB_BASE = new URL('db/VIS/semillas/', document.currentScript.src);
  // Base de los assets SVG compartidos (common/assets/), también relativa a db.js.
  var ASSETS_BASE = new URL('assets/', document.currentScript.src);

  // Íconos SVG que se inyectan inline en el markup (nombre → archivo). Se cargan del
  // archivo en cada carga de página, así editar el .svg se refleja al refrescar
  // (no se cachean en localStorage). El color y tamaño los controla CSS vía
  // fill="currentColor" — ver .vis-icon-btn / .vis-dia-btn / .vis-tabla__toggle-icon.
  //
  // Política: todo ícono-glifo de VIS (recoloreable, escalable) vive como archivo en
  // common/assets/ y se inyecta inline vía FileyDB.icon(name) o [data-vis-icon] (app.js).
  // Quedan fuera: el logotipo (marca multicolor, <img>), el favicon (<link rel=icon>) y
  // el caret del select (pseudo-elemento ::after — usa --caret-svg como mask, no inline).
  var ICON_FILES = {
    'close': 'close.svg',
    'caret': 'caret.svg',
    'prev-day': 'prev-day.svg',
    'next-day': 'next-day.svg'
  };

  // vis-2027-001 (Benito Juárez, la escuela aplicante) NO se siembra: hasta que el
  // aplicante guarda su registro por primera vez, no existe en el pseudo-backend (así
  // "Ver convocatoria" / "Ver mi registro" y el panel admin reflejan un registro nuevo).
  var ESCUELA_IDS = ['vis-2027-008', 'vis-2027-046'];
  var CATALOGO_FECHA = '2027-03-14';
  var DEMANDA_FILE = 'demanda-por-dia.json';
  var APLICANTE_ID = 'vis-2027-001'; // única escuela visible del lado aplicante

  // Config por defecto de la convocatoria de visitas (fechas para recibir propuestas).
  function defaultConfig() {
    return { convocatoria_inicio: '2027-07-01', convocatoria_fin: '2027-08-31', convocatoria_abierta: true };
  }

  // Categoría de nivel (para agrupar cupos por nivel educativo en el dashboard).
  var CATEGORIA_NIVEL = { pe: 'Preescolar', pa: 'Primaria', pb: 'Primaria', se: 'Secundaria', pr: 'Preparatoria', un: 'Universidad' };

  // Metadatos de nivel educativo (etiqueta + clase de color del prototipo).
  var NIVELES = {
    pe: { label: 'Preescolar',    cls: 'vis-nivel--preescolar' },
    pa: { label: 'Primaria Alta', cls: 'vis-nivel--primaria-alta' },
    pb: { label: 'Primaria Baja', cls: 'vis-nivel--primaria-baja' },
    se: { label: 'Secundaria',    cls: 'vis-nivel--secundaria' },
    pr: { label: 'Preparatoria',  cls: 'vis-nivel--preparatoria' },
    un: { label: 'Universidad',   cls: 'vis-nivel--universidad' }
  };

  // Catálogo de grados por nivel educativo (para el select del formulario).
  // Universidad y Multigrado no tienen catálogo fijo → campo de texto libre.
  var GRADOS_POR_NIVEL = {
    'Preescolar':   ['1°', '2°', '3°'],
    'Primaria':     ['1°', '2°', '3°', '4°', '5°', '6°'],
    'Secundaria':   ['1°', '2°', '3°'],
    'Preparatoria': ['1°', '2°', '3°']
  };

  // Grado (texto) → sub-nivel primaria (pa/pb). Cubre palabras y símbolos.
  var GRADO_MAP = {
    'primero': 'pb', '1ro': 'pb', '1': 'pb', '1°': 'pb',
    'segundo': 'pb', '2do': 'pb', '2': 'pb', '2°': 'pb',
    'tercero': 'pb', '3ro': 'pb', '3': 'pb', '3°': 'pb',
    'cuarto':  'pa', '4to': 'pa', '4': 'pa', '4°': 'pa',
    'quinto':  'pa', '5to': 'pa', '5': 'pa', '5°': 'pa',
    'sexto':   'pa', '6to': 'pa', '6': 'pa', '6°': 'pa'
  };

  // Nivel educativo de la escuela → código de nivel del catálogo.
  var NIVEL_ESCUELA = {
    'Preescolar': 'pe', 'Secundaria': 'se', 'Preparatoria': 'pr', 'Universidad': 'un'
    // 'Primaria' se resuelve por grado (pa/pb); 'Multigrado' → sin restricción.
  };

  // ---------- estado en memoria ----------
  var store = null;       // { escuelas: [...], catalogo: {...}, seq: N }
  var icons = {};         // nombre → markup SVG normalizado (en memoria, sin cachear)
  var readyPromise = null;
  var iconsPromise = null;

  function jsonFetch(url) {
    return fetch(url, { cache: 'no-store' }).then(function (r) {
      if (!r.ok) throw new Error('No se pudo cargar ' + url + ' (' + r.status + ')');
      return r.json();
    });
  }

  function textFetch(url) {
    return fetch(url, { cache: 'no-store' }).then(function (r) {
      if (!r.ok) throw new Error('No se pudo cargar ' + url + ' (' + r.status + ')');
      return r.text();
    });
  }

  // Normaliza un SVG para inyectarlo inline y que CSS controle color/tamaño:
  // quita width/height del <svg>, mapea negros a currentColor y garantiza fill en el root.
  function normalizeIcon(svg) {
    svg = svg.replace(/<\?xml[\s\S]*?\?>/i, '').trim();
    svg = svg.replace(/(fill|stroke)="(#000000|#000|black)"/gi, '$1="currentColor"');
    svg = svg.replace(/(<svg\b[^>]*?)\s+width="[^"]*"/i, '$1')
             .replace(/(<svg\b[^>]*?)\s+height="[^"]*"/i, '$1');
    if (!/<svg\b[^>]*\bfill=/i.test(svg)) svg = svg.replace(/<svg\b/i, '<svg fill="currentColor"');
    return svg;
  }

  // Carga los íconos SVG (siempre fresco, sin localStorage) para que editar el
  // archivo se vea al refrescar. Memoizado por carga de página.
  function loadIcons() {
    if (iconsPromise) return iconsPromise;
    var names = Object.keys(ICON_FILES);
    iconsPromise = Promise.all(names.map(function (name) {
      return textFetch(new URL(ICON_FILES[name], ASSETS_BASE))
        .then(function (svg) { icons[name] = normalizeIcon(svg); });
    })).then(function () { return icons; });
    return iconsPromise;
  }

  // Descarga los 4 archivos semilla y arma el objeto de la "base de datos".
  function fetchSeed() {
    var escuelaUrls = ESCUELA_IDS.map(function (id) {
      return jsonFetch(new URL('escuelas/' + id + '.json', DB_BASE));
    });
    var catalogoUrl = jsonFetch(new URL('talleres/' + CATALOGO_FECHA + '.json', DB_BASE));
    var demandaUrl = jsonFetch(new URL(DEMANDA_FILE, DB_BASE));
    return Promise.all([Promise.all(escuelaUrls), catalogoUrl, demandaUrl]).then(function (res) {
      return {
        escuelas: res[0],
        catalogo: indexCatalogo(res[1]),
        demanda: (res[2] && res[2].dias) || [],
        config: defaultConfig(),
        seq: 100
      };
    });
  }

  // Aplana el grid del catálogo en un mapa id → taller (con turno/sala/horario).
  function indexCatalogo(cat) {
    var byId = {};
    ['matutino', 'vespertino'].forEach(function (turno) {
      (cat.grid[turno] || []).forEach(function (fila, salaIdx) {
        fila.forEach(function (celda, colIdx) {
          if (!celda.id) return;
          byId[celda.id] = {
            id: celda.id,
            tipo: celda.tipo,
            titulo: celda.titulo || 'Zona de acceso libre',
            nivel: celda.nivel || null,
            base: typeof celda.base === 'number' ? celda.base : -1,
            turno: turno,
            sala: cat.salas[salaIdx],
            horario: cat.horarios[turno][colIdx]
          };
        });
      });
    });
    cat.byId = byId;
    return cat;
  }

  function persist() {
    localStorage.setItem(STORAGE_KEY, JSON.stringify(store));
  }

  function clone(obj) { return JSON.parse(JSON.stringify(obj)); }

  // ---------- ciclo de vida ----------
  function load() {
    if (readyPromise) return readyPromise;

    // ?reset=1 fuerza re-siembra desde los archivos de fábrica.
    var forceReset = new URLSearchParams(location.search).get('reset') === '1';
    var cached = forceReset ? null : localStorage.getItem(STORAGE_KEY);

    if (cached) {
      try {
        store = JSON.parse(cached);
        readyPromise = Promise.resolve(store);
        return readyPromise;
      } catch (e) { /* corrupto → re-sembrar */ }
    }

    readyPromise = fetchSeed().then(function (seed) {
      store = seed;
      persist();
      return store;
    });
    return readyPromise;
  }

  function reset() {
    localStorage.removeItem(STORAGE_KEY);
    readyPromise = null;
    return load();
  }

  // ready() resuelve cuando la semilla (datos) Y los íconos están listos, para que
  // las páginas puedan renderizar botones con íconos de forma síncrona.
  function ready() { return Promise.all([load(), loadIcons()]).then(function () { return store; }); }

  // ---------- escuelas ----------
  function listEscuelas() {
    return clone(store.escuelas).sort(function (a, b) {
      return a.folio.localeCompare(b.folio, 'es', { numeric: true });
    });
  }

  function getEscuela(id) {
    var e = store.escuelas.find(function (x) { return x.id === id; });
    return e ? clone(e) : null;
  }

  // Reemplaza el registro completo de una escuela (incluye grupos + reservas).
  function saveEscuela(escuela) {
    var i = store.escuelas.findIndex(function (x) { return x.id === escuela.id; });
    if (i === -1) store.escuelas.push(clone(escuela));
    else store.escuelas[i] = clone(escuela);
    persist();
    return getEscuela(escuela.id);
  }

  function updateEscuela(id, patch) {
    var e = store.escuelas.find(function (x) { return x.id === id; });
    if (!e) return null;
    Object.keys(patch).forEach(function (k) { e[k] = patch[k]; });
    persist();
    return getEscuela(id);
  }

  function insertEscuela(obj) {
    store.seq += 1;
    var num = String(store.seq).padStart(3, '0');
    var nueva = Object.assign({
      id: 'vis-2027-' + num,
      folio: 'VIS-2027-' + num,
      reservas: []
    }, obj);
    store.escuelas.push(clone(nueva));
    persist();
    return getEscuela(nueva.id);
  }

  // ---------- reservas (embebidas en cada escuela) ----------
  // Cupo tomado de un taller = suma de cantidad_alumnos de TODAS las escuelas.
  function cupoTomado(tallerId, exceptoEscuelaId) {
    var t = store.catalogo.byId[tallerId];
    if (t && (t.tipo === 'libre' || t.base < 0)) return 0;
    var total = 0;
    store.escuelas.forEach(function (e) {
      if (exceptoEscuelaId && e.id === exceptoEscuelaId) return;
      (e.reservas || []).forEach(function (r) {
        if (r.taller_id === tallerId) total += (r.cantidad_alumnos || 0);
      });
    });
    return total;
  }

  function _escuela(id) {
    return store.escuelas.find(function (x) { return x.id === id; });
  }

  function addReserva(escuelaId, reserva) {
    var e = _escuela(escuelaId);
    if (!e) return null;
    if (!e.reservas) e.reservas = [];
    store.seq += 1;
    reserva.id = reserva.id || ('r-' + store.seq);
    reserva.fecha_reserva = reserva.fecha_reserva || new Date().toISOString().slice(0, 10);
    e.reservas.push(reserva);
    persist();
    return clone(reserva);
  }

  function removeReserva(escuelaId, predicate) {
    var e = _escuela(escuelaId);
    if (!e || !e.reservas) return;
    e.reservas = e.reservas.filter(function (r) { return !predicate(r); });
    persist();
  }

  // ---------- helpers de dominio ----------
  // Código visible del grupo (G1, G2…) según su orden dentro de la escuela.
  function grupoCodigo(escuela, grupoId) {
    var idx = (escuela.grupos || []).findIndex(function (g) { return g.id === grupoId; });
    return idx === -1 ? '?' : 'G' + (idx + 1);
  }

  function grupoPorCodigo(escuela, codigo) {
    var idx = parseInt(String(codigo).replace(/\D/g, ''), 10) - 1;
    return (escuela.grupos || [])[idx] || null;
  }

  // Código de nivel (pa/pb/se/pr/un/pe) de un grupo, para validar compatibilidad.
  function nivelDeGrupo(escuela, grupo) {
    if (escuela.nivel_educativo === 'Primaria') {
      return GRADO_MAP[String(grupo.grado || '').trim().toLowerCase()] || 'pa';
    }
    return NIVEL_ESCUELA[escuela.nivel_educativo] || null; // Multigrado → null (sin restricción)
  }

  function gradosPorNivel(nivel) {
    return GRADOS_POR_NIVEL[nivel] || null; // null → texto libre
  }

  function currentEscuelaId() {
    var qid = new URLSearchParams(location.search).get('id');
    if (qid && store.escuelas.some(function (e) { return e.id === qid; })) return qid;
    return APLICANTE_ID;
  }

  // ---------- configuración de la convocatoria ----------
  function getConfig() { return clone(store.config || defaultConfig()); }
  function saveConfig(patch) {
    store.config = Object.assign(defaultConfig(), store.config, patch);
    persist();
    return getConfig();
  }

  // ---------- agregados para el dashboard (Seguimiento) ----------
  // Reservado vs. total de cupos finitos (excluye zonas de acceso libre).
  function resumenCupos() {
    var cat = store.catalogo, total = 0, reservado = 0;
    Object.keys(cat.byId).forEach(function (id) {
      var t = cat.byId[id];
      if (t.tipo === 'libre' || t.base < 0) return;
      total += t.base;
    });
    store.escuelas.forEach(function (e) {
      (e.reservas || []).forEach(function (r) {
        var t = cat.byId[r.taller_id];
        if (t && t.tipo !== 'libre' && t.base >= 0) reservado += (r.cantidad_alumnos || 0);
      });
    });
    return { reservado: reservado, total: total, pct: total ? Math.round(reservado / total * 100) : 0 };
  }

  // Cupos reservados por categoría de nivel, como % del total de esa categoría.
  function cuposPorNivel() {
    var cat = store.catalogo, acc = {};
    Object.keys(cat.byId).forEach(function (id) {
      var t = cat.byId[id];
      if (t.tipo === 'libre' || t.base < 0 || !t.nivel) return;
      var c = CATEGORIA_NIVEL[t.nivel] || t.nivel;
      (acc[c] = acc[c] || { categoria: c, nivel: t.nivel, reservado: 0, total: 0 }).total += t.base;
    });
    store.escuelas.forEach(function (e) {
      (e.reservas || []).forEach(function (r) {
        var t = cat.byId[r.taller_id];
        if (!t || t.tipo === 'libre' || !t.nivel) return;
        var c = CATEGORIA_NIVEL[t.nivel] || t.nivel;
        if (acc[c]) acc[c].reservado += (r.cantidad_alumnos || 0);
      });
    });
    return Object.keys(acc).map(function (k) {
      var a = acc[k]; a.pct = a.total ? Math.round(a.reservado / a.total * 100) : 0; return a;
    });
  }

  function demandaPorDia() { return clone(store.demanda || []); }
  function diaMayorDemanda() {
    return (store.demanda || []).reduce(function (max, d) {
      return (!max || d.reservaciones > max.reservaciones) ? d : max;
    }, null);
  }

  // Escuelas con reserva en un taller (para el grid de asistencia del dashboard).
  function escuelasEnTaller(tallerId) {
    return store.escuelas.filter(function (e) {
      return (e.reservas || []).some(function (r) { return r.taller_id === tallerId; });
    }).map(function (e) { return { id: e.id, folio: e.folio, nombre: (e.institucion || {}).nombre }; });
  }

  // ---------- API pública ----------
  window.FileyDB = {
    ready: ready,
    reset: reset,
    listEscuelas: listEscuelas,
    getEscuela: getEscuela,
    saveEscuela: saveEscuela,
    updateEscuela: updateEscuela,
    insertEscuela: insertEscuela,
    getCatalogo: function () { return store.catalogo; },
    cupoTomado: cupoTomado,
    addReserva: addReserva,
    removeReserva: removeReserva,
    grupoCodigo: grupoCodigo,
    grupoPorCodigo: grupoPorCodigo,
    nivelDeGrupo: nivelDeGrupo,
    gradosPorNivel: gradosPorNivel,
    currentEscuelaId: currentEscuelaId,
    icon: function (name) { return icons[name] || ''; },
    getConfig: getConfig,
    saveConfig: saveConfig,
    resumenCupos: resumenCupos,
    cuposPorNivel: cuposPorNivel,
    demandaPorDia: demandaPorDia,
    diaMayorDemanda: diaMayorDemanda,
    escuelasEnTaller: escuelasEnTaller,
    NIVELES: NIVELES,
    APLICANTE_ID: APLICANTE_ID
  };

  // Arranca la carga (datos + íconos) cuanto antes; las páginas esperan con FileyDB.ready().
  load();
  loadIcons();
})();

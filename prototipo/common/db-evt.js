/* =========================================================
   FILEY 2027 — Pseudo-backend de la convocatoria de EVT
   JSON como "base de datos", persistido en localStorage.

   Mismo contrato que common/db.js (el de VIS): la semilla de fábrica
   vive en common/db/EVT/semillas/convocatoria.json y nunca se muta; al
   primer uso se copia a localStorage y todas las lecturas y escrituras
   de la sesión van contra esa copia. FileyEVT.reset() vuelve a sembrar.

   Quién escribe y quién lee:

     admin-evt-configuracion.html  escribe (guardar y publicar)
     convocatoria-eventos.html     lee (fechas clave y conteos)

   En el monolito esto NO es un archivo: la ventana de recepción son
   `Convocatoria.fecha_apertura` y `.fecha_cierre` (apps/convocatorias),
   los hitos posteriores son configuración de EVT, las fechas de la feria
   son `Feria.fecha_inicio` y `.fecha_fin` (apps/ferias, capa public) y
   los conteos son un `count()` sobre las propuestas.

   Usa fetch(), así que las páginas deben servirse por HTTP
   (scripts/preview-vis.sh o GitHub Pages); por file:// falla por CORS.
   ========================================================= */
(function () {
  'use strict';

  var STORAGE_KEY = 'filey_evt_conv_v1';
  var SEED_URL = new URL('db/EVT/semillas/convocatoria.json', document.currentScript.src);

  /* Fecha desde la que se juzga si un hito ya pasó: hoy de verdad, que es
     exactamente lo que hace `date.today()` en el monolito. Con las fechas
     de la convocatoria sembradas, la demo cae dentro de la ventana de
     recepción sin necesidad de fingir el calendario.

     Ojo: el estado de la recepción NO sale de aquí, sale de `estado`
     (ver estadoRecepcion). Esto solo colorea los hitos posteriores. */
  function hoy() {
    var d = new Date();
    var m = d.getMonth() + 1, dia = d.getDate();
    return d.getFullYear() + '-' + (m < 10 ? '0' : '') + m + '-' + (dia < 10 ? '0' : '') + dia;
  }
  var HOY = hoy();

  var MESES = ['enero', 'febrero', 'marzo', 'abril', 'mayo', 'junio', 'julio',
               'agosto', 'septiembre', 'octubre', 'noviembre', 'diciembre'];

  var store = null;
  var readyPromise = null;

  function clone(obj) { return JSON.parse(JSON.stringify(obj)); }
  function persist() { localStorage.setItem(STORAGE_KEY, JSON.stringify(store)); }

  function load() {
    if (readyPromise) return readyPromise;

    // ?reset=1 fuerza re-siembra desde el archivo de fábrica.
    var forceReset = new URLSearchParams(location.search).get('reset') === '1';
    var cached = forceReset ? null : localStorage.getItem(STORAGE_KEY);

    if (cached) {
      try {
        store = JSON.parse(cached);
        readyPromise = Promise.resolve(store);
        return readyPromise;
      } catch (e) { /* corrupto → re-sembrar */ }
    }

    readyPromise = fetch(SEED_URL, { cache: 'no-store' })
      .then(function (r) {
        if (!r.ok) throw new Error('No se pudo cargar la semilla (' + r.status + ')');
        return r.json();
      })
      .then(function (seed) {
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

  function getConfig() { return clone(store); }

  /* Guarda una porción de la configuración. `recepcion`, `ajustes` y
     `solicitudes` se mezclan campo a campo para poder mandar solo uno de
     los dos extremos sin borrar el otro. */
  function saveConfig(patch) {
    Object.keys(patch || {}).forEach(function (k) {
      var v = patch[k];
      if (v && typeof v === 'object' && !Array.isArray(v)) {
        store[k] = Object.assign({}, store[k], v);
      } else {
        store[k] = v;
      }
    });
    persist();
    return getConfig();
  }

  // ---------- fechas ----------
  function sumarDias(iso, n) {
    var p = iso.split('-');
    var dt = new Date(+p[0], +p[1] - 1, +p[2] + n);
    var mm = dt.getMonth() + 1, dd = dt.getDate();
    return dt.getFullYear() + '-' + (mm < 10 ? '0' : '') + mm + '-' + (dd < 10 ? '0' : '') + dd;
  }

  function partes(iso) {
    var p = iso.split('-');
    return { anio: p[0], mes: MESES[+p[1] - 1], dia: +p[2] };
  }

  /* '2027-07-01' → '1 de julio de 2027' */
  function fechaLarga(iso) {
    if (!iso) return '—';
    var f = partes(iso);
    return f.dia + ' de ' + f.mes + ' de ' + f.anio;
  }

  /* Un rango en la forma más corta que siga siendo inequívoca:
     'del 1 al 15 de octubre de 2027' si comparten mes y año,
     'del 1 de julio al 31 de agosto de 2027' si comparten año. */
  function rangoLargo(desde, hasta) {
    if (!desde || !hasta) return fechaLarga(desde || hasta);
    var a = partes(desde), b = partes(hasta);
    if (a.anio === b.anio && a.mes === b.mes) {
      return 'Del ' + a.dia + ' al ' + b.dia + ' de ' + b.mes + ' de ' + b.anio;
    }
    if (a.anio === b.anio) {
      return 'Del ' + a.dia + ' de ' + a.mes + ' al ' + b.dia + ' de ' + b.mes + ' de ' + b.anio;
    }
    return 'Del ' + fechaLarga(desde) + ' al ' + fechaLarga(hasta);
  }

  /* La ventana de ajustes no se captura: empieza al día siguiente de la
     notificación de resultados y termina en el límite configurado. Es la
     misma regla con la que el calendario de la pantalla de configuración
     pinta la banda de ajustes. */
  function ajustesInicio() {
    return store.notificacion ? sumarDias(store.notificacion, 1) : null;
  }

  /* 'pend' | 'fin' — un hito puntual no puede estar "en curso". */
  function estadoDeFecha(iso) {
    if (!iso) return 'pend';
    return iso < HOY ? 'fin' : 'pend';
  }

  /* 'pend' | 'curso' | 'fin' */
  function estadoDeRango(desde, hasta) {
    if (hasta && hasta < HOY) return 'fin';
    if (desde && desde > HOY) return 'pend';
    return 'curso';
  }

  /* La recepción de propuestas es una sola ventana y su estado NO sale de
     comparar fechas: sale de `estado`, igual que en el monolito, donde
     adelantar la fecha de cierre no cierra la convocatoria (CU-FER-008).
     Por eso apertura y cierre son los dos extremos de una fila, y no dos
     hitos con estados que se contradicen entre sí. */
  function estadoRecepcion() {
    if (store.estado === 'cerrada') return 'fin';
    if (store.estado === 'abierta') return 'curso';
    return 'pend';
  }

  // ---------- API pública ----------
  window.FileyEVT = {
    ready: load,
    reset: reset,
    getConfig: getConfig,
    saveConfig: saveConfig,
    fechaLarga: fechaLarga,
    rangoLargo: rangoLargo,
    sumarDias: sumarDias,
    ajustesInicio: ajustesInicio,
    estadoDeFecha: estadoDeFecha,
    estadoDeRango: estadoDeRango,
    estadoRecepcion: estadoRecepcion,
    HOY: HOY
  };

  // Arranca la carga cuanto antes; las páginas esperan con FileyEVT.ready().
  load();
})();

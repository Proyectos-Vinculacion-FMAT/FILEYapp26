/* =========================================================
   FILEY 2027 — Prototipo VIS · interacciones + pseudo-backend
   Lee/escribe datos vía window.FileyDB (common/db.js), que persiste
   en localStorage a partir de los JSON semilla. Cada bloque es
   feature-detect: solo actúa si su página tiene los elementos que usa.
   ========================================================= */
(function () {
  'use strict';

  var DB = window.FileyDB;

  function esc(s) {
    return String(s == null ? '' : s)
      .replace(/&/g, '&amp;').replace(/</g, '&lt;')
      .replace(/>/g, '&gt;').replace(/"/g, '&quot;');
  }
  function byId(id) { return document.getElementById(id); }
  function page() { return document.body.getAttribute('data-vis-page'); }

  // Íconos-glifo cargados del archivo (common/assets) vía FileyDB.icon(name): editar el
  // .svg se refleja al refrescar, sin tocar código. Se rellenan en DB.ready() antes de
  // renderizar. Color y tamaño los controla el CSS del contenedor vía fill="currentColor".
  //   - ICON_CLOSE / ICON_CARET: usados dentro de HTML generado por JS (strings).
  //   - hydrateIcons(): rellena elementos estáticos con [data-vis-icon="nombre"].
  var ICON_CLOSE = '';
  var ICON_CARET = '';

  function hydrateIcons(root) {
    (root || document).querySelectorAll('[data-vis-icon]').forEach(function (el) {
      el.innerHTML = DB.icon(el.getAttribute('data-vis-icon'));
    });
  }

  var MESES = ['ene', 'feb', 'mar', 'abr', 'may', 'jun', 'jul', 'ago', 'sep', 'oct', 'nov', 'dic'];
  function fechaCorta(iso) {
    var p = String(iso || '').split('-');
    if (p.length < 3) return '';
    return parseInt(p[2], 10) + ' ' + (MESES[parseInt(p[1], 10) - 1] || '');
  }
  function horaInicio(horario) { return String(horario || '').split('–')[0].trim(); }

  /* =====================================================
     Bloques genéricos (no dependen de datos)
     ===================================================== */

  // Select-wrap: gestión de .is-open
  document.querySelectorAll('.select-wrap').forEach(function (wrap) {
    var sel = wrap.querySelector('select');
    if (!sel) return;
    sel.addEventListener('focus', function () { wrap.classList.add('is-open'); });
    sel.addEventListener('change', function () { wrap.classList.remove('is-open'); sel.blur(); });
    sel.addEventListener('blur', function () { wrap.classList.remove('is-open'); });
  });

  // Sidebar de administración (overlay). Solo en páginas admin (.topbar.is-admin).
  injectAdminSidebar();
  function injectAdminSidebar() {
    if (!document.querySelector('.topbar.is-admin')) return;
    var here = location.pathname.split('/').pop();
    var seccion = /seguimiento/.test(here) ? 'seguimiento'
      : /configuracion/.test(here) ? 'configuracion' : 'propuestas';
    var items = [
      { id: 'propuestas',    href: 'admin-propuestas.html',    ico: '📋', label: 'Propuestas' },
      { id: 'seguimiento',   href: 'admin-seguimiento.html',   ico: '📊', label: 'Seguimiento' },
      { id: 'configuracion', href: 'admin-configuracion.html', ico: '⚙️', label: 'Configuración' }
    ];
    var nav = document.createElement('div');
    nav.className = 'vis-adm-nav';
    nav.innerHTML =
      '<button type="button" class="vis-adm-nav__trigger" aria-label="Abrir menú" title="Menú">☰</button>' +
      '<nav class="vis-adm-nav__panel" aria-label="Secciones de administración">' +
        '<div class="vis-adm-nav__brand"><span class="ico">🎒</span><div><strong>VIS · Admin</strong>' +
          '<small>Visitas escolares</small></div></div>' +
        '<div class="vis-adm-nav__list">' +
          items.map(function (it) {
            return '<a class="vis-adm-nav__item' + (it.id === seccion ? ' is-active' : '') + '" href="' + it.href + '">' +
              '<span class="ico">' + it.ico + '</span>' + it.label + '</a>';
          }).join('') +
        '</div>' +
      '</nav>';
    document.body.appendChild(nav);

    var trigger = nav.querySelector('.vis-adm-nav__trigger');
    var panel = nav.querySelector('.vis-adm-nav__panel');
    function open() { nav.classList.add('is-open'); }
    function close() { nav.classList.remove('is-open'); }
    trigger.addEventListener('mouseenter', open);
    trigger.addEventListener('click', open); // touch/click también abre
    panel.addEventListener('mouseleave', close);          // el cursor abandona el sidebar
    nav.addEventListener('click', function (e) {          // elegir una opción minimiza
      if (e.target.closest('.vis-adm-nav__item')) close();
    });
    document.addEventListener('keydown', function (e) { if (e.key === 'Escape') close(); });
  }

  // Sin FileyDB (p. ej. páginas de evidencia sin db.js) no seguimos.
  if (!DB) return;

  /* =====================================================
     Arranque: esperar a que la semilla esté en localStorage
     ===================================================== */
  DB.ready().then(function () {
    ICON_CLOSE = DB.icon('close');
    ICON_CARET = DB.icon('caret');
    hydrateIcons(); // rellena íconos estáticos ([data-vis-icon]) de la página
    switch (page()) {
      case 'form':             initFormulario(); break;
      case 'confirmacion':     initConfirmacion(); break;
      case 'mi-visita':        initMiVisita(); break;
      case 'reservar':         initReservar(); break;
      case 'itinerario':       initItinerario(); break;
      case 'admin-propuestas': initAdminPropuestas(); break;
      case 'seguimiento':      initSeguimiento(); break;
      case 'configuracion':    initConfiguracion(); break;
    }
  }).catch(function (err) {
    console.error('[FILEY] No se pudo cargar la base de datos de la demo. ' +
      '¿Estás sirviendo por HTTP (scripts/preview-vis.sh)?', err);
  });

  /* =====================================================
     1. Formulario (aplicante / alta / edición de escuela)
        - Precarga desde la semilla, grado como select por nivel,
          grupos dinámicos, total, y guarda en el pseudo-backend.
     ===================================================== */
  function initFormulario() {
    var form = document.querySelector('[data-vis-form]');
    var list = byId('grupos-list');
    if (!form || !list) return;

    var modo = form.getAttribute('data-vis-form'); // aplicante | edit | alta
    var MAX_GRUPOS = 3, MAX_TOTAL = 105;

    // Primera vez que el aplicante fijo (Benito Juárez) pasa por el formulario: aún no
    // hay registro en el pseudo-backend. El HTML ya trae sus datos de ejemplo como
    // value= precargado; solo necesitamos los 3 grupos reales para no regenerarlos vacíos.
    var registroPrevio = modo !== 'aplicante' ? null : DB.getEscuela(DB.APLICANTE_ID);
    var esAlta = modo === 'alta' || (modo === 'aplicante' && !registroPrevio);

    var escuela = modo === 'alta'
      ? { grupos: [{ id: 'g1', grado: '', cantidad_alumnos: 30, nombre_responsable: '' }], reservas: [] }
      : modo === 'edit' ? DB.getEscuela(DB.currentEscuelaId())
      : (registroPrevio || {
          grupos: [
            { id: 'g1', grado: '6°', cantidad_alumnos: 35, nombre_responsable: 'Erick Matos Pantoja' },
            { id: 'g2', grado: '4°', cantidad_alumnos: 35, nombre_responsable: 'Juan López Salvador' },
            { id: 'g3', grado: '5°', cantidad_alumnos: 20, nombre_responsable: 'Enrique Segoviano Ruiz' }
          ],
          reservas: []
        });

    if (!escuela) return;

    // ---- Precarga de campos de institución / responsable ----
    function setF(name, value) {
      var el = form.querySelector('[data-f="' + name + '"]');
      if (!el) return;
      if (el.tagName === 'SELECT') selectValue(el, value);
      else el.value = value == null ? '' : value;
    }
    if (!esAlta) {
      var ins = escuela.institucion || {}, resp = escuela.responsable || {};
      setF('nombre', ins.nombre); setF('cct', ins.cct); setF('sector', ins.sector);
      setF('turno', ins.turno); setF('nivel_educativo', escuela.nivel_educativo);
      setF('estado', ins.estado); setF('municipio', ins.municipio);
      setF('nombre_director', ins.nombre_director); setF('direccion', ins.direccion);
      setF('telefono', ins.telefono); setF('correo', ins.correo);
      setF('r_nombre', resp.nombre); setF('r_cargo', resp.cargo);
      setF('r_telefono', resp.telefono); setF('r_correo', resp.correo);
      setF('campo_libre', escuela.campo_libre);
      if (modo === 'edit') updateResumen(escuela); // breadcrumb/encabezado (folio, institución)
    }

    function nivelActual() {
      var el = form.querySelector('[data-f="nivel_educativo"]');
      return el ? el.value : (escuela.nivel_educativo || '');
    }

    // ---- Grupos ----
    function gradoControlHTML(nivel, value) {
      var grados = DB.gradosPorNivel(nivel);
      if (!grados) {
        return '<input type="text" class="grupo-grado" placeholder="Ej. 1er año" value="' + esc(value) + '" data-vis-required>';
      }
      var opts = grados.slice();
      if (value && opts.indexOf(value) === -1) opts.unshift(value); // no perder valor previo
      var html = '<div class="select-wrap"><select class="grupo-grado" data-vis-required>' +
        '<option value="" disabled' + (value ? '' : ' selected') + '>Selecciona…</option>' +
        opts.map(function (g) {
          return '<option' + (g === value ? ' selected' : '') + '>' + esc(g) + '</option>';
        }).join('') + '</select></div>';
      return html;
    }

    function grupoBlockHTML(grupo, nivel) {
      return '<div class="grupo-block" data-grupo>' +
        '<div class="grupo-block__head"><strong data-grupo-title>Grupo</strong>' +
        '<button type="button" class="grupo-remove" data-grupo-remove>Quitar</button></div>' +
        '<div class="grid-3">' +
          '<div class="field" data-field-grado><label>Grado <span class="req">*</span></label>' +
            gradoControlHTML(nivel, grupo.grado) +
            '<span class="field__err">Este campo es obligatorio</span></div>' +
          '<div class="field"><label>Alumnos <span class="req">*</span></label>' +
            '<input type="number" min="1" max="35" class="grupo-cant" value="' + (grupo.cantidad_alumnos || '') + '" data-vis-required>' +
            '<span class="field__err">Este campo es obligatorio</span></div>' +
          '<div class="field"><label>Representante del grupo <span class="req">*</span></label>' +
            '<input type="text" class="grupo-rep" placeholder="Nombre del responsable" value="' + esc(grupo.nombre_responsable) + '" data-vis-required>' +
            '<span class="field__err">Este campo es obligatorio</span></div>' +
        '</div></div>';
    }

    function renderGrupos() {
      var nivel = nivelActual();
      list.innerHTML = (escuela.grupos || []).map(function (g) {
        return grupoBlockHTML(g, nivel);
      }).join('');
      refreshTitlesAndTotal();
    }

    // Reconstruye solo los controles de grado (al cambiar nivel) conservando lo escrito.
    function rebuildGrados() {
      var nivel = nivelActual();
      list.querySelectorAll('[data-field-grado]').forEach(function (fieldGrado) {
        var ctrl = fieldGrado.querySelector('.grupo-grado');
        var val = ctrl ? ctrl.value : '';
        var label = fieldGrado.querySelector('label');
        fieldGrado.innerHTML = label.outerHTML + gradoControlHTML(nivel, val) +
          '<span class="field__err">Este campo es obligatorio</span>';
      });
    }

    function blocks() { return Array.prototype.slice.call(list.querySelectorAll('[data-grupo]')); }

    function refreshTitlesAndTotal() {
      var bs = blocks(), total = 0;
      bs.forEach(function (b, i) {
        var t = b.querySelector('[data-grupo-title]');
        if (t) t.textContent = 'Grupo ' + (i + 1);
        var c = b.querySelector('.grupo-cant');
        total += c ? (parseInt(c.value, 10) || 0) : 0;
        var rm = b.querySelector('[data-grupo-remove]');
        if (rm) rm.style.visibility = bs.length > 1 ? 'visible' : 'hidden';
      });
      var totalEl = byId('total-alumnos'); if (totalEl) totalEl.textContent = total;
      var over = total > MAX_TOTAL;
      var totalBox = byId('total-box'); if (totalBox) totalBox.classList.toggle('over', over);
      var overNote = byId('over-note'); if (overNote) overNote.style.display = over ? 'flex' : 'none';
      var addBtn = byId('add-grupo');
      if (addBtn) {
        addBtn.disabled = bs.length >= MAX_GRUPOS;
        addBtn.style.opacity = bs.length >= MAX_GRUPOS ? '.5' : '1';
        addBtn.style.pointerEvents = bs.length >= MAX_GRUPOS ? 'none' : 'auto';
      }
    }

    renderGrupos();

    list.addEventListener('input', function (e) {
      if (!e.target.classList.contains('grupo-cant')) return;
      if (parseInt(e.target.value, 10) > 35) e.target.value = 35; // máx. 35 alumnos por grupo
      refreshTitlesAndTotal();
    });
    list.addEventListener('click', function (e) {
      var rm = e.target.closest('[data-grupo-remove]');
      if (!rm) return;
      var block = rm.closest('[data-grupo]');
      if (block && blocks().length > 1) { block.remove(); refreshTitlesAndTotal(); }
    });

    var nivelSel = form.querySelector('[data-f="nivel_educativo"]');
    if (nivelSel) nivelSel.addEventListener('change', rebuildGrados);

    var addBtn = byId('add-grupo');
    if (addBtn) addBtn.addEventListener('click', function () {
      if (blocks().length >= MAX_GRUPOS) return;
      list.insertAdjacentHTML('beforeend',
        grupoBlockHTML({ grado: '', cantidad_alumnos: 30, nombre_responsable: '' }, nivelActual()));
      refreshTitlesAndTotal();
    });

    // ---- Lectura del formulario → objeto escuela ----
    function getF(name) {
      var el = form.querySelector('[data-f="' + name + '"]');
      return el ? el.value.trim() : '';
    }
    function readEscuela() {
      var grupos = blocks().map(function (b, i) {
        var prev = (escuela.grupos || [])[i] || {};
        return {
          id: prev.id || ('g' + (i + 1)),
          grado: (b.querySelector('.grupo-grado') || {}).value || '',
          cantidad_alumnos: parseInt((b.querySelector('.grupo-cant') || {}).value, 10) || 0,
          nombre_responsable: (b.querySelector('.grupo-rep') || {}).value || ''
        };
      });
      var grupoIds = grupos.map(function (g) { return g.id; });
      var reservas = (escuela.reservas || []).filter(function (r) {
        return grupoIds.indexOf(r.grupo_id) !== -1; // descarta reservas de grupos eliminados
      });
      var total = grupos.reduce(function (s, g) { return s + g.cantidad_alumnos; }, 0);
      return Object.assign({}, escuela, {
        institucion: {
          nombre: getF('nombre'), cct: getF('cct'), sector: getF('sector'),
          turno: getF('turno'), direccion: getF('direccion'), estado: getF('estado'),
          municipio: getF('municipio'), telefono: getF('telefono'),
          correo: getF('correo'), nombre_director: getF('nombre_director')
        },
        responsable: {
          nombre: getF('r_nombre'), cargo: getF('r_cargo'),
          telefono: getF('r_telefono'), correo: getF('r_correo')
        },
        nivel_educativo: getF('nivel_educativo'),
        campo_libre: form.querySelector('[data-f="campo_libre"]') ? getF('campo_libre') : (escuela.campo_libre || ''),
        grupos: grupos,
        reservas: reservas,
        cantidad_alumnos_visitantes: total
      });
    }

    function validar() {
      var ok = true;
      form.querySelectorAll('[data-vis-required]').forEach(function (el) {
        var field = el.closest('.field');
        var empty = !String(el.value).trim();
        if (field) field.classList.toggle('is-invalid', empty);
        if (empty) ok = false;
      });
      if (!ok) {
        var first = form.querySelector('.field.is-invalid');
        if (first) first.scrollIntoView({ behavior: 'smooth', block: 'center' });
      }
      return ok;
    }
    form.addEventListener('input', function (e) {
      if (e.target.hasAttribute('data-vis-required') && String(e.target.value).trim()) {
        var field = e.target.closest('.field');
        if (field) field.classList.remove('is-invalid');
      }
    });

    // ---- Guardado ----
    document.querySelectorAll('[data-vis-save]').forEach(function (btn) {
      btn.addEventListener('click', function (e) {
        e.preventDefault();
        if ((modo === 'aplicante') && !validar()) return;
        var destino = btn.getAttribute('data-vis-save'); // 'lista' | 'reservar' | 'confirmacion'
        var datos = readEscuela();
        // Primer guardado del aplicante fijo: conserva su id (para que mi-visita/reservar/
        // itinerario lo vuelvan a encontrar vía APLICANTE_ID) pero el folio sí se genera
        // nuevo (mayor que los anteriores) — no lo fijamos, lo asigna insertEscuela.
        if (modo === 'aplicante' && esAlta) datos.id = DB.APLICANTE_ID;
        var guardada = esAlta ? DB.insertEscuela(datos) : DB.saveEscuela(datos);
        var id = guardada.id;
        if (destino === 'confirmacion') location.href = 'confirmacion-vis.html?id=' + id;
        else if (destino === 'reservar') location.href = 'admin-reservar.html?id=' + id;
        else location.href = 'admin-propuestas.html';
      });
    });
  }

  function selectValue(sel, value) {
    var found = false;
    Array.prototype.forEach.call(sel.options, function (o) {
      if (o.value === value || o.textContent === value) { o.selected = true; found = true; }
    });
    if (!found && value) {
      var o = document.createElement('option');
      o.textContent = value; o.selected = true;
      sel.appendChild(o);
    }
  }

  /* =====================================================
     2. Confirmación: folio real del registro
     ===================================================== */
  function initConfirmacion() {
    var e = DB.getEscuela(DB.currentEscuelaId());
    if (!e) return;
    var strong = document.querySelector('.folio-box strong');
    if (strong) strong.textContent = e.folio;
  }

  /* =====================================================
     3. Mi registro (aplicante): ficha + grupos + itinerario
     ===================================================== */
  function initMiVisita() {
    // Página aplicante: siempre es el registro fijo, nunca honra ?id= de otra escuela.
    var e = DB.getEscuela(DB.APLICANTE_ID);
    if (!e) { location.href = 'convocatoria-vis.html'; return; }
    renderFicha(document.querySelector('[data-vis-ficha]'), e);
    var container = document.querySelector('[data-vis-grupos]');
    // Solo lectura: el representante ya no edita itinerario ni datos, solo puede solicitar un cambio.
    renderGrupoReservas(container, e.id, { removable: false, onChange: updateResumen });
    wireSolicitudCambio(e);
  }

  // Solicitud de cambio (motivo en texto libre): solo el admin aplica el cambio real
  // a itinerario/formulario; esto solo registra la solicitud en el registro de la escuela.
  function wireSolicitudCambio(e) {
    var form = document.querySelector('[data-solicitud-form]');
    var enviada = document.querySelector('[data-solicitud-enviada]');
    var btn = document.querySelector('[data-solicitud-enviar]');
    var textarea = document.querySelector('[data-solicitud-motivo]');
    if (!form || !enviada || !btn || !textarea) return;

    function mostrarEnviada(sol) {
      form.style.display = 'none';
      enviada.style.display = '';
      var fechaEl = enviada.querySelector('[data-solicitud-fecha]');
      var motivoEl = enviada.querySelector('[data-solicitud-motivo-texto]');
      if (fechaEl) fechaEl.textContent = 'el ' + fechaCorta(sol.fecha);
      if (motivoEl) motivoEl.textContent = sol.motivo;
    }

    if (e.solicitud_cambio && e.solicitud_cambio.estado === 'pendiente') {
      mostrarEnviada(e.solicitud_cambio);
      return;
    }

    btn.addEventListener('click', function () {
      var motivo = textarea.value.trim();
      if (!motivo) { textarea.focus(); return; }
      var sol = { motivo: motivo, fecha: new Date().toISOString().slice(0, 10), estado: 'pendiente' };
      var fresh = DB.updateEscuela(e.id, { solicitud_cambio: sol });
      mostrarEnviada(fresh.solicitud_cambio);
    });
  }

  function renderFicha(el, e) {
    if (!el) return;
    var ins = e.institucion || {}, resp = e.responsable || {};
    function kv(k, v) { return '<span class="vis-ficha__key">' + esc(k) + '</span><span class="vis-ficha__value">' + esc(v) + '</span>'; }
    el.innerHTML =
      '<p class="vis-ficha__section">Responsable de la visita</p><div class="vis-ficha__grid">' +
        kv('Nombre', resp.nombre) + kv('Cargo', resp.cargo) + kv('Teléfono', resp.telefono) + kv('Correo', resp.correo) +
      '</div><p class="vis-ficha__section" style="margin-top:14px">Institución</p><div class="vis-ficha__grid">' +
        kv('Nombre', ins.nombre) + kv('CCT', ins.cct) +
        kv('Nivel', e.nivel_educativo + ' · ' + ins.turno) + kv('Sector', ins.sector) +
        kv('Director(a)', ins.nombre_director) +
        kv('Dirección', ins.direccion + (ins.municipio ? ', ' + ins.municipio : '') + (ins.estado ? ', ' + ins.estado : '')) +
        kv('Teléfono inst.', ins.telefono) + kv('Correo inst.', ins.correo) +
      '</div><p class="vis-ficha__section" style="margin-top:14px">Observaciones</p><div class="vis-ficha__grid">' +
        kv('Comentarios del registro', e.campo_libre || 'Sin observaciones') +
      '</div>';
  }

  /* =====================================================
     4. Reservar talleres (aplicante / admin): grid desde catálogo,
        reservas persistentes, cupo compartido, mover en conflicto.
     ===================================================== */
  function initReservar() {
    var wrap = byId('horario-wrap');
    if (!wrap) return;
    // Variante admin honra ?id=; la aplicante siempre es el registro fijo.
    var isAdminReservar = document.body.hasAttribute('data-vis-admin');
    var escuelaId = isAdminReservar ? DB.currentEscuelaId() : DB.APLICANTE_ID;
    if (!isAdminReservar && !DB.getEscuela(escuelaId)) { location.href = 'convocatoria-vis.html'; return; }
    var cat = DB.getCatalogo();
    var turnoSel = byId('turno-select');
    var headerEl = document.querySelector('.vis-sel-header');

    function renderHeader(e) {
      if (!headerEl) return;
      var instituto = headerEl.querySelector('.vis-sel-header__instituto');
      if (instituto) instituto.textContent = (e.institucion || {}).nombre + ' · ' + e.nivel_educativo;
      var cards = (e.grupos || []).map(function (g, i) {
        var n = (e.reservas || []).filter(function (r) { return r.grupo_id === g.id; }).length;
        return '<div class="vis-grupo-card"><div class="vis-grupo-card__header">Grupo ' + (i + 1) + ' — G' + (i + 1) + '</div>' +
          '<div class="vis-grupo-card__body"><span>Grado: ' + esc(g.grado) + '</span>' +
          '<span>Visitantes: ' + g.cantidad_alumnos + '</span>' +
          '<span>Responsable: ' + esc(g.nombre_responsable) + '</span>' +
          '<span>Talleres reservados: ' + n + '</span></div></div>';
      }).join('');
      headerEl.querySelectorAll('.vis-grupo-card').forEach(function (c) { c.remove(); });
      headerEl.insertAdjacentHTML('beforeend', cards);
    }

    function getEsc() { return DB.getEscuela(escuelaId); }
    function reservasDe(e, tallerId) {
      return (e.reservas || []).filter(function (r) { return r.taller_id === tallerId; });
    }
    function gruposEn(e, tallerId) {
      return reservasDe(e, tallerId).map(function (r) { return DB.grupoCodigo(e, r.grupo_id); });
    }
    function tallerInfo(id) { return cat.byId[id]; }
    function esLibre(id) { var t = tallerInfo(id); return !t || t.tipo === 'libre'; }
    function bloque(id) { var t = tallerInfo(id); return t ? t.turno + '|' + t.horario : ''; }

    // ---- construcción del grid ----
    function celdaHTML(celda) {
      if (celda.tipo === 'sin')
        return '<div class="vis-horario-celda vis-horario-celda--sin-taller"><span class="vis-bloque-label">Sin taller programado</span></div>';
      if (celda.tipo === 'cer')
        return '<div class="vis-horario-celda vis-horario-celda--cerrado"><span class="vis-bloque-label">Cerrado</span></div>';
      if (celda.tipo === 'libre')
        return '<div class="vis-horario-celda vis-horario-celda--libre" data-taller-id="' + celda.id + '" data-libre="1" style="flex:0 0 ' + (celda.span * 360) + 'px">' +
          '<span class="vis-bloque-label">Zona de acceso libre</span><span class="vis-horario-celda__cupos">Cupo ilimitado</span></div>';
      var n = DB.NIVELES[celda.nivel] || { label: celda.nivel, cls: '' };
      return '<div class="vis-horario-celda" data-taller-id="' + celda.id + '" data-base="' + celda.base + '" data-nivel="' + esc(celda.nivel) + '">' +
        '<span class="vis-horario-celda__nombre">' + esc(celda.titulo) + '</span>' +
        '<div class="vis-horario-celda__meta"><span class="vis-horario-celda__cupos"></span>' +
        '<span>Nivel: <span class="vis-nivel ' + n.cls + '">' + n.label + '</span></span></div></div>';
    }
    function areaHTML(turno) {
      var head = '<div class="vis-horario-tiempos"><div class="vis-horario-tiempo vis-horario-tiempo--sala">Sala</div>' +
        cat.horarios[turno].map(function (t) { return '<div class="vis-horario-tiempo">' + t + '</div>'; }).join('') + '</div>';
      var rows = cat.grid[turno].map(function (celdas, i) {
        return '<div class="vis-horario-fila"><div class="vis-horario-celda vis-horario-celda--sala-label">' + esc(cat.salas[i]) + '</div>' +
          celdas.map(celdaHTML).join('') + '</div>';
      }).join('');
      return '<div class="vis-horario-area" data-turno="' + turno + '">' + head + rows + '</div>';
    }

    function paintCupo(cell, e) {
      if (cell.hasAttribute('data-libre')) return;
      var id = cell.getAttribute('data-taller-id');
      var base = parseInt(cell.getAttribute('data-base'), 10);
      var label = cell.querySelector('.vis-horario-celda__cupos');
      if (!label || isNaN(base)) return;
      var remaining = base - DB.cupoTomado(id);
      label.textContent = 'Cupos disponibles: ' + Math.max(remaining, 0);
      cell.classList.toggle('vis-horario-celda--llena', remaining <= 0);
    }
    function paintBadges(cell, e) {
      var id = cell.getAttribute('data-taller-id');
      var codes = gruposEn(e, id);
      var box = cell.querySelector('.vis-celda-badges');
      if (!codes.length) { if (box) box.remove(); return; }
      if (!box) { box = document.createElement('div'); box.className = 'vis-celda-badges'; cell.appendChild(box); }
      box.innerHTML = codes.sort().map(function (c) { return '<span class="vis-grupo-badge">' + c + '</span>'; }).join('');
    }
    function paintAll(e) {
      wrap.querySelectorAll('.vis-horario-celda[data-taller-id]').forEach(function (cell) {
        paintCupo(cell, e); paintBadges(cell, e);
      });
    }
    function applyTurno() {
      var val = turnoSel ? turnoSel.value : 'matutino';
      wrap.querySelectorAll('.vis-horario-area').forEach(function (a) {
        a.classList.toggle('is-active', a.getAttribute('data-turno') === val);
      });
    }
    function updateSummary(e) {
      var count = new Set((e.reservas || []).map(function (r) { return r.taller_id; })).size;
      var c = byId('reserva-count'); if (c) c.textContent = count;
      var d = byId('reserva-detalle');
      if (d) d.textContent = count === 0
        ? 'Asigna grupos a las actividades para reservarlas.'
        : 'Cupo garantizado para tus grupos en ' + count + ' actividad(es).';
    }

    function render() {
      var e = getEsc();
      wrap.innerHTML = areaHTML('matutino') + areaHTML('vespertino');
      applyTurno();
      paintAll(e);
      updateSummary(e);
      renderHeader(e);
      updateResumen(e);
      if (popup.style.display === 'flex' && currentTallerId) {
        currentCell = wrap.querySelector('[data-taller-id="' + currentTallerId + '"]');
        if (currentCell) syncRadios(); else closePopup();
      }
    }

    if (turnoSel) turnoSel.addEventListener('change', applyTurno);

    // El enlace "Ver itinerario" conserva la escuela seleccionada (lado admin).
    var itinLink = document.querySelector('[data-vis-itin-link]');
    if (itinLink) itinLink.href = 'itinerario-admin.html?id=' + escuelaId;

    // ---- popup de asignación de grupos ----
    var popup = document.createElement('div');
    popup.className = 'vis-grupo-selector';
    popup.style.cssText = 'position:fixed;z-index:9999;';
    document.body.appendChild(popup);
    var currentCell = null, currentTallerId = null;

    function buildPopup() {
      var e = getEsc();
      var items = (e.grupos || []).map(function (g, i) {
        return '<div class="vis-grupo-selector__item" data-group="G' + (i + 1) + '">' +
          '<span class="vis-radio"></span> Grupo ' + (i + 1) + ' · ' + g.cantidad_alumnos + ' alumnos</div>';
      }).join('');
      popup.innerHTML =
        '<div class="vis-grupo-selector__head"><p class="vis-grupo-selector__title">Asignar grupo completo</p>' +
        '<button type="button" class="vis-icon-btn" data-popup-close title="Cerrar" aria-label="Cerrar">' + ICON_CLOSE + '</button></div>' +
        items +
        '<div class="vis-grupo-selector__item"><button type="button" class="vis-todos-btn">Todos los grupos</button></div>' +
        '<p style="margin:6px 0 0;font-size:11px;color:var(--gris-500);line-height:1.4">Se reserva la totalidad de alumnos del grupo seleccionado.</p>';
    }
    function syncRadios() {
      if (!currentCell) return;
      var e = getEsc();
      var codes = gruposEn(e, currentTallerId);
      popup.querySelectorAll('[data-group]').forEach(function (item) {
        item.querySelector('.vis-radio').classList.toggle(
          'vis-radio--selected', codes.indexOf(item.getAttribute('data-group')) !== -1);
      });
    }
    function openPopup(cell, x, y) {
      currentCell = cell;
      currentTallerId = cell.getAttribute('data-taller-id');
      buildPopup(); syncRadios();
      popup.style.display = 'flex';
      var pw = popup.offsetWidth || 200, ph = popup.offsetHeight || 200;
      popup.style.left = Math.min(x, window.innerWidth - pw - 8) + 'px';
      popup.style.top = Math.min(y, window.innerHeight - ph - 8) + 'px';
    }
    function closePopup() { popup.style.display = 'none'; currentCell = null; currentTallerId = null; }

    function flash(cell) {
      cell.style.boxShadow = 'inset 0 0 0 2px var(--err-600)';
      setTimeout(function () { cell.style.boxShadow = ''; }, 350);
    }
    function showConflict(text) {
      var el = popup.querySelector('.vis-conflict-msg');
      if (!el) {
        el = document.createElement('p'); el.className = 'vis-conflict-msg';
        el.style.cssText = 'margin:4px 10px 0;font-size:12px;color:#b91c1c;';
        popup.appendChild(el);
      }
      el.textContent = text; el.style.display = 'block';
      clearTimeout(el._t); el._t = setTimeout(function () { el.style.display = 'none'; }, 3000);
    }

    function nivelCat(n) { return (n === 'pa' || n === 'pb') ? 'primaria' : (n || ''); }

    // Intenta asignar un grupo (code) al taller actual. Devuelve true si cambió algo.
    function tryAssign(code) {
      var e = getEsc();
      var grupo = DB.grupoPorCodigo(e, code);
      if (!grupo) return false;
      var id = currentTallerId;
      var info = tallerInfo(id);

      // ¿ya está? → alternar (quitar)
      if (gruposEn(e, id).indexOf(code) !== -1) {
        DB.removeReserva(escuelaId, function (r) { return r.taller_id === id && r.grupo_id === grupo.id; });
        return true;
      }

      // cupo
      if (!esLibre(id)) {
        var remaining = info.base - DB.cupoTomado(id);
        if (grupo.cantidad_alumnos > remaining) { flash(currentCell); showConflict('Sin cupo suficiente para ' + code + '.'); return false; }
      }
      // nivel educativo compatible (regla dura: se bloquea)
      if (!esLibre(id) && info.nivel) {
        var gN = DB.nivelDeGrupo(e, grupo);
        if (gN && nivelCat(info.nivel) !== nivelCat(gN)) {
          flash(currentCell);
          showConflict('Nivel incompatible: este taller es de ' + (DB.NIVELES[info.nivel] || {}).label + '.');
          return false;
        }
      }
      // conflicto de horario → MOVER (quita la reserva previa del grupo en ese bloque)
      if (!esLibre(id)) {
        var previa = (e.reservas || []).find(function (r) {
          return r.grupo_id === grupo.id && r.taller_id !== id &&
            !esLibre(r.taller_id) && bloque(r.taller_id) === bloque(id);
        });
        if (previa) {
          DB.removeReserva(escuelaId, function (r) { return r.grupo_id === grupo.id && r.taller_id === previa.taller_id; });
        }
      }
      DB.addReserva(escuelaId, { grupo_id: grupo.id, taller_id: id, cantidad_alumnos: grupo.cantidad_alumnos });
      return true;
    }

    // Eventos del grid
    function eligible(cell) { return cell && cell.hasAttribute('data-taller-id'); }
    wrap.addEventListener('click', function (ev) {
      var cell = ev.target.closest('.vis-horario-celda');
      if (!eligible(cell)) return;
      openPopup(cell, ev.clientX, ev.clientY);
    });
    wrap.addEventListener('contextmenu', function (ev) {
      var cell = ev.target.closest('.vis-horario-celda');
      if (!eligible(cell)) return;
      ev.preventDefault(); openPopup(cell, ev.clientX, ev.clientY);
    });

    popup.addEventListener('click', function (ev) {
      if (ev.target.closest('[data-popup-close]')) { closePopup(); return; }
      var item = ev.target.closest('[data-group]');
      if (item) { if (tryAssign(item.getAttribute('data-group'))) render(); return; }
      if (ev.target.closest('.vis-todos-btn')) {
        var e = getEsc(), changed = false;
        (e.grupos || []).forEach(function (g, i) {
          var code = 'G' + (i + 1);
          if (gruposEn(getEsc(), currentTallerId).indexOf(code) === -1) {
            if (tryAssign(code)) changed = true;
          }
        });
        if (changed) render();
      }
    });
    document.addEventListener('click', function (ev) {
      if (!popup.contains(ev.target) && !ev.target.closest('.vis-horario-celda')) closePopup();
    });
    document.addEventListener('keydown', function (ev) { if (ev.key === 'Escape') closePopup(); });

    render();
  }

  /* =====================================================
     5. Itinerario (aplicante con quitar / admin solo lectura)
     ===================================================== */
  function initItinerario() {
    var readonly = document.body.hasAttribute('data-vis-readonly'); // oculta los botones de quitar
    var isAdmin = document.body.hasAttribute('data-vis-admin'); // honra ?id=; la aplicante siempre es el registro fijo
    var e = DB.getEscuela(isAdmin ? DB.currentEscuelaId() : DB.APLICANTE_ID);
    if (!e) { if (!isAdmin) location.href = 'convocatoria-vis.html'; return; }
    var container = document.querySelector('[data-vis-grupos]');
    var opts = {
      removable: !readonly,
      onChange: function (fresh) {
        updateResumen(fresh);
        var empty = byId('itin-empty');
        if (empty) empty.style.display = (fresh.reservas || []).length ? 'none' : 'flex';
      }
    };
    renderGrupoReservas(container, e.id, opts);
    if (!readonly) wireCancelarTodas(e.id, function () { renderGrupoReservas(container, e.id, opts); });
    // El botón "Confirmar y recibir por correo" navega a convocatorias vía su href normal.
  }

  /* =====================================================
     6. Admin · lista de escuelas (tabla + detalle + cancelar)
     ===================================================== */
  function initAdminPropuestas() {
    renderStatCard();
    renderSolicitudesCambio();
    var tbody = document.querySelector('.vis-tabla tbody');
    if (!tbody) return;
    var cat = DB.getCatalogo();

    function renderSolicitudesCambio() {
      var card = document.querySelector('[data-vis-solicitudes]');
      var list = document.querySelector('[data-vis-solicitudes-list]');
      if (!card || !list) return;
      var pendientes = DB.listEscuelas().filter(function (e) {
        return e.solicitud_cambio && e.solicitud_cambio.estado === 'pendiente';
      });
      card.style.display = pendientes.length ? '' : 'none';
      list.innerHTML = pendientes.map(function (e) {
        var ins = e.institucion || {};
        return '<div class="note note-warn" data-solicitud-row="' + e.id + '" style="align-items:center">' +
          '<div class="ico">✎</div>' +
          '<div style="flex:1"><strong>' + esc(ins.nombre) + '</strong> · ' + esc(e.folio) +
            ' — solicitado el ' + esc(fechaCorta(e.solicitud_cambio.fecha)) + '<br>' +
            '«' + esc(e.solicitud_cambio.motivo) + '»</div>' +
          '<div style="display:flex; gap:8px; flex-wrap:wrap">' +
            '<a class="btn btn-ghost btn-sm" href="admin-escuela-edit.html?id=' + e.id + '">✎ Editar datos</a>' +
            '<a class="btn btn-ghost btn-sm" href="admin-reservar.html?id=' + e.id + '">🗓️ Editar itinerario</a>' +
            '<button type="button" class="btn btn-primary btn-sm" data-solicitud-atender="' + e.id + '">✓ Marcar atendida</button>' +
          '</div></div>';
      }).join('');
      list.querySelectorAll('[data-solicitud-atender]').forEach(function (btn) {
        btn.addEventListener('click', function () {
          var id = btn.getAttribute('data-solicitud-atender');
          var e = DB.getEscuela(id);
          if (e && e.solicitud_cambio) {
            DB.updateEscuela(id, { solicitud_cambio: Object.assign({}, e.solicitud_cambio, { estado: 'atendida' }) });
          }
          renderSolicitudesCambio();
        });
      });
    }

    function totalAlumnos(e) {
      return (e.grupos || []).reduce(function (s, g) { return s + (g.cantidad_alumnos || 0); }, 0);
    }
    function tallerIds(e) { return new Set((e.reservas || []).map(function (r) { return r.taller_id; })); }
    function diaVisita(e) {
      return (e.reservas || []).length ? cat.fecha_label.replace(' de 2027', '') : '—';
    }

    var CARET = '<span class="vis-tabla__toggle-icon">' + ICON_CARET + '</span>';

    function observacionesHTML(e) {
      return '<span class="vis-ficha__key">Comentarios del registro</span>' +
        '<span class="vis-ficha__value">' + esc(e.campo_libre || 'Sin observaciones') + '</span>';
    }

    function rowsHTML() {
      return DB.listEscuelas().map(function (e) {
        var ins = e.institucion || {}, resp = e.responsable || {};
        var tieneReservas = (e.reservas || []).length > 0;
        var main = '<tr class="vis-row" data-escuela="' + e.id + '">' +
          '<td class="folio">' + esc(e.folio) + '</td>' +
          '<td>' + esc(ins.nombre) + '</td>' +
          '<td>' + esc(e.nivel_educativo) + '</td>' +
          '<td>' + esc((ins.municipio === 'Otro' ? ins.direccion : ins.municipio) + ', ' + ins.estado) + '</td>' +
          '<td>' + totalAlumnos(e) + '</td><td>' + tallerIds(e).size + '</td><td>' + diaVisita(e) + '</td>' +
          '<td><button type="button" class="vis-tabla__toggle" data-toggle>Detalle ' + CARET + '</button></td></tr>';

        var accionesItin = tieneReservas
          ? '<a class="vis-itinerario-btn__pill" href="admin-reservar.html?id=' + e.id + '">🗓️ Editar itinerario</a>' +
            '<button type="button" class="btn btn-danger" data-cancel-todas>✕ Cancelar todas las reservaciones</button>'
          : '<a class="vis-itinerario-btn__pill" href="admin-reservar.html?id=' + e.id + '">🗓️ Crear itinerario</a>';

        var detail = '<tr class="vis-tabla__row-detail"><td colspan="8"><div class="vis-tabla-detail"><div class="vis-tabla-detail__inner">' +
          '<div class="vis-ficha"><p class="vis-ficha__section">Representante</p><div class="vis-ficha__grid">' +
            '<span class="vis-ficha__key">Nombre</span><span class="vis-ficha__value">' + esc(resp.nombre) + '</span>' +
            '<span class="vis-ficha__key">Cargo</span><span class="vis-ficha__value">' + esc(resp.cargo) + '</span>' +
            '<span class="vis-ficha__key">Teléfono</span><span class="vis-ficha__value">' + esc(resp.telefono) + '</span>' +
            '<span class="vis-ficha__key">Correo</span><span class="vis-ficha__value">' + esc(resp.correo) + '</span></div>' +
          '<p class="vis-ficha__section" style="margin-top:12px">Instituto</p><div class="vis-ficha__grid">' +
            '<span class="vis-ficha__key">Director</span><span class="vis-ficha__value">' + esc(ins.nombre_director) + '</span>' +
            '<span class="vis-ficha__key">CCT</span><span class="vis-ficha__value">' + esc(ins.cct) + '</span>' +
            '<span class="vis-ficha__key">Dirección</span><span class="vis-ficha__value">' + esc(ins.direccion) + '</span>' +
            '<span class="vis-ficha__key">Teléfono inst.</span><span class="vis-ficha__value">' + esc(ins.telefono) + '</span>' +
            '<span class="vis-ficha__key">Correo inst.</span><span class="vis-ficha__value">' + esc(ins.correo) + '</span></div>' +
          '<p class="vis-ficha__section" style="margin-top:12px">Observaciones</p><div class="vis-ficha__grid">' + observacionesHTML(e) + '</div></div>' +
          '<div class="vis-detail-actions">' + accionesItin +
            '<a class="btn btn-ghost btn-sm" href="admin-escuela-edit.html?id=' + e.id + '">✎ Editar datos / grupos</a></div>' +
          '</div><div class="vis-grupos-row">' +
            grupoReservasHTML(e, { removable: true, reservarHref: 'admin-reservar.html?id=' + e.id }) +
          '</div></div></td></tr>';
        return main + detail;
      }).join('');
    }

    var openIds = new Set(); // escuelas con el detalle expandido, preservado entre renders

    function render() {
      tbody.innerHTML = rowsHTML();
      tbody.querySelectorAll('[data-escuela]').forEach(function (row) {
        if (!openIds.has(row.getAttribute('data-escuela'))) return;
        var detail = row.nextElementSibling, btn = row.querySelector('[data-toggle]');
        if (detail) detail.classList.add('is-open');
        if (btn) btn.classList.add('is-open');
      });
      bindToggles();
    }
    function bindToggles() {
      tbody.querySelectorAll('.vis-tabla__toggle[data-toggle]').forEach(function (btn) {
        btn.addEventListener('click', function () {
          var row = btn.closest('tr'), detail = row && row.nextElementSibling;
          if (!detail || !detail.classList.contains('vis-tabla__row-detail')) return;
          var open = detail.classList.toggle('is-open');
          btn.classList.toggle('is-open', open);
          var id = row.getAttribute('data-escuela');
          if (open) openIds.add(id); else openIds.delete(id);
        });
      });
    }

    tbody.addEventListener('click', function (ev) {
      var row = ev.target.closest('[data-escuela]') ||
        (ev.target.closest('.vis-tabla__row-detail') && ev.target.closest('.vis-tabla__row-detail').previousElementSibling);
      var id = row && row.getAttribute('data-escuela');
      if (ev.target.closest('[data-cancel-todas]')) {
        if (id) { DB.updateEscuela(id, { reservas: [] }); render(); }
        return;
      }
      var rm = ev.target.closest('[data-remove-reserva]');
      if (rm && id) {
        var reservaId = rm.getAttribute('data-remove-reserva');
        DB.removeReserva(id, function (r) { return r.id === reservaId; });
        render();
      }
    });

    render();
  }

  /* =====================================================
     7. Admin · Seguimiento (dashboard)
     ===================================================== */
  function initSeguimiento() {
    var cat = DB.getCatalogo();

    function setKpi(k, v) {
      document.querySelectorAll('[data-kpi="' + k + '"]').forEach(function (el) { el.textContent = v; });
    }
    setKpi('escuelas', DB.listEscuelas().length);
    var cupos = DB.resumenCupos();
    setKpi('reservado', cupos.reservado.toLocaleString('es-MX'));
    var dia = DB.diaMayorDemanda();
    setKpi('dia', dia ? fechaCorta(dia.fecha) : '—');

    // --- Gráfica de barras: reservaciones por día (una serie, un solo tono, base redondeada) ---
    var bc = document.querySelector('[data-barchart]');
    if (bc) bc.innerHTML = barChartSVG(DB.demandaPorDia());

    function barChartSVG(dias) {
      var W = 560, H = 240, padL = 8, padR = 8, padTop = 26, padBottom = 28;
      var n = dias.length || 1;
      var max = dias.reduce(function (m, d) { return Math.max(m, d.reservaciones); }, 0) || 1;
      var plotH = H - padTop - padBottom, plotW = W - padL - padR;
      var slot = plotW / n, barW = Math.min(48, slot * 0.6), baseY = padTop + plotH;
      var bars = dias.map(function (d) {
        var i = dias.indexOf(d);
        var h = Math.round(plotH * d.reservaciones / max);
        var x = padL + slot * i + (slot - barW) / 2, y = baseY - h, r = Math.min(4, barW / 2);
        var isMax = d.reservaciones === max;
        var path = 'M' + x + ' ' + baseY + ' V' + (y + r) + ' Q' + x + ' ' + y + ' ' + (x + r) + ' ' + y +
          ' H' + (x + barW - r) + ' Q' + (x + barW) + ' ' + y + ' ' + (x + barW) + ' ' + (y + r) + ' V' + baseY + ' Z';
        var lbl = fechaCorta(d.fecha);
        return '<path class="bar" d="' + path + '" fill="' + (isMax ? 'var(--color-azul-institucional-enfoque)' : 'var(--color-azul-institucional)') + '">' +
          '<title>' + esc(lbl + ': ' + d.reservaciones + ' cupos') + '</title></path>' +
          '<text class="bar-value" x="' + (x + barW / 2) + '" y="' + (y - 6) + '" text-anchor="middle">' + d.reservaciones + '</text>' +
          '<text class="bar-label" x="' + (x + barW / 2) + '" y="' + (baseY + 16) + '" text-anchor="middle">' + esc(lbl) + '</text>';
      }).join('');
      var axis = '<line class="axis" x1="' + padL + '" y1="' + baseY + '" x2="' + (W - padR) + '" y2="' + baseY + '"/>';
      return '<svg class="vis-barchart" viewBox="0 0 ' + W + ' ' + H + '" role="img" aria-label="Reservaciones por día">' + axis + bars + '</svg>';
    }

    // --- Cupos por nivel: medidores horizontales, color = entidad nivel ---
    var nm = document.querySelector('[data-nivel-meters]');
    if (nm) nm.innerHTML = nivelMetersHTML(DB.cuposPorNivel());

    function nivelMetersHTML(rows) {
      var CLS = {
        Preescolar: 'vis-nivel--preescolar', Primaria: 'vis-nivel--primaria-alta',
        Secundaria: 'vis-nivel--secundaria', Preparatoria: 'vis-nivel--preparatoria', Universidad: 'vis-nivel--universidad'
      };
      var ORDER = ['Preescolar', 'Primaria', 'Secundaria', 'Preparatoria', 'Universidad'];
      rows.sort(function (a, b) { return ORDER.indexOf(a.categoria) - ORDER.indexOf(b.categoria); });
      if (!rows.length) return '<p class="vis-grupo-card__vacio">Sin talleres en el catálogo.</p>';
      return rows.map(function (r) {
        return '<div class="vis-nivel-meter"><div class="vis-nivel-meter__head">' +
          '<span>' + esc(r.categoria) + '</span><b>' + r.reservado + ' / ' + r.total + ' · ' + r.pct + '%</b></div>' +
          '<div class="vis-nivel-meter__bar"><div class="vis-nivel-meter__fill ' + (CLS[r.categoria] || '') + '" style="width:' + r.pct + '%"></div></div></div>';
      }).join('');
    }

    // --- Grid salas × horas: celdas = escuelas que asisten (vacío si ninguna) ---
    var wrap = byId('horario-wrap');
    if (wrap) {
      wrap.innerHTML = ['matutino', 'vespertino'].map(asistAreaHTML).join('');
      var turnoSel = byId('turno-select');
      function applyTurno() {
        var v = turnoSel ? turnoSel.value : 'matutino';
        wrap.querySelectorAll('.vis-horario-area').forEach(function (a) {
          a.classList.toggle('is-active', a.getAttribute('data-turno') === v);
        });
      }
      if (turnoSel) turnoSel.addEventListener('change', applyTurno);
      applyTurno();
    }

    function asistAreaHTML(turno) {
      var head = '<div class="vis-horario-tiempos"><div class="vis-horario-tiempo vis-horario-tiempo--sala">Sala</div>' +
        cat.horarios[turno].map(function (t) { return '<div class="vis-horario-tiempo">' + t + '</div>'; }).join('') + '</div>';
      var rows = cat.grid[turno].map(function (celdas, i) {
        return '<div class="vis-horario-fila"><div class="vis-horario-celda vis-horario-celda--sala-label">' + esc(cat.salas[i]) + '</div>' +
          celdas.map(asistCeldaHTML).join('') + '</div>';
      }).join('');
      return '<div class="vis-horario-area" data-turno="' + turno + '">' + head + rows + '</div>';
    }

    function asistCeldaHTML(celda) {
      if (celda.tipo === 'sin')
        return '<div class="vis-horario-celda vis-horario-celda--sin-taller"><span class="vis-bloque-label">Sin taller</span></div>';
      if (celda.tipo === 'cer')
        return '<div class="vis-horario-celda vis-horario-celda--cerrado"><span class="vis-bloque-label">Cerrado</span></div>';
      var id = celda.id;
      var escuelas = id ? DB.escuelasEnTaller(id) : [];
      if (!escuelas.length)
        return '<div class="vis-horario-celda vis-asist-celda"><span class="vis-asist-celda__vacio">—</span></div>';
      var titulo = celda.tipo === 'libre' ? 'Zona de acceso libre' : celda.titulo;
      var lista = escuelas.map(function (e) {
        return '<span class="vis-asist-escuela">🏫 ' + esc(e.nombre) + '</span>';
      }).join('');
      return '<div class="vis-horario-celda vis-asist-celda" data-taller-id="' + id + '">' +
        '<span class="vis-horario-celda__nombre" style="font-size:14px">' + esc(titulo) + '</span>' + lista + '</div>';
    }

    // --- Pestañas Calendario | Listado ---
    var tabs = document.querySelectorAll('[data-tab]');
    tabs.forEach(function (tab) {
      tab.addEventListener('click', function () {
        tabs.forEach(function (t) { t.classList.toggle('is-active', t === tab); t.setAttribute('aria-selected', t === tab ? 'true' : 'false'); });
        document.querySelectorAll('[data-tab-panel]').forEach(function (panel) {
          panel.style.display = panel.getAttribute('data-tab-panel') === tab.getAttribute('data-tab') ? '' : 'none';
        });
      });
    });

    // --- Listado: ficha básica por escuela (representante, grupos, alumnos, CCT, hora de llegada) ---
    var listadoBody = document.querySelector('[data-listado-tabla] tbody');
    if (listadoBody) {
      listadoBody.innerHTML = DB.listEscuelas().map(function (e) {
        var ins = e.institucion || {}, resp = e.responsable || {};
        var alumnosPorGrupo = (e.grupos || []).map(function (g) { return g.cantidad_alumnos; }).join(', ') || '—';
        var horaLlegada = '—';
        var reservas = (e.reservas || []).slice().sort(function (a, b) {
          var ta = cat.byId[a.taller_id], tb = cat.byId[b.taller_id];
          if (!ta || !tb) return 0;
          if (ta.turno !== tb.turno) return ta.turno === 'matutino' ? -1 : 1;
          return ta.horario < tb.horario ? -1 : ta.horario > tb.horario ? 1 : 0;
        });
        if (reservas.length) {
          var primero = cat.byId[reservas[0].taller_id];
          if (primero) horaLlegada = horaInicio(primero.horario);
        }
        return '<tr><td class="folio">' + esc(e.folio) + '</td><td>' + esc(ins.nombre) + '</td>' +
          '<td>' + esc(ins.cct) + '</td><td>' + esc(resp.nombre) + '</td>' +
          '<td>' + (e.grupos || []).length + '</td><td>' + esc(alumnosPorGrupo) + '</td>' +
          '<td>' + esc(horaLlegada) + '</td></tr>';
      }).join('');
    }

    // --- Botón "Descargar como PDF": ilustrativo, no implementado ---
    document.querySelectorAll('[data-pdf]').forEach(function (btn) {
      var label = btn.textContent;
      btn.addEventListener('click', function () {
        btn.disabled = true;
        btn.textContent = 'Función ilustrativa — no implementada';
        setTimeout(function () { btn.disabled = false; btn.textContent = label; }, 1800);
      });
    });
  }

  /* =====================================================
     8. Admin · Configuración de la convocatoria
     ===================================================== */
  function initConfiguracion() {
    var cfg = DB.getConfig();
    var inicio = document.querySelector('[data-cfg="inicio"]');
    var fin = document.querySelector('[data-cfg="fin"]');
    if (inicio) inicio.value = cfg.convocatoria_inicio || '';
    if (fin) fin.value = cfg.convocatoria_fin || '';

    function pintarEstado() {
      var c = DB.getConfig();
      document.querySelectorAll('[data-cfg-estado]').forEach(function (el) {
        el.textContent = c.convocatoria_abierta ? 'Abierta' : 'Cerrada';
        el.classList.toggle('is-abierta', !!c.convocatoria_abierta);
        el.classList.toggle('is-cerrada', !c.convocatoria_abierta);
      });
      var abrir = document.querySelector('[data-cfg-abrir]');
      var cerrar = document.querySelector('[data-cfg-cerrar]');
      if (abrir) abrir.disabled = !!c.convocatoria_abierta;
      if (cerrar) cerrar.disabled = !c.convocatoria_abierta;
    }
    pintarEstado();

    function guardarFechas() {
      DB.saveConfig({
        convocatoria_inicio: inicio ? inicio.value : cfg.convocatoria_inicio,
        convocatoria_fin: fin ? fin.value : cfg.convocatoria_fin
      });
      flashGuardado();
    }
    function flashGuardado() {
      var n = document.querySelector('[data-cfg-guardado]');
      if (!n) return;
      n.style.display = 'flex';
      clearTimeout(n._t); n._t = setTimeout(function () { n.style.display = 'none'; }, 2400);
    }

    document.querySelectorAll('[data-cfg-guardar]').forEach(function (b) {
      b.addEventListener('click', function (e) { e.preventDefault(); guardarFechas(); });
    });
    var abrir = document.querySelector('[data-cfg-abrir]');
    var cerrar = document.querySelector('[data-cfg-cerrar]');
    if (abrir) abrir.addEventListener('click', function () { DB.saveConfig({ convocatoria_abierta: true }); pintarEstado(); flashGuardado(); });
    if (cerrar) cerrar.addEventListener('click', function () { DB.saveConfig({ convocatoria_abierta: false }); pintarEstado(); flashGuardado(); });
  }

  /* =====================================================
     Helpers de render compartidos (tarjetas de grupo+reservas / resumen)
     ===================================================== */

  // Tarjetas de grupo con sus talleres reservados — componente único reutilizado
  // en mi-visita, itinerario, itinerario-admin y el detalle de admin-propuestas.
  function grupoReservasHTML(e, opts) {
    opts = opts || {};
    var cat = DB.getCatalogo();
    return (e.grupos || []).map(function (g, i) {
      var reservas = (e.reservas || []).filter(function (r) { return r.grupo_id === g.id; });
      reservas.sort(function (a, b) {
        var ta = cat.byId[a.taller_id], tb = cat.byId[b.taller_id];
        if (!ta || !tb) return 0;
        if (ta.turno !== tb.turno) return ta.turno === 'matutino' ? -1 : 1;
        return ta.horario < tb.horario ? -1 : ta.horario > tb.horario ? 1 : 0;
      });
      var lista = !reservas.length
        ? '<p class="vis-grupo-card__vacio">Sin talleres reservados</p>'
        : '<ul class="vis-grupo-card__talleres">' + reservas.map(function (r) {
            var t = cat.byId[r.taller_id]; if (!t) return '';
            return '<li><span class="vis-grupo-card__taller-info">' +
              esc(fechaCorta(cat.fecha) + ' · ' + horaInicio(t.horario) + ' · ' + t.titulo) + '</span>' +
              (opts.removable ? '<button type="button" class="vis-icon-btn" data-remove-reserva="' + r.id + '" title="Quitar este taller" aria-label="Quitar este taller">' + ICON_CLOSE + '</button>' : '') +
              '</li>';
          }).join('') + '</ul>';
      var link = opts.reservarHref ? '<a class="btn btn-ghost btn-sm" href="' + opts.reservarHref + '" style="margin-top:6px">Ir al catálogo para reservar →</a>' : '';
      return '<div class="vis-grupo-card"><div class="vis-grupo-card__header">Grupo ' + (i + 1) + '</div>' +
        '<div class="vis-grupo-card__body"><span>Grado: ' + esc(g.grado) + '</span><span>Visitantes: ' + g.cantidad_alumnos + '</span>' +
        '<span>Responsable: ' + esc(g.nombre_responsable) + '</span>' + lista + link + '</div></div>';
    }).join('');
  }

  // Pinta y cablea (una sola vez) el contenedor de tarjetas de UNA escuela.
  // opts.onChange(escuelaFresca) se llama tras cada pintado (inicial y tras cada eliminación).
  function renderGrupoReservas(container, escuelaId, opts) {
    if (!container) return;
    opts = opts || {};
    var e = DB.getEscuela(escuelaId);
    container.innerHTML = grupoReservasHTML(e, opts);
    if (opts.removable && !container._wiredRemove) {
      container._wiredRemove = true;
      container.addEventListener('click', function (ev) {
        var btn = ev.target.closest('[data-remove-reserva]');
        if (!btn) return;
        DB.removeReserva(escuelaId, function (r) { return r.id === btn.getAttribute('data-remove-reserva'); });
        renderGrupoReservas(container, escuelaId, opts);
      });
    }
    if (opts.onChange) opts.onChange(e);
  }

  function wireCancelarTodas(escuelaId, onCancel) {
    document.querySelectorAll('[data-cancel-todas]').forEach(function (btn) {
      btn.addEventListener('click', function () {
        DB.updateEscuela(escuelaId, { reservas: [] });
        onCancel();
      });
    });
  }

  // Card unificado de stats en admin-propuestas: escuelas registradas + barra reservados/totales.
  function renderStatCard() {
    var el = document.querySelector('[data-vis-stat-card]');
    if (!el) return;
    var nEscuelas = DB.listEscuelas().length;
    var c = DB.resumenCupos();
    el.innerHTML =
      '<div class="vis-stat-card__num"><strong>' + nEscuelas + '</strong><span>Escuelas registradas</span></div>' +
      '<div class="vis-stat-card__prog">' +
        '<div class="vis-stat-card__prog-head"><span>Cupos reservados</span>' +
          '<b>' + c.reservado.toLocaleString('es-MX') + ' / ' + c.total.toLocaleString('es-MX') + ' · ' + c.pct + '%</b></div>' +
        '<div class="vis-stat-card__bar"><div class="vis-stat-card__bar-fill" style="width:' + c.pct + '%"></div></div>' +
      '</div>';
  }

  function updateResumen(e) {
    var talleres = new Set((e.reservas || []).map(function (r) { return r.taller_id; })).size;
    var total = (e.grupos || []).reduce(function (s, g) { return s + (g.cantidad_alumnos || 0); }, 0);
    document.querySelectorAll('[data-kv="talleres"]').forEach(function (el) { el.textContent = talleres; });
    document.querySelectorAll('[data-kv="grupos"]').forEach(function (el) {
      el.textContent = (e.grupos || []).length + ' (' + total + ' alumnos)';
    });
    document.querySelectorAll('[data-kv="folio"]').forEach(function (el) { el.textContent = e.folio; });
    document.querySelectorAll('[data-kv="institucion"]').forEach(function (el) { el.textContent = (e.institucion || {}).nombre; });
    document.querySelectorAll('[data-kv="nivel"]').forEach(function (el) { el.textContent = e.nivel_educativo; });
    document.querySelectorAll('[data-kv="responsable"]').forEach(function (el) { el.textContent = (e.responsable || {}).nombre; });
    document.querySelectorAll('[data-kv="correo_inst"]').forEach(function (el) { el.textContent = (e.institucion || {}).correo; });
    var rc = document.getElementById('resumen-count'); if (rc) rc.textContent = talleres;
  }
})();

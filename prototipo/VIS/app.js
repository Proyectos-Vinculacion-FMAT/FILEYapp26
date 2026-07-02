/* =========================================================
   FILEY 2027 — Prototipo VIS · interacciones de demostración
   Todo es feature-detect: cada bloque solo actúa si su página
   tiene los elementos correspondientes, así un único app.js sirve
   a todas las pantallas sin lanzar errores donde no aplica.
   ========================================================= */
(function () {
  'use strict';

  /* Tamaño de cada grupo de la escuela demo (Benito Juárez García). */
  var GROUPS = { G1: 35, G2: 35, G3: 20 };
  var ORDER = ['G1', 'G2', 'G3'];

  /* =====================================================
     1. Formulario de propuesta / edición: grupos dinámicos
     ===================================================== */
  (function gruposForm() {
    var list = document.getElementById('grupos-list');
    if (!list) return;
    var addBtn = document.getElementById('add-grupo');
    var totalEl = document.getElementById('total-alumnos');
    var totalBox = document.getElementById('total-box');
    var overNote = document.getElementById('over-note');
    var MAX_GRUPOS = 3;
    var MAX_TOTAL = 105;

    function blocks() { return Array.prototype.slice.call(list.querySelectorAll('[data-grupo]')); }

    function recompute() {
      var bs = blocks();
      var total = 0;
      bs.forEach(function (b, i) {
        var title = b.querySelector('[data-grupo-title]');
        if (title) title.textContent = 'Grupo ' + (i + 1);
        var cant = b.querySelector('.grupo-cant');
        total += cant ? (parseInt(cant.value, 10) || 0) : 0;
        var rm = b.querySelector('[data-grupo-remove]');
        if (rm) rm.style.visibility = bs.length > 1 ? 'visible' : 'hidden';
      });
      if (totalEl) totalEl.textContent = total;
      var over = total > MAX_TOTAL;
      if (totalBox) totalBox.classList.toggle('over', over);
      if (overNote) overNote.style.display = over ? 'flex' : 'none';
      if (addBtn) {
        addBtn.disabled = bs.length >= MAX_GRUPOS;
        addBtn.style.opacity = bs.length >= MAX_GRUPOS ? '.5' : '1';
        addBtn.style.pointerEvents = bs.length >= MAX_GRUPOS ? 'none' : 'auto';
      }
    }

    list.addEventListener('input', function (e) {
      if (e.target.classList.contains('grupo-cant')) recompute();
    });

    list.addEventListener('click', function (e) {
      var rm = e.target.closest('[data-grupo-remove]');
      if (!rm) return;
      var block = rm.closest('[data-grupo]');
      if (block && blocks().length > 1) { block.remove(); recompute(); }
    });

    if (addBtn) addBtn.addEventListener('click', function () {
      var bs = blocks();
      if (bs.length >= MAX_GRUPOS) return;
      var n = bs.length + 1;
      var block = document.createElement('div');
      block.className = 'grupo-block';
      block.setAttribute('data-grupo', '');
      block.innerHTML =
        '<div class="grupo-block__head"><strong data-grupo-title>Grupo ' + n + '</strong>' +
        '<button type="button" class="grupo-remove" data-grupo-remove>Quitar</button></div>' +
        '<div class="grid-3">' +
        '<div class="field"><label>Grado</label><input type="text" placeholder="Ej. Tercero"></div>' +
        '<div class="field"><label>Alumnos</label><input type="number" min="1" max="35" class="grupo-cant" value="30"></div>' +
        '<div class="field"><label>Representante</label><input type="text" placeholder="Nombre del responsable"></div>' +
        '</div>';
      list.appendChild(block);
      recompute();
    });

    recompute();
  }());

  /* =====================================================
     2. Reservar talleres: cupo en vivo + selector de grupos
     ===================================================== */
  (function reservar() {
    var grid = document.querySelector('.vis-horario-wrap');
    if (!grid) return;

    /* ---- Catálogo y horario (datos de demostración) ----
       Ficha básica de cada taller: título, cupo (35 normal · 120 sala de cine)
       y nivel educativo. El nivel lo decide el organizador y puede diferir del
       nivel de registro de la escuela. */
    var NIVEL = {
      pa: { label: 'Primaria Alta',   cls: 'vis-nivel--primaria-alta' },
      pb: { label: 'Primaria - Baja', cls: 'vis-nivel--primaria-baja' },
      se: { label: 'Secundaria',      cls: 'vis-nivel--secundaria' },
      pr: { label: 'Preparatoria',    cls: 'vis-nivel--preparatoria' },
      un: { label: 'Universidad',     cls: 'vis-nivel--universidad' }
    };
    function T(title, nivel, badges) { return { type: 't', title: title, nivel: nivel, base: 35, badges: badges || '' }; }
    function C(title, nivel) { return { type: 't', title: title, nivel: nivel, base: 120, badges: '' }; }
    var SIN = { type: 'sin' }, CER = { type: 'cer' };
    function L(span, badges) { return { type: 'lib', span: span, badges: badges || '' }; }

    var SALAS = ['Ek Balam - Sala 1', 'Ek Balam - Sala 2', 'Ek Balam - Sala 3', 'Ek Balam - Sala 4',
      'Ek Balam - Sala 5', 'Ek Balam - Sala 6', 'Sala de cine 1', 'Sala de cine 2',
      'Zona de exhibición', 'Ludoteca'];
    var TIMES = {
      matutino: ['09:00 – 09:50', '10:00 – 10:50', '11:00 – 11:50', '12:00 – 12:50'],
      vespertino: ['15:00 – 15:50', '16:00 – 16:50', '17:00 – 17:50', '18:00 – 18:50']
    };
    var GRID = {
      matutino: [
        [T('Taller de Literatura Infantil', 'pa', 'G1'), T('Cuentacuentos maya', 'pa'), T('Taller de Literatura Juvenil', 'un'), T('Taller de ilustración', 'pb')],
        [T('Taller de Literatura Infantil', 'pb'), T('Teatro de sombras', 'pb'), SIN, T('Debate y oratoria', 'pr')],
        [T('Taller de Literatura Infantil', 'pa', 'G2'), T('Origami literario', 'pb'), T('Cuentacuentos maya', 'pa'), T('Taller de ilustración', 'pb')],
        [T('Taller de Literatura Infantil', 'pa', 'G3'), SIN, T('Fotografía narrativa', 'pr'), T('Escritura creativa', 'un')],
        [T('Taller de Literatura Juvenil', 'se'), T('Cine y ensayo', 'un'), T('Cómic e historieta', 'se'), T('Club de robótica', 'se')],
        [T('Debate y oratoria', 'pr'), T('Taller de Literatura Infantil', 'pb'), T('Origami literario', 'pb'), SIN],
        [C('Función de cine Infantil', 'pa'), C('Cortometrajes animados', 'pb'), C('Función de cine Infantil', 'pa'), C('Función de cine Juvenil', 'pr')],
        [C('Función de cine Juvenil', 'se'), C('Cineclub preparatoria', 'pr'), C('Matiné de cuentos', 'pb'), C('Función de cine Juvenil', 'un')],
        [CER, L(3, 'G1 G2 G3')],
        [L(4)]
      ],
      vespertino: [
        [T('Taller de Literatura Infantil', 'pa', 'G1'), T('Cuentacuentos maya', 'pa'), T('Debate y oratoria', 'pr'), T('Escritura creativa', 'un')],
        [T('Taller de ilustración', 'pb'), T('Cómic e historieta', 'se'), T('Fotografía narrativa', 'pr'), T('Debate y oratoria', 'pr')],
        [T('Taller de Literatura Infantil', 'pa', 'G2'), T('Cine y ensayo', 'un'), T('Club de robótica', 'se'), T('Escritura creativa', 'un')],
        [T('Cuentacuentos maya', 'pa', 'G3'), T('Cine y ensayo', 'un'), T('Cómic e historieta', 'se'), SIN],
        [T('Taller de ilustración', 'pa'), T('Club de robótica', 'se'), T('Escritura creativa', 'un'), SIN],
        [T('Teatro de sombras', 'pb'), T('Fotografía narrativa', 'pr'), SIN, T('Debate y oratoria', 'pr')],
        [C('Función de cine Infantil', 'pb'), C('Función de cine Juvenil', 'se'), CER, CER],
        [C('Matiné de cuentos', 'pb'), C('Documental joven', 'se'), CER, CER],
        [CER, L(3, 'G1 G2 G3')],
        [L(4)]
      ]
    };

    function esc(s) { return String(s).replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/"/g, '&quot;'); }
    function badgesHTML(str) {
      var gs = (str || '').match(/G\d/g);
      if (!gs) return '';
      return '<div class="vis-celda-badges">' + gs.map(function (g) { return '<span class="vis-grupo-badge">' + g + '</span>'; }).join('') + '</div>';
    }
    function cellHTML(c) {
      if (c.type === 'sin') return '<div class="vis-horario-celda vis-horario-celda--sin-taller"><span class="vis-bloque-label">Sin taller programado</span></div>';
      if (c.type === 'cer') return '<div class="vis-horario-celda vis-horario-celda--cerrado"><span class="vis-bloque-label">Cerrado</span></div>';
      /* Zona de acceso libre = unión de N bloques horarios → ancho = N × columna. */
      if (c.type === 'lib') return '<div class="vis-horario-celda vis-horario-celda--libre" data-taller="Zona de acceso libre" data-libre="1" style="flex:0 0 ' + (c.span * 360) + 'px">' +
        '<span class="vis-bloque-label">Zona de acceso libre</span><span class="vis-horario-celda__cupos">Cupo ilimitado</span>' + badgesHTML(c.badges) + '</div>';
      var n = NIVEL[c.nivel];
      return '<div class="vis-horario-celda" data-taller="' + esc(c.title) + '" data-base="' + c.base + '">' +
        '<span class="vis-horario-celda__nombre">' + esc(c.title) + '</span>' +
        '<div class="vis-horario-celda__meta"><span class="vis-horario-celda__cupos"></span>' +
        '<span>Nivel Educativo: <span class="vis-nivel ' + n.cls + '">' + n.label + '</span></span></div>' +
        badgesHTML(c.badges) + '</div>';
    }
    function areaHTML(turno, active) {
      var head = '<div class="vis-horario-tiempos"><div class="vis-horario-tiempo vis-horario-tiempo--sala">Sala</div>' +
        TIMES[turno].map(function (t) { return '<div class="vis-horario-tiempo">' + t + '</div>'; }).join('') + '</div>';
      var rows = GRID[turno].map(function (cells, i) {
        return '<div class="vis-horario-fila"><div class="vis-horario-celda vis-horario-celda--sala-label">' + SALAS[i] + '</div>' +
          cells.map(cellHTML).join('') + '</div>';
      }).join('');
      return '<div class="vis-horario-area' + (active ? ' is-active' : '') + '" data-turno="' + turno + '">' + head + rows + '</div>';
    }

    grid.innerHTML = areaHTML('matutino', true) + areaHTML('vespertino', false);

    /* Cambio de turno con el dropdown */
    var turnoSel = document.getElementById('turno-select');
    if (turnoSel) turnoSel.addEventListener('change', function () {
      grid.querySelectorAll('.vis-horario-area').forEach(function (a) {
        a.classList.toggle('is-active', a.getAttribute('data-turno') === turnoSel.value);
      });
    });

    function assignedSet(cell) {
      var box = cell.querySelector('.vis-celda-badges');
      if (!box) return new Set();
      return new Set(Array.prototype.map.call(
        box.querySelectorAll('.vis-grupo-badge'),
        function (b) { return b.textContent.trim(); }
      ));
    }

    function assignedSum(cell) {
      var s = 0;
      assignedSet(cell).forEach(function (g) { s += GROUPS[g] || 0; });
      return s;
    }

    function renderBadges(cell, set) {
      var box = cell.querySelector('.vis-celda-badges');
      if (set.size === 0) { if (box) box.remove(); return; }
      if (!box) { box = document.createElement('div'); box.className = 'vis-celda-badges'; cell.appendChild(box); }
      box.innerHTML = ORDER.filter(function (g) { return set.has(g); })
        .map(function (g) { return '<span class="vis-grupo-badge">' + g + '</span>'; }).join('');
    }

    function paintCupo(cell) {
      if (cell.hasAttribute('data-libre')) return;   /* Zona de acceso libre: sin cupo */
      var base = parseInt(cell.getAttribute('data-base'), 10);
      var label = cell.querySelector('.vis-horario-celda__cupos');
      if (!label || isNaN(base)) return;
      var remaining = base - assignedSum(cell);
      label.textContent = 'Cupos disponibles: ' + Math.max(remaining, 0);
      cell.classList.toggle('vis-horario-celda--llena', remaining <= 0);
    }

    function updateSummary() {
      var count = 0;
      grid.querySelectorAll('.vis-horario-celda[data-taller]').forEach(function (cell) {
        if (assignedSet(cell).size > 0) count++;
      });
      var cEl = document.getElementById('reserva-count');
      var dEl = document.getElementById('reserva-detalle');
      if (cEl) cEl.textContent = count;
      if (dEl) dEl.textContent = count === 0
        ? 'Asigna grupos a las actividades para reservarlas.'
        : 'Cupo garantizado para tus grupos en ' + count + ' actividad(es).';
    }

    /* Pinta cupos iniciales (respetando los badges precargados) */
    grid.querySelectorAll('.vis-horario-celda[data-taller]').forEach(paintCupo);
    updateSummary();

    /* --- Popup flotante único --- */
    var popup = document.createElement('div');
    popup.className = 'vis-grupo-selector';
    popup.style.cssText = 'position:fixed;z-index:9999;';
    popup.innerHTML =
      '<p class="vis-grupo-selector__title">Asignar grupos</p>' +
      '<div class="vis-grupo-selector__item" data-group="G1"><span class="vis-radio"></span> Grupo 1 · 35</div>' +
      '<div class="vis-grupo-selector__item" data-group="G2"><span class="vis-radio"></span> Grupo 2 · 35</div>' +
      '<div class="vis-grupo-selector__item" data-group="G3"><span class="vis-radio"></span> Grupo 3 · 20</div>' +
      '<div class="vis-grupo-selector__item"><button type="button" class="vis-todos-btn">Todos los grupos</button></div>';
    document.body.appendChild(popup);

    var currentCell = null;

    function syncRadios() {
      if (!currentCell) return;
      var set = assignedSet(currentCell);
      popup.querySelectorAll('[data-group]').forEach(function (item) {
        item.querySelector('.vis-radio').classList.toggle(
          'vis-radio--selected', set.has(item.getAttribute('data-group')));
      });
    }

    function flash(cell) {
      cell.style.boxShadow = 'inset 0 0 0 2px var(--err-600)';
      setTimeout(function () { cell.style.boxShadow = ''; }, 350);
    }

    /* Sin límite de cupo: Zona de acceso libre (data-libre) o data-base = -1. */
    function isUnlimited(cell) {
      var base = parseInt(cell.getAttribute('data-base'), 10);
      return cell.hasAttribute('data-libre') || base === -1 || isNaN(base);
    }

    function tryToggle(g) {
      if (!currentCell) return;
      var base = parseInt(currentCell.getAttribute('data-base'), 10);
      var set = assignedSet(currentCell);
      if (set.has(g)) {
        set.delete(g);
      } else {
        if (!isUnlimited(currentCell) && (assignedSum(currentCell) + GROUPS[g]) > base) { flash(currentCell); return; }
        set.add(g);
      }
      renderBadges(currentCell, set);
      paintCupo(currentCell);
      syncRadios();
      updateSummary();
    }

    function openPopup(cell, x, y) {
      currentCell = cell;
      syncRadios();
      popup.style.display = 'flex';
      var pw = popup.offsetWidth || 200, ph = popup.offsetHeight || 200;
      popup.style.left = Math.min(x, window.innerWidth - pw - 8) + 'px';
      popup.style.top = Math.min(y, window.innerHeight - ph - 8) + 'px';
    }

    function eligible(cell) {
      return cell && cell.hasAttribute('data-taller');
    }

    grid.addEventListener('click', function (e) {
      var cell = e.target.closest('.vis-horario-celda');
      if (!eligible(cell)) return;
      openPopup(cell, e.clientX, e.clientY);
    });
    grid.addEventListener('contextmenu', function (e) {
      var cell = e.target.closest('.vis-horario-celda');
      if (!eligible(cell)) return;
      e.preventDefault();
      openPopup(cell, e.clientX, e.clientY);
    });

    popup.addEventListener('click', function (e) {
      var item = e.target.closest('[data-group]');
      if (item) { tryToggle(item.getAttribute('data-group')); return; }
      if (e.target.closest('.vis-todos-btn')) {
        if (!currentCell) return;
        var base = parseInt(currentCell.getAttribute('data-base'), 10);
        var all = GROUPS.G1 + GROUPS.G2 + GROUPS.G3;
        if (!isUnlimited(currentCell) && all > base) { flash(currentCell); return; }
        renderBadges(currentCell, new Set(ORDER));
        paintCupo(currentCell); syncRadios(); updateSummary();
      }
    });

    document.addEventListener('click', function (e) {
      if (!popup.contains(e.target) && !e.target.closest('.vis-horario-celda')) {
        popup.style.display = 'none'; currentCell = null;
      }
    });
    document.addEventListener('keydown', function (e) {
      if (e.key === 'Escape') { popup.style.display = 'none'; currentCell = null; }
    });
  }());

  /* =====================================================
     3. Itinerario / reservas admin: quitar una fila
     ===================================================== */
  (function itinerario() {
    var removable = document.querySelector('[data-itin-remove]');
    if (!removable) return;

    function refresh() {
      var items = document.querySelectorAll('.vis-itin-item');
      var count = items.length;
      var resumen = document.getElementById('resumen-count');
      if (resumen) resumen.textContent = count;
      var empty = document.getElementById('itin-empty');
      if (empty) empty.style.display = count === 0 ? 'flex' : 'none';
    }

    document.addEventListener('click', function (e) {
      var btn = e.target.closest('[data-itin-remove]');
      if (!btn) return;
      var item = btn.closest('.vis-itin-item');
      if (item) { item.remove(); refresh(); }
    });

    var confirmar = document.getElementById('confirmar-btn');
    if (confirmar) confirmar.addEventListener('click', function (e) {
      e.preventDefault();
      var note = document.getElementById('confirmado-note');
      if (note) { note.style.display = 'flex'; note.scrollIntoView({ behavior: 'smooth', block: 'center' }); }
    });
  }());

  /* =====================================================
     4. Tabla admin: expandir / colapsar detalle de una fila
     ===================================================== */
  (function tablaAdmin() {
    var toggles = document.querySelectorAll('.vis-tabla__toggle[data-toggle]');
    if (!toggles.length) return;
    toggles.forEach(function (btn) {
      btn.addEventListener('click', function () {
        var row = btn.closest('tr');
        var detail = row ? row.nextElementSibling : null;
        if (!detail || !detail.classList.contains('vis-tabla__row-detail')) return;
        var open = detail.classList.toggle('is-open');
        btn.textContent = btn.textContent.replace(/[▸▾]/, open ? '▾' : '▸');
      });
    });
  }());

}());

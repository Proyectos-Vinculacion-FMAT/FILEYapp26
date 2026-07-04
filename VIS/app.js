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

  /* A8: nivel asignado a cada grupo según el grado declarado (Sexto/Cuarto/Quinto → Primaria Alta). */
  var GROUP_NIVEL = { G1: 'pa', G2: 'pa', G3: 'pa' };

  /* =====================================================
     1. Formulario de propuesta / edición: grupos dinámicos
        + hint de sub-nivel Primaria (A1)
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

    /* A1: mapeo de nombre de grado → código de sub-nivel primaria. */
    var GRADO_MAP = {
      'primero': 'pb', '1ro': 'pb', '1': 'pb', '1°': 'pb',
      'segundo': 'pb', '2do': 'pb', '2': 'pb', '2°': 'pb',
      'tercero': 'pb', '3ro': 'pb', '3': 'pb', '3°': 'pb',
      'cuarto':  'pa', '4to': 'pa', '4': 'pa', '4°': 'pa',
      'quinto':  'pa', '5to': 'pa', '5': 'pa', '5°': 'pa',
      'sexto':   'pa', '6to': 'pa', '6': 'pa', '6°': 'pa'
    };

    function getNivelEd() {
      var sel = document.getElementById('nivel-educativo');
      return sel ? sel.value : '';
    }

    function updateGradoHint(input) {
      var field = input.closest('[data-field-grado]');
      if (!field) return;
      var hint = field.querySelector('.vis-grado-hint');
      if (!hint) return;
      var nivel = getNivelEd();
      if (nivel !== 'Primaria') { hint.textContent = ''; hint.className = 'vis-grado-hint'; return; }
      var cat = GRADO_MAP[input.value.trim().toLowerCase()];
      if (!cat) { hint.textContent = ''; hint.className = 'vis-grado-hint'; return; }
      hint.textContent = cat === 'pa' ? 'Primaria alta (4°–6°)' : 'Primaria baja (1°–3°)';
      hint.className = 'vis-grado-hint vis-grado-hint--' + (cat === 'pa' ? 'alta' : 'baja');
    }

    function updateAllGradoHints() {
      list.querySelectorAll('[data-field-grado] input[type="text"]').forEach(updateGradoHint);
    }

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
      if (e.target.closest('[data-field-grado]')) updateGradoHint(e.target);
    });

    list.addEventListener('click', function (e) {
      var rm = e.target.closest('[data-grupo-remove]');
      if (!rm) return;
      var block = rm.closest('[data-grupo]');
      if (block && blocks().length > 1) { block.remove(); recompute(); }
    });

    /* Actualizar hints cuando cambia el nivel educativo de la escuela. */
    var nivelSel = document.getElementById('nivel-educativo');
    if (nivelSel) nivelSel.addEventListener('change', updateAllGradoHints);

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
        '<div class="field" data-field-grado>' +
          '<label>Grado <span class="req">*</span></label>' +
          '<input type="text" placeholder="Ej. Tercero" data-vis-required>' +
          '<span class="vis-grado-hint"></span>' +
          '<span class="field__err">Este campo es obligatorio</span>' +
        '</div>' +
        '<div class="field">' +
          '<label>Alumnos <span class="req">*</span></label>' +
          '<input type="number" min="1" max="35" class="grupo-cant" value="30" data-vis-required>' +
          '<span class="field__err">Este campo es obligatorio</span>' +
        '</div>' +
        '<div class="field">' +
          '<label>Representante del grupo <span class="req">*</span></label>' +
          '<input type="text" placeholder="Nombre del responsable" data-vis-required>' +
          '<span class="field__err">Este campo es obligatorio</span>' +
        '</div>' +
        '</div>';
      list.appendChild(block);
      recompute();
    });

    recompute();
    updateAllGradoHints();
  }());

  /* =====================================================
     2. Reservar talleres: cupo en vivo + selector de grupos
        + validación de nivel educativo (A2, A8, A9)
     ===================================================== */
  (function reservar() {
    var grid = document.querySelector('.vis-horario-wrap');
    if (!grid) return;

    /* ---- Catálogo y horario (datos de demostración) ---- */
    var NIVEL = {
      pe: { label: 'Preescolar',    cls: 'vis-nivel--preescolar' },    /* A2 */
      pa: { label: 'Primaria Alta', cls: 'vis-nivel--primaria-alta' },
      pb: { label: 'Primaria Baja', cls: 'vis-nivel--primaria-baja' },
      se: { label: 'Secundaria',    cls: 'vis-nivel--secundaria' },
      pr: { label: 'Preparatoria',  cls: 'vis-nivel--preparatoria' },
      un: { label: 'Universidad',   cls: 'vis-nivel--universidad' }
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
      if (c.type === 'lib') return '<div class="vis-horario-celda vis-horario-celda--libre" data-taller="Zona de acceso libre" data-libre="1" style="flex:0 0 ' + (c.span * 360) + 'px">' +
        '<span class="vis-bloque-label">Zona de acceso libre</span><span class="vis-horario-celda__cupos">Cupo ilimitado</span>' + badgesHTML(c.badges) + '</div>';
      var n = NIVEL[c.nivel];
      /* A8: data-nivel almacena el código de nivel para validación en tryToggle. */
      return '<div class="vis-horario-celda" data-taller="' + esc(c.title) + '" data-base="' + c.base + '" data-nivel="' + esc(c.nivel) + '">' +
        '<span class="vis-horario-celda__nombre">' + esc(c.title) + '</span>' +
        '<div class="vis-horario-celda__meta"><span class="vis-horario-celda__cupos"></span>' +
        '<span>Nivel: <span class="vis-nivel ' + n.cls + '">' + n.label + '</span></span></div>' +
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

    function colIndex(cell) {
      var fila = cell.closest('.vis-horario-fila');
      if (!fila) return -1;
      return Array.prototype.indexOf.call(fila.children, cell);
    }

    function hasSameTimeConflict(g, cell) {
      if (cell.hasAttribute('data-libre')) return false;
      var col = colIndex(cell);
      if (col < 1) return false;
      var area = cell.closest('.vis-horario-area');
      if (!area) return false;
      var conflict = false;
      area.querySelectorAll('.vis-horario-fila').forEach(function (fila) {
        var c = fila.children[col];
        if (!c || c === cell || !c.hasAttribute('data-taller') || c.hasAttribute('data-libre')) return;
        if (assignedSet(c).has(g)) conflict = true;
      });
      return conflict;
    }

    function showConflict(text) {
      var el = popup.querySelector('.vis-conflict-msg');
      if (!el) {
        el = document.createElement('p');
        el.className = 'vis-conflict-msg';
        el.style.cssText = 'margin:4px 10px 0;font-size:12px;color:#b91c1c;';
        popup.appendChild(el);
      }
      el.textContent = text;
      el.style.display = 'block';
      clearTimeout(el._timer);
      el._timer = setTimeout(function () { el.style.display = 'none'; }, 3000);
    }

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
      if (cell.hasAttribute('data-libre')) return;
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

    grid.querySelectorAll('.vis-horario-celda[data-taller]').forEach(paintCupo);
    updateSummary();

    /* --- Popup flotante único --- */
    var popup = document.createElement('div');
    popup.className = 'vis-grupo-selector';
    popup.style.cssText = 'position:fixed;z-index:9999;';
    /* A9: el título y la nota dejan claro que se reserva el grupo completo. */
    popup.innerHTML =
      '<p class="vis-grupo-selector__title">Asignar grupo completo</p>' +
      '<div class="vis-grupo-selector__item" data-group="G1"><span class="vis-radio"></span> Grupo 1 · 35 alumnos</div>' +
      '<div class="vis-grupo-selector__item" data-group="G2"><span class="vis-radio"></span> Grupo 2 · 35 alumnos</div>' +
      '<div class="vis-grupo-selector__item" data-group="G3"><span class="vis-radio"></span> Grupo 3 · 20 alumnos</div>' +
      '<div class="vis-grupo-selector__item"><button type="button" class="vis-todos-btn">Todos los grupos</button></div>' +
      '<p style="margin:6px 0 0;font-size:11px;color:var(--gris-500);line-height:1.4">Se reserva la totalidad de alumnos del grupo seleccionado.</p>';
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

    function isUnlimited(cell) {
      var base = parseInt(cell.getAttribute('data-base'), 10);
      return cell.hasAttribute('data-libre') || base === -1 || isNaN(base);
    }

    /* A8: categoría de nivel (pa/pb → 'primaria'; se/pr/un → su propio código). */
    function nivelCategory(n) {
      return (n === 'pa' || n === 'pb') ? 'primaria' : (n || '');
    }

    function tryToggle(g) {
      if (!currentCell) return;
      var base = parseInt(currentCell.getAttribute('data-base'), 10);
      var set = assignedSet(currentCell);
      if (set.has(g)) {
        set.delete(g);
      } else {
        if (!isUnlimited(currentCell) && (assignedSum(currentCell) + GROUPS[g]) > base) { flash(currentCell); return; }
        if (hasSameTimeConflict(g, currentCell)) {
          flash(currentCell);
          showConflict(g + ' ya tiene un taller reservado en este horario.');
          return;
        }
        /* A8: validación de nivel educativo. */
        if (!currentCell.hasAttribute('data-libre')) {
          var workshopNivel = currentCell.getAttribute('data-nivel');
          var groupNivel = GROUP_NIVEL[g];
          if (workshopNivel && groupNivel) {
            var wCat = nivelCategory(workshopNivel);
            var gCat = nivelCategory(groupNivel);
            if (wCat && gCat && wCat !== gCat) {
              /* Nivel de escuela distinto al del taller: bloquear. */
              flash(currentCell);
              var wLabel = NIVEL[workshopNivel] ? NIVEL[workshopNivel].label : workshopNivel;
              showConflict('Nivel incompatible: este taller es de ' + wLabel + '.');
              return;
            }
            if (workshopNivel !== groupNivel) {
              /* Mismo nivel de escuela (Primaria) pero sub-nivel diferente: aviso sin bloqueo. */
              var wsLabel = NIVEL[workshopNivel] ? NIVEL[workshopNivel].label : workshopNivel;
              var grLabel = NIVEL[groupNivel] ? NIVEL[groupNivel].label : groupNivel;
              showConflict('Aviso: taller de ' + wsLabel + '; el grupo es ' + grLabel + '.');
            }
          }
        }
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
      var conflictEl = popup.querySelector('.vis-conflict-msg');
      if (conflictEl) conflictEl.style.display = 'none';
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
        var available = ORDER.filter(function (g) { return !hasSameTimeConflict(g, currentCell); });
        var blocked = ORDER.filter(function (g) { return hasSameTimeConflict(g, currentCell); });
        var totalAvail = available.reduce(function (s, g) { return s + (GROUPS[g] || 0); }, 0);
        if (!isUnlimited(currentCell) && totalAvail > base) { flash(currentCell); return; }
        if (blocked.length) showConflict(blocked.join(', ') + (blocked.length === 1 ? ' ya tiene' : ' ya tienen') + ' taller en este horario.');
        renderBadges(currentCell, new Set(available));
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
        btn.classList.toggle('is-open', open);
      });
    });
  }());

  /* =====================================================
     5. Select-wrap: gestión explícita de .is-open
     ===================================================== */
  document.querySelectorAll('.select-wrap').forEach(function (wrap) {
    var sel = wrap.querySelector('select');
    if (!sel) return;
    sel.addEventListener('focus', function () { wrap.classList.add('is-open'); });
    sel.addEventListener('change', function () {
      wrap.classList.remove('is-open');
      sel.blur();
    });
    sel.addEventListener('blur', function () { wrap.classList.remove('is-open'); });
  });

  /* =====================================================
     6. Validación de formulario de propuesta (A4)
        — Bloquea el envío si hay campos obligatorios vacíos
        y muestra mensajes de error en cada campo inválido.
     ===================================================== */
  (function formValidation() {
    var btn = document.querySelector('[data-vis-submit]');
    if (!btn) return;

    function validate() {
      var invalid = false;
      document.querySelectorAll('[data-vis-required]').forEach(function (el) {
        var field = el.closest('.field');
        var empty = !String(el.value).trim();
        if (field) field.classList.toggle('is-invalid', empty);
        if (empty) invalid = true;
      });
      return !invalid;
    }

    btn.addEventListener('click', function () {
      if (validate()) {
        window.location.href = btn.getAttribute('data-href') || 'confirmacion-vis.html';
      } else {
        var first = document.querySelector('.field.is-invalid');
        if (first) first.scrollIntoView({ behavior: 'smooth', block: 'center' });
      }
    });

    /* Limpia el estado de error en cuanto el usuario escribe algo válido. */
    document.addEventListener('input', function (e) {
      if (e.target.hasAttribute('data-vis-required') && String(e.target.value).trim()) {
        var field = e.target.closest('.field');
        if (field) field.classList.remove('is-invalid');
      }
    });
  }());

  /* =====================================================
     7. Admin: selector de taller para dar de baja (A10)
        — Al hacer clic en "Quitar de un taller", se despliega
        un panel con la lista de talleres activos de esa visita.
     ===================================================== */
  (function bajaTaller() {
    document.addEventListener('click', function (e) {
      /* Abrir panel al hacer clic en el botón de baja. */
      var bajaBtn = e.target.closest('[data-baja-btn]');
      if (bajaBtn) {
        var detailCell = bajaBtn.closest('td');
        if (!detailCell) return;
        var panel = detailCell.querySelector('.vis-baja-panel');
        if (!panel) return;
        /* Cerrar cualquier otro panel abierto primero. */
        document.querySelectorAll('.vis-baja-panel.is-open').forEach(function (p) {
          if (p !== panel) p.classList.remove('is-open');
        });
        panel.classList.toggle('is-open');
        return;
      }

      /* Confirmar baja: quitar la fila de la ficha y cerrar el panel. */
      var confirmBtn = e.target.closest('[data-baja-confirm]');
      if (confirmBtn) {
        var panel = confirmBtn.closest('.vis-baja-panel');
        if (!panel) return;
        var checked = panel.querySelector('input[type="radio"]:checked');
        if (!checked) {
          checked = panel.querySelector('input[type="radio"]'); /* demo: usar el primero si no hay selección */
        }
        if (checked) {
          var label = checked.closest('label');
          /* Eliminar la entrada correspondiente de la ficha. */
          var detailCell = panel.closest('td');
          if (detailCell && label) {
            var idx = Array.prototype.indexOf.call(panel.querySelectorAll('input[type="radio"]'), checked);
            var kvValues = detailCell.querySelectorAll('.vis-ficha__value');
            var kvKeys   = detailCell.querySelectorAll('.vis-ficha__key');
            if (kvValues[idx] && kvKeys[idx]) {
              kvValues[idx].closest('.vis-ficha__grid') &&
                (kvValues[idx].parentElement === kvKeys[idx].parentElement) &&
                kvValues[idx].remove();
              kvKeys[idx].remove();
            }
            label.remove();
          }
        }
        panel.classList.remove('is-open');
        return;
      }

      /* Cancelar: solo cerrar el panel. */
      var cancelBtn = e.target.closest('[data-baja-cancel]');
      if (cancelBtn) {
        var panel = cancelBtn.closest('.vis-baja-panel');
        if (panel) panel.classList.remove('is-open');
      }
    });
  }());

}());

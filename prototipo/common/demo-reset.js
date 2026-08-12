/* =========================================================
   FILEY 2027 — Reinicio unificado de la demo
   ---------------------------------------------------------
   El prototipo vive publicado de forma permanente en GitHub
   Pages, así que el estado de localStorage (VIS, EVT, REG)
   se va acumulando entre visitas. Este botón flotante limpia
   TODAS las claves "filey_*" (los tres módulos comparten el
   prefijo) y recarga, dejando la demo como recién sembrada.

   Se carga en cualquier página que tenga estado de demo; no
   depende de FileyDB ni de FileyDemo.
   ========================================================= */
(function () {
  'use strict';

  function clearAll() {
    Object.keys(localStorage)
      .filter(function (k) { return k.indexOf('filey_') === 0; })
      .forEach(function (k) { localStorage.removeItem(k); });
  }

  function injectStyles() {
    if (document.getElementById('filey-reset-css')) return;
    var css = document.createElement('style');
    css.id = 'filey-reset-css';
    css.textContent = [
      '#filey-demo-reset{position:fixed;left:14px;bottom:14px;z-index:9998;display:inline-flex;align-items:center;gap:7px;',
      'background:rgba(255,255,255,.92);color:#6b7686;border:1px solid #e2e7ee;border-radius:999px;padding:6px 13px;',
      'font-size:12.5px;font-weight:600;font-family:var(--font-filey,sans-serif);cursor:pointer;box-shadow:0 4px 14px rgba(16,36,64,.12);',
      'backdrop-filter:saturate(1.2) blur(2px);transition:all .15s ease}',
      '#filey-demo-reset:hover{color:#01457C;border-color:#c8d0db;box-shadow:0 6px 18px rgba(16,36,64,.18)}',
      '#filey-demo-reset .dot{width:7px;height:7px;border-radius:50%;background:#c99213;display:inline-block}',
      '#filey-reset-toast-host{position:fixed;right:18px;bottom:18px;z-index:9999;display:flex;flex-direction:column;gap:10px;max-width:min(92vw,380px)}',
      '#filey-reset-toast-host .filey-toast{display:flex;align-items:flex-start;gap:10px;background:var(--ok-600,#1d8a4e);color:#fff;',
      'padding:12px 15px;border-radius:10px;box-shadow:0 18px 50px rgba(16,36,64,.28);font-size:14px;line-height:1.35;',
      'font-family:var(--font-filey,sans-serif);opacity:0;transform:translateY(12px);transition:opacity .25s ease,transform .25s ease}',
      '#filey-reset-toast-host .filey-toast.show{opacity:1;transform:translateY(0)}'
    ].join('');
    document.head.appendChild(css);
  }

  function toast(msg) {
    var host = document.getElementById('filey-reset-toast-host');
    if (!host) {
      host = document.createElement('div');
      host.id = 'filey-reset-toast-host';
      document.body.appendChild(host);
    }
    var t = document.createElement('div');
    t.className = 'filey-toast';
    t.innerHTML = '<span>✓</span><span>' + msg + '</span>';
    host.appendChild(t);
    requestAnimationFrame(function () { t.classList.add('show'); });
  }

  function injectButton() {
    if (document.getElementById('filey-demo-reset')) return;
    var b = document.createElement('button');
    b.id = 'filey-demo-reset';
    b.type = 'button';
    b.title = 'Reinicia todos los datos de la demo (VIS, EVT, REG)';
    b.innerHTML = '<span class="dot"></span> Reiniciar demo';
    b.addEventListener('click', function () {
      clearAll();
      toast('Demo reiniciada. Los datos vuelven a su estado inicial.');
      setTimeout(function () { location.reload(); }, 650);
    });
    document.body.appendChild(b);
  }

  window.FileyReset = { clearAll: clearAll };

  function init() { injectStyles(); injectButton(); }
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', init);
  else init();
})();

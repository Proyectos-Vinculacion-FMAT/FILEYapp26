/* =========================================================
   FILEY — componentes de interfaz (Alpine.js)

   Aquí vive únicamente el estado de pantalla: qué se ve
   habilitado, dónde está el cursor, cuánto falta para poder
   reenviar. Ninguna regla de negocio: quién puede reenviar y
   cuándo lo decide el servidor (services/otp.py), y esta capa
   solo refleja lo que él responde.

   Las pantallas siguen funcionando sin este archivo — se pierde
   el avance automático entre cajas y los contadores, no la
   posibilidad de entrar.
   ========================================================= */

/**
 * Quitar una fila de una lista editable (los sellos de STD).
 *
 * Es una función suelta y **no un `Alpine.data`**, a propósito. La
 * pantalla declara su estado con un objeto literal —`x-data="{ visibles:
 * 1 }"`— que no depende de este archivo: si esto no cargara, lo único
 * que se rompe es el botón de quitar, y las filas siguen visibles. Con
 * un componente con nombre, un `filey.js` que no llegue deja `visibles`
 * en `undefined`, todos los `x-show` en falso y **la sección entera
 * invisible** — que es peor que no tener JavaScript.
 *
 * Corre los valores hacia arriba en vez de esconder la fila en su sitio:
 * un hueco en medio se lee como un error, y al servidor le da igual
 * porque descarta los nombres vacíos.
 *
 * Los archivos no se pueden reasignar —el navegador no deja escribir en
 * un `<input type=file>`—, así que se limpian los de las filas movidas.
 * Es lo que avisa la plantilla.
 *
 * @returns {number} cuántas filas quedan visibles.
 */
window.fileyQuitarFila = function (raiz, indice, visibles) {
  const nombres = raiz.querySelectorAll('input[type="text"]');
  const archivos = raiz.querySelectorAll('input[type="file"]');
  for (let i = indice; i < visibles - 1; i++) {
    nombres[i].value = nombres[i + 1].value;
    archivos[i].value = '';
  }
  nombres[visibles - 1].value = '';
  archivos[visibles - 1].value = '';
  return Math.max(1, visibles - 1);
};

document.addEventListener('alpine:init', () => {

  /* ---- Avisos flotantes lanzados desde el navegador ----
     Los del servidor llegan por django.contrib.messages; estos son
     para lo que solo sabe la pantalla, como "ese módulo todavía no
     está conectado". Se usan así:  $store.avisos.agregar('texto')  */
  Alpine.store('avisos', {
    lista: [],
    siguienteId: 1,

    agregar(texto, nivel = 'info') {
      const id = this.siguienteId++;
      this.lista.push({ id, texto, nivel });
      setTimeout(() => this.quitar(id), 6000);
    },

    quitar(id) {
      this.lista = this.lista.filter((aviso) => aviso.id !== id);
    },
  });

  /* ---- Pantalla de acceso: habilita el botón con un correo válido ---- */
  Alpine.data('accesoCorreo', () => ({
    correo: '',
    tocado: false,

    // Mismo criterio que usaba el frontend anterior. Es solo para la
    // interfaz: quien valida de verdad el correo es el formulario de
    // Django, que no se puede saltar desde el navegador.
    get valido() {
      return /^[^\s@]+@[^\s@]+\.[^\s@]{2,}$/.test(this.correo.trim());
    },

    get seVeMal() {
      return this.tocado && this.correo.trim() !== '' && !this.valido;
    },
  }));

  /* ---- Pantalla de registro: habilita el botón con los datos completos ---- */
  Alpine.data('formularioRegistro', () => ({
    nombre: '',
    primerApellido: '',
    telefono: '',
    pais: 'MX',

    // Estado y ciudad solo se piden dentro de México (CU-REG-001): un
    // catálogo de 32 entidades mexicanas no describe una dirección en
    // Bogotá. Esto solo los **esconde**; quien decide es el servidor,
    // que los descarta igual si el país no es México.
    get esMexico() {
      return this.pais === 'MX';
    },

    // El segundo apellido y el país no entran en la validación: el
    // primero es opcional (CU-REG-001, E1) y el segundo es un <select>
    // que siempre trae un valor válido. Estas comprobaciones solo
    // encienden el botón antes de tiempo; quien decide es el servidor.
    get nombreValido() {
      return this.nombre.trim().length >= 2;
    },

    get apellidoValido() {
      return this.primerApellido.trim().length >= 2;
    },

    get telefonoValido() {
      return this.telefono.replace(/\D/g, '').length >= 10;
    },

    get completo() {
      return this.nombreValido && this.apellidoValido && this.telefonoValido;
    },
  }));

  /* ---- Pantalla del código: 6 cajas y los dos contadores ---- */
  Alpine.data('codigoOtp', (config) => ({
    digitos: ['', '', '', '', '', ''],
    hayError: false,
    // true cuando el código dejó de servir (expirado o sin intentos):
    // el botón de verificar se apaga hasta pedir uno nuevo.
    requiereNuevo: false,
    vigencia: config.vigencia,
    cooldown: config.cooldown,

    init() {
      this.reloj = setInterval(() => {
        if (this.vigencia > 0) this.vigencia--;
        if (this.cooldown > 0) this.cooldown--;
      }, 1000);
      this.$nextTick(() => this.enfocar(0));
    },

    destroy() {
      clearInterval(this.reloj);
    },

    get codigo() {
      return this.digitos.join('');
    },

    get completo() {
      return this.codigo.length === 6;
    },

    cajas() {
      return Array.from(this.$root.querySelectorAll('.otp-caja'));
    },

    enfocar(i) {
      this.cajas()[i]?.focus();
    },

    formatear(segundos) {
      const m = Math.floor(Math.max(segundos, 0) / 60);
      const s = Math.max(segundos, 0) % 60;
      return `${String(m).padStart(2, '0')}:${String(s).padStart(2, '0')}`;
    },

    alEscribir(i, evento) {
      this.hayError = false;
      const valor = evento.target.value.replace(/\D/g, '').slice(0, 1);
      this.digitos[i] = valor;
      evento.target.value = valor;
      if (valor && i < 5) this.enfocar(i + 1);
      // Con las 6 cajas llenas se envía solo, como en el prototipo.
      if (this.completo) {
        this.$nextTick(() => this.$root.requestSubmit());
      }
    },

    alTeclear(i, evento) {
      if (evento.key === 'Backspace' && !this.digitos[i] && i > 0) {
        evento.preventDefault();
        this.digitos[i - 1] = '';
        this.enfocar(i - 1);
      }
      if (evento.key === 'ArrowLeft' && i > 0) this.enfocar(i - 1);
      if (evento.key === 'ArrowRight' && i < 5) this.enfocar(i + 1);
    },

    alPegar(evento) {
      evento.preventDefault();
      const texto = (evento.clipboardData?.getData('text') || '').replace(/\D/g, '');
      if (!texto) return;
      this.hayError = false;
      texto.slice(0, 6).split('').forEach((digito, j) => (this.digitos[j] = digito));
      this.enfocar(Math.min(texto.length, 5));
      if (this.completo) {
        this.$nextTick(() => this.$root.requestSubmit());
      }
    },

    limpiar() {
      this.digitos = ['', '', '', '', '', ''];
      this.enfocar(0);
    },

    /* Lo dispara el servidor con HX-Trigger cuando el código falló. */
    alFallar(detalle) {
      this.hayError = true;
      this.requiereNuevo = !!detalle.requiereNuevo;
      this.limpiar();
    },

    /* Lo dispara el servidor con HX-Trigger tras un reenvío. El
       cool-down que llega manda sobre el que iba contando aquí: si el
       servidor dice que aún faltan 40 s, son 40 s. */
    alReenviar(detalle) {
      if (detalle.vigencia) this.vigencia = detalle.vigencia;
      if (detalle.cooldown) this.cooldown = detalle.cooldown;
      if (detalle.vigencia) {
        this.hayError = false;
        this.requiereNuevo = false;
        this.limpiar();
      }
    },
  }));
});

/* ══ El puente con el mapa del showfloor ═══════════════════════
   `event-stand-map` es un canvas de Godot embebido en un `<iframe>` que
   habla por `postMessage` (ADR-0008). El contrato entero está en
   `event-stand-map/docs/bridge_protocol.md`; esto es su lado del host.

   El reparto que importa: **el canvas solo dibuja y avisa de dónde se
   pulsó**. El detalle del espacio, el precio y el «añadir a mi
   selección» son de esta página — así el diseño y las palabras cambian
   sin reexportar 39 MB de WASM.

   No es un componente de Alpine: se registra a mano sobre el `<iframe>`
   que exista en la página. Un `Alpine.data` habría hecho que el mapa
   dependiera de que Alpine cargue, y el mapa ya depende de bastante. */
(function () {
  "use strict";

  var CANAL = "event-stand-map";

  function iniciarMapa(marco) {
    /* El origen del canvas se **deduce de su propio `src`**, no de un
       atributo aparte: un `data-origen` que la plantilla se olvide de
       poner deja esto en `"*"`, y con `"*"` no se comprueba de quién
       llega un mensaje ni a quién se le manda. Para un administrador,
       "a quién se le manda" incluye qué editorial reservó qué.

       El contrato lo pide de las dos partes: el canvas fija su lado con
       `?hostOrigin=`, y éste es el nuestro. */
    var origen = new URL(marco.src, window.location.href).origin;
    var urlDatos = marco.dataset.datos;
    var velo = document.getElementById("mapa-velo");
    var tarjeta = document.getElementById("mapa-tarjeta");
    var fondo = document.getElementById("mapa-tarjeta-fondo");
    var loQueTeniaElFoco = null;
    var datos = null;

    function ocultarVelo() {
      if (velo) velo.hidden = true;
    }

    function enviar(mensaje) {
      if (!marco.contentWindow) return;
      mensaje.channel = CANAL;
      marco.contentWindow.postMessage(mensaje, origen);
    }

    /* El canvas pide los datos al arrancar; se cachean para poder
       responder a un segundo `getMapData` sin volver a la red. */
    function servirDatos(reqId) {
      var responder = function (payload) {
        var mensaje = { type: "mapData", payload: payload };
        if (reqId !== undefined) mensaje.reqId = reqId;
        enviar(mensaje);
      };
      if (datos) return responder(datos);
      fetch(urlDatos, { credentials: "same-origin" })
        .then(function (r) {
          if (!r.ok) throw new Error("HTTP " + r.status);
          return r.json();
        })
        .then(function (j) {
          datos = j;
          responder(j);
          /* También aquí, y no solo en `ready`: `ready` dice que Godot
             arrancó, pero lo que hace usable el mapa es tener qué
             dibujar. Si por lo que sea no llegara el `ready` —o llegara
             antes de que este archivo se enganche— el velo se quitaría
             igual en cuanto hay mapa. */
          ocultarVelo();
        })
        .catch(function (e) {
          /* Se deja el velo puesto con su mensaje: un canvas vacío sin
             explicación se lee como "no hay espacios libres". */
          if (velo) velo.dataset.estado = "error";
          console.error("[mapa] no se pudieron cargar los datos", e);
        });
    }

    window.addEventListener("message", function (evento) {
      /* Las dos comprobaciones que el contrato pide: de dónde viene y
         por qué canal. Sin la primera, cualquier pestaña que tenga una
         referencia a esta ventana puede empujarle un mapa. */
      if (evento.origin !== origen) return;
      var m = evento.data;
      if (!m || m.channel !== CANAL) return;

      switch (m.type) {
        case "ready":
          ocultarVelo();
          break;
        case "getMapData":
          servirDatos(m.reqId);
          break;
        case "openStand":
          abrirTarjeta(m.payload);
          break;
        case "standRect":
          /* Se ignora a propósito. Servía para que la tarjeta siguiera
             al espacio al desplazar el mapa; ahora está centrada, así
             que no hay nada que mover. Se deja el caso escrito para que
             no parezca un mensaje olvidado. */
          break;
        case "standClosed":
          cerrarTarjeta(false);
          break;
        case "error":
          console.error("[mapa]", m.payload);
          break;
      }
    });

    /* ── El detalle del espacio, que es cosa de esta página ── */
    /*
       El contrato deja aquí el diálogo entero. Lo que este archivo **no**
       hace es componerlo: el cuerpo lo trae htmx de la misma vista que
       sirve la pantalla propia del espacio. Antes se armaba aquí con lo
       que el canvas manda en `openStand`, y eso dejaba fuera la zona y el
       «qué incluye» —que el canvas no conoce— y ponía el precio en dos
       sitios. */

    function abrirTarjeta(p) {
      if (!tarjeta) return;
      tarjeta.querySelector("[data-campo=clave]").textContent = p.label;

      var cuerpo = document.getElementById("mapa-tarjeta-cuerpo");
      var url = tarjeta.dataset.urlDetalle.replace("__CLAVE__", p.standId);
      if (cuerpo && window.htmx) {
        cuerpo.innerHTML = '<p class="hint">Cargando el detalle…</p>';
        window.htmx.ajax("GET", url, { target: cuerpo, swap: "innerHTML" });
      } else if (cuerpo) {
        /* Sin htmx no hay modal que llenar: se manda a la pantalla
           propia del espacio, que es la misma información. */
        window.location.href = url;
        return;
      }

      /* Quién tenía el foco antes, para devolvérselo al cerrar. Al pulsar
         en el canvas el foco está en el `<iframe>`; sin esto, cerrar deja
         el tabulador al principio de la página. */
      loQueTeniaElFoco = document.activeElement;
      if (fondo) fondo.hidden = false;
      tarjeta.hidden = false;
      /* El foco entra en el diálogo: quien navega con teclado tiene que
         poder cerrarlo sin recorrer la página entera. */
      var cerrar = tarjeta.querySelector("[data-campo=cerrar]");
      if (cerrar) cerrar.focus();
    }

    function cerrarTarjeta(avisar) {
      if (!tarjeta) return;
      tarjeta.hidden = true;
      if (fondo) fondo.hidden = true;
      if (loQueTeniaElFoco && loQueTeniaElFoco.focus) loQueTeniaElFoco.focus();
      loQueTeniaElFoco = null;
      /* Que el canvas quite su contorno de selección. Sin esto se queda
         un espacio marcado que ya no tiene tarjeta detrás. */
      if (avisar !== false) enviar({ type: "clearSelection" });
    }

    if (tarjeta) {
      tarjeta
        .querySelector("[data-campo=cerrar]")
        .addEventListener("click", function () {
          cerrarTarjeta(true);
        });
      /* Las dos formas que espera quien usa un diálogo: pulsar fuera y
         la tecla de escape. Sin ellas, la única salida es la ✕. */
      if (fondo) {
        fondo.addEventListener("click", function () {
          cerrarTarjeta(true);
        });
      }
      document.addEventListener("keydown", function (evento) {
        if (evento.key === "Escape" && !tarjeta.hidden) cerrarTarjeta(true);
      });
      /* Agregado el espacio, el diálogo se cierra solo. Quedarse abierto
         obliga a cerrarlo a mano para seguir eligiendo, que es lo que uno
         va a hacer justo después. Se escucha en la tarjeta y no en el
         formulario porque el formulario lo trae htmx: todavía no existe
         cuando esto corre. */
      tarjeta.addEventListener("htmx:afterRequest", function (evento) {
        var origen = evento.detail && evento.detail.elt;
        if (!origen || !origen.matches("[data-campo=agregar]")) return;
        if (evento.detail.successful) cerrarTarjeta(true);
      });
    }
  }

  document.addEventListener("DOMContentLoaded", function () {
    var marco = document.getElementById("mapa-canvas");
    if (marco) iniciarMapa(marco);
  });
})();

/* ══ Cerrar el modal del panel ═════════════════════════════════
   htmx deja el diálogo dentro de `#modal`; cerrarlo es vaciar ese hueco.
   Tres formas, las tres esperadas de un diálogo: el botón, el velo y la
   tecla de escape.

   Va delegado en `document` y no atado al modal porque el modal **no
   existe** cuando esto corre: lo trae htmx más tarde.

   Sin JavaScript no hay modal —el mismo enlace abre la pantalla suelta—,
   así que aquí no hay nada que degradar. */
(function () {
  "use strict";

  function hueco() {
    return document.getElementById("modal");
  }

  function cerrar() {
    var caja = hueco();
    if (caja) caja.innerHTML = "";
  }

  document.addEventListener("click", function (evento) {
    var caja = hueco();
    var velo = caja && caja.firstElementChild;
    if (!velo) return;
    var destino = evento.target;

    /* El velo cierra **solo si el clic fue en el velo**, comparando el
       elemento y no preguntando por el atributo hacia arriba: el velo
       envuelve al diálogo, así que un `closest("[data-cerrar-modal]")`
       lo encuentra desde cualquier clic de dentro y cerraría el
       formulario a medio llenar. */
    if (destino === velo) return cerrar();

    var boton = destino.closest && destino.closest("[data-cerrar-modal]");
    if (!boton || boton === velo) return;
    evento.preventDefault();
    cerrar();
  });

  document.addEventListener("keydown", function (evento) {
    if (evento.key === "Escape") cerrar();
  });
})();

/* ══ Avisar del formato antes de enviar ════════════════════════
   La ficha de expositor tiene treinta campos. Descubrir al enviar que
   tres están mal —y volver a subir los archivos, que el navegador no
   conserva— es lo que hace que se abandonen los formularios largos.

   **Ninguna regla vive aquí.** Lo que se lee son los atributos que el
   servidor ya puso en el control (`required`, `type`, `pattern`,
   `minlength`), y el `pattern` sale de `comun/validadores.py`, que es el
   mismo módulo que valida de verdad. Este archivo solo decide *cuándo*
   preguntar y *dónde* escribir la respuesta.

   El servidor vuelve a comprobarlo todo igual: esto es un aviso
   temprano, no una puerta. */
(function () {
  "use strict";

  /* Al salir del campo, no al teclear: avisar mientras alguien escribe
     su correo lo marca en rojo desde la primera letra. */
  var EVENTO_QUE_AVISA = "blur";
  /* Una vez marcado, sí conviene reaccionar al teclear — para que el
     rojo se quite en cuanto se arregla, y no al salir otra vez. */
  var EVENTO_QUE_LIMPIA = "input";

  function mensajeDe(control) {
    if (control.validity.valid) return "";
    if (control.validity.valueMissing) return "Este campo es obligatorio.";
    /* `title` lleva la ayuda de formato que puso el servidor; el mensaje
       de fábrica del navegador dice "coincide con el formato solicitado",
       que no le sirve a nadie. */
    if (control.validity.patternMismatch || control.validity.typeMismatch) {
      return control.title || control.validationMessage;
    }
    if (control.validity.tooShort) {
      return "Escribe al menos " + control.minLength + " caracteres.";
    }
    if (control.validity.rangeUnderflow) {
      return "El mínimo es " + control.min + ".";
    }
    return control.validationMessage;
  }

  function revisar(control) {
    /* El mismo `id` al que apunta el `aria-describedby` que
       genera Django: así lo que se escribe aquí lo anuncia el lector
       de pantalla sin nada más. */
    var hueco = document.getElementById(control.id + "_error");
    var malo = !control.checkValidity();
    control.classList.toggle("is-invalid", malo);
    if (malo) {
      control.setAttribute("aria-invalid", "true");
    } else {
      control.removeAttribute("aria-invalid");
    }
    if (hueco) hueco.textContent = malo ? mensajeDe(control) : "";
  }

  function vigilar(campo) {
    /* Los que el servidor ya marcó se vigilan desde el principio; los
       demás, solo después de que alguien los haya tocado una vez. Sin
       eso, saltar por encima de un campo opcional lo pinta de rojo. */
    var tocado = campo.classList.contains("is-invalid");

    campo.addEventListener(EVENTO_QUE_AVISA, function () {
      tocado = true;
      revisar(campo);
    });
    campo.addEventListener(EVENTO_QUE_LIMPIA, function () {
      if (tocado) revisar(campo);
    });
  }

  document.addEventListener("DOMContentLoaded", function () {
    var formularios = document.querySelectorAll("form[data-avisa-formato]");
    Array.prototype.forEach.call(formularios, function (formulario) {
      /* `novalidate` para quedarnos con el aviso: sin él, el navegador
         planta su propio globo y bloquea el envío con un texto que no
         controlamos y que no queda escrito en la página. */
      formulario.setAttribute("novalidate", "novalidate");
      Array.prototype.forEach.call(
        formulario.querySelectorAll("input, select, textarea"),
        vigilar
      );
      /* Al enviar se revisa todo y se lleva el foco al primero que
         falle: en un formulario de treinta campos, el que falla puede
         estar a dos pantallas de distancia del botón. */
      formulario.addEventListener("submit", function (evento) {
        var malos = [];
        Array.prototype.forEach.call(
          formulario.querySelectorAll("input, select, textarea"),
          function (campo) {
            revisar(campo);
            if (!campo.checkValidity()) malos.push(campo);
          }
        );
        if (malos.length) {
          evento.preventDefault();
          malos[0].focus();
          malos[0].scrollIntoView({ block: "center", behavior: "smooth" });
        }
      });
    });
  });
})();


/**
 * Pone o quita el asterisco de obligatorio de un campo, en vivo.
 *
 * Suelta y no dentro de un IIFE porque la usan dos reglas distintas —la
 * semblanza que se vuelve obligatoria al escribir su nombre, y el
 * presentador que hace falta cuando nadie de la publicación asiste—, y
 * duplicarla dejaría dos formas de pintar lo mismo.
 *
 * Cambia también el atributo `required`, que es lo que ve el navegador,
 * no solo el adorno de la etiqueta.
 */
function marcarObligatorio(campo, obligatorio) {
  if (!campo) return;
  campo.required = obligatorio;
  var contenedor = campo.closest('.field');
  var marca = contenedor && contenedor.querySelector('label .req, label .opt');
  if (!marca) return;
  marca.className = obligatorio ? 'req' : 'opt';
  marca.textContent = obligatorio ? '*' : '(opcional)';
}

/* ══ EVT · la captura en cascada de personas ═══════════════════

   La pantalla de propuesta trae **todas** las filas que admite el tipo,
   porque sin JavaScript no habría forma de añadir una y esconderlas del
   servidor dejaría campos inalcanzables. Esto es la mejora encima:

   · se ve solo la primera fila, y las demás aparecen de una en una;
   · la semblanza no se abre hasta que su nombre tiene algo escrito;
   · no se puede agregar a la siguiente hasta completar la anterior.

   Cada bloqueo **se ve y además se explica**: un control gris sin motivo
   se lee como una avería, no como un paso pendiente. Y no se marca con
   el cursor, que no se ve hasta que alguien ya intentó escribir.

   Nada de esto valida: quien impide que se guarde media persona o un
   hueco entre la 1 y la 3 es `validar_personas`, en el servidor. Aquí
   solo se evita llegar hasta el envío para enterarse.

   Se re-aplica tras cada swap de htmx porque elegir otro tipo de
   actividad reemplaza la sección entera.
   ═════════════════════════════════════════════════════════════ */
(function () {
  'use strict';

  function conTexto(campo) {
    return campo && campo.value.trim() !== '';
  }

  function filaCompleta(fila) {
    var nombre = fila.querySelector('input[type="text"]');
    var bloque = fila.querySelector('[data-semblanza]');
    var area = bloque && bloque.querySelector('textarea');
    return conTexto(nombre) && (!area || conTexto(area));
  }

  /* Una fila se enseña si tiene algo escrito, si trae un error que
     señalar, o si ya se reveló a mano. La primera, siempre. */
  function debeVerse(fila) {
    return (
      fila.dataset.indice === '1' ||
      fila.dataset.revelada === '1' ||
      fila.querySelector('.msg-error') !== null ||
      conTexto(fila.querySelector('input[type="text"]')) ||
      conTexto(fila.querySelector('textarea'))
    );
  }

  function refrescar(caja) {
    var filas = Array.prototype.slice.call(caja.querySelectorAll('[data-persona]'));
    var visibles = [];

    filas.forEach(function (fila) {
      var visible = debeVerse(fila);
      fila.hidden = !visible;
      if (visible) visibles.push(fila);

      var nombre = fila.querySelector('input[type="text"]');
      var bloque = fila.querySelector('[data-semblanza]');
      if (!bloque) return;
      var area = bloque.querySelector('textarea');
      var contador = bloque.querySelector('.evt-contador');
      var aviso = bloque.querySelector('[data-bloqueo]');
      var hayNombre = conTexto(nombre);

      /* No se borra lo ya escrito al vaciar el nombre: se apaga y se
         conserva. */
      area.disabled = !hayNombre;
      if (aviso) aviso.hidden = hayNombre;
      /* Y en cuanto hay nombre, su semblanza deja de ser opcional: media
         persona no se puede mandar a un comité. Es la misma regla que
         `validar_personas` hace cumplir en el servidor; esto solo la
         enseña antes de pulsar enviar. */
      marcarObligatorio(area, hayNombre);
      if (contador) {
        contador.hidden = !hayNombre;
        contador.querySelector('[data-cuenta]').textContent = area.value.length;
        contador.classList.toggle('is-tope', area.value.length >= area.maxLength);
      }
    });

    visibles.forEach(function (fila, i) {
      var quitar = fila.querySelector('[data-quitar]');
      // Solo se puede quitar la última, y solo si no es la única.
      if (quitar) quitar.hidden = !(i === visibles.length - 1 && i > 0);
    });

    var boton = caja.querySelector('[data-agregar]');
    var aviso = caja.querySelector('[data-bloqueo-agregar]');
    if (!boton) return;

    var lleno = visibles.length >= filas.length;
    var completas = visibles.every(filaCompleta);
    boton.hidden = lleno;
    boton.disabled = !completas;
    if (aviso) {
      aviso.hidden = lleno || completas;
      aviso.textContent =
        'Completa el nombre y la semblanza para agregar ' +
        (caja.dataset.singular || 'la siguiente') + ' más.';
    }
  }

  function refrescarTodo(raiz) {
    (raiz || document)
      .querySelectorAll('[data-personas]')
      .forEach(refrescar);
  }

  document.addEventListener('click', function (evento) {
    var agregar = evento.target.closest('[data-agregar]');
    if (agregar) {
      var caja = agregar.closest('[data-personas]');
      var siguiente = Array.prototype.find.call(
        caja.querySelectorAll('[data-persona]'),
        function (fila) { return fila.hidden; }
      );
      if (siguiente) siguiente.dataset.revelada = '1';
      refrescar(caja);
      return;
    }

    var quitar = evento.target.closest('[data-quitar]');
    if (quitar) {
      var fila = quitar.closest('[data-persona]');
      // Se vacía además de esconderse: una fila oculta con texto dentro
      // seguiría viajando en el POST.
      fila.querySelectorAll('input[type="text"], textarea').forEach(function (c) {
        c.value = '';
      });
      delete fila.dataset.revelada;
      refrescar(fila.closest('[data-personas]'));
    }
  });

  document.addEventListener('input', function (evento) {
    var caja = evento.target.closest('[data-personas]');
    if (caja) refrescar(caja);
  });

  document.addEventListener('DOMContentLoaded', function () { refrescarTodo(); });
  document.body.addEventListener('htmx:afterSwap', function (evento) {
    refrescarTodo(evento.target);
  });
})();


/* ══ EVT · el adjunto cargado se ve ════════════════════════════

   El control nativo de archivo no dice qué se eligió, y en un formulario
   con dos adjuntos eso deja a cualquiera sin saber si le faltó uno. Al
   elegir, el bloque se queda en verde con el nombre del archivo — y se
   queda: es la única confirmación que hay hasta que se envía.
   ═════════════════════════════════════════════════════════════ */
(function () {
  'use strict';

  document.addEventListener('change', function (evento) {
    var campo = evento.target;
    if (campo.type !== 'file') return;
    var caja = campo.closest('[data-adjunto]');
    if (!caja) return;

    var rotulo = caja.querySelector('[data-adjunto-nombre]');
    var archivo = campo.files && campo.files[0];
    caja.classList.toggle('is-cargado', !!archivo);
    if (rotulo) rotulo.textContent = archivo ? archivo.name : 'Adjuntar archivo';
  });
})();


/* ══ EVT · cuál tipo de actividad está elegido ═════════════════

   Dos cosas que sin JavaScript resuelve la recarga de la página, y que
   con htmx hay que rehacer aquí porque el swap solo cambia la sección 3:

   · **Cuál tipo está elegido.** Los ocho botones viven en la sección 2,
     que no se reemplaza; sin esto se quedarían con el resaltado del tipo
     anterior y nadie sabría qué eligió.
   · **Bajar a lo que acaba de aparecer.** La sección 3 sale debajo del
     pliegue: si la vista no se mueve, elegir un tipo parece no hacer
     nada.
   ═════════════════════════════════════════════════════════════ */
(function () {
  'use strict';

  document.addEventListener('click', function (evento) {
    var boton = evento.target.closest('[data-tipo-opt]');
    if (!boton) return;
    boton.parentNode.querySelectorAll('[data-tipo-opt]').forEach(function (otro) {
      otro.classList.toggle('is-active', otro === boton);
    });
  });

  document.body.addEventListener('htmx:afterSwap', function (evento) {
    var seccion = evento.target;
    if (!seccion || seccion.id !== 'campos-tipo' || seccion.hidden) return;
    seccion.scrollIntoView({ behavior: 'smooth', block: 'start' });
  });
})();


/* ══ EVT · quién sostiene una presentación ═════════════════════

   En libro y revista, la actividad la sostiene un autor —o editor— que
   asista, **o** un presentador. Basta con uno de los dos. Mientras nadie
   de la publicación esté marcado como que asiste, el primer presentador
   pasa a ser obligatorio; en cuanto alguien se marca, deja de serlo.

   Esto **no valida**: quien lo hace cumplir es `exigir_presentador`, en
   el servidor. Aquí solo se adelanta la respuesta, para no descubrirlo
   al pulsar enviar con treinta campos llenos detrás.

   > [!warning] La regla queda escrita en dos sitios
   > Aquí y en `formularios.py`. Se aceptó a sabiendas: la alternativa
   > —pedirle al servidor que repinte la sección con cada clic— vaciaría
   > los `<input type="file">`, porque ningún navegador deja repoblarlos,
   > y quien ya adjuntó la portada la perdería al desmarcar un autor.
   > Si la regla cambia, hay que tocar los dos.
   ═════════════════════════════════════════════════════════════ */
(function () {
  'use strict';

  function conTexto(campo) {
    return campo && campo.value.trim() !== '';
  }

  /* Las listas que llevan casilla de participación son las de la
     publicación —autores, editores—; la que no la lleva, en esos tipos,
     es la de presentadores. */
  function listasDe(seccion) {
    var todas = Array.prototype.slice.call(
      seccion.querySelectorAll('[data-personas]')
    );
    return {
      publicacion: todas.filter(function (caja) {
        return caja.querySelector('input[name$="_participa"]');
      }),
      presentadores: todas.filter(function (caja) {
        return !caja.querySelector('input[name$="_participa"]');
      })[0],
    };
  }

  function alguienAsiste(cajas) {
    return cajas.some(function (caja) {
      return Array.prototype.some.call(
        caja.querySelectorAll('[data-persona]'),
        function (fila) {
          var casilla = fila.querySelector('input[name$="_participa"]');
          return (
            casilla &&
            casilla.checked &&
            conTexto(fila.querySelector('input[type="text"]'))
          );
        }
      );
    });
  }

  function refrescar(seccion) {
    var listas = listasDe(seccion);
    if (!listas.publicacion.length || !listas.presentadores) return;

    var hacenFalta = !alguienAsiste(listas.publicacion);
    var primera = listas.presentadores.querySelector('[data-persona]');
    if (!primera) return;

    marcarObligatorio(primera.querySelector('input[type="text"]'), hacenFalta);
    marcarObligatorio(primera.querySelector('textarea'), hacenFalta);

    var aviso = listas.presentadores.querySelector('[data-aviso-personas]');
    if (aviso) {
      aviso.hidden = !hacenFalta;
      aviso.textContent =
        'Nadie de la publicación está marcado como que asiste, así que hace ' +
        'falta al menos un presentador: la actividad no puede quedarse sin ' +
        'nadie delante.';
    }
  }

  function refrescarTodo() {
    var seccion = document.getElementById('campos-tipo');
    if (seccion) refrescar(seccion);
  }

  ['change', 'input'].forEach(function (evento) {
    document.addEventListener(evento, function (e) {
      if (e.target.closest('#campos-tipo')) refrescarTodo();
    });
  });
  document.addEventListener('DOMContentLoaded', refrescarTodo);
  document.body.addEventListener('htmx:afterSwap', refrescarTodo);
})();

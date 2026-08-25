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

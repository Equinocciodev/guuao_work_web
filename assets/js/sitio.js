/* GUUAO® Work — el JavaScript del sitio. Cuatro bloques, y la página se lee
   entera sin ninguno: el tema, lo que aparece al hacer scroll, el marcador del
   menú y el menú plegable del teléfono. Los tres últimos están copiados de
   ../vendoo_web/assets/js/sitio.js, donde está la historia de cada decisión. */

/* ==========================================================================
   El botón del tema

   El tema elegido ya lo puso el script en línea del <head> ANTES del primer
   pintado (si esperara a este archivo, que va con `defer`, la página
   parpadearía en el tema equivocado). Dos valores guardados y uno implícito:
   'claro' / 'oscuro' (lo eligió la persona) y nada (sigue al sistema). El
   botón alterna partiendo de lo que se VE, para que el primer toque siempre
   cambie algo.
   ========================================================================== */
(function () {
  'use strict';

  var raiz = document.documentElement;
  var CLAVE = 'guuao-work-tema';

  function temaVisible() {
    var elegido = raiz.getAttribute('data-tema');
    if (elegido === 'claro' || elegido === 'oscuro') return elegido;
    var claro = window.matchMedia && window.matchMedia('(prefers-color-scheme: light)').matches;
    return claro ? 'claro' : 'oscuro';
  }

  function rotular(boton) {
    var siguiente = temaVisible() === 'oscuro' ? 'claro' : 'oscuro';
    boton.setAttribute('aria-label', 'Cambiar a tema ' + siguiente);
    boton.setAttribute('title', 'Cambiar a tema ' + siguiente);
  }

  document.addEventListener('DOMContentLoaded', function () {
    var boton = document.querySelector('.tema');
    if (!boton) return;
    rotular(boton);
    boton.addEventListener('click', function () {
      var nuevo = temaVisible() === 'oscuro' ? 'claro' : 'oscuro';
      raiz.setAttribute('data-tema', nuevo);
      try { localStorage.setItem(CLAVE, nuevo); } catch (e) { /* modo privado: dura lo que la pestaña */ }
      rotular(boton);
    });
  });
})();


/* ==========================================================================
   Lo que se mueve al hacer scroll

   Las piezas `.revelar` aparecen UNA vez al entrar en pantalla (y con eso
   arrancan las infografías que llevan dentro), y las cifras `data-cifra`
   cuentan hasta su valor.

   ⚠️ TODO SE VE SIN ESTE ARCHIVO. El <head> pone `data-anim` y lo RETIRA
   solo a los dos segundos si acá no se marca `data-listo`. Lo primero que
   hace este bloque es reclamar esa marca.

   ⚠️ Con `prefers-reduced-motion: reduce` no se anima NADA: se quita
   `data-anim` y cada dibujo queda en su estado final, que ya está en el HTML.

   ⚠️ El umbral es DOBLE (lección de vendoo_web, 3-sep-2026): se da por visto
   lo que muestra el 18 % de sí mismo O lo que ya ocupa el 35 % del visor. Un
   bloque más alto que la pantalla jamás cumpliría lo primero y se quedaría
   en opacity 0 para siempre.
   ========================================================================== */
(function () {
  'use strict';

  var raiz = document.documentElement;
  raiz.setAttribute('data-listo', '1');

  var quieto = window.matchMedia &&
               window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  if (quieto || !('IntersectionObserver' in window)) {
    raiz.removeAttribute('data-anim');
    return;
  }

  function contar(nodo) {
    var fin = parseFloat(nodo.getAttribute('data-cifra'));
    var molde = nodo.getAttribute('data-formato') || '%d';
    if (isNaN(fin)) return;
    var arranque = null;
    function paso(ahora) {
      if (arranque === null) arranque = ahora;
      var t = Math.min((ahora - arranque) / 1100, 1);
      nodo.textContent = molde.replace('%d', Math.round(fin * (1 - Math.pow(1 - t, 3))));
      if (t < 1) requestAnimationFrame(paso);
    }
    requestAnimationFrame(paso);
  }

  var UMBRAL_ELEMENTO = 0.18;
  var UMBRAL_VISOR = 0.35;
  var umbrales = [];
  for (var u = 0; u <= UMBRAL_ELEMENTO + 1e-9; u += 0.02) umbrales.push(Math.round(u * 100) / 100);

  function seVe(e) {
    if (!e.isIntersecting) return false;
    if (e.intersectionRatio >= UMBRAL_ELEMENTO) return true;
    var visor = e.rootBounds ? e.rootBounds.height : window.innerHeight;
    return e.intersectionRect.height >= visor * UMBRAL_VISOR;
  }

  var mirador = new IntersectionObserver(function (entradas) {
    entradas.forEach(function (e) {
      if (!seVe(e)) return;
      e.target.classList.add('visible');
      Array.prototype.forEach.call(e.target.querySelectorAll('[data-cifra]'), contar);
      mirador.unobserve(e.target);
    });
  }, { threshold: umbrales, rootMargin: '0px 0px -6% 0px' });

  Array.prototype.forEach.call(document.querySelectorAll('.revelar'), function (n) {
    mirador.observe(n);
  });
})();


/* ==========================================================================
   El marcador del menú

   Dos ítems del menú son ANCLAS de la portada (/#como, /#tu-telefono), así
   que el `aria-current` escrito en el HTML se quedaría clavado en «Inicio».
   Esto lo mueve según lo que se está leyendo. Reglas de vendoo_web:
   1. El marcado estático es la verdad sin JavaScript.
   2. Se observan TODAS las secciones: cada una hereda el ítem de la última
      ancla del menú que la precede.
   3. La línea de detección va DEBAJO del `scroll-margin-top` ([id] en el CSS:
      alto de cabecera + 20), o al saltar a un ancla se encendería la anterior.
   4. Al hacer clic se marca en el acto y se calla al observador mientras dura
      el desplazamiento suave.
   ========================================================================== */
(function () {
  'use strict';

  var nav = document.querySelector('.nav');
  var cabecera = document.querySelector('.cabecera');
  if (!nav || !('IntersectionObserver' in window)) return;

  var secciones = Array.prototype.slice.call(document.querySelectorAll('main > section'));
  if (!secciones.length) return;

  var enlaces = Array.prototype.slice.call(nav.querySelectorAll('a'));
  var inicio = null;
  var porAncla = {};
  enlaces.forEach(function (a) {
    var href = a.getAttribute('href') || '';
    if (href === '/') { inicio = a; return; }
    if (href.indexOf('/#') === 0) porAncla[href.slice(2)] = a;
  });
  if (!inicio) return;

  var deLaSeccion = [];
  var actual = inicio;
  var propias = 0;
  secciones.forEach(function (s) {
    var id = s.getAttribute('id');
    // `data-menu` dice qué ítem encender cuando la sección no tiene entrada
    // propia y heredar el de arriba sería mentir: «Pantalla por pantalla» va
    // con «Cómo funciona», no con «Tu teléfono», y «Cómo entrar» con «Inicio».
    var pide = s.getAttribute('data-menu');
    if (id && porAncla[id]) { actual = porAncla[id]; propias++; }
    else if (pide === '/') actual = inicio;
    else if (pide && porAncla[pide.slice(2)]) actual = porAncla[pide.slice(2)];
    deLaSeccion.push(actual);
  });
  // Fuera de la portada ninguna sección responde a las anclas: se deja el
  // `aria-current` que la página ya trae escrito.
  if (!propias) return;

  var cruzando = secciones.map(function () { return false; });
  var mudo = 0;

  function marcar(enlace) {
    enlaces.forEach(function (a) {
      if (a === enlace) a.setAttribute('aria-current', 'page');
      else a.removeAttribute('aria-current');
    });
  }
  function calcular() {
    for (var i = 0; i < cruzando.length; i++) if (cruzando[i]) return deLaSeccion[i];
    return deLaSeccion[deLaSeccion.length - 1];
  }
  function repintar() { if (Date.now() >= mudo) marcar(calcular()); }

  var mirador = null;
  function observar() {
    if (mirador) mirador.disconnect();
    var alto = (cabecera ? cabecera.offsetHeight : 64) + 28;
    mirador = new IntersectionObserver(function (entradas) {
      entradas.forEach(function (e) {
        var i = secciones.indexOf(e.target);
        if (i >= 0) cruzando[i] = e.isIntersecting;
      });
      repintar();
    }, { rootMargin: (-alto) + 'px 0px 0px 0px', threshold: 0 });
    secciones.forEach(function (s) { mirador.observe(s); });
  }
  observar();

  nav.addEventListener('click', function (ev) {
    var a = ev.target.closest && ev.target.closest('a');
    if (!a || enlaces.indexOf(a) === -1) return;
    if ((a.getAttribute('href') || '').indexOf('/#') !== 0) return;
    marcar(a);
    mudo = Date.now() + 900;
    setTimeout(function () { mudo = 0; repintar(); }, 950);
  });

  var reloj;
  window.addEventListener('resize', function () {
    clearTimeout(reloj);
    reloj = setTimeout(observar, 200);
  });
})();


/* ==========================================================================
   El menú plegable del teléfono

   ⚠️ ES UNA MEJORA, NO UN REQUISITO: el plegado entero cuelga de
   `:root[data-js]` en el CSS. Sin JavaScript el menú se ve completo en una
   segunda fila. El estado vive en UN solo sitio: el `aria-expanded` del
   botón, que leen el CSS y el lector de pantalla.
   ========================================================================== */
(function () {
  'use strict';

  var boton = document.querySelector('.menu__boton');
  var nav = document.querySelector('.nav');
  if (!boton || !nav) return;

  var CORTE = 1080;   // el mismo de la hoja de estilo: si se mueve allá, acá

  function abierto() { return boton.getAttribute('aria-expanded') === 'true'; }
  function poner(v) { boton.setAttribute('aria-expanded', v ? 'true' : 'false'); }

  boton.addEventListener('click', function () { poner(!abierto()); });

  /* Cualquier <a> de la CABECERA cierra el panel, no solo los del <nav>:
     «Descargar» es hermano del menú, y escuchando solo en el menú el panel se
     quedaba abierto y tapaba el destino (defecto medido en vendoo_web). */
  var cabecera = document.querySelector('.cabecera');
  (cabecera || nav).addEventListener('click', function (ev) {
    if (ev.target.closest && ev.target.closest('a')) poner(false);
  });

  document.addEventListener('keydown', function (ev) {
    if ((ev.key === 'Escape' || ev.key === 'Esc') && abierto()) {
      poner(false);
      boton.focus();
    }
  });

  var reloj;
  window.addEventListener('resize', function () {
    clearTimeout(reloj);
    reloj = setTimeout(function () {
      if (window.innerWidth > CORTE && abierto()) poner(false);
    }, 200);
  });
})();

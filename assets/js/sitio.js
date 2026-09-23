/* GUUAO® Work — lo único que el sitio hace con JavaScript: el botón del tema.

   Todo lo demás funciona con el script bloqueado. El tema elegido ya lo puso
   el script en línea del <head> ANTES del primer pintado (si esperara a este
   archivo, que va con `defer`, la página parpadearía en el tema equivocado).

   Dos valores guardados y uno implícito:
   - 'claro' / 'oscuro': lo eligió la persona y se respeta.
   - nada: sigue al sistema (`prefers-color-scheme`).
   El botón alterna entre claro y oscuro partiendo de lo que se VE, no de lo
   guardado, para que el primer toque siempre cambie algo. */
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

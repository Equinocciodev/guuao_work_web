/* GUUAO® Work — la analítica del sitio: Google Analytics 4 a través de
   Firebase (proyecto `guuaoapp`, app web propia de work.guuao.com).

   Decisión del dueño (23-sep-2026), copiada de ../vendoo_web, y es la ÚNICA
   excepción a la regla de que el sitio no le pide un byte a un tercero. Mide
   visitas y nada más: sin publicidad ni remarketing, y los hosts de anuncios
   (doubleclick, googlesyndication) NO están abiertos en la CSP, a propósito.

   Dos diferencias con el fragmento que entrega la consola de Firebase, las
   mismas de vendoo:

   1. LOS `import` SON DINÁMICOS Y ESPERAN AL EVENTO `load`. Con `import`
      estáticos el navegador baja los ~100 KB del SDK antes de pintar el
      titular. Una visita se cuenta igual medio segundo después.

   2. LAS SEÑALES DE GOOGLE VAN APAGADAS (`allow_google_signals` y
      `allow_ad_personalization_signals`). Encendidas, gtag manda hits a
      `stats.g.doubleclick.net` y a `www.google.com` que la CSP bloquea.

   La versión va FIJADA. Subirla es cambiar `VERSION_SDK` y comprobar en el
   navegador que la consola no reporta bloqueos de CSP: cada host que el SDK
   pida tiene que estar en el <meta> CSP de las cinco páginas y en `_headers`.
   Hoy pide:

     script-src   www.gstatic.com (estos módulos), www.googletagmanager.com
     connect-src  *.google-analytics.com, analytics.google.com,
                  *.analytics.google.com, www.googletagmanager.com,
                  firebase.googleapis.com, firebaseinstallations.googleapis.com
     img-src      *.google-analytics.com, www.googletagmanager.com

   Se carga en las cinco páginas o en ninguna (`tool/verificar.py` lo
   comprueba), y la política de privacidad lo dice (cláusula 6, «El sitio
   web»). Si esto se apaga, se sacan las tres cosas: el script, los hosts de
   la CSP y la frase. */

const VERSION_SDK = '12.19.0';

// La configuración web de Firebase es un IDENTIFICADOR PÚBLICO, no un
// secreto: viaja en cada visita y solo sirve para mandar eventos al proyecto.
const firebaseConfig = {
  apiKey: 'AIzaSyAs0XL0drl89-W9qA18abvCVdsjDVlmubc',
  authDomain: 'guuaoapp.firebaseapp.com',
  projectId: 'guuaoapp',
  storageBucket: 'guuaoapp.firebasestorage.app',
  messagingSenderId: '1001699259851',
  appId: '1:1001699259851:web:08f0a2f3295a98dbc0f24e',
  measurementId: 'G-0YDZ03LJMK'
};

async function medir() {
  const [{ initializeApp }, { initializeAnalytics }] = await Promise.all([
    import(`https://www.gstatic.com/firebasejs/${VERSION_SDK}/firebase-app.js`),
    import(`https://www.gstatic.com/firebasejs/${VERSION_SDK}/firebase-analytics.js`)
  ]);
  const app = initializeApp(firebaseConfig);
  initializeAnalytics(app, {
    config: {
      allow_google_signals: false,
      allow_ad_personalization_signals: false
    }
  });
}

function arrancar() {
  // Un fallo de red hacia Google no es un fallo de la página: se calla.
  medir().catch(function () { /* sin red hacia Google: no se mide y listo */ });
}

if (document.readyState === 'complete') {
  arrancar();
} else {
  window.addEventListener('load', arrancar, { once: true });
}

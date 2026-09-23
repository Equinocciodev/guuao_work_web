# guuao_work_web

Sitio público de **GUUAO® Work** — la app Android de los operadores de tienda
de GUUAO (`com.leiros.guuaowork`, repo `../guuao_work_app`) — servido en
**https://work.guuao.com**.

Existe por **Google Play**: la política de privacidad tiene que vivir en una URL
pública, cargada en la consola **y** dentro de la app, y la ficha necesita una
página de soporte con el canal para pedir la eliminación de datos. Sigue el
molde de `../vendoo_web`, recortado a lo que una app interna necesita.

**HTML, CSS y un poco de JavaScript. Sin framework, sin build y sin
dependencias.** Lo que está en el repositorio es exactamente lo que se sirve, y
cualquiera puede corregir una coma de la política sin instalar nada.

**La única excepción: la analítica** (23-sep-2026, igual que vendoo_web). GA4
por Firebase, proyecto `guuaoapp`, app web propia (`G-0YDZ03LJMK`), cargada
después de `load` y con las señales publicitarias apagadas. Sus hosts de
Google son lo único externo que abre la CSP; el detalle está en
`assets/js/analitica.js`. Si se apaga, se sacan tres cosas juntas: el script,
esos hosts de la CSP y la frase de «El sitio web» en la cláusula 6 de la
política.

## Qué vende esta página — y qué no

GUUAO® Work es **interna**: la cuenta la crea un encargado de tienda, y la app
**no permite registrarse**. El sitio no vende nada; explica qué es, cómo se
entra y qué hace con los datos. Si alguien llega buscando comprar, se le manda
a `guuao.com` (la app de clientes, GUUAO® App, es otra y tiene su propia
política en `guuao.com/legal/privacy`).

## Estructura

```
index.html        Inicio: la portada dinámica (ver «La portada», abajo)
soporte.html      Preguntas rápidas y #eliminar-datos
privacidad.html   Política de privacidad — ESTA URL está en Play y en la app
terminos.html     Términos de uso
404.html          No encontrada (Pages sirve una sola para todo el dominio)
favicon.svg       «El relevo» sobre grafito, con los paths del icono de la app
CNAME             work.guuao.com
robots.txt, sitemap.xml, site.webmanifest
_headers          REFERENCIA: Pages no sirve cabeceras. No se publica.
assets/css/estilo.css   Todo el estilo (docs/ tiene además el suyo, docs.css)
assets/js/sitio.js      Tema, animaciones de entrada, marcador del menú y menú del teléfono
assets/js/analitica.js  GA4 por Firebase (ver arriba)
assets/fonts/           Poppins 400/600/700, subconjunto latino (de vendoo_web)
assets/img/             Íconos (de docs/play/icono_512.png de la app), capturas/ y tiendas/
assets/img/tiendas/     El badge OFICIAL de Google Play (copiado de vendoo_web). No se edita
assets/img/capturas/    Maestras PNG de la portada + sus WebP 360/720/1068 + derivadas.json
tool/verificar.py       El chequeo que corre en CI y en tu máquina
tool/imagenes.py        Recorta las capturas crudas del Pixel y deriva los WebP (a mano)
.github/workflows/publicar.yml
```

### ⚠️ Las URL no se mueven

`/privacidad.html` es la URL cargada en Google Play y **fija** en
`WorkConfig.privacyUrl` de la app, que la abre desde «Acerca de» (una prueba
de la app falla si alguien la cambia allá).
`/privacidad.html#c7` es el canal de eliminación de datos que se declara en el
formulario de Seguridad de los datos. **Renombrar esos archivos o esos `id`
rompe la declaración de Play en silencio.**

### La cabecera y el pie están copiados en cada página

**Son diecisiete, no cinco**: las cinco de la raíz y las doce de `docs/`. `tool/verificar.py`
vigila las cinco y `tool/verificar_docs.py` compara las doce del manual contra la portada.

A propósito, como en vendoo: sin JavaScript que los inyecte, así existen para
cualquiera. **Si cambias una, cámbiala en las cinco.** `tool/verificar.py`
compara las cinco y falla si difieren (lo único que puede cambiar es el
`aria-current="page"`).

## La portada (23-sep-2026)

Encargo del dueño: «para la pantalla de home, algo parecido a lo de vendoo,
haz una página bonita dinámica». Sigue la regla de composición de
`../vendoo_web`: **una idea por sección** —rótulo, titular corto, una frase y
un dibujo que cuente el resto—. Si algo se puede mostrar, no se escribe.

| Sección | Qué muestra |
|---|---|
| Portada | Titular, badge de Play, «Lee el manual» y la nota de que la cuenta la da el encargado. A la derecha, la **captura real de la llamada** en un marco de teléfono, con ondas que laten y el teléfono que zumba |
| Cifras | 1 tienda a la vez · 3 tareas · 60 s para tomar una llamada · 0 avisos sin turno |
| `#que-hace` | Las tres tareas y una infografía: los tres interruptores se encienden, la perilla de «Desliza para encender» viaja y aparece «Estás activo» |
| `#como` | La llamada en tres tiempos: suena en el bolsillo → deslizas (60 s, «No puedo») → «Es tuya. ¡Dale!» |
| `#turno` | El tono que sube y el que baja, la pausa de 5/10/15 min y **los dos relojes** del servidor: 20 min sin conexión (deja de llegar trabajo, el turno sigue) y 90 min (se cierra) |
| `#pantallas` | Seis capturas reales en marco de teléfono (3 + 3 en escritorio, tira deslizable en el teléfono) |
| `#tu-telefono` | La ubicación solo en turno, dibujada sobre las 24 horas del día, y las cuatro promesas de «es tu teléfono» |
| `#entrar` | No hay registro, los cuatro pasos y la ficha de Play |

**Todo lo que dice está sacado de la app** (`../guuao_work_app/CLAUDE.md`,
`docs/MANUAL_USUARIO.md`, la ficha de Play y lo que se ve en las capturas). Si
la app cambia un número —los 60 s de la llamada, los relojes de 20 y 90 min,
los 30 días de la ubicación—, cambia aquí también.

Las infografías son **SVG en línea dibujado a mano**, pintado con clases
(`.d-*`) que leen los tokens del tema —nunca `fill="var(--x)"`—. Llevan tope de
ancho (`.info`, 440 px) y `viewBox` angostos: a 320 px el texto no puede quedar
en 5 px (la lección de vendoo_web).

### Las animaciones, y por qué la página se ve igual sin ellas

Copiado de vendoo_web. El script en línea del `<head>` pone `data-anim` antes
del primer pintado, y **todo lo que se esconde para aparecer cuelga de ese
atributo**. `sitio.js` marca `data-listo`; si a los dos segundos no lo marcó
(script bloqueado, error de red), el `<head>` quita `data-anim` y la página
queda entera y quieta. Con `prefers-reduced-motion: reduce` no se anima nada:
cada dibujo está en su estado final, que es el que trae el HTML. El
observador usa el umbral doble de vendoo (18 % del elemento **o** 35 % del
visor), o un bloque alto nunca aparecería en el teléfono.

⚠️ **Eso cambió el script en línea**, y con él su hash
(`sha256-GCNYPJpU…`): está en las cinco páginas y en `_headers`. Las páginas
de `docs/` que copien la cabecera tienen que llevar el mismo.

⚠️ **Las animaciones no se pueden revisar con `--virtual-time-budget`**: el
reloj virtual no entrega los avisos del `IntersectionObserver`. El estado
final se mira con `--force-prefers-reduced-motion`; el recorrido de verdad,
con un Chrome manejado por CDP (así se comprobó: las 22 piezas `.revelar`
aparecen a 390 y a 1280 px).

### El menú y el camino a Google Play

La cabecera es **Inicio · Cómo funciona · Tu teléfono · Manual · Soporte ·
Privacidad**, el badge oficial de Play a 40 px y el botón del tema. Por
debajo de **1080 px** (medido: la fila pide ~960 y `.envoltura` da 1032) el
menú se pliega tras un botón, como en vendoo_web, y el badge se cambia por
`.descarga-corta`, que va a `/#descargar` —donde están el badge a 48 px y la
nota de que la cuenta la da el encargado—. Sin JavaScript el menú se parte en
renglones en vez de plegarse (a 320 px una barra con scroll cortaba
«Privacidad»). Dos ítems son anclas de la portada, así que un *scroll-spy*
mueve el `aria-current`; `data-menu` en una sección dice qué ítem encender
cuando heredar el de arriba sería mentir (`#entrar` → Inicio).

⚠️ **La ficha de Play contesta 404 hasta que la app salga a producción**
(medido el 23-sep-2026). El enlace se puso igual; se comprueba con
`curl -o /dev/null -w '%{http_code}' 'https://play.google.com/store/apps/details?id=com.leiros.guuaowork'`.
Y el texto no promete que cualquiera pueda usarla: se instala desde Play,
pero sin una cuenta del encargado no hace nada.

El badge es **arte oficial** (Spanish-LATAM, el mismo archivo de vendoo_web):
va como `<img>`, sin re-teñir, sin `hover` ni `opacity`, con su zona de
respeto de ¼ del alto. El detalle y las citas de la guía de Google están en
`../vendoo_web/assets/img/tiendas/README.md`. **Work no tiene App Store.**
`tool/verificar.py` exige que todo enlace a Play nombre `com.leiros.guuaowork`.

### Las capturas

Salen de las **crudas del Pixel 7a** que acompañan la ficha de Play
(`~/Downloads/guuao work play/capturas_crudas/`), no de las compuestas (esas
ya traen marco y título). `tool/imagenes.py --crudas "<carpeta>"` les quita la
barra de estado (100 px) y el borde verde de 6 px que el sistema dibuja
mientras hay una herramienta de automatización conectada, deja la maestra PNG
de 1068 × 2294 y deriva los WebP de 360, 720 y 1068. El marco del teléfono lo
pone el CSS (`.telefono`). Son de **staging** con una operadora ficticia (María
González) y la llamada es la de prueba: por eso se ven «PRUEBAS» y «PRUEBA —
no es trabajo de verdad», y no se retocan. `08_acerca_de` **no se usa**:
muestra una razón social que falta decidir.

**Cambiar una captura son dos pasos**: la maestra nueva y `python3
tool/imagenes.py`. Si falta el segundo, el verificador se pone rojo (huella
en `assets/img/capturas/derivadas.json`).

## La eliminación de cuenta, y por qué no hay botón en la app

Igual que Vendoo: **la app no crea cuentas, así que Play no exige borrarlas
desde la app.** Las preguntas de *Data deletion* del formulario (obligatorias
desde abril de 2024) se contestan con el canal por correo:

- ¿Ofreces una forma de pedir la eliminación de datos? **Sí** →
  `https://work.guuao.com/privacidad.html#c7`.
- El correo es `contacto@guuao.com` (el que se decidió para Work en
  `guuao_app/docs/LANZAMIENTO_TIENDAS_2026-08-17.md`), asunto *Solicitud de
  datos — GUUAO Work*, **30 días hábiles**.
- Cerrar sesión, olvidar el PIN o desinstalar **no borra nada del servidor**, y
  la política lo dice.

## La política dice la verdad de la app, no de un documento

La política parte de `guuao_work_app/docs/play/POLITICA_PRIVACIDAD.md`, pero se
contrastó con el código el 23-sep-2026 y se le agregó lo que faltaba:
**Firebase Analytics, Sentry, el Navigation SDK de Google y las teselas de
OpenStreetMap** (cláusula 6), el reporte del estado del sonido, y los datos del
cliente que la app muestra. Si la app suma un paquete que saca datos del
teléfono, `tool/ci/huella-datos.sh` de la app se queja — y ese es el momento de
tocar también la cláusula 6 de aquí.

## Marca

De `guuao_work_app/docs/MARCA.md`: turquesa `#00CED1` sobre oscuro y `#0C7F84`
sobre claro, grafito `#1B1B1E`, Poppins. **Turquesa = cromo, nunca estado, y
un relleno = una acción.** El verde (`--exito`, `#3DDC84` en oscuro y `#15803D` en claro) es ESTADO —«Estás activo», «Es tuya», el tramo del turno—, en pastilla teñida con borde y nunca pegado a un relleno turquesa. El naranja de GUUAO no existe aquí y el verificador
falla si aparece. El logotipo `GUUAO® [WORK]` está en línea, sacado de
`assets/logos/guuao_work_dark.svg` con el recuadro pintado por CSS
(`.marca__recuadro`) para que cambie con el tema.

Oscuro por defecto, como la app. El claro sigue al sistema o se elige con el
botón; se guarda en `localStorage` (`guuao-work-tema`).

## Verificar y ver en local

```bash
python3 tool/verificar.py            # tiene que terminar en «Sitio en orden»
python3 -m http.server 8765          # y abre http://localhost:8765
```

Si tocas el script en línea del `<head>` cambia su hash: el verificador te dice
el nuevo, y hay que ponerlo en las cinco páginas, en `_headers` y en las de
`docs/`. El verificador también rechaza cualquier `style=`, un `<img>` sin
`alt`/`width`/`height`, un enlace a Play con otro paquete y unas capturas
cuyas WebP no salgan de la maestra actual.

## Publicar

Cada push a `main` corre `publicar.yml`: verifica y, si pasa, publica en GitHub
Pages. **Una sola vez**, en el repositorio:

1. Settings › Pages › Source: **GitHub Actions**.
2. Custom domain: **`work.guuao.com`**, y cuando aparezca, **Enforce HTTPS**.

DNS (Cloudflare, zona `guuao.com`): `CNAME work → equinocciodev.github.io` en
**DNS only (nube gris)**. Con la nube naranja Let's Encrypt no emite y el sitio
se queda sin `https`.

# guuao_work_web

Sitio público de **GUUAO® Work** — la app Android de los operadores de tienda
de GUUAO (`com.leiros.guuaowork`, repo `../guuao_work_app`) — servido en
**https://work.guuao.com**.

Existe por **Google Play**: la política de privacidad tiene que vivir en una URL
pública, cargada en la consola **y** dentro de la app, y la ficha necesita una
página de soporte con el canal para pedir la eliminación de datos. Sigue el
molde de `../vendoo_web`, recortado a lo que una app interna necesita.

**HTML, CSS y un poco de JavaScript. Sin framework, sin build, sin
dependencias y sin analítica.** Lo que está en el repositorio es exactamente lo
que se sirve. Por eso la CSP es `'self'` para todo, y cualquiera puede
corregir una coma de la política sin instalar nada.

## Qué vende esta página — y qué no

GUUAO® Work es **interna**: la cuenta la crea un encargado de tienda, y la app
**no permite registrarse**. El sitio no vende nada; explica qué es, cómo se
entra y qué hace con los datos. Si alguien llega buscando comprar, se le manda
a `guuao.com` (la app de clientes, GUUAO® App, es otra y tiene su propia
política en `guuao.com/legal/privacy`).

## Estructura

```
index.html        Inicio: qué es, las tres tareas, capturas, «es tu teléfono» y cómo entrar
soporte.html      Preguntas rápidas y #eliminar-datos
privacidad.html   Política de privacidad — ESTA URL está en Play y en la app
terminos.html     Términos de uso
404.html          No encontrada (Pages sirve una sola para todo el dominio)
favicon.svg       «El relevo» sobre grafito, con los paths del icono de la app
CNAME             work.guuao.com
robots.txt, sitemap.xml, site.webmanifest
_headers          REFERENCIA: Pages no sirve cabeceras. No se publica.
assets/css/estilo.css   Todo el estilo
assets/js/sitio.js      Solo el botón del tema
assets/fonts/           Poppins 400/600/700, subconjunto latino (de vendoo_web)
assets/img/             Íconos (de docs/play/icono_512.png de la app) y capturas/
tool/verificar.py       El chequeo que corre en CI y en tu máquina
.github/workflows/publicar.yml
```

### ⚠️ Las URL no se mueven

`/privacidad.html` es la URL cargada en Google Play y en la variable
`GUUAO_PRIVACIDAD_URL` del repo de la app, que la hornea en «Acerca de».
`/privacidad.html#c7` es el canal de eliminación de datos que se declara en el
formulario de Seguridad de los datos. **Renombrar esos archivos o esos `id`
rompe la declaración de Play en silencio.**

### La cabecera y el pie están copiados en cada página

A propósito, como en vendoo: sin JavaScript que los inyecte, así existen para
cualquiera. **Si cambias una, cámbiala en las cinco.** `tool/verificar.py`
compara las cinco y falla si difieren (lo único que puede cambiar es el
`aria-current="page"`).

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
un relleno = una acción.** El naranja de GUUAO no existe aquí y el verificador
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
el nuevo, y hay que ponerlo en las cinco páginas y en `_headers`.

## Publicar

Cada push a `main` corre `publicar.yml`: verifica y, si pasa, publica en GitHub
Pages. **Una sola vez**, en el repositorio:

1. Settings › Pages › Source: **GitHub Actions**.
2. Custom domain: **`work.guuao.com`**, y cuando aparezca, **Enforce HTTPS**.

DNS (Cloudflare, zona `guuao.com`): `CNAME work → equinocciodev.github.io` en
**DNS only (nube gris)**. Con la nube naranja Let's Encrypt no emite y el sitio
se queda sin `https`.

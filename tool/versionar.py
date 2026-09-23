#!/usr/bin/env python3
"""Estampa la huella del contenido en cada CSS y JS que enlazan las páginas:

    python3 tool/versionar.py

`/assets/css/estilo.css` pasa a `/assets/css/estilo.css?v=3f9a1c2b7d`, donde
`v` son los diez primeros caracteres del sha256 del archivo.

POR QUÉ (23-sep-2026): work.guuao.com pasa por Cloudflare, y Cloudflare sirve
los recursos con `cache-control: max-age=31536000` (UN AÑO). Una pestaña que
ya tenía la portada abierta se quedaba con el CSS viejo y el HTML nuevo: la
página se veía rota hasta abrir una pestaña nueva. Con la huella en la URL,
un CSS distinto es otra URL y ningún navegador ni caché puede mezclarlos.

Se corre después de tocar cualquier CSS o JS. `tool/verificar.py` y
`tool/verificar_docs.py` fallan si alguna página enlaza una huella vieja o
ninguna, así que olvidarlo no llega a producción.
"""
import hashlib
import pathlib
import re

RAIZ = pathlib.Path(__file__).resolve().parent.parent
PATRON = re.compile(r'((?:href|src)="(/assets/(?:css|js)/[^"?]+\.(?:css|js)))(?:\?v=[0-9a-f]*)?"')


def huella(ruta_web):
    datos = (RAIZ / ruta_web.lstrip('/')).read_bytes()
    return hashlib.sha256(datos).hexdigest()[:10]


def paginas():
    return sorted(list(RAIZ.glob('*.html')) + list((RAIZ / 'docs').glob('*.html')))


def main():
    cambiadas = 0
    for pagina in paginas():
        texto = pagina.read_text(encoding='utf-8')
        nuevo = PATRON.sub(lambda m: '%s?v=%s"' % (m.group(1), huella(m.group(2))), texto)
        if nuevo != texto:
            pagina.write_text(nuevo, encoding='utf-8')
            cambiadas += 1
    print('huellas al día; %d página(s) reescritas' % cambiadas)


if __name__ == '__main__':
    main()

#!/usr/bin/env python3
"""El chequeo del sitio. Corre en CI antes de publicar y en tu máquina:

    python3 tool/verificar.py

Sin dependencias: solo la biblioteca estándar. Revisa, en cada página:

1. HTML bien formado (toda etiqueta que abre, cierra).
2. Metadatos mínimos: lang, title, description, viewport, CSP.
3. Que el hash del script en línea coincida con el de la CSP. Si tocas ese
   script sin actualizar el hash, el navegador lo bloquea en silencio y el
   tema deja de funcionar: acá falla ruidoso y te dice el hash nuevo.
4. Cero recursos externos: ningún src/href de hoja, script, fuente o imagen
   fuera del propio origen. Los enlaces <a> a otros sitios sí se permiten.
5. Enlaces internos y anclas: el archivo existe y el #id también.
6. Cabecera y pie IDÉNTICOS en todas las páginas, salvo el aria-current.
7. Un solo aria-current, y en el enlace de la propia página.
8. El sitemap lista exactamente las páginas indexables.
9. El naranja de GUUAO (#E95019) no aparece en ningún lado (docs/MARCA.md
   de la app: en Work no existe).
10. La analítica está en las cinco páginas (assets/js/analitica.js).
"""
import base64
import hashlib
import pathlib
import re
import sys
from html.parser import HTMLParser
from urllib.parse import urlparse

RAIZ = pathlib.Path(__file__).resolve().parent.parent
DOMINIO = 'work.guuao.com'
PAGINAS = ['index.html', 'soporte.html', 'privacidad.html', 'terminos.html', '404.html']
SIN_INDICE = {'404.html'}
VACIAS = {'area', 'base', 'br', 'col', 'embed', 'hr', 'img', 'input', 'link', 'meta', 'source', 'track', 'wbr'}
# Dentro de <svg> hay elementos que se cierran solos (<path/>): el parser los
# entrega como startendtag y no hace falta listarlos.

errores = []


def error(pagina, msg):
    errores.append(f'{pagina}: {msg}')


class Lector(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.pila = []
        self.ids = set()
        self.refs = []          # (etiqueta, atributo, valor)
        self.scripts_linea = []
        self._en_script = None
        self.meta = {}
        self.lang = None
        self.titulo = ''
        self._en_titulo = False
        self.aria_current = []  # href de los enlaces con aria-current
        self.problemas = []

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if tag == 'html':
            self.lang = a.get('lang')
        if 'id' in a:
            if a['id'] in self.ids:
                self.problemas.append(f'id repetido: {a["id"]}')
            self.ids.add(a['id'])
        for atr in ('href', 'src', 'srcset'):
            if atr in a:
                self.refs.append((tag, atr, a[atr], a.get('rel', '')))
        if tag == 'meta':
            clave = a.get('name') or a.get('http-equiv') or a.get('property')
            if clave:
                self.meta.setdefault(clave.lower(), a.get('content', ''))
        if tag == 'a' and a.get('aria-current') == 'page':
            self.aria_current.append(a.get('href'))
        if tag == 'script' and 'src' not in a and a.get('type') is None:
            self._en_script = []
        if tag == 'title':
            self._en_titulo = True
        if tag not in VACIAS:
            self.pila.append((tag, self.getpos()[0]))

    def handle_startendtag(self, tag, attrs):
        a = dict(attrs)
        if 'id' in a:
            self.ids.add(a['id'])
        for atr in ('href', 'src'):
            if atr in a:
                self.refs.append((tag, atr, a[atr], a.get('rel', '')))

    def handle_endtag(self, tag):
        if tag in VACIAS:
            return
        if tag == 'script' and self._en_script is not None:
            self.scripts_linea.append(''.join(self._en_script))
            self._en_script = None
        if tag == 'title':
            self._en_titulo = False
        if not self.pila or self.pila[-1][0] != tag:
            abierta = self.pila[-1] if self.pila else ('nada', 0)
            self.problemas.append(f'</{tag}> en la línea {self.getpos()[0]} cierra <{abierta[0]}> de la {abierta[1]}')
            # Se intenta recuperar para no reportar en cascada.
            for i in range(len(self.pila) - 1, -1, -1):
                if self.pila[i][0] == tag:
                    del self.pila[i:]
                    break
            return
        self.pila.pop()

    def handle_data(self, data):
        if self._en_script is not None:
            self._en_script.append(data)
        if self._en_titulo:
            self.titulo += data


def leer(pagina):
    texto = (RAIZ / pagina).read_text(encoding='utf-8')
    lector = Lector()
    lector.feed(texto)
    lector.close()
    return texto, lector


def bloque(texto, etiqueta):
    m = re.search(rf'<{etiqueta}\b.*?</{etiqueta}>', texto, re.S)
    return m.group(0) if m else ''


def destino_local(pagina, url):
    """Devuelve (archivo, ancla) para un enlace interno, o None si es externo."""
    u = urlparse(url)
    if u.scheme in ('mailto', 'tel'):
        return None
    if u.scheme or u.netloc:
        if u.netloc == DOMINIO:
            ruta = u.path
        else:
            return None
    else:
        ruta = u.path
    if ruta == '':
        archivo = pagina
    elif ruta.startswith('/'):
        archivo = ruta.lstrip('/') or 'index.html'
    else:
        archivo = str((pathlib.PurePosixPath(pagina).parent / ruta))
    if archivo.endswith('/'):
        archivo += 'index.html'
    return archivo, u.fragment


def main():
    lectores = {}
    textos = {}
    for p in PAGINAS:
        if not (RAIZ / p).exists():
            error(p, 'no existe')
            continue
        textos[p], lectores[p] = leer(p)

    for p, lec in lectores.items():
        texto = textos[p]
        for prob in lec.problemas:
            error(p, prob)
        if lec.pila:
            error(p, 'quedan etiquetas sin cerrar: ' + ', '.join(f'<{t}> ({n})' for t, n in lec.pila))

        # 2. Metadatos
        if lec.lang != 'es-VE':
            error(p, f'lang es {lec.lang!r}, se espera es-VE')
        if not lec.titulo.strip():
            error(p, 'sin <title>')
        for m in ('description', 'viewport', 'content-security-policy'):
            if not lec.meta.get(m):
                error(p, f'falta <meta {m}>')
        if p not in SIN_INDICE and f'<link rel="canonical" href="https://{DOMINIO}' not in texto:
            error(p, 'sin canonical')

        # 3. Hash de los scripts en línea contra la CSP
        csp = lec.meta.get('content-security-policy', '')
        for s in lec.scripts_linea:
            h = base64.b64encode(hashlib.sha256(s.encode('utf-8')).digest()).decode()
            if f"'sha256-{h}'" not in csp:
                error(p, f"el script en línea no está en la CSP: agrega 'sha256-{h}' (también en _headers)")

        # 4 y 5. Recursos y enlaces
        for tag, atr, valor, rel in lec.refs:
            urls = [x.strip().split(' ')[0] for x in valor.split(',')] if atr == 'srcset' else [valor]
            for url in urls:
                # `canonical` y `dns-prefetch` no descargan nada: el primero
                # es un nombre y el segundo solo resuelve el DNS de la
                # analítica, que es la única excepción externa del sitio.
                es_recurso = tag != 'a' and not (
                    tag == 'link' and rel in ('canonical', 'dns-prefetch'))
                d = destino_local(p, url)
                if d is None:
                    if es_recurso:
                        error(p, f'recurso externo: <{tag} {atr}="{url}">')
                    continue
                archivo, ancla = d
                if not (RAIZ / archivo).exists():
                    error(p, f'enlace roto: {url}')
                    continue
                if ancla:
                    ids = lectores[archivo].ids if archivo in lectores else set()
                    if ancla not in ids:
                        error(p, f'ancla inexistente: {url}')

        # 7. aria-current
        propio = '/' if p == 'index.html' else '/' + p
        if len(lec.aria_current) > 1:
            error(p, f'más de un aria-current: {lec.aria_current}')
        if lec.aria_current and lec.aria_current[0] != propio:
            error(p, f'aria-current en {lec.aria_current[0]}, no en la propia página')

        # 10. La analítica: en las cinco páginas o en ninguna. Una página
        # sin ella no se cuenta y el informe miente sin avisar.
        if '<script type="module" src="/assets/js/analitica.js"></script>' not in texto:
            error(p, 'falta la analítica (assets/js/analitica.js)')

        # 9. El naranja
        if re.search(r'#e95019', texto, re.I):
            error(p, 'aparece el naranja #E95019, que en GUUAO Work no existe')

    # 6. Cabecera y pie idénticos
    def normal(html):
        return re.sub(r' aria-current="page"', '', html)
    base = 'index.html'
    if base in textos:
        for etiqueta in ('header', 'footer'):
            ref = normal(bloque(textos[base], etiqueta))
            for p, t in textos.items():
                if normal(bloque(t, etiqueta)) != ref:
                    error(p, f'la <{etiqueta}> no es igual a la de {base}: cámbiala en todas las páginas')

    # 8. Sitemap
    sm = (RAIZ / 'sitemap.xml').read_text(encoding='utf-8')
    en_mapa = set(re.findall(r'<loc>https://' + re.escape(DOMINIO) + r'/([^<]*)</loc>', sm))
    esperadas = {('' if p == 'index.html' else p) for p in PAGINAS if p not in SIN_INDICE}
    if en_mapa != esperadas:
        error('sitemap.xml', f'sobran {sorted(en_mapa - esperadas)} / faltan {sorted(esperadas - en_mapa)}')

    for archivo in ('assets/css/estilo.css', 'assets/js/sitio.js', 'favicon.svg'):
        if re.search(r'#e95019', (RAIZ / archivo).read_text(encoding='utf-8'), re.I):
            error(archivo, 'aparece el naranja #E95019')

    if (RAIZ / 'CNAME').read_text().strip() != DOMINIO:
        error('CNAME', f'debe decir {DOMINIO}')

    if errores:
        print('\n'.join(errores))
        print(f'\n{len(errores)} problema(s).')
        return 1
    print(f'Sitio en orden: {len(lectores)} páginas revisadas.')
    return 0


if __name__ == '__main__':
    sys.exit(main())

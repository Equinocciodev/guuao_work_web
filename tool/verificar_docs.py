#!/usr/bin/env python3
"""El chequeo del MANUAL DEL OPERADOR (docs/*.html). Solo lectura.

    python3 tool/verificar_docs.py

Reusa el lector de tool/verificar.py (sin modificarlo) y revisa en cada
página del manual lo mismo que aquel en las cinco de la raíz, más lo propio
del manual:

1. HTML bien formado, lang es-VE, title, description, viewport, CSP, canonical.
2. El script en línea tiene su hash en la CSP.
3. Cero recursos externos (la analítica y el dns-prefetch aparte).
4. Enlaces internos y anclas existen (también hacia las páginas de la raíz).
5. Cabecera y pie IDÉNTICOS a los de index.html, salvo aria-current.
6. El árbol del manual es IGUAL en todas, y cada página se marca a sí misma
   con aria-current, una sola vez.
7. Un solo <h1>, alt en toda <img>, las imágenes existen.
8. Ni rastro del naranja #E95019 (tampoco en docs.css).
9. La analítica y docs.css cargados.
"""
import base64
import hashlib
import importlib.util
import pathlib
import re
import sys

RAIZ = pathlib.Path(__file__).resolve().parent.parent
spec = importlib.util.spec_from_file_location('verificar', RAIZ / 'tool' / 'verificar.py')
V = importlib.util.module_from_spec(spec)
spec.loader.exec_module(V)

errores = []


def error(p, m):
    errores.append(f'{p}: {m}')


def leer(rel):
    texto = (RAIZ / rel).read_text(encoding='utf-8')
    lec = V.Lector()
    lec.feed(texto)
    lec.close()
    return texto, lec


def sin_current(s):
    return s.replace(' aria-current="page"', '')


def main():
    paginas = sorted(str(p.relative_to(RAIZ)) for p in (RAIZ / 'docs').glob('*.html'))
    if not paginas:
        print('No hay páginas en docs/.')
        return 1
    cache = {}

    def lector_de(rel):
        if rel not in cache:
            cache[rel] = leer(rel)
        return cache[rel]

    idx, _ = lector_de('index.html')
    ref_header = sin_current(V.bloque(idx, 'header'))
    ref_footer = sin_current(V.bloque(idx, 'footer'))
    arbol_ref = None

    for p in paginas:
        texto, lec = lector_de(p)
        for prob in lec.problemas:
            error(p, prob)
        if lec.pila:
            error(p, 'sin cerrar: ' + ', '.join(f'<{t}> ({n})' for t, n in lec.pila))
        if lec.lang != 'es-VE':
            error(p, f'lang {lec.lang!r}')
        if not lec.titulo.strip():
            error(p, 'sin <title>')
        for m in ('description', 'viewport', 'content-security-policy'):
            if not lec.meta.get(m):
                error(p, f'falta <meta {m}>')
        propio = '/docs/' if p == 'docs/index.html' else '/' + p
        if f'<link rel="canonical" href="https://{V.DOMINIO}{propio}">' not in texto:
            error(p, 'canonical ausente o equivocada')
        csp = lec.meta.get('content-security-policy', '')
        for s in lec.scripts_linea:
            h = base64.b64encode(hashlib.sha256(s.encode()).digest()).decode()
            if f"'sha256-{h}'" not in csp:
                error(p, f"script en línea fuera de la CSP (sha256-{h})")
        for tag, atr, valor, rel in lec.refs:
            urls = [x.strip().split(' ')[0] for x in valor.split(',')] if atr == 'srcset' else [valor]
            for url in urls:
                es_recurso = tag != 'a' and not (tag == 'link' and rel in ('canonical', 'dns-prefetch'))
                d = V.destino_local(p, url)
                if d is None:
                    if es_recurso:
                        error(p, f'recurso externo: {url}')
                    continue
                archivo, ancla = d
                if not (RAIZ / archivo).exists():
                    error(p, f'enlace roto: {url}')
                    continue
                if ancla and archivo.endswith('.html'):
                    if ancla not in lector_de(archivo)[1].ids:
                        error(p, f'ancla inexistente: {url}')
        if sin_current(V.bloque(texto, 'header')) != ref_header:
            error(p, 'la cabecera no es la de index.html')
        if sin_current(V.bloque(texto, 'footer')) != ref_footer:
            error(p, 'el pie no es el de index.html')
        arbol = re.search(r'<ul class="arbol">.*?</ul>', texto, re.S)
        if not arbol:
            error(p, 'sin árbol del manual')
        else:
            a = arbol.group(0)
            if arbol_ref is None:
                arbol_ref = sin_current(a)
            elif sin_current(a) != arbol_ref:
                error(p, 'el árbol del manual no es igual al de las demás')
            marcados = re.findall(r'<a href="([^"]+)" aria-current="page"', a)
            if marcados != [propio]:
                error(p, f'el árbol marca {marcados}, se espera [{propio}]')
            if f'href="{propio}"' not in a:
                error(p, 'la página no está en el árbol')
        if len(re.findall(r'<h1[\s>]', texto)) != 1:
            error(p, 'no tiene exactamente un <h1>')
        for img in re.findall(r'<img\b[^>]*>', texto):
            if not re.search(r'\balt="[^"]+"', img):
                error(p, f'<img> sin alt: {img[:60]}')
        if '<script type="module" src="/assets/js/analitica.js"></script>' not in texto:
            error(p, 'falta la analítica')
        if '<link rel="stylesheet" href="/assets/css/docs.css">' not in texto:
            error(p, 'falta docs.css')
        if re.search(r'#e95019', texto, re.I):
            error(p, 'aparece el naranja #E95019')

    if re.search(r'#e95019', (RAIZ / 'assets/css/docs.css').read_text(), re.I):
        error('assets/css/docs.css', 'aparece el naranja #E95019')

    if errores:
        print('\n'.join(errores))
        print(f'\n{len(errores)} problema(s).')
        return 1
    print(f'Manual en orden: {len(paginas)} páginas revisadas.')
    return 0


if __name__ == '__main__':
    sys.exit(main())

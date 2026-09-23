#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Deriva las capturas que sirve la portada. Se corre a mano y se versiona lo
que produce (el sitio no tiene build: lo que está en el repo es lo que se
sirve). Copia recortada de ../vendoo_web/tool/imagenes.py.

    python3 tool/imagenes.py                      # re-deriva desde las maestras
    python3 tool/imagenes.py --crudas "<carpeta>" # recorta las crudas del Pixel y re-deriva

Necesita Pillow con WebP (`pip install pillow`).

1. **Las maestras** (`assets/img/capturas/<nombre>.png`) salen de las capturas
   CRUDAS del Pixel 7a (1080 × 2400) que acompañan la ficha de Play
   (`~/Downloads/guuao work play/capturas_crudas/`). Se les quita:

   - la **barra de estado** (100 px arriba): la hora y la batería del teléfono
     de quien sacó la captura no son de la app, y el marco del sitio ya dice
     «esto es un teléfono»;
   - el **borde verde de 6 px** que el Pixel dibuja a los lados y abajo
     mientras hay una herramienta de automatización conectada. Tampoco es de
     la app (el mismo recorte que hace `armar_capturas.py` de la ficha).

   Queda 1068 × 2294. **No se reescala a 1080**: agrandar un 1 % solo
   emborrona el texto, y el marco se adapta a la proporción que venga.

   `08_acerca_de` NO entra: muestra una razón social que todavía no está
   decidida (ver el README de la carpeta de Play).

2. **Las derivadas WebP**, a 360, 720 y el ancho de la maestra. La caja del
   teléfono mide de 240 a 330 px: mandar la maestra entera a un teléfono de 2×
   es servir cuatro veces los bytes que se ven. El `<img>` de respaldo es la
   maestra PNG.

3. **`derivadas.json`**: la huella SHA-256 de cada maestra. `tool/verificar.py`
   se pone rojo si una maestra cambió y sus WebP son de la anterior.
   **Cambiar una captura es cambiar la maestra Y correr este script.**

Determinista: correrlo dos veces sin cambiar nada no produce diff.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path

try:
    from PIL import Image
except ImportError:  # pragma: no cover
    print('Hace falta Pillow: pip install pillow', file=sys.stderr)
    sys.exit(1)

RAIZ = Path(__file__).resolve().parent.parent
CAPTURAS = RAIZ / 'assets' / 'img' / 'capturas'

# cruda del Pixel -> nombre en el sitio. El orden es el del día de trabajo.
CRUDAS = {
    '01_entrar.png': 'entrar',
    '02_silencio.png': 'silencio',
    '03_elige_tienda.png': 'tienda',
    '04_turno_activo.png': 'turno',
    '05_llamada.png': 'llamada',
    '06_es_tuya.png': 'es-tuya',
    '07_ajustes.png': 'ajustes',
}
TAMANO_CRUDA = (1080, 2400)
ALTO_BARRA_DE_ESTADO = 100
BORDE_SISTEMA = 6

ANCHOS = (360, 720)


def recortar(cruda: Path, destino: Path) -> None:
    with Image.open(cruda) as im:
        if im.size != TAMANO_CRUDA:
            raise SystemExit(f'{cruda.name} mide {im.size}, se espera {TAMANO_CRUDA}')
        b = BORDE_SISTEMA
        cuerpo = im.convert('RGB').crop((b, ALTO_BARRA_DE_ESTADO, im.width - b, im.height - b))
        cuerpo.save(destino, format='PNG', optimize=True)
        print(f'  {cruda.name} -> {destino.name} ({cuerpo.width}×{cuerpo.height})')


def derivar() -> None:
    huellas: dict[str, str] = {}
    for nombre in CRUDAS.values():
        maestra = CAPTURAS / f'{nombre}.png'
        if not maestra.exists():
            raise SystemExit(f'falta la maestra {maestra.relative_to(RAIZ)}: corre con --crudas')
        huellas[maestra.name] = hashlib.sha256(maestra.read_bytes()).hexdigest()
        with Image.open(maestra) as im:
            rgb = im.convert('RGB')
            for ancho in ANCHOS + (rgb.width,):
                alto = round(rgb.height * ancho / rgb.width)
                chica = rgb if ancho == rgb.width else rgb.resize((ancho, alto), Image.LANCZOS)
                # Calidad 82 y method=6: donde una captura de interfaz deja de
                # mostrar halos alrededor de las letras (medido en vendoo_web).
                chica.save(CAPTURAS / f'{nombre}-{ancho}.webp', format='WEBP', quality=82, method=6)
            print(f'  {maestra.name} -> {len(ANCHOS) + 1} webp')
    (CAPTURAS / 'derivadas.json').write_text(
        json.dumps(huellas, indent=2, sort_keys=True) + '\n', encoding='utf-8')


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.split('\n')[0])
    ap.add_argument('--crudas', type=Path, help='carpeta con las capturas crudas del Pixel')
    args = ap.parse_args()
    CAPTURAS.mkdir(parents=True, exist_ok=True)
    if args.crudas:
        print('Maestras:')
        for archivo, nombre in CRUDAS.items():
            recortar(args.crudas / archivo, CAPTURAS / f'{nombre}.png')
    print('Derivadas:')
    derivar()
    return 0


if __name__ == '__main__':
    sys.exit(main())

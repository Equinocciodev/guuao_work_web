#!/usr/bin/env python3
"""Deriva las capturas del manual (/docs/) desde las crudas del Pixel.

    python3 tool/manual_imagenes.py "/ruta/a/capturas_crudas"

Se corre a mano, solo cuando llega una captura nueva. Necesita Pillow.

Las crudas son 1080×2400 del Pixel 7a. A cada una se le quita:
- la barra de estado (100 px arriba): la hora y los iconos del sistema no
  son de la app y envejecen la captura;
- el borde verde de 6 px que Android pinta alrededor durante la grabación
  de pantalla (a los lados y abajo);
- la píldora de gestos del sistema (los últimos ~50 px).

Salen tres archivos por captura en assets/img/manual/:
  manual-<nombre>.jpg       620 px de ancho, el <img> de respaldo
  manual-<nombre>-360.webp  para pantallas chicas
  manual-<nombre>-620.webp  para pantallas densas

⚠️ 08_acerca_de NO se publica (fuera del encargo). Y ninguna captura con
datos de un cliente real entra sin difuminar ANTES de pasar por aquí.
"""
import pathlib
import sys

from PIL import Image

RAIZ = pathlib.Path(__file__).resolve().parent.parent
DESTINO = RAIZ / 'assets' / 'img' / 'manual'
CAJA = (6, 100, 1074, 2350)   # izq, arriba, der, abajo — en px de la cruda

CAPTURAS = {
    '01_entrar.png': 'entrar',
    '02_permisos.png': 'silencio',        # es el aviso de silencio del check-in
    '03_elige_tienda.png': 'elige-tienda',
    '04_turno_activo.png': 'turno-activo',
    '05_llamada.png': 'llamada',
    '06_es_tuya.png': 'es-tuya',
    '07_ajustes.png': 'ajustes',
}


def escalar(im, ancho):
    alto = round(im.height * ancho / im.width)
    return im.resize((ancho, alto), Image.LANCZOS)


def main():
    if len(sys.argv) != 2:
        print(__doc__)
        return 2
    origen = pathlib.Path(sys.argv[1])
    DESTINO.mkdir(parents=True, exist_ok=True)
    for cruda, nombre in CAPTURAS.items():
        im = Image.open(origen / cruda).convert('RGB').crop(CAJA)
        m620 = escalar(im, 620)
        m620.save(DESTINO / f'manual-{nombre}.jpg', quality=80, optimize=True, progressive=True)
        m620.save(DESTINO / f'manual-{nombre}-620.webp', quality=78, method=6)
        escalar(im, 360).save(DESTINO / f'manual-{nombre}-360.webp', quality=78, method=6)
        print(f'manual-{nombre}: 620×{m620.height}')
    return 0


if __name__ == '__main__':
    sys.exit(main())

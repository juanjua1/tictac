from __future__ import annotations
import time
import sys
from pathlib import Path
from typing import Optional

import pyautogui as pg


def wait_and_click(image_path: Path, timeout: float = 10.0, confidence: float = 0.8, click: bool = True, center_offset=(0, 0), region=None) -> bool:
    start = time.time()
    while time.time() - start < timeout:
        loc = pg.locateOnScreen(str(image_path), confidence=confidence, region=region)
        if loc:
            x, y = pg.center(loc)
            x += center_offset[0]
            y += center_offset[1]
            pg.moveTo(x, y, duration=0.15)
            if click:
                pg.click()
            return True
        time.sleep(0.25)
    return False


def type_text(text: str):
    pg.typewrite(text, interval=0.02)


def press_enter():
    pg.press('enter')


def screenshot_region_from_anchor(anchor_path: Path, out_path: Path, pad: int = 20, confidence: float = 0.8, region=None) -> bool:
    loc = pg.locateOnScreen(str(anchor_path), confidence=confidence, region=region)
    if not loc:
        return False
    left = max(0, loc.left - pad)
    top = max(0, loc.top - pad)
    width = loc.width + 2 * pad
    height = loc.height + 2 * pad
    im = pg.screenshot(region=(left, top, width, height))
    out_path.parent.mkdir(parents=True, exist_ok=True)
    im.save(str(out_path))
    return True


def run_visual_flow(dni: str, base_confidence: float = 0.8) -> int:
    """Ejecuta el flujo visual usando imágenes de 'capturas/'."""
    base = Path(__file__).resolve().parents[2]
    anchors = base / 'capturas'
    telefono = anchors / 'cliente.jpeg'
    tipo_doc = anchors / 'tipo.de.documento.jpeg'
    dni_opcion = anchors / 'dni.jpeg'
    numero_doc = anchors / 'numero.documento.jpeg'
    primera_opcion = anchors / 'primera.opcion.jpeg'
    seleccionar_btn = anchors / 'seleccionar.jpeg'
    cliente_score = anchors / 'cliente.score.jpeg'
    captura_final_anchor = anchors / 'caputara.final.jpeg'

    try:
        import os
        step_delay = float(os.getenv('VISUAL_STEP_DELAY_S', '0.8'))
    except Exception:
        step_delay = 0.8

    region = None
    try:
        import os
        rs = os.getenv('VISUAL_REGION')
        if rs:
            x, y, w, h = [int(v.strip()) for v in rs.split(',')]
            region = (x, y, w, h)
            print(f"Usando región limitada: {region}")
    except Exception:
        region = None

    if not wait_and_click(telefono, timeout=12, confidence=base_confidence, region=region):
        print('No se encontró el círculo de Cliente (cliente.jpeg)')
        return 1
    time.sleep(step_delay)

    if not wait_and_click(tipo_doc, timeout=10, confidence=base_confidence, region=region):
        print('No se encontró el combo Tipo de Documento (tipo.de.documento.jpeg)')
        return 1
    time.sleep(step_delay)

    if not wait_and_click(dni_opcion, timeout=10, confidence=base_confidence, region=region):
        print('No se encontró la opción Documento Nacional Identidad (dni.jpeg)')
        return 1
    time.sleep(step_delay)

    if not wait_and_click(numero_doc, timeout=10, confidence=base_confidence, click=True, region=region):
        print('No se encontró la casilla de Número de Documento (numero.documento.jpeg)')
        return 1
    time.sleep(0.2)
    type_text(dni)
    time.sleep(0.2)
    press_enter()
    time.sleep(step_delay + 1.0)

    if not wait_and_click(primera_opcion, timeout=12, confidence=base_confidence, region=region):
        print('No se encontró el círculo de la primera opción (primera.opcion.jpeg)')
        return 1
    time.sleep(step_delay)

    if not wait_and_click(seleccionar_btn, timeout=10, confidence=base_confidence, region=region):
        print('No se encontró el apartado Seleccionar (seleccionar.jpeg)')
        return 1
    time.sleep(step_delay + 0.5)

    if not wait_and_click(cliente_score, timeout=12, confidence=max(0.5, base_confidence - 0.05), region=region):
        print('No se encontró el nombre subrayado (cliente.score.jpeg)')
        return 1
    time.sleep(step_delay)

    out = base / 'capturas' / f'resultado_final_{dni}.png'
    if not screenshot_region_from_anchor(captura_final_anchor, out, pad=30, confidence=max(0.5, base_confidence - 0.1), region=region):
        img = pg.screenshot()
        out.parent.mkdir(parents=True, exist_ok=True)
        img.save(str(out))
        print(f'Captura fallback guardada en {out}')
    else:
        print(f'Captura guardada en {out}')

    print('Flujo visual completado.')
    return 0


if __name__ == '__main__':  # pragma: no cover
    if len(sys.argv) > 1:
        rc = run_visual_flow(dni=sys.argv[1])
    else:
        print('Uso: python runner_visual.py <DNI>')
        rc = 1
    sys.exit(rc)

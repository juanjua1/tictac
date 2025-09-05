from __future__ import annotations
import time
import sys
from pathlib import Path
from typing import Optional

import pyautogui as pg


def _img(path: str | Path) -> Optional[Path]:
    p = Path(path)
    return p if p.exists() else None


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
    # expand region
    left = max(0, loc.left - pad)
    top = max(0, loc.top - pad)
    width = loc.width + 2 * pad
    height = loc.height + 2 * pad
    im = pg.screenshot(region=(left, top, width, height))
    out_path.parent.mkdir(parents=True, exist_ok=True)
    im.save(str(out_path))
    return True


def main() -> int:
    base = Path(__file__).resolve().parents[2]
    anchors = base / 'capturas'
    # Archivos provistos por el usuario
    telefono = anchors / 'cliente.jpeg'  # círculo a la derecha de Cliente
    tipo_doc = anchors / 'tipo.de.documento.jpeg'  # combo "Seleccione..." junto a Tipo de Documento
    dni_opcion = anchors / 'dni.jpeg'  # opción Documento Nacional Identidad
    numero_doc = anchors / 'numero.documento.jpeg'  # casilla a la derecha de "Número de Documento"
    primera_opcion = anchors / 'primera.opcion.jpeg'  # círculo gris a la izquierda de la primera fila
    seleccionar_btn = anchors / 'seleccionar.jpeg'  # botón/sector Seleccionar
    cliente_score = anchors / 'cliente.score.jpeg'  # nombre subrayado en blanco a la derecha de "cliente:"
    captura_final_anchor = anchors / 'caputara.final.jpeg'  # región de referencia a capturar

    # delay configurable (ENV VISUAL_STEP_DELAY_S)
    try:
        import os
        step_delay = float(os.getenv('VISUAL_STEP_DELAY_S', '0.8'))
    except Exception:
        step_delay = 0.8

    # región objetivo (ENV VISUAL_REGION="x,y,w,h") p/ limitar a pantalla 2 (AnyDesk)
    region = None
    try:
        import os
        rs = os.getenv('VISUAL_REGION')
        if rs:
            x, y, w, h = [int(v.strip()) for v in rs.split(',')]
            region = (x, y, w, h)
            print(f"Usando región AnyDesk: {region}")
    except Exception:
        region = None

    # 1) Click en círculo a la derecha de "Cliente"
    if not wait_and_click(telefono, timeout=12, confidence=0.8, region=region):
        print('No se encontró el círculo de Cliente (cliente.jpeg)')
        return 1
    time.sleep(step_delay)

    # 2) Abrir combo "Tipo de Documento" => click en "Seleccione..."
    if not wait_and_click(tipo_doc, timeout=10, confidence=0.8, region=region):
        print('No se encontró el combo Tipo de Documento (tipo.de.documento.jpeg)')
        return 1
    time.sleep(step_delay)

    # 3) Elegir "Documento Nacional Identidad"
    if not wait_and_click(dni_opcion, timeout=10, confidence=0.8, region=region):
        print('No se encontró la opción Documento Nacional Identidad (dni.jpeg)')
        return 1
    time.sleep(step_delay)

    # 4) Foco en "Número de Documento" y tipear 29940807, luego Enter
    if not wait_and_click(numero_doc, timeout=10, confidence=0.8, click=True, region=region):
        print('No se encontró la casilla de Número de Documento (numero.documento.jpeg)')
        return 1
    time.sleep(0.2)
    type_text('29940807')
    time.sleep(0.2)
    press_enter()
    time.sleep(step_delay + 1.0)

    # 5) Seleccionar primera opción de la lista (círculo gris izquierda)
    if not wait_and_click(primera_opcion, timeout=12, confidence=0.8, region=region):
        print('No se encontró el círculo de la primera opción (primera.opcion.jpeg)')
        return 1
    time.sleep(step_delay)

    # 6) Click en "Seleccionar" (apartado debajo)
    if not wait_and_click(seleccionar_btn, timeout=10, confidence=0.8, region=region):
        print('No se encontró el apartado Seleccionar (seleccionar.jpeg)')
        return 1
    time.sleep(step_delay + 0.5)

    # 7) Seleccionar el nombre subrayado en blanco (cliente.score.jpeg)
    if not wait_and_click(cliente_score, timeout=12, confidence=0.75, region=region):
        print('No se encontró el nombre subrayado a la derecha de cliente: (cliente.score.jpeg)')
        return 1
    time.sleep(step_delay)

    # 8) Captura de pantalla del apartado específico
    out = base / 'capturas' / 'resultado_final.png'
    if not screenshot_region_from_anchor(captura_final_anchor, out, pad=30, confidence=0.7, region=region):
        # si falla, tomar captura de pantalla completa como fallback
        img = pg.screenshot()
        out.parent.mkdir(parents=True, exist_ok=True)
        img.save(str(out))
        print(f'Captura fallback guardada en {out}')
    else:
        print(f'Captura guardada en {out}')

    print('Flujo visual completado.')
    return 0


if __name__ == '__main__':
    sys.exit(main())

"""CLI simplificado: solo modo visual (PyAutoGUI).

Uso:
    python -m src.scraper.cli --dni 29940807 [--step-delay 0.8] [--region x,y,w,h]

Opcionalmente se puede usar el ejecutable PyInstaller.
"""

from __future__ import annotations
import argparse
from typing import Optional


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Automatización visual por DNI (solo modo pantalla)")
    p.add_argument("--dni", required=True, help="DNI a ingresar")
    p.add_argument("--step-delay", type=float, default=0.8, help="Segundos entre pasos (default 0.8)")
    p.add_argument("--region", help="Región de pantalla 'x,y,w,h' (opcional, para limitar búsqueda)")
    p.add_argument("--confidence", type=float, default=0.8, help="Confianza base para matching (0.0-1.0)")
    return p.parse_args()


def main() -> int:
    args = parse_args()
    # Propagar parámetros vía variables de entorno para el runner visual
    import os
    os.environ['VISUAL_STEP_DELAY_S'] = str(args.step_delay)
    if args.region:
        os.environ['VISUAL_REGION'] = args.region
    # El runner visual ahora acepta DNI dinámico
    try:
        from ..visual.runner_visual import run_visual_flow
    except Exception as e:
        print(f"Error importando runner visual: {e}")
        return 2
    return run_visual_flow(dni=args.dni, base_confidence=args.confidence)


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())

from __future__ import annotations
import yaml
from pathlib import Path
import sys
import os
from typing import Any, Dict

class FlowSpec:
    def __init__(self, data: Dict[str, Any], path: Path):
        self.data = data
        self.path = path

    @property
    def meta(self) -> Dict[str, Any]:
        return self.data.get("meta", {})

    @property
    def steps(self) -> list[dict]:
        return self.data.get("pasos", [])

    def __repr__(self) -> str:
        return f"FlowSpec(path={self.path}, steps={len(self.steps)})"


def _candidate_paths(name: str | Path) -> list[Path]:
    p = Path(name)
    cands: list[Path] = []
    # 1) Ruta absoluta o relativa desde CWD
    cands.append(p)
    # 2) Carpeta del ejecutable (útil en PyInstaller onefile)
    try:
        exe_dir = Path(sys.executable).parent
        cands.append(exe_dir / p.name)
    except Exception:
        pass
    # 3) Carpeta temporal de PyInstaller (_MEIPASS) donde se extraen los datos
    meipass = getattr(sys, "_MEIPASS", None)
    if meipass:
        cands.append(Path(meipass) / p.name)
        # subcarpetas (por si se empaquetó con prefijo)
        cands.append(Path(meipass) / str(p))
    return cands


def load_flow(path: str | Path) -> FlowSpec:
    last_err: Exception | None = None
    for cand in _candidate_paths(path):
        try:
            if cand.exists():
                with cand.open("r", encoding="utf-8") as f:
                    data = yaml.safe_load(f)
                return FlowSpec(data, cand)
        except Exception as e:
            last_err = e
            continue
    # Si no se encontró por ninguno de los caminos, lanzar un error claro
    raise FileNotFoundError(f"No se pudo cargar el flujo: {path}. Intenté: {', '.join(str(c) for c in _candidate_paths(path))}. Error: {last_err}")

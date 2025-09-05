from __future__ import annotations
import re

def parse_number_es_ar(value: str) -> float | None:
    if not value:
        return None
    # Remover espacios y símbolos comunes
    s = value.strip()
    # Reemplazar separadores: miles '.' y decimal ',' -> '.' decimal
    s = s.replace('.', '').replace(',', '.')
    # Extraer número (opcional $ u otros)
    m = re.search(r"-?\d+(?:\.\d+)?", s)
    if not m:
        return None
    try:
        return float(m.group(0))
    except ValueError:
        return None

from __future__ import annotations
from typing import List

# Placeholder: aquí iría la integración con Meta WhatsApp Cloud API o Twilio.
# Provee una firma simple para futuro uso.

def build_message_text(dni: str, resultados_cf: List[dict]) -> str:
    lines = [f"DNI {dni} - Cuentas Financieras con saldo:"]
    for item in resultados_cf:
        cf = item.get("cf_nombre") or item.get("cf_id") or "CF"
        saldo = item.get("saldo_texto") or str(item.get("saldo_numero", ""))
        lines.append(f"- {cf}: {saldo}")
    return "\n".join(lines)

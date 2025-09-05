# Scraping T3.0 (Amdocs) - Automatización por DNI

Este proyecto automatiza el flujo descrito en `flow_spect10.yaml`:
- Ingresar al portal (VPN a nivel sistema requerida).
- Abrir buscador, seleccionar tipo de documento, ingresar DNI y buscar.
- Abrir primer resultado, navegar a "Resumen de Facturación".
- Iterar Cuentas Financieras con saldo > 0, extraer Saldo y capturar encabezado.
- Compilar salida para WhatsApp (texto + adjuntos).

## Requisitos
- Python 3.10+
- VPN activa en el sistema antes de ejecutar

## Instalación rápida

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python -m playwright install --with-deps
```

## Uso

```bash
python -m src.scraper.cli --dni 2994**** --flow flow_spect10.yaml --head
```

Parámetros:
- `--dni`: DNI a consultar.
- `--flow`: ruta al YAML de flujo (por defecto `flow_spect10.yaml`).
- `--head/--no-head`: ejecutar con o sin UI del navegador.
- `--slowmo`: ms de retraso entre acciones.

Las capturas se guardan en `capturas/`.

## Notas
- No se incluyen credenciales ni URL del portal; completar `portal_url` en el YAML.
- Evitar datos personales reales durante pruebas.

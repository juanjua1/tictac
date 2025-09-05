# Modo visual (Linux + AnyDesk)

Este modo controla la ventana de AnyDesk con anclas de imagen (carpeta `capturas/`).

Requisitos:
- Linux con sesión X11 (no Wayland)
- AnyDesk a 100% (sin auto-escala), ventana fija o pantalla completa
- Windows remoto a 100% de escala y tema estable
- Paquete Python: pyautogui, opencv-python (instalar con `pip install -r requirements.txt`)

Archivos de ancla usados (en `capturas/`):
- `cliente.jpeg`, `tipo.de.documento.jpeg`, `dni.jpeg`, `numero.documento.jpeg`,
  `primera.opcion.jpeg`, `seleccionar.jpeg`, `ver.score.jpeg`, `caputara.final.jpeg`

Cómo ejecutar:
```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# Opcional: ajustar delay en segundos entre pasos
export VISUAL_STEP_DELAY_S=1.0

python -m src.scraper.cli --visual
```

Salida:
- Captura final en `capturas/resultado_final.png`

Tips:
- Si una ancla no se detecta, recortá una versión PNG nítida del control.
- Evitá cambiar zoom/escala/tema entre capturas y ejecución.
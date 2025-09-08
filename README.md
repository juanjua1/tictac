# Automatización Visual por DNI

Proyecto reducido: sólo modo visual (PyAutoGUI + reconocimiento de imágenes). Se eliminó la ejecución Playwright y los YAML de flujo. El bot simula clicks y tipeo sobre una sesión remota / escritorio usando capturas de referencia en `capturas/`.

## Requisitos
* Python 3.10+
* Dependencias del sistema para `pyautogui` (en Windows ya incluidas). En Linux: librerías X11 y acceso a pantalla.

## Instalación
```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

## Uso (fuente)
```bash
python -m src.scraper.cli --dni 29940807 --step-delay 0.8
```
Parámetros:
* `--dni` (obligatorio)
* `--step-delay` segundos entre pasos (default 0.8)
* `--region` limitar búsqueda de imágenes: x,y,ancho,alto (ej: `--region 1920,0,1920,1080` para segunda pantalla)
* `--confidence` umbral de matching (default 0.8)

Salida: genera una captura final `capturas/resultado_final_<DNI>.png` (o fallback de pantalla completa).

## Empaquetado (PyInstaller)
```bash
pyinstaller --clean --onefile --name t3bot pyinstaller.spec
```
Ejecutable resultante en `dist/`.

## Notas
* Ajustá las imágenes en `capturas/` para el entorno (resolución, tema).
* Si cambia el layout visual, reemplazá las imágenes manteniendo los nombres.
* Para mejorar robustez, bajar `--confidence` o recortar mejor las anclas.

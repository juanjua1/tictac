# Ejecutable Windows (modo visual solamente)

Proyecto reducido: sólo interacción por imágenes (PyAutoGUI). Eliminado Playwright y YAML.

## Requisitos
* Windows 10/11 64-bit
* Python 3.10+ (sólo para construir, no necesario en máquina destino si usás el .exe)

## Construir
```powershell
python -m venv .venv
./.venv/Scripts/Activate.ps1
pip install -r requirements.txt
pip install pyinstaller
pyinstaller --clean --onefile --name t3bot pyinstaller.spec
```
Salida: `dist\t3bot.exe`.

## Uso
Colocá `t3bot.exe` en una carpeta junto a la carpeta `capturas\` con las imágenes ancla.
```powershell
./t3bot.exe --dni 29940807 --step-delay 0.8
```
Parámetros opcionales:
* `--region x,y,w,h` limitar búsqueda (ej: segunda pantalla).
* `--confidence 0.75` ajustar umbral.

Genera `capturas\resultado_final_<DNI>.png`.

## Tips
* Si no encuentra una imagen, ajustá resolución o reemplazá la captura.
* Bajar `--confidence` mejora tolerancia pero aumenta falsos positivos.

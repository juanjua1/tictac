# Ejecutable para Windows 10/11

Este proyecto se puede empaquetar como un ejecutable único para Windows (t3bot.exe) usando PyInstaller.

Requisitos en Windows:
- Windows 10 u 11 (64-bit)
- Python 3.10 o 3.11 instalado
- Acceso a Internet para descargar navegadores de Playwright
- VPN activa a nivel sistema (cliente de VPN del equipo)

Si usás OpenVPN Connect:
- Conectate al perfil correcto en OpenVPN Connect antes de ejecutar el bot.
- Podés pedirle al bot que verifique la conectividad al portal con `--check-vpn` o esperar hasta N segundos con `--vpn-wait N`.

## Construir el ejecutable en Windows
1. Abrí PowerShell y ubicáte en la carpeta del proyecto
2. Crear y activar venv, instalar dependencias y PyInstaller:
   ```powershell
   python -m venv .venv
   .\.venv\Scripts\Activate.ps1
   pip install -r requirements.txt
   pip install pyinstaller
   ```
3. (Opcional) Instalar Playwright y navegadores para probar localmente:
   ```powershell
   python -m playwright install
   ```
4. Generar el ejecutable con PyInstaller usando el spec incluido:
   ```powershell
   pyinstaller --clean --onefile --name t3bot pyinstaller.spec
   ```
5. El ejecutable quedará en `dist\t3bot.exe`.

## Uso en la PC destino (Windows)
1. Copiá `dist\t3bot.exe` y `flow_spect10.yaml` a una carpeta de trabajo (por ejemplo `C:\t3bot`).
2. Abrí PowerShell en esa carpeta y ejecutá una sola vez para instalar los navegadores de Playwright:
   ```powershell
   .\t3bot.exe --install-browsers
   ```
3. Definí la URL del portal de una de estas formas (prioridad CLI > .env > YAML):
   - CLI: agrega `--portal-url "https://tu.portal.com"`
   - .env: crea un archivo `.env` con `PORTAL_URL=https://tu.portal.com`
   - YAML: completa `meta.portal_url` en `flow_spect10.yaml`
4. Ejecutá verificando VPN/portal (útil con OpenVPN Connect):
   ```powershell
   .\t3bot.exe --dni 2994**** --flow flow_spect10.yaml --no-head --check-vpn --vpn-wait 60
   ```
5. Para una corrida real headless (sin ventana):
   ```powershell
   .\t3bot.exe --dni 2994**** --flow flow_spect10.yaml --no-head
   ```
6. Las capturas se guardarán en la subcarpeta `capturas\`.

Notas:
- Si SmartScreen te advierte, seleccioná “Más información” > “Ejecutar de todas formas”.
- Si el portal usa SSO o login, agregá esos pasos al YAML antes de correr.
- El flag `--check-vpn`/`--vpn-wait` valida que el portal sea alcanzable (útil para confirmar que la VPN esté activa).
 - Si la VPN se corta, el bot puede fallar en los `wait` por visibilidad; reconectá la VPN en OpenVPN Connect y reintentá.

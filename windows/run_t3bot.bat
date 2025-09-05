@echo off
setlocal

REM Cambiar el DNI y el nombre del YAML según corresponda
REM Lanzador por defecto para entorno Windows
setlocal enabledelayedexpansion
if "%~1"=="" (
	echo Uso: run_t3bot.bat DNI [PORTAL_URL]
	echo Ej:  run_t3bot.bat 29941234 https://portal.example.com
	exit /b 1
)
set DNI=%~1
set PORTAL=%~2

if not defined PORTAL (
	echo [INFO] Usando portal_url de .env o del YAML
	set PORTAL_FLAG=
) else (
	set PORTAL_FLAG=--portal-url "%PORTAL%"
)

REM Instalar navegadores la primera vez (si ya estan, no hace nada)
echo [STEP] Instalando navegadores Playwright si faltan...
t3bot.exe --install-browsers

echo [STEP] Ejecutando bot...
t3bot.exe --dni %DNI% --flow flow_spect10.yaml %PORTAL_FLAG% --no-head --check-vpn --vpn-wait 60 --step-delay 800
endlocal




endlocal

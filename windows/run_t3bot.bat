@echo off
setlocal

if "%~1"=="" (
	echo Uso: run_t3bot.bat DNI [STEP_DELAY_MS]
	echo Ej:  run_t3bot.bat 29941234 800
	exit /b 1
)
set DNI=%~1
set DELAY=%~2
if not defined DELAY set DELAY=800

set SECS=0
for /f "tokens=*" %%A in ("%DELAY%") do set /a SECS=%%A/1000

echo [INFO] Ejecutando visual bot DNI=%DNI% delay=%SECS%s
t3bot.exe --dni %DNI% --step-delay %SECS%

endlocal
endlocal

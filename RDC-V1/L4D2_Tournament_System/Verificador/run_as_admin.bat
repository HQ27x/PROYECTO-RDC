@echo off
:: Script para ejecutar el verificador como administrador

:: Verificar si ya se ejecuta como administrador
net session >nul 2>&1
if %errorlevel% == 0 (
    echo [OK] Ejecutando como administrador
    goto :run
)

:: Solicitar elevación
echo [INFO] Este programa necesita permisos de administrador para configurar el firewall
echo [INFO] Por favor, confirma la elevacion de privilegios
echo.

powershell -Command "Start-Process '%~f0' -Verb RunAs"
exit /b

:run
echo.
echo L4D2 Tournament Integrity Checker
echo ==================================
echo.

:: Ejecutar el verificador
if exist "L4D2_Verifier_Console.exe" (
    L4D2_Verifier_Console.exe
) else if exist "L4D2_Verifier.exe" (
    L4D2_Verifier.exe
) else (
    echo ERROR: No se encontro el verificador
    echo Asegurate de que L4D2_Verifier.exe o L4D2_Verifier_Console.exe este en este directorio
    pause
    exit /b 1
)

pause


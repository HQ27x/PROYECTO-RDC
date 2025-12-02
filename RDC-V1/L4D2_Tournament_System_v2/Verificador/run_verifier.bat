@echo off
echo L4D2 Tournament Integrity Checker - Verificador
echo ================================================
echo.
echo Selecciona el modo de ejecucion:
echo 1. Interfaz Grafica (Recomendado)
echo 2. Modo Consola
echo.
set /p choice="Ingresa tu opcion (1 o 2): "

if "%choice%"=="1" (
    echo.
    echo Iniciando verificador con interfaz grafica...
    start "" "L4D2_Verifier.exe"
) else if "%choice%"=="2" (
    echo.
    echo Iniciando verificador en modo consola...
    "L4D2_Verifier_Console.exe"
) else (
    echo.
    echo Opcion invalida. Iniciando interfaz grafica por defecto...
    start "" "L4D2_Verifier.exe"
)

pause


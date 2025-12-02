@echo off
title L4D2 Tournament Integrity Checker
echo.
echo L4D2 Tournament Integrity Checker
echo ==================================
echo.
echo Seleccione el modo de ejecucion:
echo.
echo 1. Modo Interfaz Grafica (Recomendado)
echo 2. Modo Consola
echo.
set /p choice="Ingrese su opcion (1 o 2): "

if "%choice%"=="1" (
    echo.
    echo Iniciando en modo interfaz grafica...
    L4D2_Verifier.exe
) else if "%choice%"=="2" (
    echo.
    echo Iniciando en modo consola...
    L4D2_Verifier_Console.exe
) else (
    echo.
    echo Opcion invalida. Iniciando modo interfaz grafica por defecto...
    L4D2_Verifier.exe
)

if errorlevel 1 (
    echo.
    echo ERROR: No se pudo ejecutar el verificador
    echo.
    pause
)

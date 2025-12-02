@echo off
title L4D2 Tournament System - Compilador
echo.
echo ================================================================
echo L4D2 TOURNAMENT SYSTEM - COMPILADOR AUTOMATICO
echo ================================================================
echo.
echo Este script compilara ambos ejecutables:
echo - Verificador de integridad
echo - Generador de tokens
echo.
echo Presiona cualquier tecla para comenzar...
pause >nul
echo.

python build_all.py

if errorlevel 1 (
    echo.
    echo ERROR: La compilacion fallo
    echo.
    pause
    exit /b 1
)

echo.
echo Compilacion completada exitosamente!
echo.
echo El paquete de distribucion esta en la carpeta:
echo L4D2_Tournament_System/
echo.
pause

@echo off
title L4D2 Verifier - Compilador
echo.
echo ================================================================
echo L4D2 TOURNAMENT INTEGRITY CHECKER - COMPILADOR
echo ================================================================
echo.
echo Este script compilara solo el verificador de integridad.
echo.
echo Presiona cualquier tecla para comenzar...
pause >nul
echo.

python build_verifier.py

if errorlevel 1 (
    echo.
    echo ERROR: La compilacion del verificador fallo
    echo.
    pause
    exit /b 1
)

echo.
echo Verificador compilado exitosamente!
echo.
echo Los archivos estan en la carpeta: dist/
echo.
pause

@echo off
title L4D2 Token Generator - Compilador
echo.
echo ================================================================
echo L4D2 TOURNAMENT TOKEN GENERATOR - COMPILADOR
echo ================================================================
echo.
echo Este script compilara solo el generador de tokens.
echo.
echo Presiona cualquier tecla para comenzar...
pause >nul
echo.

python build_token_generator.py

if errorlevel 1 (
    echo.
    echo ERROR: La compilacion del generador fallo
    echo.
    pause
    exit /b 1
)

echo.
echo Generador de tokens compilado exitosamente!
echo.
echo Los archivos estan en la carpeta: dist/L4D2_Token_Generator/
echo.
pause

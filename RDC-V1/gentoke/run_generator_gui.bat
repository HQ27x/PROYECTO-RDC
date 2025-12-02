@echo off
echo L4D2 Tournament Token Generator - Interfaz Grafica
echo ==================================================
echo.

python token_generator.py

if errorlevel 1 (
    echo.
    echo ERROR: No se pudo ejecutar el generador
    echo Asegurate de que Python y las dependencias esten instaladas
    echo.
    pause
)

@echo off
echo L4D2 Tournament Integrity Checker
echo ==================================
echo.

python main.py --gui

if errorlevel 1 (
    echo.
    echo ERROR: No se pudo ejecutar el programa
    echo Asegurate de que Python y las dependencias esten instaladas
    echo.
    pause
)

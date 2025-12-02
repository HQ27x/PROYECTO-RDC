@echo off
title Test Loading GIF
echo.
echo Probando loading.gif...
echo.

python test_loading_gif.py

if errorlevel 1 (
    echo.
    echo ERROR: La prueba fallo
    echo.
    pause
    exit /b 1
)

echo.
pause



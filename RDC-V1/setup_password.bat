@echo off
echo L4D2 Tournament Integrity Checker - Configuracion de Contrasena
echo ================================================================
echo.

python setup_password.py

if errorlevel 1 (
    echo.
    echo ERROR: No se pudo configurar la contrasena
    echo.
    pause
) else (
    echo.
    echo Configuracion completada exitosamente!
    echo.
    pause
)

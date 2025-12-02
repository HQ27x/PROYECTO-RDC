@echo off
echo L4D2 Tournament Integrity Checker - Instalador
echo ================================================
echo.

echo Verificando Python...
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python no esta instalado o no esta en el PATH
    echo Por favor instala Python desde https://python.org
    pause
    exit /b 1
)

echo Python encontrado!
echo.

echo Instalando dependencias...
pip install -r requirements.txt

if errorlevel 1 (
    echo ERROR: No se pudieron instalar las dependencias
    pause
    exit /b 1
)

echo.
echo Instalacion completada exitosamente!
echo.
echo Para ejecutar el programa:
echo   Modo consola: python main.py
echo   Modo GUI:     python main.py --gui
echo.
pause

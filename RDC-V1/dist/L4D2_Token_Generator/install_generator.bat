@echo off
title L4D2 Tournament Token Generator - Instalador
echo.
echo L4D2 Tournament Token Generator - Instalador
echo ============================================
echo.
echo Este instalador configurara el generador de tokens.
echo.
echo Presiona cualquier tecla para continuar...
pause >nul
echo.
echo Configurando generador de tokens...
echo.

REM Crear directorio de trabajo si no existe
if not exist "tokens" mkdir tokens
if not exist "backups" mkdir backups

echo Directorios creados:
echo - tokens (para almacenar tokens generados)
echo - backups (para respaldos de la base de datos)
echo.

echo Configuracion completada!
echo.
echo Para usar el generador:
echo 1. Ejecuta run_generator.bat
echo 2. O ejecuta L4D2_Token_Generator.exe directamente
echo.
echo Presiona cualquier tecla para salir...
pause >nul

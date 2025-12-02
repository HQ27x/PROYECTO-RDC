@echo off
title L4D2 Tournament Token Generator
echo.
echo L4D2 Tournament Token Generator
echo ================================
echo.
echo Iniciando generador de tokens...
echo.

L4D2_Token_Generator.exe

if errorlevel 1 (
    echo.
    echo ERROR: No se pudo ejecutar el generador
    echo.
    pause
)

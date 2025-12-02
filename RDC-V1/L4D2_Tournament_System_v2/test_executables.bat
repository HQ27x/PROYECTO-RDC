@echo off
echo ========================================
echo L4D2 Tournament System - Prueba Rapida
echo ========================================
echo.
echo Verificando ejecutables...
echo.

echo [1/3] Verificando L4D2_Verifier.exe...
if exist "Verificador\L4D2_Verifier.exe" (
    echo    ✓ L4D2_Verifier.exe encontrado
) else (
    echo    ✗ L4D2_Verifier.exe NO encontrado
)

echo [2/3] Verificando L4D2_Verifier_Console.exe...
if exist "Verificador\L4D2_Verifier_Console.exe" (
    echo    ✓ L4D2_Verifier_Console.exe encontrado
) else (
    echo    ✗ L4D2_Verifier_Console.exe NO encontrado
)

echo [3/3] Verificando L4D2_Token_Generator.exe...
if exist "Generador_Tokens\L4D2_Token_Generator.exe" (
    echo    ✓ L4D2_Token_Generator.exe encontrado
) else (
    echo    ✗ L4D2_Token_Generator.exe NO encontrado
)

echo.
echo ========================================
echo Verificacion completada
echo ========================================
echo.
echo IMPORTANTE: Si el antivirus borro los archivos:
echo 1. Leer ANTIVIRUS_INSTRUCTIONS.txt
echo 2. Agregar excepciones en el antivirus
echo 3. Recompilar los ejecutables
echo.
pause


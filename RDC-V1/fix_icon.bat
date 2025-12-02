@echo off
echo Corrigiendo icono en los ejecutables...
echo.

cd /d "C:\Users\nhuay\OneDrive\Imágenes\RDC-V1"

echo Verificando archivo de icono...
if not exist "rdc.ico" (
    echo ERROR: No se encontro el archivo rdc.ico
    pause
    exit /b 1
)
echo OK - Icono encontrado

echo.
echo Limpiando compilaciones anteriores...
if exist "dist" rmdir /s /q "dist"
if exist "build" rmdir /s /q "build"
del /q "*.spec" 2>nul
echo OK - Limpieza completada

echo.
echo Compilando verificador GUI con icono...
python -m PyInstaller --onefile --windowed --icon=rdc.ico --add-data="gentoke;gentoke" --name=L4D2_Verifier main.py
if errorlevel 1 (
    echo ERROR: Error al compilar verificador GUI
    pause
    exit /b 1
)
echo OK - Verificador GUI compilado

echo.
echo Compilando verificador consola con icono...
python -m PyInstaller --onefile --console --icon=rdc.ico --add-data="gentoke;gentoke" --name=L4D2_Verifier_Console main.py
if errorlevel 1 (
    echo ERROR: Error al compilar verificador consola
    pause
    exit /b 1
)
echo OK - Verificador consola compilado

echo.
echo Compilando generador con icono...
python -m PyInstaller --onefile --windowed --icon=rdc.ico --name=L4D2_Token_Generator gentoke/token_generator.py
if errorlevel 1 (
    echo ERROR: Error al compilar generador
    pause
    exit /b 1
)
echo OK - Generador compilado

echo.
echo Copiando ejecutables...
if exist "L4D2_Tournament_System" rmdir /s /q "L4D2_Tournament_System"
mkdir "L4D2_Tournament_System"
mkdir "L4D2_Tournament_System\Verificador"
mkdir "L4D2_Tournament_System\Generador_Tokens"

copy "dist\L4D2_Verifier.exe" "L4D2_Tournament_System\Verificador\"
copy "dist\L4D2_Verifier_Console.exe" "L4D2_Tournament_System\Verificador\"
copy "dist\L4D2_Token_Generator.exe" "L4D2_Tournament_System\Generador_Tokens\"

echo OK - Ejecutables copiados

echo.
echo ==================================================
echo COMPILACION CON ICONO COMPLETADA!
echo ==================================================
echo Los ejecutables ahora tienen el icono rdc.ico
echo Ubicacion: L4D2_Tournament_System/
echo ==================================================
echo.
pause

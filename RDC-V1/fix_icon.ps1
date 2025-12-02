# Script de PowerShell para corregir el icono
Write-Host "Corrigiendo icono en los ejecutables..." -ForegroundColor Green
Write-Host ""

# Cambiar al directorio correcto
Set-Location "C:\Users\nhuay\OneDrive\Imágenes\RDC-V1"

Write-Host "Verificando archivo de icono..." -ForegroundColor Yellow
if (-not (Test-Path "rdc.ico")) {
    Write-Host "ERROR: No se encontró el archivo rdc.ico" -ForegroundColor Red
    Read-Host "Presiona Enter para salir"
    exit 1
}
Write-Host "OK - Icono encontrado" -ForegroundColor Green

Write-Host ""
Write-Host "Limpiando compilaciones anteriores..." -ForegroundColor Yellow
if (Test-Path "dist") { Remove-Item -Recurse -Force "dist" }
if (Test-Path "build") { Remove-Item -Recurse -Force "build" }
Get-ChildItem "*.spec" | Remove-Item -Force
Write-Host "OK - Limpieza completada" -ForegroundColor Green

Write-Host ""
Write-Host "Compilando verificador GUI con icono..." -ForegroundColor Yellow
try {
    & python -m PyInstaller --onefile --windowed --icon=rdc.ico --add-data="gentoke;gentoke" --name=L4D2_Verifier main.py
    Write-Host "OK - Verificador GUI compilado" -ForegroundColor Green
} catch {
    Write-Host "ERROR: Error al compilar verificador GUI" -ForegroundColor Red
    Read-Host "Presiona Enter para salir"
    exit 1
}

Write-Host ""
Write-Host "Compilando verificador consola con icono..." -ForegroundColor Yellow
try {
    & python -m PyInstaller --onefile --console --icon=rdc.ico --add-data="gentoke;gentoke" --name=L4D2_Verifier_Console main.py
    Write-Host "OK - Verificador consola compilado" -ForegroundColor Green
} catch {
    Write-Host "ERROR: Error al compilar verificador consola" -ForegroundColor Red
    Read-Host "Presiona Enter para salir"
    exit 1
}

Write-Host ""
Write-Host "Compilando generador con icono..." -ForegroundColor Yellow
try {
    & python -m PyInstaller --onefile --windowed --icon=rdc.ico --name=L4D2_Token_Generator gentoke/token_generator.py
    Write-Host "OK - Generador compilado" -ForegroundColor Green
} catch {
    Write-Host "ERROR: Error al compilar generador" -ForegroundColor Red
    Read-Host "Presiona Enter para salir"
    exit 1
}

Write-Host ""
Write-Host "Copiando ejecutables..." -ForegroundColor Yellow
if (Test-Path "L4D2_Tournament_System") { Remove-Item -Recurse -Force "L4D2_Tournament_System" }
New-Item -ItemType Directory -Path "L4D2_Tournament_System" | Out-Null
New-Item -ItemType Directory -Path "L4D2_Tournament_System\Verificador" | Out-Null
New-Item -ItemType Directory -Path "L4D2_Tournament_System\Generador_Tokens" | Out-Null

Copy-Item "dist\L4D2_Verifier.exe" "L4D2_Tournament_System\Verificador\"
Copy-Item "dist\L4D2_Verifier_Console.exe" "L4D2_Tournament_System\Verificador\"
Copy-Item "dist\L4D2_Token_Generator.exe" "L4D2_Tournament_System\Generador_Tokens\"

Write-Host "OK - Ejecutables copiados" -ForegroundColor Green

Write-Host ""
Write-Host "==================================================" -ForegroundColor Cyan
Write-Host "COMPILACION CON ICONO COMPLETADA!" -ForegroundColor Green
Write-Host "==================================================" -ForegroundColor Cyan
Write-Host "Los ejecutables ahora tienen el icono rdc.ico" -ForegroundColor White
Write-Host "Ubicación: L4D2_Tournament_System/" -ForegroundColor White
Write-Host "==================================================" -ForegroundColor Cyan
Write-Host ""
Read-Host "Presiona Enter para salir"

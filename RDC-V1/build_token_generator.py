#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para empaquetar el L4D2 Tournament Token Generator
Crea un ejecutable independiente del generador de tokens
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path

def install_pyinstaller():
    """Instala PyInstaller si no está disponible"""
    try:
        import PyInstaller
        print("[OK] PyInstaller ya esta instalado")
        return True
    except ImportError:
        print("Instalando PyInstaller...")
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", "pyinstaller"])
            print("[OK] PyInstaller instalado correctamente")
            return True
        except subprocess.CalledProcessError as e:
            print(f"[ERROR] Error al instalar PyInstaller: {e}")
            return False

def create_generator_spec():
    """Crea el archivo .spec para el generador de tokens"""
    spec_content = '''# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['gentoke/token_generator.py'],
    pathex=[],
    binaries=[],
    datas=[],
    hiddenimports=[
        'tkinter',
        'tkinter.ttk',
        'tkinter.messagebox',
        'tkinter.scrolledtext',
        'json',
        'hashlib',
        'base64',
        'secrets',
        'datetime',
        'qrcode',
        'PIL',
        'PIL.Image',
        'PIL.ImageTk',
        'os',
        'sys',
        'io',
        'pathlib'
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='L4D2_Token_Generator',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='icon.ico' if os.path.exists('icon.ico') else None,
)
'''
    
    with open('L4D2_Token_Generator.spec', 'w', encoding='utf-8') as f:
        f.write(spec_content)
    
    print("[OK] Archivo .spec creado para el generador de tokens")

def build_generator():
    """Compila el generador de tokens"""
    print("Compilando generador de tokens...")
    
    try:
        subprocess.check_call([
            sys.executable, "-m", "PyInstaller", 
            "--clean", 
            "L4D2_Token_Generator.spec"
        ])
        print("[OK] Generador de tokens compilado correctamente")
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"[ERROR] Error al compilar: {e}")
        return False

def create_generator_launcher():
    """Crea un launcher para el generador"""
    # Crear directorio si no existe
    import os
    os.makedirs('dist/L4D2_Token_Generator', exist_ok=True)
    
    # Mover el ejecutable a la carpeta
    if os.path.exists('dist/L4D2_Token_Generator.exe'):
        import shutil
        shutil.move('dist/L4D2_Token_Generator.exe', 'dist/L4D2_Token_Generator/L4D2_Token_Generator.exe')
    
    launcher_content = '''@echo off
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
'''
    
    with open('dist/L4D2_Token_Generator/run_generator.bat', 'w', encoding='utf-8') as f:
        f.write(launcher_content)
    
    print("[OK] Launcher creado para el generador")

def create_generator_readme():
    """Crea README para el generador"""
    readme_content = '''# L4D2 Tournament Token Generator - Ejecutable

## 🎫 Generador de Tokens para Torneos de Left 4 Dead 2

### 📋 Características
- ✅ Generación de tokens únicos para jugadores
- ✅ Interfaz gráfica intuitiva
- ✅ Gestión completa de tokens
- ✅ Generación de códigos QR
- ✅ Base de datos de tokens
- ✅ Validación y estadísticas

### 🚀 Cómo Usar

#### Ejecutar el Generador
1. Ejecutar `run_generator.bat` o `L4D2_Token_Generator.exe`
2. La interfaz gráfica se abrirá automáticamente

#### Generar Token para Jugador
1. **Completar Información**:
   - Nombre del Jugador (obligatorio)
   - Nombre del Torneo (opcional)
   - Días de validez (por defecto 30)

2. **Generar Token**:
   - Hacer clic en "Generar Token"
   - El token se mostrará en el área de texto

3. **Distribuir Token**:
   - Copiar token con "Copiar Token"
   - Generar QR con "Generar QR"
   - Enviar al jugador

### 🔧 Gestión de Tokens

#### Ver Todos los Tokens
- Hacer clic en "Ver Todos los Tokens"
- Lista completa con estados y fechas

#### Validar Token
- Hacer clic en "Validar Token"
- Pegar el token a validar
- Verificar información del jugador

#### Estadísticas
- Hacer clic en "Estadísticas"
- Ver resumen de tokens activos/expirados

### 📊 Formato de Token

Los tokens generados incluyen:

```
TOKEN GENERADO EXITOSAMENTE
==================================================

Jugador: NombreDelJugador
Torneo: L4D2 Tournament
Token: abc123def456ghi789...
Creado: 2024-01-15T10:30:00
Expira: 2024-02-14T10:30:00
Hash: a1b2c3d4e5f6...
```

### 🛡️ Seguridad

- **Tokens Únicos**: Cada token es irrepetible
- **Hash SHA256**: Verificación segura
- **Expiración**: Control de validez temporal
- **Base de Datos**: Almacenamiento seguro en JSON

### 📁 Archivos Importantes

- `tokens_database.json`: Base de datos de tokens (se crea automáticamente)
- `run_generator.bat`: Launcher del generador
- `L4D2_Token_Generator.exe`: Ejecutable principal

### ⚠️ Requisitos del Sistema
- Windows 10/11
- Python (ya incluido en el ejecutable)

### 🔄 Flujo de Trabajo

1. **Generar Tokens**: Crear tokens para todos los participantes
2. **Distribuir**: Enviar tokens a cada jugador
3. **Monitorear**: Verificar uso y estadísticas
4. **Gestionar**: Activar/desactivar tokens según necesidad

### 🆘 Solución de Problemas

**"Error al generar token"**
- Verificar que el nombre del jugador no esté vacío
- Verificar que los días de validez sean un número válido

**"Error al validar token"**
- Verificar que el token esté completo
- Verificar que el token no haya expirado

**"Error de ejecución"**
- Verificar que no haya antivirus bloqueando
- Ejecutar como administrador

### 📞 Soporte
Para problemas o preguntas, revisa la documentación o contacta al desarrollador.

---
**L4D2 Tournament Token Generator v1.0**
'''
    
    with open('dist/L4D2_Token_Generator/README_GENERATOR.txt', 'w', encoding='utf-8') as f:
        f.write(readme_content)
    
    print("[OK] README creado para el generador")

def create_installer_script():
    """Crea un script de instalación para el generador"""
    installer_content = '''@echo off
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
'''
    
    with open('dist/L4D2_Token_Generator/install_generator.bat', 'w', encoding='utf-8') as f:
        f.write(installer_content)
    
    print("[OK] Script de instalacion creado")

def main():
    """Función principal"""
    print("L4D2 Tournament Token Generator - Compilador")
    print("=" * 60)
    print()
    
    # Verificar que estamos en el directorio correcto
    if not os.path.exists('gentoke/token_generator.py'):
        print("[ERROR] No se encontro gentoke/token_generator.py")
        print("   Ejecuta este script desde el directorio del proyecto")
        return False
    
    # Instalar PyInstaller
    if not install_pyinstaller():
        return False
    
    # Crear archivo .spec
    create_generator_spec()
    
    # Compilar
    if not build_generator():
        return False
    
    # Crear archivos adicionales
    create_generator_launcher()
    create_generator_readme()
    create_installer_script()
    
    print()
    print("COMPILACION COMPLETADA EXITOSAMENTE!")
    print()
    print("Archivos generados en la carpeta 'dist/L4D2_Token_Generator':")
    print("   - L4D2_Token_Generator.exe (Ejecutable principal)")
    print("   - run_generator.bat (Launcher)")
    print("   - install_generator.bat (Instalador)")
    print("   - README_GENERATOR.txt (Documentacion)")
    print()
    print("Para usar:")
    print("   1. Ejecuta install_generator.bat (primera vez)")
    print("   2. Ejecuta run_generator.bat para usar")
    print("   3. Genera tokens para los jugadores del torneo")
    print()
    
    return True

if __name__ == "__main__":
    success = main()
    if not success:
        sys.exit(1)
    
    input("Presiona Enter para continuar...")

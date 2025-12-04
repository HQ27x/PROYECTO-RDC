#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para empaquetar el L4D2 Tournament Integrity Checker
Crea un ejecutable independiente del verificador
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

def create_verifier_spec():
    """Crea el archivo .spec para el verificador"""
    spec_content = '''# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('gentoke', 'gentoke'),
        ('loading.gif', '.'),
        ('pfprogam', 'pfprogam'),
    ],
    hiddenimports=[
        'psutil',
        'winreg',
        'tkinter',
        'tkinter.ttk',
        'tkinter.messagebox',
        'tkinter.scrolledtext',
        'tkinter.simpledialog',
        'PIL',
        'PIL.Image',
        'PIL.ImageTk',
        'json',
        'hashlib',
        'base64',
        'secrets',
        'datetime',
        'threading',
        'pathlib',
        'os',
        'sys',
        'time',
        'platform',
        're',
        'io',
        'contextlib'
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
    name='L4D2_Verifier',
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
    icon='rdc.ico',
)
'''
    
    with open('L4D2_Verifier.spec', 'w', encoding='utf-8') as f:
        f.write(spec_content)
    
    print("[OK] Archivo .spec creado para el verificador")

def create_verifier_console_spec():
    """Crea el archivo .spec para el verificador en modo consola"""
    spec_content = '''# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('gentoke', 'gentoke'),
        ('loading.gif', '.'),
        ('pfprogam', 'pfprogam'),
    ],
    hiddenimports=[
        'psutil',
        'winreg',
        'PIL',
        'PIL.Image',
        'PIL.ImageTk',
        'json',
        'hashlib',
        'base64',
        'secrets',
        'datetime',
        'pathlib',
        'os',
        'sys',
        'time',
        'platform',
        're',
        'io',
        'contextlib'
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
    name='L4D2_Verifier_Console',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='rdc.ico',
)
'''
    
    with open('L4D2_Verifier_Console.spec', 'w', encoding='utf-8') as f:
        f.write(spec_content)
    
    print("[OK] Archivo .spec creado para el verificador consola")

def build_verifier():
    """Compila el verificador"""
    print("Compilando verificador...")
    
    try:
        # Compilar versión GUI
        subprocess.check_call([
            sys.executable, "-m", "PyInstaller", 
            "--clean", 
            "L4D2_Verifier.spec"
        ])
        print("[OK] Verificador GUI compilado correctamente")
        
        # Compilar versión consola
        subprocess.check_call([
            sys.executable, "-m", "PyInstaller", 
            "--clean", 
            "L4D2_Verifier_Console.spec"
        ])
        print("[OK] Verificador consola compilado correctamente")
        
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"[ERROR] Error al compilar: {e}")
        return False

def create_verifier_launcher():
    """Crea un launcher para el verificador"""
    launcher_content = '''@echo off
title L4D2 Tournament Integrity Checker
echo.
echo L4D2 Tournament Integrity Checker
echo ==================================
echo.
echo Seleccione el modo de ejecucion:
echo.
echo 1. Modo Interfaz Grafica (Recomendado)
echo 2. Modo Consola
echo.
set /p choice="Ingrese su opcion (1 o 2): "

if "%choice%"=="1" (
    echo.
    echo Iniciando en modo interfaz grafica...
    L4D2_Verifier.exe
) else if "%choice%"=="2" (
    echo.
    echo Iniciando en modo consola...
    L4D2_Verifier_Console.exe
) else (
    echo.
    echo Opcion invalida. Iniciando modo interfaz grafica por defecto...
    L4D2_Verifier.exe
)

if errorlevel 1 (
    echo.
    echo ERROR: No se pudo ejecutar el verificador
    echo.
    pause
)
'''
    
    with open('dist/run_verifier.bat', 'w', encoding='utf-8') as f:
        f.write(launcher_content)
    
    # Copiar loading.gif a la carpeta dist
    if os.path.exists('loading.gif'):
        try:
            shutil.copy2('loading.gif', 'dist/loading.gif')
            print("[OK] loading.gif copiado a dist/")
        except Exception as e:
            print(f"[WARNING] No se pudo copiar loading.gif: {e}")
    
    # Copiar run_as_admin.bat a la carpeta dist
    if os.path.exists('run_as_admin.bat'):
        try:
            shutil.copy2('run_as_admin.bat', 'dist/run_as_admin.bat')
            print("[OK] run_as_admin.bat copiado a dist/")
        except Exception as e:
            print(f"[WARNING] No se pudo copiar run_as_admin.bat: {e}")
    
    print("[OK] Launcher creado para el verificador")

def create_verifier_readme():
    """Crea README para el verificador"""
    readme_content = '''# L4D2 Tournament Integrity Checker - Ejecutable

## 🎮 Verificador de Integridad para Torneos de Left 4 Dead 2

### 📋 Características
- ✅ Detección de mods instalados
- ✅ Análisis de cuentas Steam con IDs completos
- ✅ Detección de procesos sospechosos
- ✅ Reportes detallados en JSON y texto
- ✅ Sistema de autenticación con tokens
- ✅ Interfaz gráfica y modo consola

### 🚀 Cómo Usar

#### Opción 1: Como Administrador (Recomendado)
1. Ejecutar `run_as_admin.bat`
2. Confirmar la elevación de privilegios si se solicita
3. Seleccionar modo (Interfaz Gráfica o Consola)
4. El firewall se configurará automáticamente

#### Opción 2: Launcher Automático
1. Ejecutar `run_verifier.bat`
2. Seleccionar modo (Interfaz Gráfica o Consola)
3. El programa se ejecutará automáticamente

#### Opción 3: Ejecutables Directos
- **Interfaz Gráfica**: `L4D2_Verifier.exe`
- **Modo Consola**: `L4D2_Verifier_Console.exe`

### 🔐 Autenticación

El verificador requiere un token válido para funcionar:

1. **Obtener Token**: Contacta al administrador del torneo
2. **Pegar Token**: En la ventana de autenticación
3. **Autenticar**: Hacer clic en "Autenticar"
4. **Verificar**: Ejecutar la verificación completa

### 📊 Reportes

El programa genera reportes detallados que incluyen:
- Información de la PC
- Análisis de mods detectados
- Cuentas Steam con IDs completos
- Procesos sospechosos
- Estado de integridad general

### ⚠️ Requisitos del Sistema
- Windows 10/11
- Steam instalado
- Left 4 Dead 2 instalado

### 🆘 Solución de Problemas

**"Steam no encontrado"**
- Verificar que Steam esté instalado
- Ejecutar como administrador

**"Token inválido"**
- Verificar que el token esté completo
- Contactar al administrador del torneo

**"Error de ejecución"**
- Verificar que no haya antivirus bloqueando
- Ejecutar como administrador

**"No se pueden enviar reportes a Discord"**
- Ejecutar `run_as_admin.bat` para configurar el firewall automáticamente
- Agregar manualmente "L4D2 Tournament Verifier" al firewall de Windows
- Ejecutar como administrador

### 📞 Soporte
Para problemas o preguntas, contacta al administrador del torneo.

---
**L4D2 Tournament Integrity Checker v1.0**
'''
    
    with open('dist/README_VERIFIER.txt', 'w', encoding='utf-8') as f:
        f.write(readme_content)
    
    print("[OK] README creado para el verificador")

def main():
    """Función principal"""
    print("L4D2 Tournament Integrity Checker - Compilador")
    print("=" * 60)
    print()
    
    # Verificar que estamos en el directorio correcto
    if not os.path.exists('main.py'):
        print("[ERROR] No se encontro main.py")
        print("   Ejecuta este script desde el directorio del proyecto")
        return False
    
    if not os.path.exists('gentoke'):
        print("[ERROR] No se encontro la carpeta gentoke")
        print("   Asegurate de que el generador de tokens este presente")
        return False
    
    # Instalar PyInstaller
    if not install_pyinstaller():
        return False
    
    # Crear archivos .spec
    create_verifier_spec()
    create_verifier_console_spec()
    
    # Compilar
    if not build_verifier():
        return False
    
    # Crear archivos adicionales
    create_verifier_launcher()
    create_verifier_readme()
    
    print()
    print("COMPILACION COMPLETADA EXITOSAMENTE!")
    print()
    print("Archivos generados en la carpeta 'dist':")
    print("   - L4D2_Verifier.exe (Interfaz Grafica)")
    print("   - L4D2_Verifier_Console.exe (Modo Consola)")
    print("   - run_verifier.bat (Launcher)")
    print("   - README_VERIFIER.txt (Documentacion)")
    print()
    print("Para distribuir:")
    print("   1. Copia toda la carpeta 'dist'")
    print("   2. Envia a los jugadores del torneo")
    print("   3. Los jugadores ejecutan run_verifier.bat")
    print()
    
    return True

if __name__ == "__main__":
    success = main()
    if not success:
        sys.exit(1)
    
    input("Presiona Enter para continuar...")

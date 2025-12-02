#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script simplificado para compilar ambos ejecutables
L4D2 Tournament Integrity Checker + Token Generator
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path

def print_banner():
    """Muestra el banner del compilador"""
    print("=" * 70)
    print("L4D2 TOURNAMENT SYSTEM - COMPILADOR COMPLETO")
    print("=" * 70)
    print("Compilando verificador y generador de tokens")
    print("=" * 70)
    print()

def check_requirements():
    """Verifica los requisitos del sistema"""
    print("Verificando requisitos del sistema...")
    
    # Verificar Python
    if sys.version_info < (3, 7):
        print("ERROR: Se requiere Python 3.7 o superior")
        return False
    
    print(f"OK - Python {sys.version.split()[0]} detectado")
    
    # Verificar archivos necesarios
    required_files = [
        'main.py',
        'gentoke/token_generator.py',
        'gentoke/requirements.txt'
    ]
    
    for file in required_files:
        if not os.path.exists(file):
            print(f"ERROR: No se encontro {file}")
            return False
        print(f"OK - {file} encontrado")
    
    print("OK - Todos los requisitos cumplidos")
    return True

def install_dependencies():
    """Instala las dependencias necesarias"""
    print("\nInstalando dependencias...")
    
    dependencies = [
        'pyinstaller',
        'psutil',
        'qrcode[pil]',
        'Pillow'
    ]
    
    for dep in dependencies:
        print(f"   Instalando {dep}...")
        try:
            subprocess.check_call([
                sys.executable, "-m", "pip", "install", dep, "--quiet"
            ])
            print(f"   OK - {dep} instalado")
        except subprocess.CalledProcessError:
            print(f"   ADVERTENCIA: No se pudo instalar {dep}")
    
    print("OK - Dependencias instaladas")

def clean_build_dirs():
    """Limpia directorios de compilacion anteriores"""
    print("\nLimpiando compilaciones anteriores...")
    
    dirs_to_clean = ['build', 'dist', '__pycache__']
    
    for dir_name in dirs_to_clean:
        if os.path.exists(dir_name):
            shutil.rmtree(dir_name)
            print(f"   OK - {dir_name} eliminado")
    
    # Limpiar archivos .spec
    for spec_file in Path('.').glob('*.spec'):
        spec_file.unlink()
        print(f"   OK - {spec_file} eliminado")
    
    print("OK - Limpieza completada")

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
    ],
    hiddenimports=[
        'psutil',
        'winreg',
        'tkinter',
        'tkinter.ttk',
        'tkinter.messagebox',
        'tkinter.scrolledtext',
        'tkinter.simpledialog',
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
    icon=os.path.abspath('rdc.ico'),
)
'''
    
    with open('L4D2_Verifier.spec', 'w', encoding='utf-8') as f:
        f.write(spec_content)
    
    print("OK - Archivo .spec creado para el verificador")

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
    ],
    hiddenimports=[
        'psutil',
        'winreg',
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
    icon=os.path.abspath('rdc.ico'),
)
'''
    
    with open('L4D2_Verifier_Console.spec', 'w', encoding='utf-8') as f:
        f.write(spec_content)
    
    print("OK - Archivo .spec creado para el verificador consola")

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
    icon=os.path.abspath('rdc.ico'),
)
'''
    
    with open('L4D2_Token_Generator.spec', 'w', encoding='utf-8') as f:
        f.write(spec_content)
    
    print("OK - Archivo .spec creado para el generador de tokens")

def build_executables():
    """Compila todos los ejecutables"""
    print("\nCompilando ejecutables...")
    
    try:
        # Compilar verificador GUI
        print("   Compilando verificador GUI...")
        subprocess.check_call([
            sys.executable, "-m", "PyInstaller", 
            "--clean", 
            "L4D2_Verifier.spec"
        ])
        print("   OK - Verificador GUI compilado")
        
        # Compilar verificador consola
        print("   Compilando verificador consola...")
        subprocess.check_call([
            sys.executable, "-m", "PyInstaller", 
            "--clean", 
            "L4D2_Verifier_Console.spec"
        ])
        print("   OK - Verificador consola compilado")
        
        # Compilar generador
        print("   Compilando generador de tokens...")
        subprocess.check_call([
            sys.executable, "-m", "PyInstaller", 
            "--clean", 
            "L4D2_Token_Generator.spec"
        ])
        print("   OK - Generador de tokens compilado")
        
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"ERROR: Error al compilar: {e}")
        return False

def create_distribution_package():
    """Crea el paquete de distribucion final"""
    print("\nCreando paquete de distribucion...")
    
    # Crear directorio de distribucion
    dist_dir = Path('L4D2_Tournament_System')
    if dist_dir.exists():
        shutil.rmtree(dist_dir)
    dist_dir.mkdir()
    
    # Copiar verificador
    verifier_dir = dist_dir / 'Verificador'
    verifier_dir.mkdir()
    
    if Path('dist/L4D2_Verifier.exe').exists():
        shutil.copy2('dist/L4D2_Verifier.exe', verifier_dir)
        print("   OK - Verificador copiado")
    
    if Path('dist/L4D2_Verifier_Console.exe').exists():
        shutil.copy2('dist/L4D2_Verifier_Console.exe', verifier_dir)
        print("   OK - Verificador consola copiado")
    
    # Copiar generador de tokens
    generator_dir = dist_dir / 'Generador_Tokens'
    generator_dir.mkdir()
    
    if Path('dist/L4D2_Token_Generator.exe').exists():
        shutil.copy2('dist/L4D2_Token_Generator.exe', generator_dir)
        print("   OK - Generador copiado")
    
    # Crear launchers
    create_launchers(verifier_dir, generator_dir)
    
    print("OK - Paquete de distribucion creado")

def create_launchers(verifier_dir, generator_dir):
    """Crea los launchers para los ejecutables"""
    
    # Launcher del verificador
    verifier_launcher = '''@echo off
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
    
    with open(verifier_dir / 'run_verifier.bat', 'w', encoding='utf-8') as f:
        f.write(verifier_launcher)
    
    # Launcher del generador
    generator_launcher = '''@echo off
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
    
    with open(generator_dir / 'run_generator.bat', 'w', encoding='utf-8') as f:
        f.write(generator_launcher)
    
    print("   OK - Launchers creados")

def show_final_summary():
    """Muestra el resumen final"""
    print("\n" + "=" * 70)
    print("COMPILACION COMPLETADA EXITOSAMENTE!")
    print("=" * 70)
    print()
    print("Paquete de distribucion creado en:")
    print("   L4D2_Tournament_System/")
    print()
    print("Estructura del paquete:")
    print("   Verificador/")
    print("      - L4D2_Verifier.exe (Interfaz Grafica)")
    print("      - L4D2_Verifier_Console.exe (Modo Consola)")
    print("      - run_verifier.bat (Launcher)")
    print()
    print("   Generador_Tokens/")
    print("      - L4D2_Token_Generator.exe")
    print("      - run_generator.bat")
    print()
    print("Proximos pasos:")
    print("   1. Probar ambos ejecutables")
    print("   2. Generar tokens para los jugadores")
    print("   3. Distribuir el verificador a los jugadores")
    print("   4. Comenzar el torneo!")
    print()
    print("=" * 70)

def main():
    """Funcion principal"""
    print_banner()
    
    # Verificar requisitos
    if not check_requirements():
        print("\nERROR: Requisitos no cumplidos")
        return False
    
    # Instalar dependencias
    install_dependencies()
    
    # Limpiar compilaciones anteriores
    clean_build_dirs()
    
    # Crear archivos .spec
    create_verifier_spec()
    create_verifier_console_spec()
    create_generator_spec()
    
    # Compilar ejecutables
    if not build_executables():
        print("\nERROR: No se pudieron compilar los ejecutables")
        return False
    
    # Crear paquete de distribucion
    create_distribution_package()
    
    # Mostrar resumen final
    show_final_summary()
    
    return True

if __name__ == "__main__":
    success = main()
    if not success:
        print("\nERROR: La compilacion fallo")
        sys.exit(1)
    
    input("\nPresiona Enter para salir...")

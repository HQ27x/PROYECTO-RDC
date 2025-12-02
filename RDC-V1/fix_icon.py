#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para recompilar solo con el icono corregido
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path

def main():
    print("Corrigiendo icono en los ejecutables...")
    
    # Verificar que el icono existe
    icon_path = os.path.abspath('rdc.ico')
    if not os.path.exists(icon_path):
        print(f"ERROR: No se encontró el archivo {icon_path}")
        return False
    
    print(f"OK - Icono encontrado: {icon_path}")
    
    # Limpiar compilaciones anteriores
    if os.path.exists('dist'):
        shutil.rmtree('dist')
        print("OK - Directorio dist eliminado")
    
    if os.path.exists('build'):
        shutil.rmtree('build')
        print("OK - Directorio build eliminado")
    
    # Eliminar archivos .spec
    for spec_file in Path('.').glob('*.spec'):
        spec_file.unlink()
        print(f"OK - {spec_file} eliminado")
    
    # Recompilar verificador GUI
    print("\nCompilando verificador GUI con icono...")
    try:
        subprocess.check_call([
            sys.executable, "-m", "PyInstaller",
            "--onefile",
            "--windowed",
            f"--icon={icon_path}",
            "--add-data=gentoke;gentoke",
            "--name=L4D2_Verifier",
            "main.py"
        ])
        print("OK - Verificador GUI compilado")
    except subprocess.CalledProcessError as e:
        print(f"ERROR: Error al compilar verificador GUI: {e}")
        return False
    
    # Recompilar verificador consola
    print("\nCompilando verificador consola con icono...")
    try:
        subprocess.check_call([
            sys.executable, "-m", "PyInstaller",
            "--onefile",
            "--console",
            f"--icon={icon_path}",
            "--add-data=gentoke;gentoke",
            "--name=L4D2_Verifier_Console",
            "main.py"
        ])
        print("OK - Verificador consola compilado")
    except subprocess.CalledProcessError as e:
        print(f"ERROR: Error al compilar verificador consola: {e}")
        return False
    
    # Recompilar generador
    print("\nCompilando generador con icono...")
    try:
        subprocess.check_call([
            sys.executable, "-m", "PyInstaller",
            "--onefile",
            "--windowed",
            f"--icon={icon_path}",
            "--name=L4D2_Token_Generator",
            "gentoke/token_generator.py"
        ])
        print("OK - Generador compilado")
    except subprocess.CalledProcessError as e:
        print(f"ERROR: Error al compilar generador: {e}")
        return False
    
    # Copiar a directorio de distribución
    print("\nCopiando ejecutables...")
    dist_dir = Path('L4D2_Tournament_System')
    if dist_dir.exists():
        shutil.rmtree(dist_dir)
    dist_dir.mkdir()
    
    verifier_dir = dist_dir / 'Verificador'
    verifier_dir.mkdir()
    
    generator_dir = dist_dir / 'Generador_Tokens'
    generator_dir.mkdir()
    
    # Copiar ejecutables
    shutil.copy2('dist/L4D2_Verifier.exe', verifier_dir)
    shutil.copy2('dist/L4D2_Verifier_Console.exe', verifier_dir)
    shutil.copy2('dist/L4D2_Token_Generator.exe', generator_dir)
    
    print("OK - Ejecutables copiados")
    
    print("\n" + "="*50)
    print("COMPILACION CON ICONO COMPLETADA!")
    print("="*50)
    print("Los ejecutables ahora tienen el icono rdc.ico")
    print("Ubicación: L4D2_Tournament_System/")
    
    return True

if __name__ == "__main__":
    success = main()
    if not success:
        print("\nERROR: La compilación falló")
        sys.exit(1)
    
    try:
        input("\nPresiona Enter para salir...")
    except (EOFError, RuntimeError):
        pass

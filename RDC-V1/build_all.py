#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script principal para compilar ambos ejecutables
L4D2 Tournament Integrity Checker + Token Generator
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path
import time

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
        print("[ERROR] Se requiere Python 3.7 o superior")
        return False
    
    print(f"[OK] Python {sys.version.split()[0]} detectado")
    
    # Verificar archivos necesarios
    required_files = [
        'main.py',
        'gentoke/token_generator.py',
        'gentoke/requirements.txt',
        'loading.gif'
    ]
    
    for file in required_files:
        if not os.path.exists(file):
            print(f"[ERROR] No se encontro {file}")
            return False
        print(f"[OK] {file} encontrado")
    
    print("[OK] Todos los requisitos cumplidos")
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
            print(f"   [OK] {dep} instalado")
        except subprocess.CalledProcessError:
            print(f"   [WARNING] No se pudo instalar {dep}")
    
    print("[OK] Dependencias instaladas")

def clean_build_dirs():
    """Limpia directorios de compilación anteriores"""
    print("\nLimpiando compilaciones anteriores...")
    
    dirs_to_clean = ['build', 'dist', '__pycache__']
    files_to_clean = ['*.spec']
    
    for dir_name in dirs_to_clean:
        if os.path.exists(dir_name):
            shutil.rmtree(dir_name)
            print(f"   [OK] {dir_name} eliminado")
    
    # Limpiar archivos .spec
    for spec_file in Path('.').glob('*.spec'):
        spec_file.unlink()
        print(f"   [OK] {spec_file} eliminado")
    
    print("[OK] Limpieza completada")

def build_verifier():
    """Compila el verificador"""
    print("\nCompilando verificador...")
    
    try:
        # Importar y ejecutar el compilador del verificador
        from build_verifier import main as build_verifier_main
        success = build_verifier_main()
        
        if success:
            print("[OK] Verificador compilado exitosamente")
            return True
        else:
            print("[ERROR] Error al compilar verificador")
            return False
            
    except Exception as e:
        print(f"[ERROR] Error al compilar verificador: {e}")
        return False

def build_token_generator():
    """Compila el generador de tokens"""
    print("\nCompilando generador de tokens...")
    
    try:
        # Importar y ejecutar el compilador del generador
        from build_token_generator import main as build_generator_main
        success = build_generator_main()
        
        if success:
            print("[OK] Generador de tokens compilado exitosamente")
            return True
        else:
            print("[ERROR] Error al compilar generador de tokens")
            return False
            
    except Exception as e:
        print(f"[ERROR] Error al compilar generador de tokens: {e}")
        return False

def create_distribution_package():
    """Crea el paquete de distribución final"""
    print("\nCreando paquete de distribucion...")
    
    # Crear directorio de distribución
    dist_dir = Path('L4D2_Tournament_System')
    if dist_dir.exists():
        shutil.rmtree(dist_dir)
    dist_dir.mkdir()
    
    # Copiar verificador
    verifier_dir = dist_dir / 'Verificador'
    verifier_dir.mkdir()
    
    if Path('dist/L4D2_Verifier.exe').exists():
        shutil.copy2('dist/L4D2_Verifier.exe', verifier_dir)
        print("   [OK] Verificador copiado")
    
    if Path('dist/L4D2_Verifier_Console.exe').exists():
        shutil.copy2('dist/L4D2_Verifier_Console.exe', verifier_dir)
        print("   [OK] Verificador consola copiado")
    
    if Path('dist/run_verifier.bat').exists():
        shutil.copy2('dist/run_verifier.bat', verifier_dir)
        print("   [OK] Launcher verificador copiado")
    
    if Path('dist/README_VERIFIER.txt').exists():
        shutil.copy2('dist/README_VERIFIER.txt', verifier_dir)
        print("   [OK] README verificador copiado")
    
    if Path('dist/run_as_admin.bat').exists():
        shutil.copy2('dist/run_as_admin.bat', verifier_dir)
        print("   [OK] run_as_admin.bat copiado")
    
    # Copiar loading.gif al verificador
    if Path('loading.gif').exists():
        shutil.copy2('loading.gif', verifier_dir)
        print("   [OK] loading.gif copiado al verificador")
    elif Path('dist/loading.gif').exists():
        shutil.copy2('dist/loading.gif', verifier_dir)
        print("   [OK] loading.gif copiado al verificador")
    
    # Copiar generador de tokens
    generator_dir = dist_dir / 'Generador_Tokens'
    generator_dir.mkdir()
    
    if Path('dist/L4D2_Token_Generator/L4D2_Token_Generator.exe').exists():
        shutil.copy2('dist/L4D2_Token_Generator/L4D2_Token_Generator.exe', generator_dir)
        print("   [OK] Generador copiado")
    
    if Path('dist/L4D2_Token_Generator/run_generator.bat').exists():
        shutil.copy2('dist/L4D2_Token_Generator/run_generator.bat', generator_dir)
        print("   [OK] Launcher generador copiado")
    
    if Path('dist/L4D2_Token_Generator/install_generator.bat').exists():
        shutil.copy2('dist/L4D2_Token_Generator/install_generator.bat', generator_dir)
        print("   [OK] Instalador generador copiado")
    
    if Path('dist/L4D2_Token_Generator/README_GENERATOR.txt').exists():
        shutil.copy2('dist/L4D2_Token_Generator/README_GENERATOR.txt', generator_dir)
        print("   [OK] README generador copiado")
    
    # Crear README principal
    create_main_readme(dist_dir)
    
    print("[OK] Paquete de distribucion creado")

def create_main_readme(dist_dir):
    """Crea el README principal del paquete"""
    readme_content = '''# L4D2 Tournament System - Paquete Completo

## 🎮 Sistema Completo para Torneos de Left 4 Dead 2

Este paquete incluye todo lo necesario para organizar y verificar un torneo de Left 4 Dead 2.

### 📁 Contenido del Paquete

#### 📂 Verificador/
- **L4D2_Verifier.exe** - Verificador con interfaz gráfica
- **L4D2_Verifier_Console.exe** - Verificador en modo consola
- **run_verifier.bat** - Launcher automático
- **run_as_admin.bat** - Ejecutar como administrador (recomendado)
- **README_VERIFIER.txt** - Documentación del verificador

#### 📂 Generador_Tokens/
- **L4D2_Token_Generator.exe** - Generador de tokens
- **run_generator.bat** - Launcher del generador
- **install_generator.bat** - Instalador (primera vez)
- **README_GENERATOR.txt** - Documentación del generador

### 🚀 Guía de Uso Rápido

#### Para el Administrador del Torneo:

1. **Configurar Generador**:
   - Ir a la carpeta `Generador_Tokens`
   - Ejecutar `install_generator.bat` (primera vez)
   - Ejecutar `run_generator.bat`

2. **Generar Tokens**:
   - Crear tokens para cada jugador
   - Copiar y enviar tokens a los jugadores

3. **Distribuir Verificador**:
   - Copiar la carpeta `Verificador` a cada jugador
   - Los jugadores ejecutan `run_verifier.bat`

#### Para los Jugadores:

1. **Ejecutar Verificador**:
   - Ejecutar `run_as_admin.bat` (recomendado para configurar firewall automáticamente)
   - O ejecutar `run_verifier.bat` si ya se configuró anteriormente
   - Seleccionar modo (Interfaz Gráfica recomendado)

2. **Autenticar**:
   - Pegar el token recibido del administrador
   - Hacer clic en "Autenticar"

3. **Verificar**:
   - Ejecutar verificación completa
   - Obtener reporte detallado

### 🔐 Sistema de Seguridad

- **Tokens Únicos**: Cada jugador tiene un token único
- **Validación Automática**: El verificador valida tokens automáticamente
- **Reportes Detallados**: Incluye IDs completos de Steam
- **Control Total**: Solo el administrador puede generar tokens

### 📊 Características del Verificador

- ✅ Detección de mods instalados
- ✅ Análisis de cuentas Steam con IDs completos
- ✅ Detección de procesos sospechosos
- ✅ Reportes en JSON y texto
- ✅ Interfaz gráfica y modo consola

### 🎫 Características del Generador

- ✅ Generación de tokens únicos
- ✅ Interfaz gráfica intuitiva
- ✅ Gestión completa de tokens
- ✅ Generación de códigos QR
- ✅ Base de datos de tokens
- ✅ Validación y estadísticas

### ⚠️ Requisitos del Sistema

- Windows 10/11
- Steam instalado (para el verificador)
- Left 4 Dead 2 instalado (para el verificador)

### 🆘 Solución de Problemas

**Verificador no funciona**:
- Verificar que Steam y L4D2 estén instalados
- Ejecutar como administrador
- Verificar que el token sea válido

**Generador no funciona**:
- Ejecutar `install_generator.bat` primero
- Ejecutar como administrador
- Verificar que no haya antivirus bloqueando

### 📞 Soporte

Para problemas o preguntas:
1. Revisar la documentación en cada carpeta
2. Verificar requisitos del sistema
3. Contactar al administrador del torneo

---
**L4D2 Tournament System v1.0**
**Desarrollado para torneos profesionales de Left 4 Dead 2**
'''
    
    with open(dist_dir / 'README.txt', 'w', encoding='utf-8') as f:
        f.write(readme_content)
    
    print("   [OK] README principal creado")

def show_final_summary():
    """Muestra el resumen final"""
    print("\n" + "=" * 70)
    print("COMPILACION COMPLETADA EXITOSAMENTE!")
    print("=" * 70)
    print()
    print("Paquete de distribucion creado en:")
    print("   > L4D2_Tournament_System/")
    print()
    print("Estructura del paquete:")
    print("   > Verificador/")
    print("      - L4D2_Verifier.exe (Interfaz Grafica)")
    print("      - L4D2_Verifier_Console.exe (Modo Consola)")
    print("      - run_verifier.bat (Launcher)")
    print("      - README_VERIFIER.txt")
    print()
    print("   > Generador_Tokens/")
    print("      - L4D2_Token_Generator.exe")
    print("      - run_generator.bat")
    print("      - install_generator.bat")
    print("      - README_GENERATOR.txt")
    print()
    print("   > README.txt (Documentacion principal)")
    print()
    print("Proximos pasos:")
    print("   1. Probar ambos ejecutables")
    print("   2. Generar tokens para los jugadores")
    print("   3. Distribuir el verificador a los jugadores")
    print("   4. Comenzar el torneo!")
    print()
    print("=" * 70)

def main():
    """Función principal"""
    print_banner()
    
    # Verificar requisitos
    if not check_requirements():
        print("\n[ERROR] Requisitos no cumplidos")
        return False
    
    # Instalar dependencias
    install_dependencies()
    
    # Limpiar compilaciones anteriores
    clean_build_dirs()
    
    # Compilar verificador
    if not build_verifier():
        print("\n[ERROR] No se pudo compilar el verificador")
        return False
    
    # Compilar generador de tokens
    if not build_token_generator():
        print("\n[ERROR] No se pudo compilar el generador de tokens")
        return False
    
    # Crear paquete de distribución
    create_distribution_package()
    
    # Mostrar resumen final
    show_final_summary()
    
    return True

if __name__ == "__main__":
    success = main()
    if not success:
        print("\n[ERROR] La compilacion fallo")
        sys.exit(1)
    
    input("\nPresiona Enter para salir...")

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para configurar la contraseña del L4D2 Tournament Integrity Checker
"""

import sys
import os
import json
import hashlib
import base64
import secrets
import getpass

def setup_password():
    """Configura la contraseña del administrador"""
    print("L4D2 Tournament Integrity Checker - Configuración de Contraseña")
    print("=" * 60)
    print()
    
    config_file = "l4d2_checker_config.json"
    
    # Verificar si ya existe configuración
    if os.path.exists(config_file):
        print("⚠️  Ya existe una configuración. ¿Desea cambiarla? (s/n): ", end="")
        response = input().lower()
        if response != 's':
            print("Configuración cancelada.")
            return False
    
    print("Esta contraseña protegerá el acceso al programa.")
    print("Solo tú podrás usar el verificador con esta contraseña.")
    print()
    
    # Solicitar contraseña
    while True:
        password = getpass.getpass("Ingrese la contraseña (mínimo 4 caracteres): ")
        
        if len(password) < 4:
            print("❌ La contraseña debe tener al menos 4 caracteres.")
            continue
        
        confirm = getpass.getpass("Confirme la contraseña: ")
        
        if password != confirm:
            print("❌ Las contraseñas no coinciden. Intente nuevamente.")
            continue
        
        break
    
    # Generar hash de la contraseña
    salt = secrets.token_hex(32)
    password_hash = hashlib.pbkdf2_hmac('sha256', password.encode(), salt.encode(), 100000)
    
    # Crear configuración
    config = {
        'password_hash': base64.b64encode(password_hash).decode(),
        'salt': salt,
        'admin_token': secrets.token_urlsafe(32)
    }
    
    # Guardar configuración
    try:
        with open(config_file, 'w') as f:
            json.dump(config, f, indent=2)
        
        print()
        print("✅ Contraseña configurada correctamente!")
        print(f"📁 Configuración guardada en: {config_file}")
        print()
        print("🔐 Ahora solo tú podrás usar el programa con esta contraseña.")
        print("💡 Para cambiar la contraseña, usa el botón 'Cambiar Contraseña' en la interfaz.")
        
        return True
        
    except Exception as e:
        print(f"❌ Error al guardar la configuración: {e}")
        return False

def main():
    """Función principal"""
    try:
        success = setup_password()
        if not success:
            sys.exit(1)
    except KeyboardInterrupt:
        print("\n\nConfiguración cancelada por el usuario.")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Error inesperado: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()

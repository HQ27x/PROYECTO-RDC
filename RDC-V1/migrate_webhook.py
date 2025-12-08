#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para migrar el webhook de Discord hardcodeado a configuración externa
Este script debe ejecutarse ANTES de distribuir el código
"""

import os
import json
import base64
from cryptography.fernet import Fernet
from pathlib import Path

def generate_key():
    """Genera una clave de cifrado"""
    return Fernet.generate_key()

def encrypt_webhook(webhook_url, key):
    """Cifra el webhook usando Fernet"""
    f = Fernet(key)
    encrypted = f.encrypt(webhook_url.encode())
    return encrypted

def migrate_webhook():
    """Migra el webhook hardcodeado a configuración externa"""
    
    # Webhook actual (hardcodeado en main.py línea 563)
    HARDCODED_WEBHOOK = "https://discord.com/api/webhooks/1425316527070249042/TsKDgYSxrFEL8r0u3I_W3pcon8xnzHxISceFtq7lKCWxiKkQNJfBK5f8uNsfKSuRz5dF"
    
    print("=" * 60)
    print("Migración de Webhook de Discord")
    print("=" * 60)
    print()
    
    # Verificar si ya existe configuración cifrada
    config_file = Path("l4d2_checker_config.json")
    encrypted_config_file = Path("l4d2_checker_config.enc")
    
    if encrypted_config_file.exists():
        print("⚠️  Ya existe un archivo de configuración cifrado.")
        response = input("¿Desea sobrescribirlo? (s/N): ")
        if response.lower() != 's':
            print("Operación cancelada.")
            return False
    
    # Generar clave de cifrado
    print("🔑 Generando clave de cifrado...")
    key = generate_key()
    
    # Cifrar webhook
    print("🔐 Cifrando webhook...")
    encrypted_webhook = encrypt_webhook(HARDCODED_WEBHOOK, key)
    
    # Guardar configuración cifrada
    encrypted_config = {
        'encrypted_webhook': base64.b64encode(encrypted_webhook).decode(),
        'key': base64.b64encode(key).decode()
    }
    
    try:
        with open(encrypted_config_file, 'w') as f:
            json.dump(encrypted_config, f, indent=2)
        print(f"✅ Configuración cifrada guardada en: {encrypted_config_file}")
    except Exception as e:
        print(f"❌ Error al guardar configuración: {e}")
        return False
    
    # Guardar clave por separado (para el servidor/administrador)
    key_file = Path("webhook_key.key")
    try:
        with open(key_file, 'wb') as f:
            f.write(key)
        print(f"✅ Clave guardada en: {key_file}")
        print("⚠️  IMPORTANTE: Guarde este archivo de forma segura. NO lo comparta.")
    except Exception as e:
        print(f"❌ Error al guardar clave: {e}")
        return False
    
    # Actualizar configuración JSON existente (sin webhook)
    if config_file.exists():
        try:
            with open(config_file, 'r') as f:
                config = json.load(f)
            
            # Remover webhook del archivo de configuración
            if 'discord_webhook_url' in config:
                config['discord_webhook_url'] = None
                config['webhook_encrypted'] = True
            
            with open(config_file, 'w') as f:
                json.dump(config, f, indent=2)
            print(f"✅ Configuración actualizada: {config_file}")
        except Exception as e:
            print(f"⚠️  Advertencia: No se pudo actualizar {config_file}: {e}")
    
    print()
    print("=" * 60)
    print("✅ Migración completada")
    print("=" * 60)
    print()
    print("📋 Próximos pasos:")
    print("1. Actualizar main.py para leer el webhook cifrado")
    print("2. Agregar l4d2_checker_config.enc a .gitignore")
    print("3. Agregar webhook_key.key a .gitignore")
    print("4. Rotar el webhook de Discord (el actual está expuesto)")
    print("5. Distribuir el archivo cifrado por separado")
    print()
    
    return True

def decrypt_webhook(encrypted_config_file, key_file):
    """Descifra el webhook desde la configuración cifrada"""
    try:
        from cryptography.fernet import Fernet
        
        # Leer clave
        with open(key_file, 'rb') as f:
            key = f.read()
        
        # Leer configuración cifrada
        with open(encrypted_config_file, 'r') as f:
            encrypted_config = json.load(f)
        
        # Descifrar
        f = Fernet(key)
        encrypted_webhook = base64.b64decode(encrypted_config['encrypted_webhook'])
        webhook_url = f.decrypt(encrypted_webhook).decode()
        
        return webhook_url
    except Exception as e:
        print(f"Error al descifrar: {e}")
        return None

if __name__ == "__main__":
    try:
        # Verificar si cryptography está instalado
        import cryptography
    except ImportError:
        print("❌ Error: El paquete 'cryptography' no está instalado.")
        print("   Instálelo con: pip install cryptography")
        exit(1)
    
    success = migrate_webhook()
    if not success:
        exit(1)


#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script de prueba para verificar la identificación del sistema
"""

import sys
import os
import hashlib
import platform
import socket
import uuid
import subprocess
import requests

def test_system_identification():
    """Prueba la obtención de identificadores únicos del sistema"""
    print("🔍 PRUEBA DE IDENTIFICACIÓN DEL SISTEMA")
    print("=" * 50)
    
    pc_info = {}
    
    # Información básica
    pc_info['computer_name'] = platform.node()
    pc_info['os'] = platform.system()
    pc_info['os_version'] = platform.version()
    pc_info['processor'] = platform.processor()
    pc_info['architecture'] = platform.architecture()[0]
    pc_info['username'] = os.getenv('USERNAME', 'Unknown')
    
    print(f"🖥️ PC: {pc_info['computer_name']}")
    print(f"👤 Usuario: {pc_info['username']}")
    print(f"💻 OS: {pc_info['os']} {pc_info['os_version']}")
    print(f"🔧 Procesador: {pc_info['processor']}")
    print(f"🏗️ Arquitectura: {pc_info['architecture']}")
    print()
    
    # MAC Address
    try:
        mac = uuid.getnode()
        pc_info['mac_address'] = ':'.join(['{:02x}'.format((mac >> ele) & 0xff) for ele in range(0,8*6,8)][::-1])
        print(f"📡 MAC Address: {pc_info['mac_address']}")
    except Exception as e:
        pc_info['mac_address'] = 'Unknown'
        print(f"📡 MAC Address: Error - {e}")
    
    # IP Local
    try:
        hostname = socket.gethostname()
        local_ip = socket.gethostbyname(hostname)
        pc_info['local_ip'] = local_ip
        print(f"🏠 IP Local: {pc_info['local_ip']}")
    except Exception as e:
        pc_info['local_ip'] = 'Unknown'
        print(f"🏠 IP Local: Error - {e}")
    
    # IP Externa
    try:
        response = requests.get('https://api.ipify.org', timeout=5)
        if response.status_code == 200:
            pc_info['external_ip'] = response.text.strip()
            print(f"🌐 IP Externa: {pc_info['external_ip']}")
        else:
            pc_info['external_ip'] = 'Unknown'
            print(f"🌐 IP Externa: Error - Status {response.status_code}")
    except Exception as e:
        pc_info['external_ip'] = 'Unknown'
        print(f"🌐 IP Externa: Error - {e}")
    
    # System UUID (Windows)
    try:
        if platform.system() == 'Windows':
            result = subprocess.run(['wmic', 'csproduct', 'get', 'UUID'], 
                                  capture_output=True, text=True, timeout=10)
            if result.returncode == 0:
                lines = result.stdout.strip().split('\n')
                for line in lines:
                    if line.strip() and line.strip() != 'UUID':
                        pc_info['system_uuid'] = line.strip()
                        break
                if 'system_uuid' not in pc_info:
                    pc_info['system_uuid'] = 'Unknown'
            else:
                pc_info['system_uuid'] = 'Unknown'
        else:
            pc_info['system_uuid'] = 'Unknown'
        print(f"🆔 System UUID: {pc_info['system_uuid']}")
    except Exception as e:
        pc_info['system_uuid'] = 'Unknown'
        print(f"🆔 System UUID: Error - {e}")
    
    # Disk Serial (Windows)
    try:
        if platform.system() == 'Windows':
            result = subprocess.run(['wmic', 'diskdrive', 'get', 'SerialNumber'], 
                                  capture_output=True, text=True, timeout=10)
            if result.returncode == 0:
                lines = result.stdout.strip().split('\n')
                for line in lines:
                    if line.strip() and line.strip() != 'SerialNumber':
                        pc_info['disk_serial'] = line.strip()
                        break
                if 'disk_serial' not in pc_info:
                    pc_info['disk_serial'] = 'Unknown'
            else:
                pc_info['disk_serial'] = 'Unknown'
        else:
            pc_info['disk_serial'] = 'Unknown'
        print(f"💾 Disk Serial: {pc_info['disk_serial']}")
    except Exception as e:
        pc_info['disk_serial'] = 'Unknown'
        print(f"💾 Disk Serial: Error - {e}")
    
    # Crear huella digital única
    fingerprint_parts = [
        pc_info.get('computer_name', ''),
        pc_info.get('mac_address', ''),
        pc_info.get('system_uuid', ''),
        pc_info.get('disk_serial', '')
    ]
    fingerprint = hashlib.md5('|'.join(fingerprint_parts).encode()).hexdigest()
    pc_info['system_fingerprint'] = fingerprint
    print(f"🔑 System Fingerprint: {pc_info['system_fingerprint']}")
    
    print()
    print("📊 RESUMEN:")
    print(f"   Identificadores obtenidos: {len([k for k, v in pc_info.items() if v != 'Unknown'])}")
    print(f"   Identificadores fallidos: {len([k for k, v in pc_info.items() if v == 'Unknown'])}")
    
    return pc_info

def test_discord_message():
    """Prueba el mensaje de Discord con la nueva información"""
    print("\n📱 PRUEBA DE MENSAJE DISCORD")
    print("=" * 50)
    
    pc_info = test_system_identification()
    
    # Simular mensaje de Discord
    embed = {
        "title": "🎮 L4D2 Tournament - Verificación de Integridad",
        "description": "**Estado General**: ✅ CLEAN\n**Resumen**: Sistema limpio detectado",
        "color": 0x00ff00,
        "fields": [
            {
                "name": "🖥️ PC",
                "value": f"{pc_info.get('computer_name', 'Unknown')} ({pc_info.get('username', 'Unknown')})",
                "inline": True
            },
            {
                "name": "📅 Fecha",
                "value": "2024-01-15 10:30:00",
                "inline": True
            },
            {
                "name": "🎯 Estado",
                "value": "✅ CLEAN",
                "inline": True
            },
            {
                "name": "🔐 Identificación del Sistema",
                "value": f"🌐 **IP Externa**: `{pc_info.get('external_ip', 'Unknown')}`\n"
                        f"🏠 **IP Local**: `{pc_info.get('local_ip', 'Unknown')}`\n"
                        f"📡 **MAC Address**: `{pc_info.get('mac_address', 'Unknown')}`\n"
                        f"🆔 **System UUID**: `{pc_info.get('system_uuid', 'Unknown')[:8]}...`\n"
                        f"💾 **Disk Serial**: `{pc_info.get('disk_serial', 'Unknown')[:8]}...`\n"
                        f"🔑 **Fingerprint**: `{pc_info.get('system_fingerprint', 'Unknown')[:16]}...`",
                "inline": False
            }
        ],
        "footer": {
            "text": "L4D2 Tournament Integrity Checker - Prueba de Identificación"
        }
    }
    
    print("📤 Mensaje de Discord generado:")
    print(f"   Título: {embed['title']}")
    print(f"   Descripción: {embed['description']}")
    print(f"   Campos: {len(embed['fields'])}")
    print(f"   Identificación incluida: ✅")
    
    return embed

if __name__ == "__main__":
    print("🔍 L4D2 Tournament - Prueba de Identificación del Sistema")
    print("=" * 60)
    
    # Probar identificación del sistema
    pc_info = test_system_identification()
    
    # Probar mensaje de Discord
    discord_embed = test_discord_message()
    
    print("\n✅ PRUEBA COMPLETADA")
    print("=" * 60)
    print("La nueva funcionalidad de identificación del sistema está lista.")
    print("Ahora cada verificación incluirá identificadores únicos para detectar suplantaciones.")
    
    input("\nPresiona Enter para salir...")

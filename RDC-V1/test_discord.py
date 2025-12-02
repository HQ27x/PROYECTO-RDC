#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script de prueba para verificar la conexión con Discord
"""

import requests
import json
from datetime import datetime

def test_discord_webhook():
    """Prueba el webhook de Discord"""
    
    webhook_url = "https://discord.com/api/webhooks/1425304759207989268/5bzUrB8yIIWoLrzmOZJwoLWQkubgSFqE3jwEOZR5KrEeybsRh6_GJLV_rOQCZeyx3Vh5"
    
    # Crear mensaje de prueba
    embed = {
        "title": "🎮 L4D2 Tournament - Prueba de Conexión",
        "description": "¡El verificador está configurado correctamente!",
        "color": 0x00ff00,  # Verde
        "fields": [
            {
                "name": "🖥️ PC",
                "value": "PC de Prueba (Usuario de Prueba)",
                "inline": True
            },
            {
                "name": "📅 Fecha",
                "value": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "inline": True
            },
            {
                "name": "🎯 Estado",
                "value": "✅ PRUEBA EXITOSA",
                "inline": True
            },
            {
                "name": "👥 Cuentas Steam",
                "value": "0",
                "inline": True
            },
            {
                "name": "🔧 Mods Detectados",
                "value": "0",
                "inline": True
            },
            {
                "name": "⚠️ Procesos Sospechosos",
                "value": "0",
                "inline": True
            }
        ],
        "footer": {
            "text": "L4D2 Tournament Integrity Checker - Prueba de Conexión"
        },
        "timestamp": datetime.now().isoformat()
    }
    
    payload = {
        "embeds": [embed]
    }
    
    try:
        print("📤 Enviando mensaje de prueba a Discord...")
        response = requests.post(webhook_url, json=payload, timeout=10)
        response.raise_for_status()
        
        print("✅ ¡Mensaje enviado exitosamente!")
        print("📱 Revisa tu canal de Discord para ver el mensaje")
        
        return True
        
    except Exception as e:
        print(f"❌ Error al enviar mensaje: {e}")
        return False

if __name__ == "__main__":
    print("🎮 L4D2 Tournament - Prueba de Discord")
    print("=" * 50)
    test_discord_webhook()
    input("\nPresiona Enter para salir...")

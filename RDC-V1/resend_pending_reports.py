#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para reenviar reportes pendientes de Discord
Ejecuta este script cuando tengas conexión estable para enviar reportes guardados
"""

import os
import sys
import json
import requests
from datetime import datetime

def is_compiled():
    """Verifica si el script está compilado"""
    return getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS')

def resend_pending_reports():
    """Reenvía todos los reportes pendientes"""
    try:
        # Buscar carpeta de reportes pendientes
        if is_compiled():
            pending_dir = os.path.join(os.path.dirname(sys.executable), "PendingReports")
        else:
            pending_dir = "PendingReports"
        
        if not os.path.exists(pending_dir):
            print("📁 No se encontró la carpeta 'PendingReports'")
            print("✅ No hay reportes pendientes que reenviar")
            return 0, 0
        
        pending_files = [f for f in os.listdir(pending_dir) if f.startswith("pending_") and f.endswith(".json")]
        
        if not pending_files:
            print("📦 No hay reportes pendientes en la cola")
            return 0, 0
        
        successful = 0
        failed = 0
        
        print("="*60)
        print("🔄 L4D2 Tournament - Reenvío de Reportes Pendientes")
        print("="*60)
        print(f"\n📦 Encontrados {len(pending_files)} reporte(s) pendiente(s)\n")
        
        for pending_file in pending_files:
            file_path = os.path.join(pending_dir, pending_file)
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    pending_data = json.load(f)
                
                filename = pending_data['filename']
                report_txt = pending_data['report_txt']
                payload = pending_data['payload']
                webhook_url = pending_data['webhook_url']
                
                # Preparar archivo para envío
                files = {
                    'file': (filename, report_txt.encode('utf-8'), 'text/plain')
                }
                
                # Mostrar información del reporte
                print(f"[{pending_files.index(pending_file) + 1}/{len(pending_files)}] {filename}")
                print(f"  📅 Creado: {pending_data.get('created_at', 'N/A')}")
                print(f"  🔢 Intentos previos: {pending_data.get('attempts', 0)}")
                
                # Intentar enviar
                print(f"  📤 Enviando a Discord...", end=" ")
                try:
                    response = requests.post(
                        webhook_url,
                        data={'payload_json': json.dumps(payload)},
                        files=files,
                        timeout=30
                    )
                    response.raise_for_status()
                    
                    print("✅ EXITOSO")
                    successful += 1
                    
                    # Eliminar archivo pendiente si se envió correctamente
                    os.remove(file_path)
                    
                    # También eliminar el TXT si existe
                    txt_path = os.path.join(pending_dir, filename)
                    if os.path.exists(txt_path):
                        os.remove(txt_path)
                    
                    print(f"  🗑️ Reporte eliminado de la cola\n")
                
                except requests.exceptions.Timeout:
                    print("❌ TIMEOUT")
                    failed += 1
                    pending_data['attempts'] = pending_data.get('attempts', 0) + 1
                    pending_data['last_attempt'] = datetime.now().isoformat()
                    pending_data['last_error'] = "Timeout"
                    with open(file_path, 'w', encoding='utf-8') as f:
                        json.dump(pending_data, f, indent=2, ensure_ascii=False)
                    print(f"  ⏳ Reintenta más tarde\n")
                
                except requests.exceptions.ConnectionError as e:
                    print(f"❌ ERROR DE CONEXIÓN")
                    failed += 1
                    pending_data['attempts'] = pending_data.get('attempts', 0) + 1
                    pending_data['last_attempt'] = datetime.now().isoformat()
                    pending_data['last_error'] = f"ConnectionError: {str(e)}"
                    with open(file_path, 'w', encoding='utf-8') as f:
                        json.dump(pending_data, f, indent=2, ensure_ascii=False)
                    print(f"  ⚠️ Verifica tu conexión a internet\n")
                
                except requests.exceptions.HTTPError as e:
                    print(f"❌ ERROR HTTP: {e.response.status_code if hasattr(e, 'response') else 'N/A'}")
                    failed += 1
                    pending_data['attempts'] = pending_data.get('attempts', 0) + 1
                    pending_data['last_attempt'] = datetime.now().isoformat()
                    pending_data['last_error'] = f"HTTPError: {str(e)}"
                    with open(file_path, 'w', encoding='utf-8') as f:
                        json.dump(pending_data, f, indent=2, ensure_ascii=False)
                    print(f"  ⚠️ Problema con el webhook de Discord\n")
                
                except Exception as e:
                    print(f"❌ ERROR: {type(e).__name__}")
                    failed += 1
                    pending_data['attempts'] = pending_data.get('attempts', 0) + 1
                    pending_data['last_attempt'] = datetime.now().isoformat()
                    pending_data['last_error'] = f"{type(e).__name__}: {str(e)}"
                    with open(file_path, 'w', encoding='utf-8') as f:
                        json.dump(pending_data, f, indent=2, ensure_ascii=False)
                    print(f"  ⚠️ Error inesperado\n")
            
            except Exception as e:
                print(f"⚠️ Error al procesar {pending_file}: {e}")
                failed += 1
        
        # Resumen final
        print("="*60)
        print("📊 RESUMEN")
        print("="*60)
        print(f"✅ Reportes enviados exitosamente: {successful}")
        print(f"❌ Reportes que fallaron: {failed}")
        print(f"📦 Total procesado: {successful + failed}")
        print("="*60)
        
        if successful > 0:
            print("\n✅ ¡Algunos reportes se reenviaron correctamente!")
        
        if failed > 0:
            print("\n⚠️ Algunos reportes no se pudieron enviar.")
            print("   Verifica tu conexión a internet e intenta de nuevo ejecutando este script.")
        
        return successful, failed
        
    except Exception as e:
        print(f"❌ Error crítico: {e}")
        return 0, 0

if __name__ == "__main__":
    print("\n🔄 Iniciando reenvío de reportes pendientes...\n")
    successful, failed = resend_pending_reports()
    
    if successful == 0 and failed == 0:
        print("\n✅ No hay reportes pendientes")
    
    print("\nPresiona Enter para salir...")
    try:
        input()
    except:
        pass


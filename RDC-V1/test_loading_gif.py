#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script de prueba para verificar que loading.gif funciona correctamente
"""

import os
import sys
import tkinter as tk
from tkinter import ttk

def test_gif():
    """Prueba la carga y animación del GIF"""
    print("🔍 Probando loading.gif...")
    print()
    
    # Verificar que el archivo existe
    if not os.path.exists('loading.gif'):
        print("❌ Error: No se encontró loading.gif")
        print("   Asegúrate de que el archivo esté en el directorio actual")
        return False
    
    print("✅ loading.gif encontrado")
    
    # Verificar PIL/Pillow
    try:
        from PIL import Image, ImageTk
        print("✅ PIL/Pillow instalado correctamente")
    except ImportError:
        print("❌ Error: PIL/Pillow no está instalado")
        print("   Ejecuta: pip install Pillow")
        return False
    
    # Intentar cargar el GIF
    try:
        pil_image = Image.open('loading.gif')
        print(f"✅ GIF cargado correctamente")
        print(f"   Formato: {pil_image.format}")
        print(f"   Tamaño: {pil_image.size}")
        print(f"   Modo: {pil_image.mode}")
        
        # Verificar si es animado
        if hasattr(pil_image, 'n_frames'):
            print(f"   Frames: {pil_image.n_frames}")
            print(f"   Duración: {pil_image.info.get('duration', 'No especificada')}ms por frame")
        else:
            print("   ⚠️  Advertencia: El GIF no parece ser animado")
        
    except Exception as e:
        print(f"❌ Error al cargar GIF: {e}")
        return False
    
    # Crear ventana de prueba
    print()
    print("📺 Abriendo ventana de prueba...")
    print("   (Cierra la ventana para continuar)")
    
    try:
        root = tk.Tk()
        root.title("Test - Loading GIF")
        root.geometry("600x500")
        
        # Frame principal
        main_frame = ttk.Frame(root, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Título
        title_label = ttk.Label(main_frame, 
                               text="🔍 Prueba de Loading GIF", 
                               font=("Arial", 16, "bold"))
        title_label.pack(pady=(0, 20))
        
        # Mostrar GIF
        gif_label = ttk.Label(main_frame)
        gif_label.pack(pady=(0, 20))
        
        # Información
        info_label = ttk.Label(main_frame, 
                              text=f"Archivo: loading.gif\n"
                                   f"Tamaño: {pil_image.size[0]}x{pil_image.size[1]}\n"
                                   f"Frames: {getattr(pil_image, 'n_frames', 1)}", 
                              font=("Arial", 10))
        info_label.pack(pady=(0, 20))
        
        # Mensaje
        msg_label = ttk.Label(main_frame, 
                             text="Si ves la animación moviéndose,\n"
                                  "el GIF funciona correctamente! ✅", 
                             font=("Arial", 12))
        msg_label.pack(pady=(0, 20))
        
        # Botón cerrar
        close_button = ttk.Button(main_frame, text="Cerrar", command=root.destroy)
        close_button.pack()
        
        # Animar GIF
        def animate_gif(frame_index=0):
            try:
                pil_image.seek(frame_index)
                photo = ImageTk.PhotoImage(pil_image)
                gif_label.config(image=photo)
                gif_label.image = photo
                
                delay = pil_image.info.get('duration', 50)
                next_frame = (frame_index + 1) % pil_image.n_frames
                root.after(delay, lambda: animate_gif(next_frame))
            except:
                root.after(50, lambda: animate_gif(0))
        
        animate_gif()
        
        root.mainloop()
        
        print()
        print("✅ Prueba completada")
        return True
        
    except Exception as e:
        print(f"❌ Error al crear ventana de prueba: {e}")
        return False

def main():
    """Función principal"""
    print("=" * 60)
    print("🧪 TEST DE LOADING.GIF")
    print("=" * 60)
    print()
    
    success = test_gif()
    
    print()
    print("=" * 60)
    if success:
        print("🎉 ¡TODAS LAS PRUEBAS PASARON!")
        print("=" * 60)
        print()
        print("El loading.gif está listo para usarse en el verificador.")
        print("Puedes proceder a compilar con build_all.py")
    else:
        print("❌ ALGUNAS PRUEBAS FALLARON")
        print("=" * 60)
        print()
        print("Por favor corrige los errores antes de compilar.")
    
    print()
    return success

if __name__ == "__main__":
    success = main()
    if not success:
        sys.exit(1)
    
    input("Presiona Enter para salir...")



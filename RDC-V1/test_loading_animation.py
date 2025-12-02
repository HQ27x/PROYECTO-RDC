#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script de prueba para la animación de carga
"""

import tkinter as tk
from tkinter import ttk
import os
import time
import threading

def test_loading_animation():
    """Prueba la animación de carga"""
    root = tk.Tk()
    root.title("Prueba de Animación de Carga")
    root.geometry("500x400")
    
    def show_loading():
        """Muestra la ventana de carga"""
        loading_window = tk.Toplevel(root)
        loading_window.title("Verificando Integridad...")
        loading_window.geometry("400x300")
        loading_window.resizable(False, False)
        
        # Centrar la ventana
        loading_window.transient(root)
        loading_window.grab_set()
        
        # Centrar en la pantalla
        loading_window.geometry("+%d+%d" % (
            root.winfo_rootx() + 50, 
            root.winfo_rooty() + 50
        ))
        
        # Frame principal
        main_frame = ttk.Frame(loading_window, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Título
        title_label = ttk.Label(main_frame, text="🔍 Verificando Integridad del Sistema", 
                               font=("Arial", 14, "bold"))
        title_label.pack(pady=(0, 20))
        
        # Frame para el GIF
        gif_frame = ttk.Frame(main_frame)
        gif_frame.pack(pady=(0, 20))
        
        # Intentar cargar el GIF
        try:
            from PIL import Image, ImageTk
            
            # Cargar el GIF
            gif_path = "loading.gif"
            if os.path.exists(gif_path):
                print(f"✓ GIF encontrado: {gif_path}")
                
                # Crear imagen PIL
                pil_image = Image.open(gif_path)
                print(f"✓ GIF cargado: {pil_image.n_frames} frames")
                
                # Convertir a PhotoImage
                loading_image = ImageTk.PhotoImage(pil_image)
                
                # Mostrar la imagen
                gif_label = ttk.Label(gif_frame, image=loading_image)
                gif_label.pack()
                
                # Iniciar animación del GIF
                animate_gif(pil_image, gif_label, 0)
            else:
                print(f"✗ GIF no encontrado: {gif_path}")
                show_text_animation(gif_frame)
                
        except ImportError:
            print("✗ PIL no disponible, usando animación de texto")
            show_text_animation(gif_frame)
        except Exception as e:
            print(f"✗ Error al cargar GIF: {e}")
            show_text_animation(gif_frame)
        
        # Mensaje de progreso
        progress_label = ttk.Label(main_frame, text="Iniciando verificación...", 
                                  font=("Arial", 10))
        progress_label.pack(pady=(0, 10))
        
        # Barra de progreso
        progress_bar = ttk.Progressbar(main_frame, mode='indeterminate')
        progress_bar.pack(fill=tk.X, pady=(0, 20))
        progress_bar.start()
        
        # Mensaje informativo
        info_text = ("Analizando sistema...\n"
                    "• Detectando mods instalados\n"
                    "• Analizando cuentas Steam\n"
                    "• Escaneando procesos\n"
                    "• Obteniendo identificadores del sistema\n"
                    "• Generando reporte completo")
        
        info_label = ttk.Label(main_frame, text=info_text, 
                              font=("Arial", 9), justify=tk.LEFT)
        info_label.pack(pady=(0, 20))
        
        # Botón cerrar
        close_button = ttk.Button(main_frame, text="Cerrar", 
                                 command=loading_window.destroy)
        close_button.pack()
        
        # Actualizar mensajes de progreso
        update_progress_messages(progress_label, loading_window)
        
        return loading_window
    
    def animate_gif(pil_image, label, frame_index):
        """Anima el GIF frame por frame"""
        try:
            # Obtener el frame actual
            pil_image.seek(frame_index)
            
            # Convertir a PhotoImage
            photo = ImageTk.PhotoImage(pil_image)
            
            # Actualizar la imagen
            label.config(image=photo)
            label.image = photo  # Mantener referencia
            
            # Programar el siguiente frame
            root.after(100, lambda: animate_gif(pil_image, label, (frame_index + 1) % pil_image.n_frames))
            
        except Exception:
            # Si hay error, reiniciar desde el frame 0
            root.after(100, lambda: animate_gif(pil_image, label, 0))
    
    def show_text_animation(parent):
        """Muestra animación de texto si no hay GIF"""
        loading_text = ttk.Label(parent, text="⏳", font=("Arial", 24))
        loading_text.pack()
        
        # Animar el texto
        animate_text(loading_text)
    
    def animate_text(loading_text):
        """Anima el texto de carga"""
        symbols = ["⏳", "⏰", "🔄", "⚡", "🔍", "📊", "🛡️", "✅"]
        current_symbol = loading_text.cget("text")
        try:
            current_index = symbols.index(current_symbol)
            next_index = (current_index + 1) % len(symbols)
            loading_text.config(text=symbols[next_index])
        except ValueError:
            loading_text.config(text=symbols[0])
        
        # Programar siguiente animación
        root.after(500, lambda: animate_text(loading_text))
    
    def update_progress_messages(progress_label, loading_window):
        """Actualiza los mensajes de progreso"""
        messages = [
            "Iniciando verificación...",
            "Detectando mods instalados...",
            "Analizando cuentas Steam...",
            "Escaneando procesos del sistema...",
            "Obteniendo identificadores únicos...",
            "Generando reporte completo...",
            "Enviando resultados a Discord...",
            "Finalizando verificación..."
        ]
        
        try:
            current_text = progress_label.cget("text")
            try:
                current_index = messages.index(current_text)
                next_index = (current_index + 1) % len(messages)
                progress_label.config(text=messages[next_index])
            except ValueError:
                progress_label.config(text=messages[0])
            
            # Programar siguiente mensaje
            root.after(2000, lambda: update_progress_messages(progress_label, loading_window))
        except tk.TclError:
            # La ventana fue cerrada
            pass
    
    # Botón para probar la animación
    test_button = ttk.Button(root, text="Probar Animación de Carga", 
                           command=show_loading)
    test_button.pack(pady=50)
    
    # Información
    info_text = """Prueba de Animación de Carga
=====================================

Este script prueba la funcionalidad de carga que se agregó al verificador.

Características:
• Animación GIF (si está disponible)
• Animación de texto (fallback)
• Mensajes de progreso dinámicos
• Barra de progreso indeterminada
• Ventana modal centrada

El GIF loading.gif debe estar en el directorio actual."""
    
    info_label = ttk.Label(root, text=info_text, font=("Arial", 10), justify=tk.LEFT)
    info_label.pack(pady=20, padx=20)
    
    root.mainloop()

if __name__ == "__main__":
    print("🔍 Prueba de Animación de Carga")
    print("=" * 40)
    
    # Verificar si existe el GIF
    if os.path.exists("loading.gif"):
        print("✓ GIF loading.gif encontrado")
    else:
        print("✗ GIF loading.gif NO encontrado - se usará animación de texto")
    
    test_loading_animation()


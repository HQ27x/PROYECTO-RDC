#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Generador de Tokens Únicos para L4D2 Tournament Integrity Checker
Genera tokens únicos para cada jugador del torneo
"""

import os
import json
import secrets
import hashlib
import base64
from datetime import datetime, timedelta
import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import qrcode
from PIL import Image, ImageTk
import io

class TokenGenerator:
    def __init__(self):
        self.tokens_file = "tokens_database.json"
        self.tokens = self.load_tokens()
        
    def load_tokens(self):
        """Carga la base de datos de tokens"""
        if os.path.exists(self.tokens_file):
            try:
                with open(self.tokens_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except (json.JSONDecodeError, FileNotFoundError):
                return {}
        return {}
    
    def save_tokens(self):
        """Guarda la base de datos de tokens"""
        try:
            with open(self.tokens_file, 'w', encoding='utf-8') as f:
                json.dump(self.tokens, f, indent=2, ensure_ascii=False)
            return True
        except Exception as e:
            print(f"Error al guardar tokens: {e}")
            return False
    
    def generate_token(self, player_name, tournament_name="L4D2 Tournament", expires_days=30):
        """Genera un token único para un jugador"""
        # Generar token único
        token = secrets.token_urlsafe(32)
        
        # Crear hash del token para verificación
        token_hash = hashlib.sha256(token.encode()).hexdigest()
        
        # Fecha de expiración
        expires_date = datetime.now() + timedelta(days=expires_days)
        
        # Crear entrada del token
        token_data = {
            'player_name': player_name,
            'tournament_name': tournament_name,
            'token': token,
            'token_hash': token_hash,
            'created_date': datetime.now().isoformat(),
            'expires_date': expires_date.isoformat(),
            'is_active': True,
            'used_count': 0,
            'last_used': None
        }
        
        # Guardar token
        self.tokens[token_hash] = token_data
        
        if self.save_tokens():
            return token_data
        else:
            return None
    
    def validate_token(self, token):
        """Valida un token"""
        token_hash = hashlib.sha256(token.encode()).hexdigest()
        
        if token_hash not in self.tokens:
            return False, "Token no encontrado"
        
        token_data = self.tokens[token_hash]
        
        # Verificar si está activo
        if not token_data.get('is_active', True):
            return False, "Token desactivado"
        
        # Verificar expiración
        expires_date = datetime.fromisoformat(token_data['expires_date'])
        if datetime.now() > expires_date:
            return False, "Token expirado"
        
        # Actualizar uso
        token_data['used_count'] += 1
        token_data['last_used'] = datetime.now().isoformat()
        self.save_tokens()
        
        return True, token_data
    
    def deactivate_token(self, token):
        """Desactiva un token"""
        token_hash = hashlib.sha256(token.encode()).hexdigest()
        
        if token_hash in self.tokens:
            self.tokens[token_hash]['is_active'] = False
            self.save_tokens()
            return True
        return False
    
    def get_token_stats(self):
        """Obtiene estadísticas de tokens"""
        total_tokens = len(self.tokens)
        active_tokens = sum(1 for t in self.tokens.values() if t.get('is_active', True))
        expired_tokens = 0
        
        for token_data in self.tokens.values():
            expires_date = datetime.fromisoformat(token_data['expires_date'])
            if datetime.now() > expires_date:
                expired_tokens += 1
        
        return {
            'total_tokens': total_tokens,
            'active_tokens': active_tokens,
            'expired_tokens': expired_tokens
        }
    
    def list_tokens(self):
        """Lista todos los tokens"""
        return self.tokens

class TokenGeneratorGUI:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("L4D2 Tournament Token Generator")
        self.root.geometry("1000x700")
        self.root.resizable(True, True)
        
        self.generator = TokenGenerator()
        self.setup_ui()
    
    def setup_ui(self):
        """Configura la interfaz de usuario"""
        # Frame principal
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configurar grid
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        
        # Título
        title_label = ttk.Label(main_frame, text="L4D2 Tournament Token Generator", 
                               font=("Arial", 16, "bold"))
        title_label.grid(row=0, column=0, columnspan=2, pady=(0, 20))
        
        # Frame izquierdo - Generar tokens
        left_frame = ttk.LabelFrame(main_frame, text="Generar Token", padding="10")
        left_frame.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), padx=(0, 10))
        
        # Campos de entrada
        ttk.Label(left_frame, text="Nombre del Jugador:").grid(row=0, column=0, sticky=tk.W, pady=(0, 5))
        self.player_name_entry = ttk.Entry(left_frame, width=30)
        self.player_name_entry.grid(row=0, column=1, sticky=(tk.W, tk.E), pady=(0, 5))
        
        ttk.Label(left_frame, text="Nombre del Torneo:").grid(row=1, column=0, sticky=tk.W, pady=(0, 5))
        self.tournament_entry = ttk.Entry(left_frame, width=30)
        self.tournament_entry.insert(0, "L4D2 Tournament")
        self.tournament_entry.grid(row=1, column=1, sticky=(tk.W, tk.E), pady=(0, 5))
        
        ttk.Label(left_frame, text="Días de validez:").grid(row=2, column=0, sticky=tk.W, pady=(0, 5))
        self.days_entry = ttk.Entry(left_frame, width=30)
        self.days_entry.insert(0, "30")
        self.days_entry.grid(row=2, column=1, sticky=(tk.W, tk.E), pady=(0, 10))
        
        # Botón generar
        self.generate_button = ttk.Button(left_frame, text="Generar Token", 
                                         command=self.generate_token)
        self.generate_button.grid(row=3, column=0, columnspan=2, pady=(0, 20))
        
        # Área de token generado
        ttk.Label(left_frame, text="Token Generado:").grid(row=4, column=0, sticky=tk.W, pady=(0, 5))
        self.token_text = scrolledtext.ScrolledText(left_frame, height=6, width=40)
        self.token_text.grid(row=5, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        
        # Botones de acción
        button_frame = ttk.Frame(left_frame)
        button_frame.grid(row=6, column=0, columnspan=2, sticky=(tk.W, tk.E))
        
        ttk.Button(button_frame, text="Copiar Token", 
                  command=self.copy_token).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(button_frame, text="Generar QR", 
                  command=self.generate_qr).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(button_frame, text="Limpiar", 
                  command=self.clear_token).pack(side=tk.LEFT)
        
        # Frame derecho - Gestión de tokens
        right_frame = ttk.LabelFrame(main_frame, text="Gestión de Tokens", padding="10")
        right_frame.grid(row=1, column=1, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Botones de gestión
        manage_frame = ttk.Frame(right_frame)
        manage_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        
        ttk.Button(manage_frame, text="Ver Todos los Tokens", 
                  command=self.show_all_tokens).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(manage_frame, text="Estadísticas", 
                  command=self.show_stats).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(manage_frame, text="Validar Token", 
                  command=self.validate_token_dialog).pack(side=tk.LEFT)
        
        # Área de resultados
        self.results_text = scrolledtext.ScrolledText(right_frame, height=20, width=50)
        self.results_text.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 10))
        
        # Configurar grid weights
        main_frame.rowconfigure(1, weight=1)
        left_frame.columnconfigure(1, weight=1)
        right_frame.columnconfigure(0, weight=1)
        right_frame.rowconfigure(1, weight=1)
    
    def generate_token(self):
        """Genera un nuevo token"""
        player_name = self.player_name_entry.get().strip()
        tournament_name = self.tournament_entry.get().strip()
        
        try:
            days = int(self.days_entry.get())
        except ValueError:
            messagebox.showerror("Error", "Los días de validez deben ser un número")
            return
        
        if not player_name:
            messagebox.showerror("Error", "El nombre del jugador es obligatorio")
            return
        
        token_data = self.generator.generate_token(player_name, tournament_name, days)
        
        if token_data:
            self.token_text.delete(1.0, tk.END)
            self.token_text.insert(tk.END, f"TOKEN GENERADO EXITOSAMENTE\n")
            self.token_text.insert(tk.END, f"{'='*50}\n\n")
            self.token_text.insert(tk.END, f"Jugador: {token_data['player_name']}\n")
            self.token_text.insert(tk.END, f"Torneo: {token_data['tournament_name']}\n")
            self.token_text.insert(tk.END, f"Token: {token_data['token']}\n")
            self.token_text.insert(tk.END, f"Creado: {token_data['created_date']}\n")
            self.token_text.insert(tk.END, f"Expira: {token_data['expires_date']}\n")
            self.token_text.insert(tk.END, f"Hash: {token_data['token_hash']}\n")
            
            messagebox.showinfo("Éxito", "Token generado correctamente")
        else:
            messagebox.showerror("Error", "No se pudo generar el token")
    
    def copy_token(self):
        """Copia el token al portapapeles"""
        token_content = self.token_text.get(1.0, tk.END).strip()
        if token_content:
            self.root.clipboard_clear()
            self.root.clipboard_append(token_content)
            messagebox.showinfo("Éxito", "Token copiado al portapapeles")
        else:
            messagebox.showwarning("Advertencia", "No hay token para copiar")
    
    def generate_qr(self):
        """Genera un código QR del token"""
        token_content = self.token_text.get(1.0, tk.END).strip()
        if not token_content:
            messagebox.showwarning("Advertencia", "No hay token para generar QR")
            return
        
        try:
            # Crear QR
            qr = qrcode.QRCode(version=1, box_size=10, border=5)
            qr.add_data(token_content)
            qr.make(fit=True)
            
            # Crear imagen
            img = qr.make_image(fill_color="black", back_color="white")
            
            # Mostrar en ventana
            self.show_qr_window(img)
            
        except Exception as e:
            messagebox.showerror("Error", f"Error al generar QR: {e}")
    
    def show_qr_window(self, img):
        """Muestra el QR en una ventana"""
        qr_window = tk.Toplevel(self.root)
        qr_window.title("Código QR del Token")
        qr_window.geometry("400x450")
        
        # Convertir imagen para tkinter
        img_tk = ImageTk.PhotoImage(img)
        
        # Mostrar imagen
        label = ttk.Label(qr_window, image=img_tk)
        label.image = img_tk  # Mantener referencia
        label.pack(pady=20)
        
        # Botón cerrar
        ttk.Button(qr_window, text="Cerrar", 
                  command=qr_window.destroy).pack(pady=10)
    
    def clear_token(self):
        """Limpia el área de token"""
        self.token_text.delete(1.0, tk.END)
        self.player_name_entry.delete(0, tk.END)
        self.tournament_entry.delete(0, tk.END)
        self.tournament_entry.insert(0, "L4D2 Tournament")
        self.days_entry.delete(0, tk.END)
        self.days_entry.insert(0, "30")
    
    def show_all_tokens(self):
        """Muestra todos los tokens"""
        self.results_text.delete(1.0, tk.END)
        
        tokens = self.generator.list_tokens()
        if not tokens:
            self.results_text.insert(tk.END, "No hay tokens generados")
            return
        
        self.results_text.insert(tk.END, f"TOKENS GENERADOS ({len(tokens)})\n")
        self.results_text.insert(tk.END, f"{'='*60}\n\n")
        
        for i, (token_hash, token_data) in enumerate(tokens.items(), 1):
            status = "ACTIVO" if token_data.get('is_active', True) else "INACTIVO"
            expires_date = datetime.fromisoformat(token_data['expires_date'])
            is_expired = datetime.now() > expires_date
            
            if is_expired:
                status = "EXPIRADO"
            
            self.results_text.insert(tk.END, f"{i}. {token_data['player_name']}\n")
            self.results_text.insert(tk.END, f"   Torneo: {token_data['tournament_name']}\n")
            self.results_text.insert(tk.END, f"   Token: {token_data['token'][:20]}...\n")
            self.results_text.insert(tk.END, f"   Estado: {status}\n")
            self.results_text.insert(tk.END, f"   Usado: {token_data['used_count']} veces\n")
            self.results_text.insert(tk.END, f"   Expira: {token_data['expires_date']}\n")
            self.results_text.insert(tk.END, f"   Hash: {token_hash[:20]}...\n\n")
    
    def show_stats(self):
        """Muestra estadísticas de tokens"""
        stats = self.generator.get_token_stats()
        
        self.results_text.delete(1.0, tk.END)
        self.results_text.insert(tk.END, "ESTADÍSTICAS DE TOKENS\n")
        self.results_text.insert(tk.END, f"{'='*30}\n\n")
        self.results_text.insert(tk.END, f"Total de tokens: {stats['total_tokens']}\n")
        self.results_text.insert(tk.END, f"Tokens activos: {stats['active_tokens']}\n")
        self.results_text.insert(tk.END, f"Tokens expirados: {stats['expired_tokens']}\n")
    
    def validate_token_dialog(self):
        """Muestra diálogo para validar token"""
        dialog = TokenValidationDialog(self.root, self.generator)
        self.root.wait_window(dialog.dialog)
        
        if dialog.result:
            self.results_text.delete(1.0, tk.END)
            self.results_text.insert(tk.END, f"VALIDACIÓN DE TOKEN\n")
            self.results_text.insert(tk.END, f"{'='*30}\n\n")
            self.results_text.insert(tk.END, f"Token: {dialog.token}\n")
            self.results_text.insert(tk.END, f"Válido: {'SÍ' if dialog.valid else 'NO'}\n")
            if dialog.message:
                self.results_text.insert(tk.END, f"Mensaje: {dialog.message}\n")
            if dialog.token_data:
                self.results_text.insert(tk.END, f"Jugador: {dialog.token_data['player_name']}\n")
                self.results_text.insert(tk.END, f"Torneo: {dialog.token_data['tournament_name']}\n")
                self.results_text.insert(tk.END, f"Usado: {dialog.token_data['used_count']} veces\n")
    
    def run(self):
        """Ejecuta la aplicación"""
        self.root.mainloop()

class TokenValidationDialog:
    def __init__(self, parent, generator):
        self.generator = generator
        self.token = None
        self.valid = False
        self.message = None
        self.token_data = None
        self.result = False
        
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("Validar Token")
        self.dialog.geometry("500x300")
        self.dialog.resizable(False, False)
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        # Centrar ventana
        self.dialog.geometry("+%d+%d" % (parent.winfo_rootx() + 50, parent.winfo_rooty() + 50))
        
        self.setup_ui()
    
    def setup_ui(self):
        frame = ttk.Frame(self.dialog, padding="20")
        frame.pack(fill=tk.BOTH, expand=True)
        
        ttk.Label(frame, text="Validar Token", 
                 font=("Arial", 12, "bold")).pack(pady=(0, 20))
        
        ttk.Label(frame, text="Ingrese el token a validar:").pack(anchor=tk.W)
        self.token_entry = scrolledtext.ScrolledText(frame, height=8, width=50)
        self.token_entry.pack(fill=tk.BOTH, expand=True, pady=(5, 20))
        
        button_frame = ttk.Frame(frame)
        button_frame.pack(fill=tk.X)
        
        ttk.Button(button_frame, text="Validar", 
                  command=self.validate).pack(side=tk.RIGHT, padx=(10, 0))
        ttk.Button(button_frame, text="Cancelar", 
                  command=self.cancel).pack(side=tk.RIGHT)
    
    def validate(self):
        token_text = self.token_entry.get(1.0, tk.END).strip()
        
        if not token_text:
            messagebox.showerror("Error", "Ingrese un token para validar")
            return
        
        # Extraer token de la línea que contiene "Token:"
        lines = token_text.split('\n')
        token = None
        for line in lines:
            if line.startswith('Token:'):
                token = line.replace('Token:', '').strip()
                break
        
        if not token:
            # Si no encuentra "Token:", usar todo el texto
            token = token_text
        
        self.token = token
        self.valid, result = self.generator.validate_token(token)
        
        if isinstance(result, str):
            self.message = result
        else:
            self.token_data = result
        
        self.result = True
        self.dialog.destroy()
    
    def cancel(self):
        self.dialog.destroy()

def main():
    """Función principal"""
    print("L4D2 Tournament Token Generator")
    print("=" * 40)
    
    app = TokenGeneratorGUI()
    app.run()

if __name__ == "__main__":
    main()

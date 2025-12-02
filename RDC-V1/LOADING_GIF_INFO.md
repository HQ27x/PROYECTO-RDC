# 🎬 Loading GIF - Pantalla de Carga Animada

## 📋 Descripción

El verificador ahora muestra una pantalla de carga animada usando el archivo `loading.gif` mientras realiza la verificación completa del sistema.

## ✨ Características

- ✅ **Animación Suave**: Usa el GIF animado original
- ✅ **Detección Automática**: Busca el GIF en múltiples ubicaciones
- ✅ **Fallback Inteligente**: Si no encuentra el GIF, muestra animación de texto
- ✅ **Compatible con Ejecutables**: Funciona tanto en desarrollo como compilado
- ✅ **Mensajes de Progreso**: Muestra qué está haciendo en cada momento

## 🎯 Cómo Funciona

### En Desarrollo (Python)
Cuando ejecutas `main.py` directamente, el sistema busca `loading.gif` en:
1. Directorio actual
2. Directorio del script
3. Directorio del ejecutable

### En Ejecutable Compilado
Cuando usas `L4D2_Verifier.exe`, el GIF está empaquetado dentro del ejecutable y se extrae automáticamente al directorio temporal de PyInstaller.

## 🧪 Probar el GIF

### Opción 1: Script de Prueba
```bash
python test_loading_gif.py
```

### Opción 2: Archivo .bat
```bash
test_gif.bat
```

El script de prueba:
- ✅ Verifica que `loading.gif` existe
- ✅ Verifica que PIL/Pillow está instalado
- ✅ Carga el GIF y muestra información
- ✅ Abre una ventana de prueba con la animación

## 📦 Compilación

El GIF se incluye automáticamente al compilar:

### Compilar Verificador
```bash
python build_verifier.py
```

### Compilar Todo
```bash
python build_all.py
```

Los scripts de compilación:
- ✅ Incluyen `loading.gif` en los datos del ejecutable
- ✅ Copian el GIF a la carpeta `dist/`
- ✅ Incluyen PIL/Pillow en las dependencias ocultas

## 🎨 Personalizar el GIF

Puedes reemplazar `loading.gif` con tu propio GIF:

### Requisitos del GIF:
- **Formato**: GIF animado
- **Tamaño recomendado**: 200x200 a 400x400 píxeles
- **Frames**: Cualquier cantidad (más frames = animación más suave)
- **Duración**: 50-100ms por frame (recomendado)

### Pasos:
1. Reemplaza el archivo `loading.gif` en el directorio raíz
2. Ejecuta `test_loading_gif.py` para verificar
3. Recompila el ejecutable con `build_verifier.py`

## 📐 Dimensiones de la Ventana

La ventana de carga tiene las siguientes dimensiones:
- **Ancho**: 500 píxeles
- **Alto**: 400 píxeles
- **GIF centrado**: Se muestra en el centro de la ventana

## 🔧 Configuración Avanzada

### Cambiar Velocidad de Animación
El sistema respeta la velocidad del GIF original (metadata `duration`). Si quieres cambiarla:

1. Edita `main.py`, línea ~2304
2. Modifica el valor de `delay` (en milisegundos)

```python
delay = pil_image.info.get('duration', 50)  # Cambiar 50 por otro valor
```

### Cambiar Tamaño de la Ventana
Para ajustar el tamaño de la ventana de carga:

1. Edita `main.py`, línea ~2179
2. Modifica el valor de `geometry`

```python
self.loading_window.geometry("500x400")  # Cambiar dimensiones
```

## 📊 Mensajes de Progreso

La pantalla de carga muestra mensajes que van cambiando:
- ⏳ Iniciando verificación...
- 🔍 Detectando mods instalados...
- 👥 Analizando cuentas Steam...
- 🔎 Escaneando procesos del sistema...
- 🆔 Obteniendo identificadores únicos...
- 📝 Generando reporte completo...
- 📤 Enviando resultados a Discord...
- ✅ Finalizando verificación...

## 🐛 Solución de Problemas

### El GIF no se muestra
**Solución**:
1. Verifica que `loading.gif` existe en el directorio
2. Ejecuta `test_loading_gif.py` para diagnosticar
3. Verifica que PIL/Pillow está instalado: `pip install Pillow`

### La animación está muy lenta/rápida
**Solución**:
- Ajusta el GIF original con un editor de GIF
- O modifica el código (ver "Cambiar Velocidad de Animación")

### El GIF no se muestra en el ejecutable
**Solución**:
1. Verifica que recompilaste después de agregar el GIF
2. Verifica que `build_verifier.py` incluye el GIF en `datas`
3. Revisa los mensajes de compilación para errores

### Error "PIL module not found"
**Solución**:
```bash
pip install Pillow
```

## 📝 Código de Ejemplo

### Cargar y Animar GIF en Tkinter
```python
from PIL import Image, ImageTk
import tkinter as tk

# Cargar GIF
pil_image = Image.open('loading.gif')

# Crear label
gif_label = tk.Label(root)
gif_label.pack()

# Función de animación
def animate_gif(frame_index=0):
    pil_image.seek(frame_index)
    photo = ImageTk.PhotoImage(pil_image)
    gif_label.config(image=photo)
    gif_label.image = photo
    
    delay = pil_image.info.get('duration', 50)
    next_frame = (frame_index + 1) % pil_image.n_frames
    root.after(delay, lambda: animate_gif(next_frame))

animate_gif()
```

## 📚 Referencias

- **PIL/Pillow**: https://pillow.readthedocs.io/
- **Tkinter**: https://docs.python.org/3/library/tkinter.html
- **PyInstaller Data Files**: https://pyinstaller.org/en/stable/spec-files.html#adding-data-files

## ✅ Checklist de Implementación

- [x] Código de carga de GIF implementado
- [x] Búsqueda en múltiples ubicaciones
- [x] Animación frame por frame
- [x] Fallback a texto si falla
- [x] Inclusión en compilación
- [x] Script de prueba
- [x] Documentación

---

**Desarrollado para L4D2 Tournament System v2.0**



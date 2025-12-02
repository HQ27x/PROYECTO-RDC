# 🔨 Guía de Compilación - L4D2 Tournament System

## 📋 Descripción

Esta guía te explica cómo compilar los ejecutables del sistema de torneos de Left 4 Dead 2.

## 🎯 ¿Qué se Compila?

### 1. **Verificador de Integridad**
- `L4D2_Verifier.exe` - Interfaz gráfica
- `L4D2_Verifier_Console.exe` - Modo consola
- `run_verifier.bat` - Launcher automático

### 2. **Generador de Tokens**
- `L4D2_Token_Generator.exe` - Generador principal
- `run_generator.bat` - Launcher
- `install_generator.bat` - Instalador

## 🚀 Compilación Rápida

### **Opción 1: Compilar Todo (Recomendado)**
```bash
build.bat
```
Esto compila ambos ejecutables y crea el paquete completo.

### **Opción 2: Compilar Individualmente**

#### Solo Verificador:
```bash
build_verifier.bat
```

#### Solo Generador de Tokens:
```bash
build_generator.bat
```

## 🔧 Compilación Manual

### **Requisitos Previos**
1. **Python 3.7+** instalado
2. **Archivos del proyecto** en el directorio actual
3. **Conexión a internet** para descargar dependencias

### **Pasos Manuales**

#### 1. Instalar PyInstaller
```bash
pip install pyinstaller
```

#### 2. Instalar Dependencias
```bash
pip install psutil qrcode[pil] Pillow
```

#### 3. Compilar Verificador
```bash
python build_verifier.py
```

#### 4. Compilar Generador
```bash
python build_token_generator.py
```

## 📁 Estructura de Salida

### **Después de Compilar Todo:**
```
L4D2_Tournament_System/
├── Verificador/
│   ├── L4D2_Verifier.exe
│   ├── L4D2_Verifier_Console.exe
│   ├── run_verifier.bat
│   └── README_VERIFIER.txt
├── Generador_Tokens/
│   ├── L4D2_Token_Generator.exe
│   ├── run_generator.bat
│   ├── install_generator.bat
│   └── README_GENERATOR.txt
└── README.txt
```

### **Solo Verificador:**
```
dist/
├── L4D2_Verifier.exe
├── L4D2_Verifier_Console.exe
├── run_verifier.bat
└── README_VERIFIER.txt
```

### **Solo Generador:**
```
dist/L4D2_Token_Generator/
├── L4D2_Token_Generator.exe
├── run_generator.bat
├── install_generator.bat
└── README_GENERATOR.txt
```

## ⚙️ Configuración Avanzada

### **Personalizar Iconos**
1. Coloca un archivo `icon.ico` en el directorio raíz
2. Los scripts lo detectarán automáticamente
3. Se aplicará a todos los ejecutables

### **Modificar Configuración de PyInstaller**
Los archivos `.spec` se generan automáticamente, pero puedes editarlos:
- `L4D2_Verifier.spec` - Configuración del verificador
- `L4D2_Verifier_Console.spec` - Configuración del verificador consola
- `L4D2_Token_Generator.spec` - Configuración del generador

### **Opciones de Compilación**
- **UPX**: Habilitado por defecto (comprime ejecutables)
- **Console**: Solo para el verificador consola
- **One-file**: Todos los ejecutables son de un solo archivo

## 🐛 Solución de Problemas

### **Error: "PyInstaller no encontrado"**
```bash
pip install pyinstaller
```

### **Error: "Módulo no encontrado"**
```bash
pip install psutil qrcode[pil] Pillow
```

### **Error: "Archivo no encontrado"**
- Verificar que estés en el directorio correcto
- Verificar que todos los archivos estén presentes

### **Error: "Acceso denegado"**
- Ejecutar como administrador
- Cerrar antivirus temporalmente

### **Error: "Memoria insuficiente"**
- Cerrar otros programas
- Aumentar memoria virtual
- Compilar uno por uno

## 📊 Tamaños de Archivos

### **Tamaños Aproximados:**
- **Verificador GUI**: ~50-80 MB
- **Verificador Consola**: ~40-60 MB
- **Generador**: ~60-90 MB

### **Optimización:**
- Los archivos se comprimen con UPX
- Tamaño final: ~30-50% del original
- Tiempo de inicio: +1-2 segundos

## 🔄 Actualizaciones

### **Recompilar después de cambios:**
1. Modificar el código fuente
2. Ejecutar `build.bat` nuevamente
3. Los archivos se actualizarán automáticamente

### **Limpiar compilaciones anteriores:**
Los scripts limpian automáticamente:
- Directorio `build/`
- Directorio `dist/`
- Archivos `.spec`

## 📦 Distribución

### **Para Distribuir:**
1. **Compilar**: Ejecutar `build.bat`
2. **Probar**: Verificar que ambos ejecutables funcionen
3. **Empaquetar**: Comprimir la carpeta `L4D2_Tournament_System/`
4. **Distribuir**: Enviar a los jugadores

### **Estructura de Distribución:**
- **Administrador**: Recibe el paquete completo
- **Jugadores**: Reciben solo la carpeta `Verificador/`

## ⚠️ Notas Importantes

1. **Primera Compilación**: Puede tardar 5-10 minutos
2. **Antivirus**: Puede marcar como falso positivo
3. **Windows Defender**: Agregar excepción si es necesario
4. **Dependencias**: Se incluyen automáticamente
5. **Portabilidad**: Los ejecutables son independientes

## 🆘 Soporte

Si encuentras problemas:
1. Verificar requisitos del sistema
2. Revisar logs de error
3. Probar compilación individual
4. Contactar al desarrollador

---
**L4D2 Tournament System v1.0 - Guía de Compilación**

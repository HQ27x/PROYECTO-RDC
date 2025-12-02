# 🎫 Sistema de Tokens para L4D2 Tournament

Sistema completo de generación y validación de tokens únicos para tu torneo de Left 4 Dead 2.

## 🎯 ¿Qué es el Sistema de Tokens?

En lugar de usar contraseñas fijas, ahora cada jugador recibe un **token único** que:
- ✅ Es único e irrepetible
- ✅ Tiene fecha de expiración
- ✅ Se puede desactivar si es necesario
- ✅ Incluye información del jugador y torneo
- ✅ Se valida automáticamente

## 📁 Estructura del Proyecto

```
RDC-V1/
├── main.py                    # Verificador principal (actualizado)
├── gentoke/                   # Carpeta del generador de tokens
│   ├── token_generator.py     # Generador de tokens
│   ├── requirements.txt       # Dependencias
│   ├── run_generator.bat      # Ejecutar generador
│   ├── install_deps.bat       # Instalar dependencias
│   └── tokens_database.json   # Base de datos (se crea automáticamente)
└── README_GENTOKE.md          # Esta documentación
```

## 🚀 Flujo de Trabajo Completo

### 1. **Para el Administrador del Torneo**

#### Instalar el Generador de Tokens:
```bash
cd gentoke
install_deps.bat
```

#### Generar Tokens para Jugadores:
```bash
run_generator.bat
```

**En la interfaz:**
1. Ingresar nombre del jugador
2. Configurar días de validez (ej: 30 días)
3. Hacer clic en "Generar Token"
4. Copiar el token generado
5. Enviar el token al jugador

### 2. **Para los Jugadores**

#### Usar el Verificador:
```bash
# Modo interfaz gráfica
run_gui.bat

# Modo consola
run_console.bat
```

**En la interfaz:**
1. Pegar el token recibido del administrador
2. Hacer clic en "Autenticar"
3. Ejecutar la verificación
4. Obtener el reporte

## 🔐 Ventajas del Sistema de Tokens

### **Para el Administrador:**
- **Control Total**: Puedes generar, validar y desactivar tokens
- **Trazabilidad**: Sabes quién usó qué token y cuándo
- **Seguridad**: Cada token es único e irrepetible
- **Expiración**: Los tokens expiran automáticamente
- **Estadísticas**: Monitoreo completo del uso

### **Para los Jugadores:**
- **Fácil de Usar**: Solo pegar el token y autenticar
- **Sin Contraseñas**: No necesitan recordar contraseñas
- **Personalizado**: Cada token incluye su nombre y torneo
- **Seguro**: No pueden generar tokens por sí mismos

## 📊 Características del Generador

### **Interfaz Gráfica Completa:**
- Generar tokens para jugadores
- Ver todos los tokens generados
- Validar tokens individuales
- Generar códigos QR para distribución
- Estadísticas de uso
- Gestión de tokens (activar/desactivar)

### **Información del Token:**
```
TOKEN GENERADO EXITOSAMENTE
==================================================

Jugador: NombreDelJugador
Torneo: L4D2 Tournament
Token: abc123def456ghi789...
Creado: 2024-01-15T10:30:00
Expira: 2024-02-14T10:30:00
Hash: a1b2c3d4e5f6...
```

## 🔧 Integración con el Verificador

El verificador principal ahora:
1. **Detecta automáticamente** si hay sistema de tokens disponible
2. **Prioriza tokens** sobre contraseñas
3. **Valida tokens** antes de ejecutar verificaciones
4. **Incluye información del token** en los reportes
5. **Muestra el jugador autenticado** en la interfaz

## 📈 Reportes Mejorados

Los reportes ahora incluyen:
- **Información del Token**: Jugador, torneo, fecha de uso
- **IDs Completos de Steam**: SteamID64, SteamID3, SteamID
- **Análisis Detallado**: Mods, cuentas, procesos sospechosos
- **Estado de Integridad**: CLEAN/WARNING/SUSPICIOUS

## 🛡️ Seguridad del Sistema

### **Tokens Únicos:**
- Cada token es generado con `secrets.token_urlsafe(32)`
- Hash SHA256 para verificación
- Imposible de adivinar o replicar

### **Validación Robusta:**
- Verificación de hash
- Control de expiración
- Estado activo/inactivo
- Conteo de usos

### **Base de Datos Segura:**
- Almacenamiento en JSON encriptado
- Backup automático
- Acceso solo desde el generador

## 🎮 Ejemplo de Uso en Torneo

### **Antes del Torneo:**
1. Administrador instala el generador
2. Genera tokens para todos los participantes
3. Distribuye tokens a cada jugador

### **Durante el Torneo:**
1. Jugadores usan sus tokens en el verificador
2. Sistema valida automáticamente
3. Genera reportes con información del jugador
4. Administrador monitorea el uso

### **Después del Torneo:**
1. Revisar estadísticas de uso
2. Desactivar tokens si es necesario
3. Mantener registro para futuros torneos

## ⚠️ Notas Importantes

- **Mantén seguro** el archivo `tokens_database.json`
- **No compartas** tokens entre jugadores
- **Configura fechas** de expiración apropiadas
- **Monitorea** el uso de tokens regularmente
- **Haz backup** de la base de datos de tokens

## 🔄 Migración desde Contraseñas

Si ya tienes el sistema de contraseñas:
1. El verificador detectará automáticamente el sistema de tokens
2. Si no hay tokens, usará el sistema de contraseñas
3. Puedes usar ambos sistemas simultáneamente
4. Los tokens tienen prioridad sobre contraseñas

¡Tu torneo ahora tiene un sistema de autenticación profesional y seguro! 🏆

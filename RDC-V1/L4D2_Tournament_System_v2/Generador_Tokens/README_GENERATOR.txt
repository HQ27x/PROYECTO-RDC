# 🎫 L4D2 Tournament Token Generator v2.0

## 🆕 NUEVA FUNCIONALIDAD: Sistema de Tokens Mejorado

Esta versión incluye un sistema completo de generación y validación de tokens únicos para torneos.

## 🚀 Uso Rápido

1. Ejecutar `run_generator.bat`
2. En la interfaz gráfica:
   - Ingresar nombre del jugador
   - Configurar días de validez (ej: 30 días)
   - Hacer clic en "Generar Token"
   - Copiar el token generado
   - Enviar el token al jugador

## 🎯 Características Principales

### Generación de Tokens:
- **Tokens Únicos**: Cada token es irrepetible
- **Fecha de Expiración**: Configurable (por defecto 30 días)
- **Información del Jugador**: Incluye nombre y torneo
- **Hash de Seguridad**: SHA256 para verificación

### Gestión de Tokens:
- **Base de Datos**: Almacena todos los tokens generados
- **Validación**: Verifica tokens automáticamente
- **Estadísticas**: Monitoreo de uso y estado
- **Desactivación**: Posibilidad de desactivar tokens

### Interfaz Gráfica:
- **Generación Fácil**: Interfaz intuitiva
- **Códigos QR**: Generación automática para distribución
- **Gestión Completa**: Ver, validar y administrar tokens
- **Estadísticas**: Monitoreo en tiempo real

## 🔐 Seguridad del Sistema

### Tokens Únicos:
- Generados con `secrets.token_urlsafe(32)`
- Hash SHA256 para verificación
- Imposible de adivinar o replicar

### Validación Robusta:
- Verificación de hash
- Control de expiración
- Estado activo/inactivo
- Conteo de usos

### Base de Datos Segura:
- Almacenamiento en JSON
- Backup automático
- Acceso solo desde el generador

## 📊 Información del Token

Cada token incluye:
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

## 🎮 Flujo de Trabajo en Torneos

### Para el Administrador:
1. **Instalar Generador**: Ejecutar `run_generator.bat`
2. **Generar Tokens**: Crear tokens para cada jugador
3. **Distribuir Tokens**: Enviar tokens a los participantes
4. **Monitorear Uso**: Revisar estadísticas de uso

### Para los Jugadores:
1. **Recibir Token**: Del administrador del torneo
2. **Usar en Verificador**: Pegar token en el verificador
3. **Autenticar**: El verificador valida automáticamente
4. **Verificar**: Ejecutar verificación completa

## 🔧 Funcionalidades Avanzadas

### Gestión de Tokens:
- **Ver Todos los Tokens**: Lista completa con estado
- **Validar Token**: Verificar tokens individuales
- **Estadísticas**: Total, activos, expirados
- **Desactivar**: Desactivar tokens si es necesario

### Códigos QR:
- **Generación Automática**: Para distribución fácil
- **Ventana Dedicada**: Mostrar QR en pantalla
- **Fácil Distribución**: Escanear y enviar

### Base de Datos:
- **Almacenamiento Local**: Archivo `tokens_database.json`
- **Backup Automático**: Se guarda automáticamente
- **Formato JSON**: Fácil de leer y procesar

## ⚠️ Requisitos del Sistema

- Windows 10/11
- Python 3.7+ (si se ejecuta desde código fuente)
- Conexión a internet (para algunas funcionalidades)

## 🔧 Solución de Problemas

### "Error al generar token"
- Verificar que el nombre del jugador no esté vacío
- Verificar que los días de validez sean un número válido

### "Error al guardar tokens"
- Verificar permisos de escritura en el directorio
- Ejecutar como administrador si es necesario

### "No se puede generar QR"
- Verificar que Pillow esté instalado
- Reinstalar dependencias si es necesario

### "Base de datos corrupta"
- Eliminar `tokens_database.json` para reiniciar
- Los tokens anteriores se perderán

## 🛡️ Mejores Prácticas

### Seguridad:
- **Mantener Seguro**: El archivo `tokens_database.json`
- **No Compartir**: Tokens entre jugadores
- **Configurar Fechas**: De expiración apropiadas
- **Monitorear Uso**: Regularmente

### Administración:
- **Hacer Backup**: De la base de datos de tokens
- **Documentar**: Qué token corresponde a qué jugador
- **Limpiar**: Tokens expirados periódicamente

## 📞 Soporte

Para problemas o preguntas:
1. Revisar esta documentación
2. Verificar requisitos del sistema
3. Contactar al desarrollador

---
**L4D2 Tournament Token Generator v2.0**
**Sistema completo de tokens para torneos profesionales**


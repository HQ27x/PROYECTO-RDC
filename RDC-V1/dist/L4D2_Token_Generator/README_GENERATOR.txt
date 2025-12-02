# L4D2 Tournament Token Generator - Ejecutable

## 🎫 Generador de Tokens para Torneos de Left 4 Dead 2

### 📋 Características
- ✅ Generación de tokens únicos para jugadores
- ✅ Interfaz gráfica intuitiva
- ✅ Gestión completa de tokens
- ✅ Generación de códigos QR
- ✅ Base de datos de tokens
- ✅ Validación y estadísticas

### 🚀 Cómo Usar

#### Ejecutar el Generador
1. Ejecutar `run_generator.bat` o `L4D2_Token_Generator.exe`
2. La interfaz gráfica se abrirá automáticamente

#### Generar Token para Jugador
1. **Completar Información**:
   - Nombre del Jugador (obligatorio)
   - Nombre del Torneo (opcional)
   - Días de validez (por defecto 30)

2. **Generar Token**:
   - Hacer clic en "Generar Token"
   - El token se mostrará en el área de texto

3. **Distribuir Token**:
   - Copiar token con "Copiar Token"
   - Generar QR con "Generar QR"
   - Enviar al jugador

### 🔧 Gestión de Tokens

#### Ver Todos los Tokens
- Hacer clic en "Ver Todos los Tokens"
- Lista completa con estados y fechas

#### Validar Token
- Hacer clic en "Validar Token"
- Pegar el token a validar
- Verificar información del jugador

#### Estadísticas
- Hacer clic en "Estadísticas"
- Ver resumen de tokens activos/expirados

### 📊 Formato de Token

Los tokens generados incluyen:

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

### 🛡️ Seguridad

- **Tokens Únicos**: Cada token es irrepetible
- **Hash SHA256**: Verificación segura
- **Expiración**: Control de validez temporal
- **Base de Datos**: Almacenamiento seguro en JSON

### 📁 Archivos Importantes

- `tokens_database.json`: Base de datos de tokens (se crea automáticamente)
- `run_generator.bat`: Launcher del generador
- `L4D2_Token_Generator.exe`: Ejecutable principal

### ⚠️ Requisitos del Sistema
- Windows 10/11
- Python (ya incluido en el ejecutable)

### 🔄 Flujo de Trabajo

1. **Generar Tokens**: Crear tokens para todos los participantes
2. **Distribuir**: Enviar tokens a cada jugador
3. **Monitorear**: Verificar uso y estadísticas
4. **Gestionar**: Activar/desactivar tokens según necesidad

### 🆘 Solución de Problemas

**"Error al generar token"**
- Verificar que el nombre del jugador no esté vacío
- Verificar que los días de validez sean un número válido

**"Error al validar token"**
- Verificar que el token esté completo
- Verificar que el token no haya expirado

**"Error de ejecución"**
- Verificar que no haya antivirus bloqueando
- Ejecutar como administrador

### 📞 Soporte
Para problemas o preguntas, revisa la documentación o contacta al desarrollador.

---
**L4D2 Tournament Token Generator v1.0**

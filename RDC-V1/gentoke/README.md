# L4D2 Tournament Token Generator

Generador de tokens únicos para el sistema de verificación de integridad de Left 4 Dead 2.

## 🎯 Características

- **Generación de Tokens Únicos**: Crea tokens seguros para cada jugador
- **Gestión de Tokens**: Administra, valida y desactiva tokens
- **Códigos QR**: Genera códigos QR para fácil distribución
- **Base de Datos**: Almacena todos los tokens en formato JSON
- **Validación**: Sistema de validación con expiración automática
- **Estadísticas**: Monitoreo de uso y estado de tokens

## 🔐 Seguridad

- **Tokens Únicos**: Cada token es único e irrepetible
- **Hash SHA256**: Verificación segura de tokens
- **Expiración**: Tokens con fecha de expiración configurable
- **Activación/Desactivación**: Control total sobre tokens

## 📦 Instalación

1. **Instalar Dependencias**:
   ```bash
   install_deps.bat
   ```

2. **Ejecutar Generador**:
   ```bash
   run_generator.bat
   ```

## 🚀 Uso

### Generar Token para Jugador

1. **Abrir el Generador**:
   - Ejecutar `run_generator.bat`
   - O usar `python token_generator.py`

2. **Completar Información**:
   - Nombre del Jugador (obligatorio)
   - Nombre del Torneo (opcional)
   - Días de validez (por defecto 30)

3. **Generar Token**:
   - Hacer clic en "Generar Token"
   - El token se mostrará en el área de texto

4. **Distribuir Token**:
   - Copiar token con "Copiar Token"
   - Generar QR con "Generar QR"
   - Enviar al jugador

### Validar Token

1. **Abrir Validación**:
   - Hacer clic en "Validar Token"
   - Pegar el token en el área de texto

2. **Verificar Resultado**:
   - El sistema mostrará si el token es válido
   - Información del jugador asociado
   - Estado de uso del token

### Gestión de Tokens

- **Ver Todos los Tokens**: Lista completa con estados
- **Estadísticas**: Resumen de tokens activos/expirados
- **Validar Token**: Verificar tokens individuales

## 📊 Formato de Token

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

## 🔧 Integración con Verificador

Los tokens generados aquí se usan en el programa principal:

1. **Generar tokens** para cada jugador del torneo
2. **Distribuir tokens** a los jugadores
3. **Los jugadores usan los tokens** en el verificador principal
4. **El verificador valida** los tokens antes de ejecutar

## 📁 Archivos

- `token_generator.py` - Programa principal
- `requirements.txt` - Dependencias de Python
- `tokens_database.json` - Base de datos de tokens (se crea automáticamente)
- `run_generator.bat` - Ejecutar generador
- `install_deps.bat` - Instalar dependencias

## 🛡️ Seguridad del Sistema

### Para el Administrador del Torneo:
1. **Genera tokens únicos** para cada jugador
2. **Controla la validez** de cada token
3. **Monitorea el uso** de tokens
4. **Puede desactivar** tokens si es necesario

### Para los Jugadores:
1. **Reciben un token único** del administrador
2. **Usan el token** en el verificador
3. **El token expira** automáticamente
4. **No pueden generar** tokens por sí mismos

## 🔄 Flujo de Trabajo Recomendado

1. **Antes del Torneo**:
   - Instalar el generador de tokens
   - Generar tokens para todos los participantes
   - Distribuir tokens a cada jugador

2. **Durante el Torneo**:
   - Los jugadores usan sus tokens en el verificador
   - Monitorear el uso de tokens
   - Validar tokens si es necesario

3. **Después del Torneo**:
   - Revisar estadísticas de uso
   - Desactivar tokens si es necesario
   - Mantener registro para futuros torneos

## ⚠️ Notas Importantes

- **Mantén seguro** el archivo `tokens_database.json`
- **No compartas** tokens entre jugadores
- **Configura fechas** de expiración apropiadas
- **Monitorea** el uso de tokens regularmente

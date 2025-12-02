# L4D2 Tournament Integrity Checker - Ejecutable

## 🎮 Verificador de Integridad para Torneos de Left 4 Dead 2

### 📋 Características
- ✅ Detección de mods instalados
- ✅ Análisis de cuentas Steam con IDs completos
- ✅ Detección de procesos sospechosos
- ✅ Reportes detallados en JSON y texto
- ✅ Sistema de autenticación con tokens
- ✅ Interfaz gráfica y modo consola

### 🚀 Cómo Usar

#### Opción 1: Como Administrador (Recomendado)
1. Ejecutar `run_as_admin.bat`
2. Confirmar la elevación de privilegios si se solicita
3. Seleccionar modo (Interfaz Gráfica o Consola)
4. El firewall se configurará automáticamente

#### Opción 2: Launcher Automático
1. Ejecutar `run_verifier.bat`
2. Seleccionar modo (Interfaz Gráfica o Consola)
3. El programa se ejecutará automáticamente

#### Opción 3: Ejecutables Directos
- **Interfaz Gráfica**: `L4D2_Verifier.exe`
- **Modo Consola**: `L4D2_Verifier_Console.exe`

### 🔐 Autenticación

El verificador requiere un token válido para funcionar:

1. **Obtener Token**: Contacta al administrador del torneo
2. **Pegar Token**: En la ventana de autenticación
3. **Autenticar**: Hacer clic en "Autenticar"
4. **Verificar**: Ejecutar la verificación completa

### 📊 Reportes

El programa genera reportes detallados que incluyen:
- Información de la PC
- Análisis de mods detectados
- Cuentas Steam con IDs completos
- Procesos sospechosos
- Estado de integridad general

### ⚠️ Requisitos del Sistema
- Windows 10/11
- Steam instalado
- Left 4 Dead 2 instalado

### 🆘 Solución de Problemas

**"Steam no encontrado"**
- Verificar que Steam esté instalado
- Ejecutar como administrador

**"Token inválido"**
- Verificar que el token esté completo
- Contactar al administrador del torneo

**"Error de ejecución"**
- Verificar que no haya antivirus bloqueando
- Ejecutar como administrador

**"No se pueden enviar reportes a Discord"**
- Ejecutar `run_as_admin.bat` para configurar el firewall automáticamente
- Agregar manualmente "L4D2 Tournament Verifier" al firewall de Windows
- Ejecutar como administrador

### 📞 Soporte
Para problemas o preguntas, contacta al administrador del torneo.

---
**L4D2 Tournament Integrity Checker v1.0**

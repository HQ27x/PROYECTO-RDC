# L4D2 Tournament System - Paquete Completo

## 🎮 Sistema Completo para Torneos de Left 4 Dead 2

Este paquete incluye todo lo necesario para organizar y verificar un torneo de Left 4 Dead 2.

### 📁 Contenido del Paquete

#### 📂 Verificador/
- **L4D2_Verifier.exe** - Verificador con interfaz gráfica
- **L4D2_Verifier_Console.exe** - Verificador en modo consola
- **run_verifier.bat** - Launcher automático
- **run_as_admin.bat** - Ejecutar como administrador (recomendado)
- **README_VERIFIER.txt** - Documentación del verificador

#### 📂 Generador_Tokens/
- **L4D2_Token_Generator.exe** - Generador de tokens
- **run_generator.bat** - Launcher del generador
- **install_generator.bat** - Instalador (primera vez)
- **README_GENERATOR.txt** - Documentación del generador

### 🚀 Guía de Uso Rápido

#### Para el Administrador del Torneo:

1. **Configurar Generador**:
   - Ir a la carpeta `Generador_Tokens`
   - Ejecutar `install_generator.bat` (primera vez)
   - Ejecutar `run_generator.bat`

2. **Generar Tokens**:
   - Crear tokens para cada jugador
   - Copiar y enviar tokens a los jugadores

3. **Distribuir Verificador**:
   - Copiar la carpeta `Verificador` a cada jugador
   - Los jugadores ejecutan `run_verifier.bat`

#### Para los Jugadores:

1. **Ejecutar Verificador**:
   - Ejecutar `run_as_admin.bat` (recomendado para configurar firewall automáticamente)
   - O ejecutar `run_verifier.bat` si ya se configuró anteriormente
   - Seleccionar modo (Interfaz Gráfica recomendado)

2. **Autenticar**:
   - Pegar el token recibido del administrador
   - Hacer clic en "Autenticar"

3. **Verificar**:
   - Ejecutar verificación completa
   - Obtener reporte detallado

### 🔐 Sistema de Seguridad

- **Tokens Únicos**: Cada jugador tiene un token único
- **Validación Automática**: El verificador valida tokens automáticamente
- **Reportes Detallados**: Incluye IDs completos de Steam
- **Control Total**: Solo el administrador puede generar tokens

### 📊 Características del Verificador

- ✅ Detección de mods instalados
- ✅ Análisis de cuentas Steam con IDs completos
- ✅ Detección de procesos sospechosos
- ✅ Reportes en JSON y texto
- ✅ Interfaz gráfica y modo consola

### 🎫 Características del Generador

- ✅ Generación de tokens únicos
- ✅ Interfaz gráfica intuitiva
- ✅ Gestión completa de tokens
- ✅ Generación de códigos QR
- ✅ Base de datos de tokens
- ✅ Validación y estadísticas

### ⚠️ Requisitos del Sistema

- Windows 10/11
- Steam instalado (para el verificador)
- Left 4 Dead 2 instalado (para el verificador)

### 🆘 Solución de Problemas

**Verificador no funciona**:
- Verificar que Steam y L4D2 estén instalados
- Ejecutar como administrador
- Verificar que el token sea válido

**Generador no funciona**:
- Ejecutar `install_generator.bat` primero
- Ejecutar como administrador
- Verificar que no haya antivirus bloqueando

### 📞 Soporte

Para problemas o preguntas:
1. Revisar la documentación en cada carpeta
2. Verificar requisitos del sistema
3. Contactar al administrador del torneo

---
**L4D2 Tournament System v1.0**
**Desarrollado para torneos profesionales de Left 4 Dead 2**

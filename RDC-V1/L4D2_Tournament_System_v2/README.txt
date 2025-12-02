# 🎮 L4D2 Tournament System v2.0 - Con Identificación de Sistema

## 🔐 NUEVA FUNCIONALIDAD: Detección de Suplantaciones

Esta versión incluye **identificación única del sistema** para detectar intentos de suplantación en torneos.

### 📊 Identificadores Únicos Incluidos:
- **🌐 IP Externa**: Ubicación/ISP del jugador
- **🏠 IP Local**: Red local del jugador  
- **📡 MAC Address**: Dirección única de la tarjeta de red
- **🆔 System UUID**: Identificador único del sistema
- **💾 Disk Serial**: Número de serie del disco duro
- **🔑 System Fingerprint**: Huella digital única del equipo

## 📁 Contenido del Paquete

### 📂 Verificador/
- **L4D2_Verifier.exe** - Verificador con interfaz gráfica
- **L4D2_Verifier_Console.exe** - Verificador en modo consola
- **run_verifier.bat** - Launcher automático
- **README_VERIFIER.txt** - Documentación del verificador

### 📂 Generador_Tokens/
- **L4D2_Token_Generator.exe** - Generador de tokens
- **run_generator.bat** - Launcher del generador
- **README_GENERATOR.txt** - Documentación del generador

## 🚀 Guía de Uso Rápido

### Para el Administrador del Torneo:

1. **Configurar Generador**:
   - Ir a la carpeta `Generador_Tokens`
   - Ejecutar `run_generator.bat`
   - Generar tokens para cada jugador

2. **Distribuir Verificador**:
   - Copiar la carpeta `Verificador` a cada jugador
   - Los jugadores ejecutan `run_verifier.bat`

### Para los Jugadores:

1. **Ejecutar Verificador**:
   - Ejecutar `run_verifier.bat`
   - Seleccionar modo (Interfaz Gráfica recomendado)

2. **Autenticar**:
   - Pegar el token recibido del administrador
   - Hacer clic en "Autenticar"

3. **Verificar**:
   - Ejecutar verificación completa
   - Obtener reporte con identificación del sistema

## 🛡️ Detección de Suplantaciones

### Cómo Funciona:

1. **Primera Verificación**: Cada jugador hace su primera verificación
2. **Registro de Identificadores**: Se guardan todos los identificadores únicos
3. **Verificaciones Posteriores**: Se comparan con los registros anteriores
4. **Detección Automática**: Si cambian los identificadores críticos, es sospechoso

### Ejemplo de Detección:

**Primera Verificación:**
```
Jugador: Juan
MAC: 00:1B:44:11:3A:B7
IP Externa: 192.168.1.100
Fingerprint: a1b2c3d4e5f67890
```

**Segunda Verificación (Sospechosa):**
```
Jugador: Juan (mismo nombre)
MAC: 00:2C:55:22:4B:C8 (DIFERENTE!)
IP Externa: 192.168.1.100 (misma IP)
Fingerprint: b2c3d4e5f6789012 (DIFERENTE!)
```

**🚨 ALERTA**: El jugador está usando un equipo diferente, posible suplantación.

## 📱 Notificaciones Discord

Cada verificación se envía automáticamente a Discord con:
- Estado de integridad del sistema
- Identificación completa del equipo
- Análisis de mods y cuentas Steam
- Información del jugador autenticado

## ⚠️ Requisitos del Sistema

- Windows 10/11
- Steam instalado (para el verificador)
- Left 4 Dead 2 instalado (para el verificador)
- Conexión a internet (para obtener IP externa)

## 🔧 Características Técnicas

### Identificadores Recopilados:
- **MAC Address**: Único por tarjeta de red (muy difícil de cambiar)
- **System UUID**: Único por motherboard/sistema
- **Disk Serial**: Único por disco duro
- **System Fingerprint**: Combinación única de todos los identificadores

### Seguridad:
- **Manejo de Errores**: Si algún identificador falla, se marca como "Unknown"
- **Timeouts**: Las consultas externas tienen timeout de 5-10 segundos
- **Privacidad**: Los identificadores se muestran parcialmente en Discord

## 🆘 Solución de Problemas

**Verificador no funciona**:
- Verificar que Steam y L4D2 estén instalados
- Ejecutar como administrador
- Verificar que el token sea válido

**No se obtiene IP externa**:
- Verificar conexión a internet
- El sistema funcionará sin IP externa (se marcará como "Unknown")

**Antivirus marca como sospechoso**:
- Agregar excepción en el antivirus
- El programa accede a información del sistema (normal)

## 📞 Soporte

Para problemas o preguntas:
1. Revisar la documentación en cada carpeta
2. Verificar requisitos del sistema
3. Contactar al administrador del torneo

---
**L4D2 Tournament System v2.0**
**Desarrollado para torneos profesionales de Left 4 Dead 2**
**Con protección avanzada contra suplantaciones**


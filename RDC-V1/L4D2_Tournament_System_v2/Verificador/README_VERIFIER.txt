# 🔍 L4D2 Tournament Integrity Checker v2.0

## 🆕 NUEVA FUNCIONALIDAD: Identificación de Sistema + Animación de Carga

Esta versión incluye **identificación única del sistema** para detectar intentos de suplantación y una **animación de carga profesional** durante la verificación.

## 🚀 Uso Rápido

### Opción 1: Interfaz Gráfica (Recomendado)
1. Ejecutar `run_verifier.bat`
2. Seleccionar opción 1 (Interfaz Gráfica)
3. Pegar el token recibido del administrador
4. Hacer clic en "Autenticar"
5. Hacer clic en "Ejecutar Verificación"
6. **¡NUEVO!** Se mostrará una ventana de carga con animación GIF
7. Revisar el reporte con identificación del sistema

### Opción 2: Modo Consola
1. Ejecutar `run_verifier.bat`
2. Seleccionar opción 2 (Modo Consola)
3. Seguir las instrucciones en pantalla

## 🎬 Animación de Carga

### Características:
- **Animación GIF**: Muestra el archivo `loading.gif` durante la verificación
- **Fallback Inteligente**: Si no hay GIF, muestra animación de texto con emojis
- **Mensajes de Progreso**: Actualiza dinámicamente el estado de la verificación
- **Barra de Progreso**: Indicador visual del progreso
- **Ventana Modal**: Centrada y no se puede cerrar accidentalmente
- **Botón Cancelar**: Opción para cancelar la verificación

### Mensajes de Progreso:
- "Iniciando verificación..."
- "Detectando mods instalados..."
- "Analizando cuentas Steam..."
- "Escaneando procesos del sistema..."
- "Obteniendo identificadores únicos..."
- "Generando reporte completo..."
- "Enviando resultados a Discord..."
- "Finalizando verificación..."

## 🔐 Identificación del Sistema

El verificador ahora recopila automáticamente:

### Identificadores Únicos:
- **🌐 IP Externa**: Ubicación/ISP del jugador
- **🏠 IP Local**: Red local del jugador
- **📡 MAC Address**: Dirección única de la tarjeta de red
- **🆔 System UUID**: Identificador único del sistema
- **💾 Disk Serial**: Número de serie del disco duro
- **🔑 System Fingerprint**: Huella digital única del equipo

### Detección de Suplantaciones:
1. **Primera Verificación**: Se registran todos los identificadores
2. **Verificaciones Posteriores**: Se comparan con registros anteriores
3. **Alerta Automática**: Si cambian identificadores críticos, es sospechoso

## 📱 Notificaciones Discord

Cada verificación se envía automáticamente a Discord con:
- Estado de integridad del sistema
- Identificación completa del equipo
- Análisis detallado de mods y cuentas Steam
- Información del jugador autenticado

## 📊 Reportes Generados

### Información Incluida:
- **Identificación del Sistema**: Todos los identificadores únicos
- **Análisis de Mods**: Lista completa de mods detectados
- **Cuentas Steam**: IDs completos (SteamID64, SteamID3, SteamID)
- **Procesos Sospechosos**: Procesos que podrían ser cheats
- **Estado de Integridad**: CLEAN/WARNING/SUSPICIOUS

### Formatos de Reporte:
- **JSON Detallado**: Para análisis programático
- **Texto Simple**: Para lectura rápida
- **Discord Embed**: Notificación automática

## ⚠️ Requisitos del Sistema

- Windows 10/11
- Steam instalado
- Left 4 Dead 2 instalado
- Conexión a internet (para IP externa)

## 🔧 Solución de Problemas

### "Steam no encontrado"
- Verificar que Steam esté instalado
- Ejecutar como administrador

### "Left 4 Dead 2 no encontrado"
- Verificar que L4D2 esté instalado a través de Steam
- Asegurarse de que la instalación esté completa

### "No se obtiene IP externa"
- Verificar conexión a internet
- El sistema funcionará sin IP externa

### "Acceso denegado a procesos"
- Ejecutar como administrador
- Desactivar temporalmente el antivirus si es necesario

### "Token inválido"
- Verificar que el token sea correcto
- Contactar al administrador del torneo

### "Animación de carga no funciona"
- Verificar que `loading.gif` esté en la misma carpeta que el ejecutable
- Si no hay GIF, se usará animación de texto automáticamente

## 🛡️ Seguridad

### Identificadores Únicos:
- **MAC Address**: Muy difícil de cambiar
- **System UUID**: Único por motherboard
- **Disk Serial**: Único por disco duro
- **System Fingerprint**: Combinación única

### Privacidad:
- Los identificadores se muestran parcialmente en Discord
- Se almacenan localmente en reportes
- No se envían a servidores externos (excepto Discord)

## 📞 Soporte

Para problemas o preguntas:
1. Revisar esta documentación
2. Verificar requisitos del sistema
3. Contactar al administrador del torneo

---
**L4D2 Tournament Integrity Checker v2.0**
**Con protección avanzada contra suplantaciones y animación de carga profesional**

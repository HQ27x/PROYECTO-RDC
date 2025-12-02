# L4D2 Tournament Integrity Checker

Un programa completo para verificar la integridad de los jugadores en torneos de Left 4 Dead 2. Detecta mods instalados, cuenta cuentas de Steam y identifica procesos sospechosos que podrían ser cheats.

## 🔐 Características de Seguridad

- **Sistema de Autenticación**: Protegido con contraseña - solo tú puedes usarlo
- **Reportes Detallados**: Incluye IDs completos de cuentas Steam y análisis exhaustivo
- **Configuración Segura**: Contraseña encriptada con hash PBKDF2 y salt
- **Configuración Automática de Firewall**: Configura automáticamente el firewall de Windows cuando se ejecuta como administrador

## 🎯 Funcionalidades Principales

- **Detección de Mods**: Escanea la carpeta de addons de L4D2 para detectar mods instalados
- **Análisis de Cuentas Steam**: Cuenta y analiza todas las cuentas de Steam con IDs completos
- **Detección de Procesos Sospechosos**: Identifica procesos que podrían ser cheats o hacks
- **Interfaz Gráfica Segura**: Interfaz protegida con autenticación
- **Reportes Detallados**: Genera reportes completos en JSON y texto
- **Verificación de Integridad**: Determina el estado general de integridad del sistema

## Instalación

1. **Requisitos del Sistema**:
   - Windows 10/11
   - Python 3.7 o superior
   - Steam instalado
   - Left 4 Dead 2 instalado

2. **Instalar Dependencias**:
   ```bash
   pip install -r requirements.txt
   ```

## Uso

### 🔐 Primera Configuración
Antes de usar el programa por primera vez, debes configurar una contraseña:

```bash
# Opción 1: Usar el script de configuración
python setup_password.py

# Opción 2: Usar el archivo .bat
setup_password.bat
```

### 🖥️ Modo Interfaz Gráfica (Recomendado)
```bash
# Opción 1: Usar el archivo .bat
run_gui.bat

# Opción 2: Comando directo
python main.py --gui
```

### 💻 Modo Consola
```bash
# Opción 1: Usar el archivo .bat
run_console.bat

# Opción 2: Comando directo
python main.py
```

### 🔧 Ejecutar como Administrador (Recomendado)
Para configurar automáticamente el firewall y permitir envío de reportes a Discord:

```bash
# Opción 1: Usar el script con elevación automática
run_as_admin.bat

# Opción 2: Ejecutar manualmente como administrador
# Clic derecho en L4D2_Verifier.exe > Ejecutar como administrador
```

**Nota**: La ejecución como administrador permite:
- Configurar automáticamente el firewall de Windows
- Enviar reportes de verificación a Discord sin problemas
- Acceso completo al sistema para escaneo detallado

## Funcionalidades Detalladas

### 1. Detección de Mods
- Busca automáticamente la instalación de Steam y L4D2
- Escanea la carpeta `addons` en busca de archivos `.vpk`
- Ignora archivos oficiales del juego
- Muestra nombre, tamaño y ruta de cada mod encontrado

### 2. Análisis de Cuentas Steam
- Lee el archivo `loginusers.vdf` de Steam
- Extrae **IDs completos** de todas las cuentas (SteamID64, SteamID3, SteamID)
- Obtiene nombres de usuario asociados
- Detecta cuentas sospechosas (más de 10 cuentas)
- Convierte automáticamente entre formatos de ID

### 3. Detección de Procesos Sospechosos
- Escanea procesos en ejecución
- Busca palabras clave relacionadas con cheats
- Identifica procesos con nombres sospechosos

### 4. Estados de Integridad
- **CLEAN**: Sistema limpio, sin problemas detectados
- **WARNING**: Un problema menor detectado
- **SUSPICIOUS**: Múltiples problemas o comportamiento sospechoso

## Estructura del Proyecto

```
L4D2-V1/
├── main.py                    # Programa principal
├── setup_password.py          # Script de configuración de contraseña
├── requirements.txt           # Dependencias de Python
├── install.bat               # Instalador automático
├── run_gui.bat               # Ejecutar con interfaz gráfica
├── run_console.bat           # Ejecutar en modo consola
├── setup_password.bat        # Configurar contraseña
├── l4d2_checker_config.json  # Configuración (se crea automáticamente)
└── README.md                 # Documentación
```

## 📊 Reportes Detallados

El programa genera **reportes completos** que incluyen:

### Información del Sistema
- Timestamp de la verificación
- Información de la PC (nombre, usuario, OS)
- Estado de Steam y L4D2

### Análisis de Mods
- Lista completa de mods detectados
- Tamaño y ubicación de cada mod
- Estado de integridad de mods

### Análisis de Cuentas Steam
- **IDs completos** de todas las cuentas:
  - SteamID64 (formato largo)
  - SteamID3 (formato [U:1:XXXXX])
  - SteamID (formato STEAM_0:X:XXXXX)
- Nombres de usuario asociados
- Detección de cuentas sospechosas

### Análisis de Cheats
- Procesos sospechosos encontrados
- Nombres y PIDs de procesos
- Estado de detección de cheats

### Estado General
- Estado de integridad general (CLEAN/WARNING/SUSPICIOUS)
- Resumen de problemas detectados

### Formatos de Reporte
- **JSON Detallado**: Para análisis programático
- **Texto Simple**: Para lectura rápida
- **Guardado Automático**: Se guarda automáticamente al finalizar

## Limitaciones

- **Detección de Cheats**: La detección de cheats es básica y se basa en nombres de procesos. Los cheats avanzados pueden evadir esta detección.
- **Privacidad**: El programa accede a información del sistema. Los usuarios deben ser informados sobre qué se está verificando.
- **Antivirus**: Algunos antivirus pueden marcar el programa como sospechoso debido a su acceso a procesos del sistema.

## Recomendaciones para Torneos

1. **Ejecutar antes de cada partida**: Todos los jugadores deben ejecutar el verificador
2. **Verificar reportes**: Revisar los reportes generados por cada jugador
3. **Combinar con VAC**: Usar este programa junto con VAC (Valve Anti-Cheat)
4. **Transparencia**: Informar a los jugadores sobre qué se está verificando

## Solución de Problemas

### "Steam no encontrado"
- Verifica que Steam esté instalado
- Ejecuta el programa como administrador

### "Left 4 Dead 2 no encontrado"
- Verifica que L4D2 esté instalado a través de Steam
- Asegúrate de que la instalación esté completa

### "Acceso denegado a procesos"
- Ejecuta el programa como administrador
- Desactiva temporalmente el antivirus si es necesario

### "No se pueden enviar reportes a Discord"
- El verificador necesita permisos de firewall para conectarse a Discord
- **Automático**: Si ejecutas como administrador, se configura automáticamente
- **Manual**: Ejecuta `run_as_admin.bat` para configurar el firewall
- **Alternativa**: Agrega manualmente "L4D2 Tournament Verifier" al firewall de Windows

## Desarrollo

Para contribuir o modificar el programa:

1. Clona el repositorio
2. Instala las dependencias: `pip install -r requirements.txt`
3. Modifica el código según necesites
4. Prueba con diferentes configuraciones de Steam y L4D2

## Licencia

Este proyecto es de código abierto. Úsalo y modifícalo según tus necesidades para tu torneo.

## Contacto

Para preguntas o problemas, revisa la documentación o crea un issue en el repositorio.

# 🚨 Detección de Hacks Comerciales y Conocidos

## 📋 Descripción

Se ha implementado detección mejorada para los **hacks comerciales y conocidos** más populares de Left 4 Dead 2, con escaneo prioritario en las rutas críticas donde estos hacks se instalan o ejecutan.

## 🎯 Hacks Comerciales Detectados

### 1. **Aimware** 🚨 CRÍTICO
- **Tipo**: Sistema de aimbot profesional de pago
- **Características**: Loader + Aimbot + ESP + HvH (Hack vs Hack)
- **Patrones detectados**: `aimware`, `aim-ware`, `aw.dll`, `awloader`, `aimwareloader`
- **Ubicaciones comunes**: %TEMP%, %APPDATA%, Desktop, Downloads

### 2. **BauntiCheats** 🚨 CRÍTICO
- **Tipo**: Left 4 Dead 2 Helper (Popular en comunidad rusa/hispana)
- **Patrones detectados**: `baunti`, `baunticheats`, `l4d2helper`, `bauntiloader`
- **Ubicaciones comunes**: %TEMP%, %APPDATA%, Desktop

### 3. **Interwebz** 🚨 CRÍTICO
- **Tipo**: Cheat conocido para juegos Valve (TF2, CSS, L4D2)
- **Patrones detectados**: `interwebz`, `iwz`, `interwebzloader`
- **Ubicaciones comunes**: %TEMP%, %APPDATA%

### 4. **LMAOBOX** 🚨 CRÍTICO
- **Tipo**: Cheat originalmente de TF2, portado a L4D2
- **Patrones detectados**: `lmaobox`, `lmao`, `lmaoloader`
- **Ubicaciones comunes**: %TEMP%, %APPDATA%

### 5. **FleepHack / Fleep** 🚨 CRÍTICO
- **Tipo**: Hack gratuito muy distribuido en foros y YouTube
- **Patrones detectados**: `fleep`, `fleephack`, `fleeploader`
- **Ubicaciones comunes**: %TEMP%, %APPDATA%, Downloads

### 6. **Osiris / RatPoison** 🚨 CRÍTICO
- **Tipo**: Open Source usado como base para hacks privados
- **Patrones detectados**: `osiris`, `ratpoison`, `osirisloader`
- **Ubicaciones comunes**: %TEMP%, %APPDATA%, Downloads

## 🔍 Rutas Críticas Escaneadas (Prioridad)

### Prioridad CRÍTICA:

1. **`%TEMP%`** - ⚠️ **MÁS COMÚN**
   - Los loaders descomprimen archivos aquí antes de inyectar
   - Escaneo limitado a profundidad 1 (rápido pero efectivo)

2. **`%APPDATA%`** - ⚠️ **MÁS COMÚN**
   - Archivos temporales de loaders
   - Escaneo limitado a profundidad 1

3. **`%LOCALAPPDATA%`**
   - Archivos de aplicación de loaders
   - Escaneo limitado a profundidad 1

4. **`left4dead2\cfg\`** - ⚠️ **CRÍTICO**
   - Scripts maliciosos en archivos .cfg
   - Comandos prohibidos: `sv_cheats 1`, `mat_wireframe 1`, scripts de Bhop, etc.

5. **`Left 4 Dead 2\bin\`** - ⚠️ **CRÍTICO**
   - DLLs reemplazadas (d3d9.dll, opengl32.dll, etc.)
   - Wrappers/hooks para inyección

6. **`left4dead2\addons\`** - ⚠️ **CRÍTICO**
   - Archivos VPK sospechosos (Glow Hack, Material Wallhack)
   - Mods camuflados como texturas

### Prioridad ALTA:

7. **Memoria RAM del proceso `left4dead2.exe`**
   - DLLs inyectadas en memoria
   - Módulos sin firma digital
   - Hooks y patches en memoria

8. **Procesos en ejecución**
   - Loaders de hacks comerciales
   - Inyectores de DLLs
   - Herramientas de memoria

## ✅ Mejoras Implementadas

### 1. **Base de Datos de Hacks Comerciales**
- ✅ Agregados 6 hacks comerciales conocidos a `KNOWN_CHEAT_SIGNATURES`
- ✅ Patrones de detección para loaders y DLLs
- ✅ Descripciones detalladas de cada hack

### 2. **Detección en Rutas Críticas**
- ✅ Escaneo prioritario en `%TEMP%` y `%APPDATA%`
- ✅ Detección de DLLs reemplazadas en `bin/`
- ✅ Detección de scripts maliciosos en `cfg/`
- ✅ Detección de VPK sospechosos en `addons/`

### 3. **Detección en Memoria**
- ✅ Escaneo de DLLs cargadas en `left4dead2.exe`
- ✅ Detección de módulos sin firma digital
- ✅ Búsqueda de nombres de hacks conocidos en DLLs

### 4. **Detección de Procesos**
- ✅ Detección de loaders de hacks comerciales
- ✅ Detección de inyectores de DLLs
- ✅ Análisis de procesos sospechosos

### 5. **Detección de Comandos en CFG**
- ✅ Comandos prohibidos: `sv_cheats 1`, `mat_wireframe 1`
- ✅ Scripts de Bhop: `alias +bhop`, `bind space +bhop`
- ✅ Scripts de auto-fire: `+attack;wait;`
- ✅ Scripts de triggerbot: `alias +trigger`

### 6. **Detección de DLLs Reemplazadas**
- ✅ Detección de `d3d9.dll`, `d3d11.dll`, `dxgi.dll`, `opengl32.dll` en `bin/`
- ✅ Verificación de tamaño (DLLs reemplazadas suelen tener tamaños diferentes)
- ✅ Marcado como CRÍTICO si está en `bin/`

## 📊 Información Reportada

Cuando se detecta un hack comercial, el reporte incluye:

- ✅ **Nombre del hack**: Aimware, BauntiCheats, etc.
- ✅ **Tipo**: Comercial, Gratuito, Open Source
- ✅ **Severidad**: CRITICAL
- ✅ **Ubicación**: Ruta completa del archivo/processo
- ✅ **Descripción**: Información detallada del hack

## 🎯 Casos de Uso Detectados

### Caso 1: Loader en %TEMP%
```
C:\Users\...\AppData\Local\Temp\aimwareloader.exe
```
**Detección**: ✅ Loader de Aimware detectado en %TEMP%

### Caso 2: DLL Inyectada en Memoria
```
left4dead2.exe -> baunti.dll (cargada desde %TEMP%)
```
**Detección**: ✅ DLL de BauntiCheats detectada en memoria

### Caso 3: DLL Reemplazada en bin/
```
C:\...\Left 4 Dead 2\bin\d3d9.dll (tamaño sospechoso)
```
**Detección**: ✅ DLL reemplazada en bin/ - Posible wrapper/hook

### Caso 4: Script Malicioso en cfg/
```
C:\...\left4dead2\cfg\autoexec.cfg contiene: sv_cheats 1
```
**Detección**: ✅ Comando prohibido detectado en archivo .cfg

## 🧪 Pruebas

Para verificar que funciona:

1. **Colocar loader de hack** en %TEMP% o %APPDATA%
2. **Ejecutar el verificador**
3. **Verificar que detecta** el loader y lo marca como CRÍTICO
4. **Verificar que aparece** en "Firmas de Cheats Conocidos"

## 📝 Notas Importantes

1. **Los hacks comerciales se detectan por nombre** - Si cambian el nombre, puede no detectarse
2. **La detección en memoria requiere** que el juego esté ejecutándose
3. **Los loaders en %TEMP% se eliminan** después de inyectar - Puede no detectarse si ya se ejecutó
4. **La detección de DLLs reemplazadas** es más confiable que la detección de memoria

## 🔄 Compatibilidad

- ✅ Windows 10/11
- ✅ Requiere permisos de administrador para escaneo completo
- ✅ Funciona con o sin el juego ejecutándose

---

**Fecha de Implementación**: 2025-01-XX
**Estado**: ✅ Implementado y listo para usar


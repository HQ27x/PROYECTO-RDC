# 🚨 Detección de Mods para Versus/Competitivo

## 📋 Descripción

Se ha mejorado la detección de mods utilizados en modo Versus/Competitivo, que dan ventajas injustas a los jugadores. Estos mods se implementan de varias formas:

1. **Modificando `gameinfo.txt`** - Agregando rutas no oficiales en `SearchPaths`
2. **Creando carpetas no oficiales** - En la raíz de Left 4 Dead 2
3. **Agregando archivos VPK** - En la carpeta `left4dead2/` directamente

## ✅ Mejoras Implementadas

### 1. **Detección Mejorada de Modificaciones en `gameinfo.txt`**

#### Características:
- ✅ Detecta **CUALQUIER** ruta no oficial en `SearchPaths`
- ✅ Detecta errores de tipeo (ej: "Gmme" en lugar de "Game")
- ✅ Verifica si las carpetas referenciadas existen
- ✅ Cuenta archivos VPK en carpetas sospechosas
- ✅ Marca como **CRÍTICO** cualquier modificación

#### Ejemplo de Detección:

**Archivo Original (Oficial):**
```
SearchPaths
{
    Game    update
    Game    left4dead2_dlc3
    Game    left4dead2_dlc2
    Game    left4dead2_dlc1
    Game    |gameinfo_path|.
    Game    hl2
}
```

**Archivo Modificado (DETECTADO):**
```
SearchPaths
{
    Game    modsversus    ← 🚨 DETECTADO
    Game    update
    Game    left4dead2_dlc3
    ...
}
```

### 2. **Detección de Carpetas No Oficiales en Raíz**

#### Características:
- ✅ Detecta **CUALQUIER** carpeta no oficial en la raíz de L4D2
- ✅ Analiza contenido de carpetas sospechosas
- ✅ Cuenta archivos VPK dentro de carpetas
- ✅ Lista nombres de archivos VPK encontrados
- ✅ Detecta subdirectorios (estructura de mod)

#### Carpetas Oficiales (Whitelist):
- `bin`, `config`, `hl2`, `left4dead2`, `left4dead2_dlc1`, `left4dead2_dlc2`, `left4dead2_dlc3`, `left4dead2_dlc3_spanish`, `left4dead2_spanish`, `platform`, `sdk_content`, `sdk_tools`, `update`

#### Ejemplo:
```
C:\...\Left 4 Dead 2\
├── bin (oficial) ✅
├── left4dead2 (oficial) ✅
├── modsversus (no oficial) 🚨 DETECTADO
│   ├── mod1.vpk
│   └── mod2.vpk
└── update (oficial) ✅
```

### 3. **Detección de Archivos VPK No Oficiales en `left4dead2/`**

#### Características:
- ✅ Detecta archivos VPK en `left4dead2/` que NO son oficiales
- ✅ Ignora archivos oficiales: `pak01_dir.vpk`, `pak02_dir.vpk`, etc.
- ✅ Ignora archivos `pak01_XXX.vpk` (patrón oficial: `pak01_` seguido de 3 dígitos)
- ✅ Marca como **CRÍTICO** cualquier VPK no oficial en esta ubicación

#### Archivos Oficiales (Ignorados):
- `pak01_dir.vpk`, `pak02_dir.vpk`, ..., `pak12_dir.vpk`
- `pak01_000.vpk`, `pak01_001.vpk`, ..., `pak01_040.vpk` (patrón oficial)
- `german_censorship.vpk`

#### Ejemplo:
```
C:\...\left4dead2\
├── pak01_dir.vpk (oficial) ✅
├── pak01_000.vpk (oficial) ✅
├── pak01_001.vpk (oficial) ✅
├── cheat_mod.vpk (no oficial) 🚨 DETECTADO
└── modsversus.vpk (no oficial) 🚨 DETECTADO
```

## 🔍 Cómo Funciona

### Flujo de Detección:

1. **Validación de `gameinfo.txt`**
   - Lee el archivo completo
   - Extrae la sección `SearchPaths`
   - Compara con rutas oficiales
   - Detecta cualquier ruta no oficial
   - Verifica si las carpetas existen

2. **Detección de Carpetas No Oficiales**
   - Escanea la raíz de L4D2
   - Compara con whitelist oficial
   - Analiza contenido de carpetas sospechosas
   - Cuenta archivos VPK

3. **Detección de VPK No Oficiales**
   - Escanea carpeta `left4dead2/`
   - Filtra archivos oficiales
   - Detecta cualquier VPK restante

## 📊 Información Reportada

Cuando se detecta un mod para Versus/Competitivo, el reporte incluye:

### Para `gameinfo.txt`:
- ✅ Estado: MODIFIED
- ✅ Severidad: CRITICAL
- ✅ Lista de rutas no oficiales encontradas
- ✅ Ruta de carpetas detectadas
- ✅ Cantidad de archivos VPK en carpetas

### Para Carpetas No Oficiales:
- ✅ Nombre de la carpeta
- ✅ Ruta completa
- ✅ Cantidad de archivos
- ✅ Lista de archivos VPK encontrados
- ✅ Subdirectorios (si existen)

### Para VPK No Oficiales:
- ✅ Nombre del archivo
- ✅ Tamaño
- ✅ Ruta completa
- ✅ Análisis de sospecha

## ⚠️ Niveles de Severidad

- **CRITICAL**: Modificación detectada que permite mods en Versus/Competitivo
- **HIGH**: Modificación sospechosa pero no confirmada
- **NONE**: Sin modificaciones detectadas

## 🎯 Casos de Uso Detectados

### Caso 1: Carpeta "modsversus" en raíz
```
C:\...\Left 4 Dead 2\modsversus\
├── mod1.vpk
└── mod2.vpk
```
**Detección**: ✅ Carpeta no oficial detectada + VPK encontrados

### Caso 2: Modificación en gameinfo.txt
```
SearchPaths {
    Game    modsversus  ← Agregado
    Game    update
    ...
}
```
**Detección**: ✅ Ruta no oficial en SearchPaths + Carpeta verificada

### Caso 3: VPK en left4dead2/
```
C:\...\left4dead2\cheat_mod.vpk
```
**Detección**: ✅ VPK no oficial en carpeta crítica

## 🧪 Pruebas

Para verificar que funciona:

1. **Crear carpeta "modsversus"** en raíz de L4D2
2. **Agregar archivo VPK** dentro
3. **Modificar gameinfo.txt** para agregar "Game modsversus"
4. **Ejecutar verificador**
5. **Verificar que detecta**:
   - Carpeta no oficial
   - Modificación en gameinfo.txt
   - Archivos VPK en la carpeta

## 📝 Notas Importantes

1. **Los archivos oficiales se ignoran automáticamente** - No se reportan como sospechosos
2. **La detección es case-insensitive** - "ModsVersus" y "modsversus" se detectan igual
3. **Se detectan errores de tipeo** - "Gmme" en lugar de "Game" también se detecta
4. **Se verifica existencia de carpetas** - Si gameinfo.txt referencia una carpeta, se verifica si existe

---

**Fecha de Implementación**: 2025-01-XX
**Estado**: ✅ Implementado y listo para usar


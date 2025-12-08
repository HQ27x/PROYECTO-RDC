# 🎬 Ignorar Archivos DEM (Demos/Grabaciones)

## 📋 Descripción

Se ha implementado la funcionalidad para **ignorar completamente** los archivos `.dem` (demos/grabaciones del juego) durante el escaneo del anticheat.

## 🎯 ¿Qué son los archivos DEM?

Los archivos `.dem` son **grabaciones/replays del juego** que los jugadores pueden crear para:
- Ver repeticiones de partidas
- Analizar jugadas
- Compartir momentos destacados
- Grabar partidas sin usar software externo (útil para PCs de bajos recursos)

**Estos archivos NO son mods ni cheats** - Son simplemente grabaciones del juego.

## ✅ Solución Implementada

### 1. **Ignorar en Detección de Mods**

Los archivos `.dem` se ignoran completamente durante el escaneo de mods:

```python
# IGNORAR archivos DEM (demos/grabaciones del juego) - No son mods ni cheats
if filename.endswith(".dem") or filename.lower().endswith(".dem"):
    continue  # Ignorar completamente los archivos DEM
```

### 2. **Ignorar en Verificación de Archivos Sospechosos**

Los archivos `.dem` no se marcan como sospechosos:

```python
# IGNORAR archivos DEM (demos/grabaciones del juego) - No son sospechosos
if filename_lower.endswith('.dem'):
    return False  # No es sospechoso
```

## 📁 Ubicación de Archivos DEM

Los archivos DEM típicamente se encuentran en:
- `C:\Program Files (x86)\Steam\steamapps\common\Left 4 Dead 2\left4dead2\`
- Pueden tener nombres como: `1.dem`, `1_2.dem`, `1_3.dem`, etc.

## 🔍 Ejemplos de Archivos DEM

Ejemplos de archivos DEM que ahora se ignoran:
- `1.dem` (7,880 KB)
- `1_2.dem` (14,947 KB)
- `1_3.dem` (10,109 KB)
- `1_4.dem` (57,847 KB)
- `1_5.dem` (23,228 KB)
- Cualquier archivo con extensión `.dem`

## ✅ Resultado

**Antes:**
- ❌ Los archivos DEM podían ser detectados como archivos sospechosos
- ❌ Aparecían en reportes como archivos no identificados

**Ahora:**
- ✅ Los archivos DEM se ignoran completamente
- ✅ No aparecen en reportes de mods detectados
- ✅ No se marcan como sospechosos
- ✅ El escaneo es más rápido (ignora archivos irrelevantes)

## 🧪 Pruebas

Para verificar que funciona:

1. **Crear o verificar archivos DEM** en `left4dead2/`
2. **Ejecutar el verificador**
3. **Verificar que NO aparecen** en "Mods Detectados"
4. **Verificar que NO aparecen** en "Archivos Sospechosos"

## 📝 Notas Importantes

1. **Solo archivos `.dem`** - Otras extensiones se verifican normalmente
2. **Case-insensitive** - `.dem`, `.DEM`, `.Dem` se ignoran igual
3. **Cualquier ubicación** - Se ignoran en todas las carpetas escaneadas
4. **No afecta otros archivos** - Solo los archivos DEM se ignoran

## 🔄 Cambios en el Código

### Archivos Modificados:
- `main.py`:
  - Función `detect_mods()`: Agregada verificación para ignorar `.dem`
  - Función `_is_suspicious_file()`: Agregada verificación para ignorar `.dem`

---

**Fecha de Implementación**: 2025-01-XX
**Estado**: ✅ Implementado y listo para usar


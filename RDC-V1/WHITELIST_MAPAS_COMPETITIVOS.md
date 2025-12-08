# 🗺️ Whitelist de Mapas Competitivos

## 📋 Descripción

Se ha implementado una whitelist de mapas competitivos legítimos que son utilizados en servidores competitivos de Left 4 Dead 2 (zonemod, servidores competitivos, etc.).

Estos mapas se descargan manualmente y se colocan en la carpeta `addons/` directamente (no en `addons/workshop/`), por lo que el anticheat los detectaba como mods sospechosos.

## ✅ Solución Implementada

El anticheat ahora **ignora automáticamente** estos mapas competitivos cuando están en la ubicación correcta:
- ✅ Ubicación: `C:\Program Files (x86)\Steam\steamapps\common\Left 4 Dead 2\left4dead2\addons\`
- ❌ NO se ignoran si están en: `addons\workshop\` (estos son de Steam Workshop y se verifican normalmente)

## 🗺️ Mapas en Whitelist

Los siguientes mapas competitivos están en la whitelist y **NO se reportarán como mods detectados**:

1. bloodtracks
2. cmpn_FatalFreightFix
3. dead_center_reconstructed
4. detourahead
5. highwaytohell
6. NoEcho
7. red_tide
8. undead_zone
9. bts_l4d2
10. dark carnival remix
11. deadbeforedawn2_dc
12. downpour
13. ihatemountains2
14. nomercyrehab
15. suicideblitz2
16. warcelona
17. carriedoff
18. darkblood2_v3
19. deathaboardv2
20. energycrisis
21. l4d2_diescraper_362
22. openroad
23. sunrise_carnival
24. WhispersOfWinter
25. city of the dead map
26. daybreak_v3
27. DeathRow
28. hauntedforest_v3
29. l4d2_thebloodymoors
30. parish overgrowth
31. the_dark_parish
32. white_forest
33. city17l4d2
34. dead_center_rebirth
35. deathsentence
36. heavencanwaitl4d2
37. left_behind
38. ravenholm
39. tourofterror
40. Yama

## 🔧 Cómo Funciona

### Lógica de Detección:

1. **Verifica el nombre del archivo** (sin extensión `.vpk`)
2. **Verifica la ubicación**:
   - ✅ Si está en `addons/` directamente → Se ignora si está en whitelist
   - ❌ Si está en `addons/workshop/` → NO se ignora (se verifica normalmente)
   - ❌ Si está en otras carpetas → NO se ignora (se verifica normalmente)

### Ejemplo:

```
✅ IGNORADO:
C:\...\addons\deadbeforedawn2_dc.vpk  → Mapa competitivo en whitelist

❌ DETECTADO:
C:\...\addons\workshop\deadbeforedawn2_dc.vpk  → En workshop, se verifica
C:\...\addons\cheat_mod.vpk  → No está en whitelist, se detecta
```

## ➕ Agregar Nuevos Mapas

Si necesitas agregar más mapas competitivos a la whitelist:

1. Editar `main.py`
2. Buscar la constante `COMPETITIVE_MAPS_WHITELIST`
3. Agregar el nombre del mapa (sin extensión, en minúsculas)

Ejemplo:
```python
COMPETITIVE_MAPS_WHITELIST = {
    # ... mapas existentes ...
    'nuevo_mapa_competitivo',  # Agregar aquí
}
```

## ⚠️ Notas Importantes

1. **Solo se ignoran mapas en `addons/` directamente** - Los mapas en `workshop/` siempre se verifican
2. **La comparación es case-insensitive** - `DeadBeforeDawn2_DC.vpk` y `deadbeforedawn2_dc.vpk` son tratados igual
3. **Solo archivos `.vpk`** - Otros tipos de archivos no se ignoran
4. **Los mapas deben estar en la whitelist** - Si un mapa no está listado, se detectará normalmente

## 🧪 Pruebas

Para verificar que funciona:

1. Colocar un mapa competitivo (ej: `deadbeforedawn2_dc.vpk`) en `addons/`
2. Ejecutar el verificador
3. Verificar que **NO aparece** en "Mods Detectados"
4. Colocar el mismo archivo en `addons/workshop/`
5. Ejecutar el verificador
6. Verificar que **SÍ aparece** en "Mods Detectados" (porque está en workshop)

---

**Fecha de Implementación**: 2025-01-XX
**Estado**: ✅ Implementado y listo para usar


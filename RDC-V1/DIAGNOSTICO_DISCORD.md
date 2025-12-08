# 🔍 Diagnóstico: Problema de Envío a Discord

## 📋 Problema Reportado

Algunos reportes se envían correctamente a Discord (desarrolladores) pero otros no (jugadores).

## 🔎 Análisis del Código

### Posibles Causas Identificadas

1. **Límites de Discord Excedidos** ⚠️ **MÁS PROBABLE**
   - Discord tiene límites estrictos:
     - Cada campo `value`: **máximo 1024 caracteres**
     - Embed completo: **máximo 6000 caracteres**
     - Payload total: **máximo 25MB** (pero webhooks tienen límites más bajos)
   
   - **Problema**: Cuando hay muchos mods, procesos sospechosos, o información detallada, el embed puede exceder estos límites
   - **Resultado**: Discord rechaza el mensaje con error 400 (Bad Request) pero el código no lo maneja correctamente

2. **Errores Silenciosos**
   - El código captura excepciones pero no siempre las registra
   - Los errores HTTP pueden no estar siendo manejados correctamente

3. **Problemas de Red/Timeout**
   - Algunos usuarios pueden tener conexiones más lentas
   - Los timeouts pueden fallar sin reintentos suficientes

4. **Tamaño del Archivo Adjunto**
   - Los archivos TXT pueden ser muy grandes (40KB+ según las capturas)
   - Discord puede rechazar archivos muy grandes

## 🛠️ Solución Propuesta

### 1. Validar Tamaño de Embed Antes de Enviar

Agregar función para verificar y truncar contenido:

```python
def _validate_embed_size(self, embed):
    """Valida y ajusta el tamaño del embed para cumplir límites de Discord"""
    # Límites de Discord
    MAX_FIELD_VALUE = 1024
    MAX_EMBED_TOTAL = 6000
    
    # Verificar cada campo
    for field in embed.get('fields', []):
        value = field.get('value', '')
        if len(value) > MAX_FIELD_VALUE:
            # Truncar y agregar nota
            truncated = value[:MAX_FIELD_VALUE - 50]
            field['value'] = truncated + f"\n\n⚠️ _Contenido truncado (ver archivo TXT completo)_"
    
    # Verificar tamaño total del embed (aproximado)
    embed_str = json.dumps(embed)
    if len(embed_str) > MAX_EMBED_TOTAL:
        # Reducir campos menos importantes
        self._reduce_embed_size(embed)
    
    return embed
```

### 2. Mejorar Manejo de Errores

Agregar logging detallado de errores:

```python
except requests.exceptions.HTTPError as e:
    error_code = e.response.status_code if hasattr(e, 'response') else 'N/A'
    error_text = e.response.text if hasattr(e, 'response') and e.response else 'N/A'
    
    # Log detallado
    self._log_discord_error(error_code, error_text, payload_size)
    
    if error_code == 400:
        # Bad Request - probablemente payload muy grande
        print(" ⚠️ Payload muy grande, intentando método simplificado...")
        return self._send_simplified_embed(embed)
```

### 3. Dividir Embed en Múltiples Mensajes

Si el embed es muy grande, dividirlo:

```python
def _split_large_embed(self, embed):
    """Divide un embed grande en múltiples embeds más pequeños"""
    # Crear embed principal (resumen)
    main_embed = {
        "title": embed['title'],
        "description": embed['description'],
        "color": embed['color'],
        "fields": embed['fields'][:5]  # Primeros 5 campos
    }
    
    # Crear embeds adicionales para detalles
    detail_embeds = []
    remaining_fields = embed['fields'][5:]
    
    # Dividir campos restantes en grupos de 5
    for i in range(0, len(remaining_fields), 5):
        detail_embed = {
            "title": "📋 Detalles Adicionales",
            "color": embed['color'],
            "fields": remaining_fields[i:i+5]
        }
        detail_embeds.append(detail_embed)
    
    return [main_embed] + detail_embeds
```

### 4. Agregar Diagnóstico

Crear función para diagnosticar problemas:

```python
def _diagnose_discord_issue(self, embed, payload):
    """Diagnostica problemas potenciales con el payload de Discord"""
    issues = []
    
    # Verificar tamaño de campos
    for i, field in enumerate(embed.get('fields', [])):
        value_len = len(field.get('value', ''))
        if value_len > 1024:
            issues.append(f"Campo {i} ({field.get('name', 'Unknown')}) excede 1024 caracteres: {value_len}")
    
    # Verificar tamaño total
    embed_size = len(json.dumps(embed))
    if embed_size > 6000:
        issues.append(f"Embed completo excede 6000 caracteres: {embed_size}")
    
    # Verificar tamaño del payload
    payload_size = len(json.dumps(payload))
    if payload_size > 200000:  # ~200KB
        issues.append(f"Payload muy grande: {payload_size} bytes")
    
    return issues
```

## 📝 Cambios Necesarios en main.py

### Ubicación: Función `send_to_discord` (línea ~5083)

1. **Agregar validación de tamaño** antes de crear el payload
2. **Mejorar manejo de errores HTTP 400** (Bad Request)
3. **Agregar logging detallado** de errores
4. **Implementar método simplificado** como fallback

## 🧪 Cómo Probar

1. **Generar reporte con muchos mods** (simular jugador con muchos mods)
2. **Verificar logs** en `PendingReports/error_*.log`
3. **Probar con diferentes tamaños** de reportes
4. **Verificar respuesta de Discord** (código de error)

## 📊 Información de Diagnóstico

Para diagnosticar el problema actual:

1. **Revisar carpeta `PendingReports/`** en la PC del jugador
2. **Buscar archivos `error_*.log`** con detalles del error
3. **Verificar tamaño del archivo TXT** generado
4. **Revisar logs de consola** si están disponibles

## 🎯 Próximos Pasos

1. ✅ Implementar validación de tamaño de embed
2. ✅ Mejorar manejo de errores HTTP
3. ✅ Agregar logging detallado
4. ✅ Probar con reportes grandes
5. ✅ Verificar que todos los reportes se envíen correctamente

---

**Fecha**: 2025-01-XX
**Prioridad**: 🔴 ALTA - Afecta funcionalidad core del sistema


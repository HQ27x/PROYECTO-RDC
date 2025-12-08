# 🔒 Guía de Corrección de Problemas de Seguridad

## 🚨 Problema Crítico: Webhook de Discord Hardcodeado

### Situación Actual

El webhook de Discord está hardcodeado en `main.py` línea 563:

```python
self.discord_webhook_url = "https://discord.com/api/webhooks/1425316527070249042/TsKDgYSxrFEL8r0u3I_W3pcon8xnzHxISceFtq7lKCWxiKkQNJfBK5f8uNsfKSuRz5dF"
```

**⚠️ ESTE WEBHOOK ESTÁ COMPROMETIDO** - Cualquiera que vea el código puede usarlo.

---

## ✅ Solución Paso a Paso

### Paso 1: Rotar el Webhook de Discord (INMEDIATO)

1. Ve a tu servidor de Discord
2. Configuración del Canal > Integraciones > Webhooks
3. **Elimina el webhook actual** (ya está expuesto)
4. **Crea un nuevo webhook**
5. **Copia la nueva URL** (no la compartas)

### Paso 2: Migrar a Configuración Externa

#### Opción A: Usar Script de Migración (Recomendado)

```bash
# Instalar dependencia
pip install cryptography

# Ejecutar migración
python migrate_webhook.py
```

Este script:
- Cifra el webhook usando Fernet
- Guarda la configuración en `l4d2_checker_config.enc`
- Genera una clave de cifrado

#### Opción B: Configuración Manual

1. Crear archivo `.env` (no versionar en Git):
```env
DISCORD_WEBHOOK=https://discord.com/api/webhooks/NUEVO_WEBHOOK_AQUI
```

2. Instalar `python-dotenv`:
```bash
pip install python-dotenv
```

3. Modificar `main.py`:
```python
import os
from dotenv import load_dotenv

load_dotenv()
self.discord_webhook_url = os.getenv('DISCORD_WEBHOOK')
```

### Paso 3: Actualizar main.py

Reemplazar la línea 563 con:

```python
# Opción 1: Desde archivo cifrado
def load_encrypted_webhook(self):
    """Carga el webhook desde configuración cifrada"""
    try:
        from cryptography.fernet import Fernet
        import base64
        
        encrypted_config_file = Path("l4d2_checker_config.enc")
        key_file = Path("webhook_key.key")
        
        if not encrypted_config_file.exists() or not key_file.exists():
            return None
        
        # Leer clave
        with open(key_file, 'rb') as f:
            key = f.read()
        
        # Leer configuración
        with open(encrypted_config_file, 'r') as f:
            config = json.load(f)
        
        # Descifrar
        f = Fernet(key)
        encrypted = base64.b64decode(config['encrypted_webhook'])
        return f.decrypt(encrypted).decode()
    except Exception as e:
        print(f"Error al cargar webhook cifrado: {e}")
        return None

# En __init__:
self.discord_webhook_url = self.load_encrypted_webhook()
if not self.discord_webhook_url:
    # Fallback: intentar desde config.json (sin cifrar)
    self.discord_webhook_url = self.config.get('discord_webhook_url')
```

### Paso 4: Actualizar .gitignore

Agregar a `.gitignore`:

```
# Configuración sensible
l4d2_checker_config.enc
webhook_key.key
.env
*.key
```

### Paso 5: Documentar para Distribución

Crear `SETUP_WEBHOOK.md`:

```markdown
# Configuración del Webhook de Discord

## Para Administradores

1. Ejecutar `migrate_webhook.py` con el nuevo webhook
2. Distribuir `l4d2_checker_config.enc` y `webhook_key.key` por separado
3. NO incluir estos archivos en el código fuente

## Para Jugadores

Los archivos de configuración se proporcionarán por separado.
```

---

## 🔐 Mejoras Adicionales de Seguridad

### 1. Cifrar Datos Sensibles en Reportes

Modificar `send_to_discord()` para cifrar información sensible:

```python
def encrypt_sensitive_data(self, data):
    """Cifra datos sensibles antes de enviar"""
    from cryptography.fernet import Fernet
    
    # Usar clave pública del servidor
    public_key = self.get_server_public_key()
    f = Fernet(public_key)
    
    sensitive_fields = ['external_ip', 'local_ip', 'mac_address', 
                        'system_uuid', 'disk_serial', 'system_fingerprint']
    
    encrypted_data = data.copy()
    for field in sensitive_fields:
        if field in encrypted_data:
            encrypted_data[field] = f.encrypt(
                str(encrypted_data[field]).encode()
            ).decode()
    
    return encrypted_data
```

### 2. Implementar Firma Digital

Firmar reportes para verificar autenticidad:

```python
import hmac
import hashlib

def sign_report(self, report_data):
    """Firma el reporte con HMAC"""
    secret_key = self.get_secret_key()
    report_json = json.dumps(report_data, sort_keys=True)
    signature = hmac.new(
        secret_key.encode(),
        report_json.encode(),
        hashlib.sha256
    ).hexdigest()
    return signature
```

### 3. Validación de Entrada

Agregar validación robusta:

```python
def validate_token(self, token):
    """Valida formato y contenido del token"""
    if not token or len(token) < 32:
        return False, "Token inválido: muy corto"
    
    if not re.match(r'^[A-Za-z0-9_-]+$', token):
        return False, "Token inválido: caracteres no permitidos"
    
    # Validación adicional...
    return True, None
```

---

## 📋 Checklist de Seguridad

Antes de distribuir:

- [ ] Webhook rotado y nuevo webhook configurado
- [ ] Webhook movido fuera del código fuente
- [ ] Archivos sensibles agregados a `.gitignore`
- [ ] Configuración cifrada implementada
- [ ] Documentación actualizada
- [ ] Tests de seguridad realizados
- [ ] Revisión de código completada

---

## 🆘 Si el Webhook ya fue Comprometido

1. **Eliminar el webhook inmediatamente** en Discord
2. **Crear nuevo webhook** con nombre diferente
3. **Revisar logs** del canal para actividad sospechosa
4. **Actualizar código** con nuevo webhook (usando método seguro)
5. **Notificar a usuarios** si es necesario

---

## 📚 Recursos

- [Discord Webhooks Documentation](https://discord.com/developers/docs/resources/webhook)
- [Python Cryptography](https://cryptography.io/)
- [OWASP Secrets Management](https://cheatsheetseries.owasp.org/cheatsheets/Secrets_Management_Cheat_Sheet.html)

---

**Última actualización**: 2025-01-XX
**Prioridad**: 🔴 CRÍTICA


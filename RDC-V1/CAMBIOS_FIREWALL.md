# 🔥 Cambios: Configuración Automática de Firewall

## 📋 Resumen

Se agregó funcionalidad para configurar automáticamente el Firewall de Windows cuando el verificador se ejecuta como administrador, permitiendo el envío de reportes a Discord sin bloqueos.

## ✅ Cambios Realizados

### 1. **main.py** - Nuevas Funciones

#### `is_admin()`
- Verifica si el programa se ejecuta con privilegios de administrador
- Usa `ctypes.windll.shell32.IsUserAnAdmin()`

#### `setup_firewall_exception()`
- Se ejecuta **automáticamente** al inicio del programa
- Verifica si ya existe la regla del firewall
- Si el programa tiene privilegios de administrador, crea la regla automáticamente
- La regla se llama: **"L4D2 Tournament Verifier"**
- Permite todas las conexiones salientes del programa

### 2. **run_as_admin.bat** - Nuevo Script

Script que:
- Solicita elevación de privilegios automáticamente
- Ejecuta el verificador con permisos de administrador
- Permite que se configure el firewall automáticamente

**Uso:**
```bash
run_as_admin.bat
```

### 3. **README.md** - Documentación Actualizada

Se agregaron secciones:
- Característica de "Configuración Automática de Firewall"
- Sección "Ejecutar como Administrador (Recomendado)"
- Solución de problemas para reportes de Discord

## 🎯 Funcionalidad

### Cómo Funciona

1. **Al iniciar el verificador:**
   - Se llama automáticamente a `setup_firewall_exception()`
   - Verifica si ya existe la regla "L4D2 Tournament Verifier"
   - Si existe: continúa normalmente
   - Si no existe: intenta crearla

2. **Si tiene permisos de administrador:**
   - Crea la regla automáticamente usando `netsh advfirewall firewall add rule`
   - Permite todas las conexiones salientes del programa
   - El envío a Discord funcionará sin problemas

3. **Si NO tiene permisos de administrador:**
   - No puede crear la regla
   - Continúa de todas formas (puede que el firewall permita la conexión)
   - Si hay problemas, el usuario puede usar `run_as_admin.bat`

## 🚀 Ventajas

- ✅ **Automático**: No requiere configuración manual
- ✅ **Transparente**: El usuario no nota ningún cambio
- ✅ **Seguro**: Solo se configura si tiene permisos
- ✅ **No intrusivo**: Si falla, el programa continúa funcionando
- ✅ **Reutilizable**: La regla se crea una sola vez

## 📝 Notas Técnicas

### Comando de Firewall

```bash
netsh advfirewall firewall add rule name="L4D2 Tournament Verifier" dir=out action=allow program="C:\ruta\al\ejecutable.exe" enable=yes profile=any
```

### Verificar si la regla existe

```bash
netsh advfirewall firewall show rule name="L4D2 Tournament Verifier"
```

### Eliminar la regla (si es necesario)

```bash
netsh advfirewall firewall delete rule name="L4D2 Tournament Verifier"
```

## 🧪 Pruebas

Para probar la funcionalidad:

1. Elimina la regla del firewall si existe:
   ```bash
   netsh advfirewall firewall delete rule name="L4D2 Tournament Verifier"
   ```

2. Ejecuta el verificador como usuario normal:
   - No debería crear la regla
   - El programa debería funcionar igual

3. Ejecuta `run_as_admin.bat`:
   - Debería solicitar elevación
   - Debería crear la regla automáticamente
   - El verificador debería funcionar con conexión a Discord

## ⚠️ Consideraciones

- **Permisos**: Requiere ejecutarse como administrador para funcionar
- **UAC**: Windows puede mostrar un diálogo de UAC
- **Antivirus**: Algunos antivirus pueden marcar esta acción como sospechosa
- **Políticas**: En entornos corporativos, puede estar bloqueado por políticas de grupo

## 🔄 Compatibilidad

- ✅ Windows 10/11
- ✅ Todos los perfiles de firewall (dominio, privado, público)
- ✅ Funciona con Windows Defender Firewall
- ✅ Funciona con firewalls de terceros que soporten `netsh`

## 📚 Archivos Modificados

```
RDC-V1/
├── main.py                    # Funciones agregadas: is_admin(), setup_firewall_exception()
├── run_as_admin.bat          # NUEVO: Script para ejecutar como admin
├── README.md                  # Documentación actualizada
└── CAMBIOS_FIREWALL.md       # Este documento
```

## 🎉 Resultado

Ahora el verificador puede configurar automáticamente el firewall de Windows, eliminando el problema de bloqueo de conexiones a Discord cuando se ejecuta en equipos nuevos.


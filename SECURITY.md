# Política de seguridad

## Versiones soportadas

| Versión | Soportada |
|---------|-----------|
| última en `main` | ✅ |

## Reportar una vulnerabilidad

Si descubre una vulnerabilidad de seguridad en AIComply, le pedimos que **no abra un issue público**.

Envíe un correo a **aicomply.request@gmail.com** con:

- Descripción de la vulnerabilidad
- Pasos para reproducirla
- Impacto potencial estimado
- Si dispone de ella, una propuesta de solución

Nos comprometemos a:

- Acusar recibo en un plazo de 72 horas
- Proporcionar una estimación del tiempo de resolución en un plazo de 7 días
- Notificarle cuando la vulnerabilidad haya sido corregida

## Consideraciones de seguridad por diseño

### Sin persistencia de datos

AIComply no almacena ni persiste ninguna conversación ni documento analizado entre sesiones. Todo el procesamiento ocurre en memoria durante la sesión activa.

### Modelo BYOK (Bring Your Own Key)

AIComply no incluye claves de API propias. El usuario aporta su propia clave, bien mediante variables de entorno (fichero `.env`, excluido del control de versiones mediante `.gitignore`) o a través del selector interactivo de la interfaz. En ningún caso se incluyen claves en el código fuente ni se almacenan en el servidor.

### Modelos locales y privacidad máxima

Las APIs compatibles con OpenAI (Ollama, LM Studio, vLLM, llama.cpp) se conectan a través del endpoint `/v1/chat/completions` estándar configurando `OPENAI_COMPATIBLE_BASE_URL`. En este modo ningún dato abandona la infraestructura del usuario.

### Control de destinos de red — AICOMPLY_MODE

La variable de entorno `AICOMPLY_MODE` controla el nivel de restricción de red:

- `local` (por defecto): sin restricciones; válido para demos y desarrollo local.
- `hosted`: bloquea conexiones salientes a direcciones de loopback (127.x, ::1), rangos RFC1918 (10.x, 172.16–31.x, 192.168.x) y la IP de metadata de instancia (169.254.169.254), previniendo ataques SSRF cuando AIComply se despliega en un servidor accesible desde internet.

### Validación de entradas y límites

- Los campos de texto de la interfaz tienen longitud máxima (`max_chars`) para evitar peticiones desproporcionadas al LLM.
- La interpolación de contenido de usuario en prompts usa `.replace()` en lugar de `.format()`, eliminando el riesgo de `KeyError` por llaves literales en el texto.
- La salida del LLM se escapa con `html.escape()` antes de inyectarse en bloques HTML con `unsafe_allow_html=True`.

### Rate limiting por sesión

Cada sesión dispone de un token bucket en memoria de proceso (burst de 30 mensajes, recarga de 0,5 tokens/s). Esto limita el abuso en despliegues expuestos sin necesidad de autenticación.

> **Nota:** En despliegues multiusuario de alta concurrencia, sustituya el bucket en memoria por un almacén compartido (Redis, Upstash) para garantizar la aplicación entre procesos.

### Gestión segura de errores

Los mensajes de error mostrados al usuario son genéricos y no filtran detalles internos (traza de pila, mensajes de excepción). El detalle completo se registra exclusivamente en el log del servidor.

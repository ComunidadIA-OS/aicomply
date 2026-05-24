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

AIComply no almacena ni persiste ninguna conversación ni documento analizado entre sesiones. Todo el procesamiento ocurre en memoria durante la sesión activa.

Las claves de API se gestionan exclusivamente mediante variables de entorno (fichero `.env` excluido del control de versiones mediante `.gitignore`) y nunca se incluyen en el código fuente.

El uso de modelos locales (Ollama, LM Studio) garantiza que ningún dato abandona la infraestructura del usuario.

# Evaluación de Impacto en Protección de Datos (EIPD) — AIComply

**Versión:** 1.0 · **Fecha:** 2026-05-27
**Reglamento de referencia:** RGPD (UE) 2016/679 · Art. 35

---

## 1. Descripción del tratamiento

AIComply es una herramienta de autoevaluación de cumplimiento con el AI Act europeo
(Reglamento (UE) 2024/1689). El usuario describe su sistema de IA en lenguaje natural
y/o sube documentación técnica (README, ficha de producto). Esa información se envía
al proveedor de modelo de lenguaje (LLM) seleccionado para generar una clasificación de
riesgo y un análisis de obligaciones.

El flujo de datos es el siguiente:

```
Usuario → Navegador/App Streamlit → Proveedor LLM externo (o local)
                                   → Respuesta generada → Usuario
```

No existe base de datos propia, servidor intermedio ni capa de persistencia.

---

## 2. Datos tratados y categorías

| Categoría | Descripción | Sensibilidad |
|-----------|-------------|--------------|
| Descripción del sistema de IA | Texto libre introducido por el usuario | Baja - media (puede contener información empresarial confidencial) |
| Documentación técnica | README u otro fichero subido voluntariamente | Media (puede contener datos de diseño o arquitectura propietaria) |
| Datos personales | **No se solicitan ni son necesarios.** El usuario puede introducirlos de forma involuntaria en la descripción o en la documentación subida. | Alta si se introducen |

La herramienta **no trata datos de categorías especiales** (Art. 9 RGPD) por diseño.

---

## 3. Finalidad y base jurídica

**Finalidad:** orientación de cumplimiento normativo con el AI Act europeo. La información
se usa exclusivamente para generar la clasificación de riesgo y el análisis de
obligaciones del sistema evaluado.

**Base jurídica:** interés legítimo del usuario en evaluar el cumplimiento de su propio
sistema (Art. 6.1.f RGPD), complementado por la ejecución del servicio solicitado
(Art. 6.1.b).

---

## 4. Destinatarios y transferencias internacionales

El proveedor LLM activo en cada sesión recibe el contenido de la conversación. Véase
la tabla de privacidad del README para las condiciones específicas de cada proveedor.

| Proveedor | Ubicación | Entrenamiento con datos de usuario |
|-----------|-----------|-------------------------------------|
| Anthropic (Claude) | EE. UU. | No (política comercial) |
| OpenAI (GPT) | EE. UU. | No (plan de pago); Sí en plan gratuito |
| Mistral AI | Francia (UE) | Sí en plan gratuito; No en plan de pago |
| Ollama / LM Studio | Local — sin transferencia | N/A |

Las transferencias a EE. UU. (Anthropic, OpenAI) se amparan en las salvaguardas
contractuales estándar (SCCs) o en el marco UE-EE. UU. de privacidad de datos,
según el contrato vigente con cada proveedor. Se recomienda revisar los DPA de cada
proveedor antes del uso empresarial.

---

## 5. Conservación

**Sin persistencia.** Todo el contenido (conversación, documentación subida, informes
generados) reside exclusivamente en la memoria de sesión del navegador y del proceso
Streamlit activo. Al cerrar la pestaña o reiniciar la sesión, los datos se descartan.

AIComply no escribe bases de datos, no guarda ficheros en disco ni registra logs que
contengan el texto de las conversaciones.

---

## 6. Análisis de riesgos

| Riesgo | Probabilidad | Impacto | Nivel |
|--------|-------------|---------|-------|
| Envío involuntario de datos personales o confidenciales al proveedor LLM externo | Media | Alto | **Alto** |
| Transferencia internacional de datos a proveedores en EE. UU. sin DPA adecuado | Baja (depende del proveedor elegido) | Alto | **Medio** |
| Prompt injection mediante documentación maliciosa subida por el usuario | Baja | Medio | **Bajo** |
| Filtración de datos por acceso no autorizado al proceso Streamlit | Muy baja (sin persistencia) | Bajo | **Muy bajo** |

---

## 7. Medidas de mitigación implementadas

| Medida | Implementación |
|--------|----------------|
| **Sin persistencia de datos** | No hay base de datos ni escritura a disco; todo en memoria de sesión |
| **Opción de procesamiento local** | El usuario puede usar Ollama / LM Studio para que ningún dato salga de su infraestructura |
| **BYOK (Bring Your Own Key)** | El usuario aporta su propia clave API; AIComply no almacena credenciales |
| **Validación SSRF** | `src/security.py::validar_base_url` bloquea URLs internas en modo `hosted` (Art. AICOMPLY_MODE) |
| **Rate limiting por sesión** | `TokenBucketSesion` limita el número de peticiones por sesión (30 burst, 1 req/2 s) |
| **Saneamiento de entradas (anti prompt injection)** | `src/security.py::envolver_contenido_no_confiable` delimita el contenido de usuario con marcadores explícitos; neutraliza secuencias `<<<`/`>>>` antes de interpolación en el prompt |
| **Aviso de privacidad por proveedor** | La interfaz muestra las condiciones de cada proveedor antes de enviar datos |
| **Aviso Art. 50.1** | El usuario es informado de que interactúa con un sistema de IA en cada sesión |

---

## 8. Recomendación al usuario

> **No introduzca datos personales innecesarios** en las descripciones del sistema ni en
> la documentación que suba. Si su sistema procesa datos de personas, descríbalo de forma
> genérica (p. ej. «procesa datos de empleados») sin incluir registros reales, nombres,
> números de identificación u otra información personal identificable.
>
> Si su organización está sujeta al RGPD y el sistema que evalúa procesa datos
> personales a gran escala o de categorías especiales, consulte con su Delegado de
> Protección de Datos (DPD) antes de utilizar esta herramienta con información real.

---

## 9. Responsable y fecha de revisión

Esta EIPD debe revisarse cuando se introduzca un nuevo proveedor LLM, cuando cambie
el flujo de datos descrito en la Sección 1, o cuando una nueva versión del corpus o
del prompt suponga un cambio material en la naturaleza del tratamiento.

**Próxima revisión recomendada:** diciembre de 2026, cuando vence el periodo de gracia del
Art. 111.4 para los sistemas generativos que ya estuvieran en el mercado antes del 2 de agosto
de 2026. El Art. 50.2 es exigible desde esa fecha con carácter general.

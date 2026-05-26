# Changelog

Todos los cambios relevantes de AIComply se documentan en este fichero.
Formato basado en [Keep a Changelog](https://keepachangelog.com/es/1.0.0/).

---

## [0.1.0] - 2026-05-27

Primera versión de AIComply, desarrollada íntegramente durante el Hackathon Reto IA Responsable y Abierta en Industria (SEDIA / AESIA), del 22 al 27 de mayo de 2026.

### Fase 1 — Núcleo de la aplicación (22–23 mayo)

- Arquitectura de tres pestañas independientes: Evaluador, Cumplimiento, Informe
- Árbol de decisión conversacional completo basado en Art. 5, Art. 6 y Anexo III del Reglamento (UE) 2024/1689, con señal de fin y soporte de roles múltiples
- Capa de abstracción LLM multi-provider (`LLMProvider`) con implementaciones para Anthropic Claude y APIs compatibles con OpenAI (Ollama, LM Studio, Groq, Mistral, vLLM...)
- Tres tipos de informe exportables: solo clasificación, solo cumplimiento, informe completo (PDF y texto plano)
- Clasificaciones precisas del AI Act: PROHIBIDO, ALTO, LIMITADO, MÍNIMO, NO CUMPLE LA DEFINICIÓN DE SISTEMA DE IA, EXCLUIDO
- `pyproject.toml` con configuración del proyecto, dependencias y herramientas de desarrollo (ruff, mypy, pytest)

### Fase 2 — Corpus normativo y RAG (23–24 mayo)

- Corpus normativo completo — 27 documentos, 282 fragmentos indexados: AI Act, AESIA (16 guías), GDPR/AEPD, anteproyecto Ley española de IA, directrices Comisión Europea mayo 2026
- 25 artículos del AI Act estructurados en JSON con metadatos normativos (título, nivel de riesgo, rol, requisitos clave, palabras clave)
- Pipeline de ingesta `scripts/ingest_txt.py` para convertir documentos legales `.txt` al formato JSON del RAG
- RAG dinámico conectado al Evaluador — el árbol de decisión consulta el corpus en tiempo real para contextualizar cada nodo

### Fase 3 — Informe PDF y trazabilidad (24–25 mayo)

- Plantilla visual PDF con portada, métricas de cumplimiento, cajas de color por obligación (cubierta / parcial / área de mejora), badge del plan de acción y paginación
- Trazabilidad auditable — cada respuesta del informe indica si provino de entrada directa del usuario, inferencia confirmada o nodo INDETERMINADO
- Soporte de roles múltiples diferenciados — evaluación completa por cada rol (Proveedor, Implementador, Distribuidor, Importador) con obligaciones separadas
- Análisis de cumplimiento con documentación técnica — incorpora el README del sistema evaluado para afinar la detección de obligaciones cubiertas

### Fase 4 — Seguridad, calidad y pulido (25–27 mayo)

- `AICOMPLY_MODE=hosted` — validación SSRF de la URL base del provider (bloquea loopback, RFC1918 y metadata de instancia)
- Rate limiting por sesión mediante token bucket en memoria (burst 30 mensajes, recarga 0,5 tokens/s)
- Errores seguros: mensajes genéricos al usuario, detalle completo solo en log del servidor
- Escape de salida del LLM con `html.escape()` antes de inyección en HTML
- Interpolación de prompts con `.replace()` en lugar de `.format()` para evitar `KeyError`
- Backoff acotado con `Retry-After` en providers; rollback del historial si `chat_stream` falla
- GitHub Actions CI — pipeline de tests automáticos con soporte Python 3.10–3.12
- Suite de tests unitarios para árbol de decisión, chatbot, generador PDF y streaming
- Guardar y restaurar sesión en JSON desde el sidebar
- Casos de ejemplo: caso 01 (horno industrial, ALTO) y caso 02 (chatbot de reservas, LIMITADO) con informes PDF reales

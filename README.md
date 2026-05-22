# AIComply

[![License](https://img.shields.io/badge/License-Apache_2.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)
[![Python](https://img.shields.io/badge/python-3.10%2B-blue)](https://www.python.org/)
[![Streamlit](https://img.shields.io/badge/built%20with-Streamlit-FF4B4B)](https://streamlit.io/)

**Asistente conversacional en español para evaluar el cumplimiento de sistemas de IA con el AI Act europeo (Reglamento UE 2024/1689), orientado a PYMEs industriales.**

Compatible con **Anthropic Claude**, **OpenAI**, **Ollama** (modelos locales) y cualquier **API compatible con OpenAI** (LM Studio, vLLM, Groq, Together AI, Mistral API...).

---

> **AVISO LEGAL:** AIComply es una herramienta auxiliar de orientación. Los resultados no constituyen asesoramiento legal. Se recomienda consultar con especialistas antes de tomar decisiones de cumplimiento normativo.

---

## Descripción

AIComply ayuda a PYMEs industriales a evaluar si sus sistemas de IA cumplen con el AI Act europeo. El sistema consta de tres fases:

1. **Chatbot conversacional:** Conversa con la empresa para entender su sistema de IA, determina el nivel de riesgo e identifica los artículos aplicables con sus definiciones oficiales.

2. **Análisis documental:** El usuario sube o pega su README o documentación técnica. El sistema detecta gaps con referencias concretas a artículos.

3. **Informe de cumplimiento:** Exportable en Markdown y PDF. Tres niveles por artículo: cumple, parcial, gap. Incluye recomendaciones concretas.

## Configuración del modelo de lenguaje

AIComply incluye una pantalla de configuración inicial donde puede elegir su proveedor de IA con información clara sobre las implicaciones de privacidad de cada opción.

### Tabla comparativa de privacidad

| Provider | Plan | Datos en servidores de terceros | Uso para entrenamiento | Recomendado para |
|----------|------|---------------------------------|------------------------|------------------|
| Ollama (local) | Gratuito | No — todo local | No | Documentación confidencial, máxima privacidad |
| LM Studio / vLLM | Gratuito | No — todo local | No | Documentación confidencial, máxima privacidad |
| Anthropic Claude | API Enterprise | Si (EE. UU.) | No | Documentación empresarial confidencial |
| Anthropic Claude | API de pago | Si (EE. UU.) | No | Uso empresarial general |
| OpenAI | ChatGPT Enterprise | Si (EE. UU.) | No | Documentación empresarial confidencial |
| OpenAI | API de pago Tier 1+ | Si (EE. UU.) | No por defecto | Uso empresarial, revisar DPA |
| Groq / Together AI | API externa | Si (terceros) | Revisar política | Uso general sin datos sensibles |
| OpenAI | Cuenta gratuita | Si (EE. UU.) | **Si** | **No recomendado para datos confidenciales** |

### Configuración via .env (despliegues fijos)

Copie `.env.example` a `.env` y configure el provider deseado:

**Ollama (recomendado para demo y datos sensibles):**
```bash
LLM_PROVIDER=ollama
OLLAMA_MODEL=llama3
OLLAMA_BASE_URL=http://localhost:11434
```

**Anthropic Claude:**
```bash
LLM_PROVIDER=anthropic
ANTHROPIC_API_KEY=sk-ant-...
ANTHROPIC_MODEL=claude-sonnet-4-6
```

**LM Studio (local, gratuito):**
```bash
LLM_PROVIDER=openai_compatible
OPENAI_COMPATIBLE_BASE_URL=http://localhost:1234/v1
OPENAI_COMPATIBLE_MODEL=llama-3.1-8b-instruct
```

**Groq (servicio externo rápido):**
```bash
LLM_PROVIDER=openai_compatible
OPENAI_COMPATIBLE_BASE_URL=https://api.groq.com/openai/v1
OPENAI_COMPATIBLE_API_KEY=gsk_...
OPENAI_COMPATIBLE_MODEL=llama-3.1-70b-versatile
```

Si `LLM_PROVIDER` está vacío, la interfaz mostrará el selector interactivo en cada inicio.

### Ejemplos de modelos compatibles

| Modelo | Provider | Comando de instalación |
|--------|----------|------------------------|
| Llama 3.1 8B | Ollama | `ollama pull llama3.1` |
| Llama 3.1 70B | Ollama | `ollama pull llama3.1:70b` |
| Mistral 7B | Ollama | `ollama pull mistral` |
| Qwen2.5 7B | Ollama | `ollama pull qwen2.5` |
| DeepSeek-R1 | Ollama | `ollama pull deepseek-r1` |
| Gemma 2 9B | Ollama | `ollama pull gemma2` |
| Llama 3.1 8B | LM Studio | Descargar desde la interfaz de LM Studio |
| Mistral 7B Instruct | LM Studio | Descargar desde la interfaz de LM Studio |

## Estructura del proyecto

```
aicomply/
├── app.py                          # Aplicación principal Streamlit
├── config.py                       # Configuración y constantes
├── src/
│   ├── chatbot.py                  # Chatbot conversacional con RAG
│   ├── readme_analyzer.py          # Análisis de documentación técnica
│   ├── report_generator.py         # Generación del informe (sin API)
│   ├── risk_classifier.py          # Clasificación rápida de riesgo
│   └── llm/
│       ├── provider.py             # Clase abstracta LLMProvider
│       ├── anthropic_provider.py   # Implementación Anthropic Claude
│       ├── ollama_provider.py      # Implementación Ollama (local)
│       ├── openai_provider.py      # Implementación OpenAI-compatible
│       └── factory.py             # Fábrica de providers
│   └── rag/
│       ├── vectorstore.py          # Vectorstore TF-IDF (sin FAISS)
│       └── retriever.py            # Recuperador de artículos relevantes
├── data/
│   └── ai_act/
│       └── ai_act_articles.json   # Artículos reales del AI Act en español
├── prompts/
│   └── system_prompts.py          # Prompts del sistema
├── LICENSE                         # Licencia Apache 2.0
├── README.md
├── CONTRIBUTING.md
├── requirements.txt
├── .env.example
└── .gitignore
```

## Instalación

### Requisitos previos

- Python 3.10 o superior
- Una fuente de LLM: API de Anthropic/OpenAI, Ollama instalado, o LM Studio

### Pasos

1. **Clonar el repositorio:**
   ```bash
   git clone https://github.com/tu-usuario/aicomply.git
   cd aicomply
   ```

2. **Crear y activar un entorno virtual:**
   ```bash
   python -m venv .venv
   source .venv/bin/activate    # Linux/macOS
   .venv\Scripts\activate       # Windows
   ```

3. **Instalar las dependencias:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configurar el provider (opcional):**
   ```bash
   cp .env.example .env
   # Edite .env con su configuración preferida
   ```
   Si no configura `.env`, la aplicación mostrará el selector interactivo.

5. **Ejecutar:**
   ```bash
   streamlit run app.py
   ```

### Inicio rápido con Ollama

```bash
# 1. Instalar Ollama
curl -fsSL https://ollama.ai/install.sh | sh   # Linux/macOS

# 2. Descargar un modelo
ollama pull llama3.1

# 3. Ejecutar AIComply (sin .env — usará el selector interactivo)
streamlit run app.py
```

## Uso

1. **Elija su provider:** En la pantalla inicial, seleccione el modelo de IA y lea las condiciones de privacidad.
2. **Acepte el aviso legal** de AIComply.
3. **Chatbot:** Describa su sistema de IA respondiendo las preguntas del asistente.
4. **Análisis documental:** Suba o pegue su README para detectar gaps.
5. **Informe:** Genere y descargue el informe en Markdown o PDF.

## Artículos del AI Act cubiertos

| Artículo | Título | Nivel de riesgo |
|----------|--------|-----------------|
| Art. 5   | Prácticas prohibidas | Inaceptable |
| Art. 6   | Clasificación de sistemas de alto riesgo | Alto |
| Art. 9   | Sistema de gestión de riesgos | Alto |
| Art. 10  | Datos y gobernanza de datos | Alto |
| Art. 13  | Transparencia e información | Alto |
| Art. 14  | Supervisión humana | Alto |
| Art. 15  | Exactitud, solidez y ciberseguridad | Alto |
| Art. 52  | Obligaciones de transparencia (chatbots, deepfakes) | Limitado |
| Art. 69  | Códigos de conducta voluntarios | Mínimo |

## Stack tecnológico

| Componente | Tecnología |
|-----------|-----------|
| Interfaz | Streamlit |
| Abstracción LLM | `LLMProvider` (clase abstracta propia) |
| Anthropic Claude | `anthropic` SDK |
| Ollama / modelos locales | `httpx` (API REST de Ollama) |
| OpenAI y compatibles | `openai` SDK |
| RAG (recuperación) | TF-IDF con `scikit-learn` (sin FAISS) |
| Exportación PDF | `fpdf2` |
| Variables de entorno | `python-dotenv` |

## Hoja de ruta

### v1.x
- [ ] Soporte para artículos 11, 12, 16-17, 71 del AI Act
- [ ] Plantillas de documentación técnica (Art. 11) descargables
- [ ] Comparación entre versiones del sistema a lo largo del tiempo

### v2.x
- [ ] API REST para integración con CI/CD
- [ ] Modo autoevaluación con listas de verificación por artículo
- [ ] Integración con el AI Office de la UE para actualizaciones normativas

## Contribuir

Las contribuciones son bienvenidas. Consulte [CONTRIBUTING.md](CONTRIBUTING.md) para las directrices de contribución, incluyendo cómo añadir nuevos providers de LLM.

## Licencia

Este proyecto está licenciado bajo la [Licencia Apache 2.0](LICENSE).

---

**AIComply es una herramienta auxiliar de orientación. Los resultados no constituyen asesoramiento legal. Se recomienda consultar con especialistas antes de tomar decisiones de cumplimiento normativo.**

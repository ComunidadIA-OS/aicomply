# AIComply

[![License](https://img.shields.io/badge/License-Apache_2.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)
[![Python](https://img.shields.io/badge/python-3.10%2B-blue)](https://www.python.org/)
[![Streamlit](https://img.shields.io/badge/built%20with-Streamlit-FF4B4B)](https://streamlit.io/)

**Asistente conversacional en español para evaluar el cumplimiento de sistemas de IA con el AI Act europeo (Reglamento UE 2024/1689), orientado a PYMEs industriales.**

---

> **AVISO LEGAL:** AIComply es una herramienta auxiliar de orientación. Los resultados no constituyen asesoramiento legal. Se recomienda consultar con especialistas antes de tomar decisiones de cumplimiento normativo.

---

## Descripción

AIComply ayuda a PYMEs industriales a evaluar si sus sistemas de IA cumplen con el Reglamento de Inteligencia Artificial de la Unión Europea (AI Act). El sistema consta de tres fases:

1. **Chatbot conversacional:** Conversa con la empresa para entender su sistema de IA, determina el nivel de riesgo (prohibido, alto, limitado o mínimo) e identifica los artículos aplicables del AI Act. Cada concepto técnico muestra su definición oficial con referencia al artículo correspondiente.

2. **Análisis documental:** El usuario sube o pega su README o documentación técnica. El sistema lo analiza contra los requisitos del AI Act identificados y detecta gaps con referencias concretas a artículos.

3. **Informe de cumplimiento:** Exportable en Markdown y PDF. Tres niveles de evaluación por artículo: cumple, parcial, gap. Incluye recomendaciones concretas para cada gap.

### Artículos del AI Act cubiertos

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

## Estructura del proyecto

```
aicomply/
├── app.py                          # Aplicación principal Streamlit
├── config.py                       # Configuración y constantes
├── src/
│   ├── chatbot.py                  # Chatbot conversacional con RAG
│   ├── readme_analyzer.py          # Análisis de documentación técnica
│   ├── report_generator.py         # Generación del informe de cumplimiento
│   ├── risk_classifier.py          # Clasificación rápida de riesgo
│   └── rag/
│       ├── vectorstore.py          # Vectorstore TF-IDF (sin FAISS)
│       └── retriever.py            # Recuperador de artículos relevantes
├── data/
│   └── ai_act/
│       └── ai_act_articles.json   # Artículos reales del AI Act en español
├── prompts/
│   └── system_prompts.py          # Prompts del sistema para Claude
├── LICENSE                         # Licencia Apache 2.0
├── README.md                       # Este fichero
├── CONTRIBUTING.md                 # Guía de contribución
├── requirements.txt                # Dependencias Python
├── .env.example                    # Ejemplo de variables de entorno
└── .gitignore                      # Ficheros excluidos de Git
```

## Instalación

### Requisitos previos

- Python 3.10 o superior
- Una clave de API de Anthropic ([obtener aquí](https://console.anthropic.com/))

### Pasos

1. **Clonar el repositorio:**

   ```bash
   git clone https://github.com/tu-usuario/aicomply.git
   cd aicomply
   ```

2. **Crear y activar un entorno virtual:**

   ```bash
   python -m venv .venv
   source .venv/bin/activate        # Linux/macOS
   .venv\Scripts\activate           # Windows
   ```

3. **Instalar las dependencias:**

   ```bash
   pip install -r requirements.txt
   ```

4. **Configurar la clave de API:**

   ```bash
   cp .env.example .env
   ```

   Edite el fichero `.env` y añada su clave de API de Anthropic:

   ```
   ANTHROPIC_API_KEY=sk-ant-...
   ```

5. **Ejecutar la aplicación:**

   ```bash
   streamlit run app.py
   ```

   La aplicación se abrirá automáticamente en su navegador en `http://localhost:8501`.

## Uso

### Fase 1: Evaluación conversacional

1. Acepte el aviso legal en la pantalla de bienvenida.
2. En la pestaña **Chatbot de evaluación**, describa su sistema de IA respondiendo a las preguntas del asistente.
3. El asistente determinará el nivel de riesgo y los artículos aplicables.
4. Pulse **Generar resumen de la conversación** para preparar el informe.

### Fase 2: Análisis documental

1. Vaya a la pestaña **Análisis documental**.
2. Suba un fichero `.md`, `.txt` o `.rst`, o pegue directamente el contenido de su README.
3. Pulse **Analizar documentación** para obtener el análisis de gaps.

### Fase 3: Informe de cumplimiento

1. Vaya a la pestaña **Informe de cumplimiento**.
2. Pulse **Generar informe** para crear el informe completo.
3. Descargue el informe en formato Markdown o PDF.

### Clasificación rápida

En el chatbot, use el botón **Clasificación rápida por descripción** para obtener una clasificación inmediata a partir de una descripción breve de su sistema.

## Stack tecnológico

| Componente | Tecnología |
|-----------|-----------|
| Interfaz | [Streamlit](https://streamlit.io/) |
| Modelo de lenguaje | [Claude (Anthropic)](https://www.anthropic.com/) via `anthropic` SDK |
| RAG (recuperación) | TF-IDF con `scikit-learn` (sin FAISS) |
| Exportación PDF | `fpdf2` |
| Variables de entorno | `python-dotenv` |

## Hoja de ruta

### v1.x (próximas mejoras)
- [ ] Soporte para más artículos del AI Act (Arts. 11, 12, 16-17, 71)
- [ ] Integración con la base de datos de la UE para registro de sistemas de alto riesgo
- [ ] Plantillas de documentación técnica (Art. 11) descargables
- [ ] Comparación entre versiones del mismo sistema a lo largo del tiempo

### v2.x (largo plazo)
- [ ] Soporte multilingüe (inglés, francés, alemán)
- [ ] API REST para integración con herramientas de CI/CD
- [ ] Modo autoevaluación guiada con listas de verificación por artículo
- [ ] Integración con el AI Office de la UE para actualizaciones automáticas de la normativa
- [ ] Panel de seguimiento del progreso de cumplimiento a lo largo del tiempo

## Contribuir

Las contribuciones son bienvenidas. Consulte [CONTRIBUTING.md](CONTRIBUTING.md) para las directrices de contribución.

## Licencia

Este proyecto está licenciado bajo la [Licencia Apache 2.0](LICENSE).

---

**AIComply es una herramienta auxiliar de orientación. Los resultados no constituyen asesoramiento legal. Se recomienda consultar con especialistas antes de tomar decisiones de cumplimiento normativo.**

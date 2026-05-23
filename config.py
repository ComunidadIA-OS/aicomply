# Copyright 2025 AIComply Contributors
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import os
from dotenv import load_dotenv

load_dotenv()

# ── Selección de provider ──────────────────────────────────────────────────────
# Si LLM_PROVIDER está vacío, la interfaz mostrará el selector interactivo.
# Valores válidos: anthropic | ollama | openai_compatible
LLM_PROVIDER = os.getenv("LLM_PROVIDER", "")

# ── Anthropic Claude ───────────────────────────────────────────────────────────
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", "")
ANTHROPIC_MODEL = os.getenv("ANTHROPIC_MODEL", "claude-sonnet-4-6")

# ── Ollama (modelos locales) ───────────────────────────────────────────────────
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "llama3")
OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")

# ── API compatible con OpenAI ──────────────────────────────────────────────────
OPENAI_COMPATIBLE_BASE_URL = os.getenv("OPENAI_COMPATIBLE_BASE_URL", "http://localhost:1234/v1")
OPENAI_COMPATIBLE_API_KEY = os.getenv("OPENAI_COMPATIBLE_API_KEY", "")
OPENAI_COMPATIBLE_MODEL = os.getenv("OPENAI_COMPATIBLE_MODEL", "")

# ── Textos de la interfaz ──────────────────────────────────────────────────────
DISCLAIMER_INICIAL = """
**AVISO LEGAL IMPORTANTE**

AIComply es una herramienta de apoyo para la autoevaluación de cumplimiento con el AI Act europeo.

- Esta herramienta **NO constituye asesoramiento legal** y no sustituye la consulta con un experto jurídico.
- Los análisis generados son orientativos y pueden contener errores o estar desactualizados.
- El AI Act es una normativa compleja; su aplicación concreta depende del contexto específico de cada organización.
- Para decisiones con impacto legal o regulatorio, consulte siempre con un abogado especializado.

Al continuar, acepta estas condiciones.
"""

NIVELES_RIESGO = {
    "PROHIBIDO": {
        "color": "#FF0000",
        "descripcion": "Sistema de IA prohibido por el AI Act (Artículo 5)",
    },
    "ALTO": {
        "color": "#FF4444",
        "descripcion": "Sistema de IA de alto riesgo (Artículos 6-17)",
    },
    "LIMITADO": {
        "color": "#FFA500",
        "descripcion": "Sistema de IA de riesgo limitado (Art. 50)",
    },
    "MINIMO": {
        "color": "#00AA00",
        "descripcion": "Sistema de IA de riesgo mínimo — sin obligaciones específicas del AI Act",
    },
    "NO CUMPLE LA DEFINICIÓN DE SISTEMA DE IA": {
        "color": "#9E9E9E",
        "descripcion": "El sistema evaluado no cumple la definición de sistema de IA del Art. 3.1 — el Reglamento (UE) 2024/1689 no es aplicable",
    },
    "EXCLUIDO": {
        "color": "#757575",
        "descripcion": "Sistema de IA fuera del ámbito de aplicación del Reglamento (UE) 2024/1689 (Art. 2)",
    },
}


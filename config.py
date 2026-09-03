# Copyright 2026 AIComply Contributors
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
# Valores válidos: anthropic | openai_compatible
# Para Ollama: use openai_compatible con OPENAI_COMPATIBLE_BASE_URL=http://localhost:11434/v1
LLM_PROVIDER = os.getenv("LLM_PROVIDER", "")

# ── Modo de despliegue ─────────────────────────────────────────────────────────
# "local"  — sin restricciones de red (por defecto; apto para demos y desarrollo)
# "hosted" — bloquea URLs internas (loopback, RFC1918, metadata) para prevenir SSRF
AICOMPLY_MODE = os.getenv("AICOMPLY_MODE", "local")

# ── Techo de longitud de la respuesta ──────────────────────────────────────────
# Es un techo, no un gasto: solo se consume si el modelo lo llena. Con 2048 el informe
# final de un caso de alto riesgo con doble rol se cortaba a media tabla. Bájelo si su
# servidor local tiene una ventana de contexto corta.
LLM_MAX_TOKENS = os.getenv("LLM_MAX_TOKENS", "8192")

# ── Anthropic Claude ───────────────────────────────────────────────────────────
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", "")
ANTHROPIC_MODEL = os.getenv("ANTHROPIC_MODEL", "claude-sonnet-4-6")

# ── API compatible con OpenAI ──────────────────────────────────────────────────
OPENAI_COMPATIBLE_BASE_URL = os.getenv("OPENAI_COMPATIBLE_BASE_URL", "http://localhost:1234/v1")
OPENAI_COMPATIBLE_API_KEY = os.getenv("OPENAI_COMPATIBLE_API_KEY", "")
OPENAI_COMPATIBLE_MODEL = os.getenv("OPENAI_COMPATIBLE_MODEL", "")

# ── Textos de la interfaz ──────────────────────────────────────────────────────
AVISO_IA_ART50 = (
    "Está interactuando con un sistema de inteligencia artificial. "
    "Las respuestas se generan automáticamente y son orientativas "
    "(Art. 50.1 del Reglamento (UE) 2024/1689)."
)

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
        "descripcion": "Sistema de IA de riesgo mínimo — no se identifican obligaciones propias de sistemas de alto riesgo; pueden aplicar obligaciones horizontales (Art. 4, transparencia, normativa sectorial)",
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


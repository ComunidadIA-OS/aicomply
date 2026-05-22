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

import json
import anthropic
from config import ANTHROPIC_API_KEY, MODEL


PROMPT_CLASIFICACION = """Analiza el siguiente sistema de IA y clasifícalo según el AI Act europeo (Reglamento UE 2024/1689).

Sistema descrito: {descripcion}

Devuelve ÚNICAMENTE un JSON con este formato (sin texto adicional ni bloques de código markdown):
{{
  "nivel_riesgo": "PROHIBIDO|ALTO|LIMITADO|MINIMO",
  "confianza": "alta|media|baja",
  "justificacion": "explicación breve de la clasificación con referencias al AI Act",
  "articulos_principales": ["Art. 5", "Art. 6"],
  "categoria_alto_riesgo": "solo si es ALTO: infraestructura_critica|educacion|empleo_rrhh|servicios_esenciales|seguridad_publica|migracion_asilo|justicia|biometria|otro",
  "obligaciones_clave": ["obligación 1 (Art. X)", "obligación 2 (Art. Y)", "obligación 3 (Art. Z)"]
}}

Criterios de clasificación del AI Act:
- PROHIBIDO (Art. 5): Manipulación subliminal, scoring social gubernamental, identificación biométrica en tiempo real en espacios públicos, explotación de vulnerabilidades de grupos específicos
- ALTO (Art. 6 + Anexo III): Infraestructura crítica, educación y formación, RRHH y empleo, servicios esenciales (crédito, seguros, emergencias), aplicación de la ley, migración y asilo, administración de justicia, biometría de identificación
- LIMITADO (Art. 52): Chatbots e interfaces conversacionales, sistemas de generación de contenido (texto, imágenes, audio, video), sistemas de recomendación que interactúan con usuarios
- MINIMO: Control de calidad en producción, optimización logística, mantenimiento predictivo en maquinaria sin impacto en personas, análisis de datos internos sin decisiones sobre personas"""


class ClasificadorRiesgo:
    """Clasifica el nivel de riesgo de un sistema de IA según el AI Act."""

    def __init__(self):
        self.client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)

    def clasificar(self, descripcion: str) -> dict:
        """Clasifica el riesgo dado una descripción del sistema de IA."""
        respuesta = self.client.messages.create(
            model=MODEL,
            max_tokens=512,
            messages=[
                {
                    "role": "user",
                    "content": PROMPT_CLASIFICACION.format(descripcion=descripcion),
                }
            ],
        )

        texto = respuesta.content[0].text.strip()
        if texto.startswith("```"):
            texto = texto.split("```")[1]
            if texto.startswith("json"):
                texto = texto[4:]

        try:
            return json.loads(texto.strip())
        except json.JSONDecodeError:
            return {
                "nivel_riesgo": "DESCONOCIDO",
                "confianza": "baja",
                "justificacion": "No se pudo clasificar automáticamente. Por favor, proporcione más detalles.",
                "articulos_principales": [],
                "obligaciones_clave": [],
            }

    def obtener_obligaciones_por_nivel(self, nivel: str) -> list[str]:
        """Devuelve las obligaciones principales para cada nivel de riesgo."""
        obligaciones = {
            "PROHIBIDO": [
                "El sistema NO puede desarrollarse ni desplegarse (Art. 5 AI Act)",
                "Posibles sanciones de hasta 35.000.000 EUR o 7% de la facturación global",
            ],
            "ALTO": [
                "Sistema de gestión de riesgos documentado (Art. 9)",
                "Gobernanza de datos de entrenamiento (Art. 10)",
                "Documentación técnica completa (Art. 11)",
                "Registro automático de actividad (Art. 12)",
                "Transparencia e instrucciones de uso (Art. 13)",
                "Supervisión humana efectiva (Art. 14)",
                "Exactitud, solidez y ciberseguridad (Art. 15)",
                "Registro en base de datos UE antes del despliegue (Art. 71)",
            ],
            "LIMITADO": [
                "Informar al usuario que interactúa con IA (Art. 52)",
                "Marcar contenido generado por IA",
                "Transparencia en sistemas de recomendación",
            ],
            "MINIMO": [
                "No hay obligaciones específicas del AI Act",
                "Se recomienda seguir buenas prácticas voluntarias",
                "Considerar adhesión a códigos de conducta voluntarios (Art. 69)",
            ],
        }
        return obligaciones.get(nivel, [])

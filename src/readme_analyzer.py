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
from prompts.system_prompts import SYSTEM_PROMPT_README


class AnalizadorReadme:
    """Analiza el README o documentación técnica de un proyecto de IA contra los requisitos del AI Act."""

    def __init__(self):
        self.client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)

    def analizar(self, contenido_readme: str) -> dict:
        """Analiza el contenido de un README y devuelve un informe de gaps."""
        respuesta = self.client.messages.create(
            model=MODEL,
            max_tokens=2048,
            system=SYSTEM_PROMPT_README,
            messages=[
                {
                    "role": "user",
                    "content": f"Analiza el siguiente README de un proyecto de IA:\n\n{contenido_readme}",
                }
            ],
        )

        texto = respuesta.content[0].text.strip()
        texto = self._limpiar_json(texto)

        try:
            return json.loads(texto)
        except json.JSONDecodeError:
            return self._resultado_error()

    def analizar_con_contexto(self, contenido_readme: str, nivel_riesgo: str) -> dict:
        """Analiza el README teniendo en cuenta el nivel de riesgo ya identificado en el chat."""
        prompt = (
            f"El sistema de IA ha sido clasificado previamente como nivel de riesgo: {nivel_riesgo}\n\n"
            f"Analiza el siguiente README considerando específicamente las obligaciones del AI Act "
            f"que aplican a sistemas de nivel {nivel_riesgo}:\n\n{contenido_readme}"
        )

        respuesta = self.client.messages.create(
            model=MODEL,
            max_tokens=2048,
            system=SYSTEM_PROMPT_README,
            messages=[{"role": "user", "content": prompt}],
        )

        texto = respuesta.content[0].text.strip()
        texto = self._limpiar_json(texto)

        try:
            return json.loads(texto)
        except json.JSONDecodeError:
            return self._resultado_error()

    def _limpiar_json(self, texto: str) -> str:
        """Extrae el JSON puro de una respuesta que puede contener bloques de código markdown."""
        if texto.startswith("```"):
            partes = texto.split("```")
            if len(partes) >= 2:
                texto = partes[1]
                if texto.startswith("json"):
                    texto = texto[4:]
        return texto.strip()

    def _resultado_error(self) -> dict:
        return {
            "nivel_riesgo": "DESCONOCIDO",
            "justificacion_riesgo": "No se pudo analizar el documento automáticamente.",
            "articulos_aplicables": [],
            "gaps": [],
            "fortalezas": [],
            "resumen": "Error en el análisis. Por favor, inténtelo de nuevo.",
        }

    def calcular_puntuacion_cumplimiento(self, analisis: dict) -> dict:
        """Calcula métricas de cumplimiento a partir del análisis de gaps."""
        gaps = analisis.get("gaps", [])
        if not gaps:
            return {"total": 0, "cumple": 0, "parcial": 0, "gap": 0, "porcentaje": 0}

        conteo = {"cumple": 0, "parcial": 0, "gap": 0}
        for item in gaps:
            estado = item.get("estado", "gap")
            if estado in conteo:
                conteo[estado] += 1

        total = len(gaps)
        puntos = conteo["cumple"] * 2 + conteo["parcial"] * 1
        puntos_max = total * 2
        porcentaje = round((puntos / puntos_max * 100) if puntos_max > 0 else 0)

        return {
            "total": total,
            "cumple": conteo["cumple"],
            "parcial": conteo["parcial"],
            "gap": conteo["gap"],
            "porcentaje": porcentaje,
        }

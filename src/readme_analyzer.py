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

from prompts.system_prompts import SYSTEM_PROMPT_README
from src.llm.provider import LLMProvider


class AnalizadorReadme:
    """Analiza documentación técnica de un proyecto de IA contra los requisitos del AI Act."""

    def __init__(self, provider: LLMProvider):
        self.provider = provider

    def analizar(self, contenido_readme: str) -> dict:
        """Analiza el contenido de un README y devuelve un informe de gaps."""
        respuesta = self.provider.chat(
            messages=[
                {
                    "role": "user",
                    "content": f"Analiza el siguiente README de un proyecto de IA:\n\n{contenido_readme}",
                }
            ],
            system_prompt=SYSTEM_PROMPT_README,
        )
        return self._parsear_respuesta(respuesta)

    def analizar_con_contexto(self, contenido_readme: str, nivel_riesgo: str) -> dict:
        """Analiza el README considerando el nivel de riesgo ya identificado en el chat."""
        prompt = (
            f"El sistema de IA ha sido clasificado como nivel de riesgo: {nivel_riesgo}\n\n"
            f"Analiza el siguiente README considerando específicamente las obligaciones "
            f"del AI Act que aplican a sistemas de nivel {nivel_riesgo}:\n\n{contenido_readme}"
        )
        respuesta = self.provider.chat(
            messages=[{"role": "user", "content": prompt}],
            system_prompt=SYSTEM_PROMPT_README,
        )
        return self._parsear_respuesta(respuesta)

    def _parsear_respuesta(self, texto: str) -> dict:
        texto = texto.strip()
        if texto.startswith("```"):
            partes = texto.split("```")
            if len(partes) >= 2:
                texto = partes[1]
                if texto.startswith("json"):
                    texto = texto[4:]
        try:
            return json.loads(texto.strip())
        except json.JSONDecodeError:
            return self._resultado_error()

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
        puntos = conteo["cumple"] * 2 + conteo["parcial"]
        puntos_max = total * 2
        porcentaje = round((puntos / puntos_max * 100) if puntos_max > 0 else 0)

        return {
            "total": total,
            "cumple": conteo["cumple"],
            "parcial": conteo["parcial"],
            "gap": conteo["gap"],
            "porcentaje": porcentaje,
        }

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

import anthropic
import json
from typing import Generator
from config import ANTHROPIC_API_KEY, MODEL
from prompts.system_prompts import SYSTEM_PROMPT_CHATBOT
from src.rag.retriever import formatear_contexto_rag


class AIComplyChat:
    """Gestiona la conversación con Claude para el análisis de cumplimiento del AI Act."""

    def __init__(self):
        self.client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)
        self.historial: list[dict] = []
        self.contexto_empresa: dict = {}
        self.nivel_riesgo: str | None = None

    def _construir_system_con_rag(self, mensaje: str) -> str:
        """Añade contexto RAG de artículos relevantes al system prompt."""
        contexto_rag = formatear_contexto_rag(mensaje, top_k=3)
        if contexto_rag:
            return f"{SYSTEM_PROMPT_CHATBOT}\n\n{contexto_rag}"
        return SYSTEM_PROMPT_CHATBOT

    def chat_stream(self, mensaje_usuario: str) -> Generator[str, None, None]:
        """Envía un mensaje y recibe la respuesta en streaming con contexto RAG."""
        self.historial.append({"role": "user", "content": mensaje_usuario})
        system_con_rag = self._construir_system_con_rag(mensaje_usuario)

        with self.client.messages.stream(
            model=MODEL,
            max_tokens=2048,
            system=system_con_rag,
            messages=self.historial,
        ) as stream:
            respuesta_completa = ""
            for texto in stream.text_stream:
                respuesta_completa += texto
                yield texto

        self.historial.append({"role": "assistant", "content": respuesta_completa})
        self._extraer_nivel_riesgo(respuesta_completa)

    def chat_completo(self, mensaje_usuario: str) -> str:
        """Envía un mensaje y recibe la respuesta completa (sin streaming)."""
        self.historial.append({"role": "user", "content": mensaje_usuario})
        system_con_rag = self._construir_system_con_rag(mensaje_usuario)

        respuesta = self.client.messages.create(
            model=MODEL,
            max_tokens=2048,
            system=system_con_rag,
            messages=self.historial,
        )

        texto_respuesta = respuesta.content[0].text
        self.historial.append({"role": "assistant", "content": texto_respuesta})
        self._extraer_nivel_riesgo(texto_respuesta)
        return texto_respuesta

    def _extraer_nivel_riesgo(self, texto: str) -> None:
        """Detecta el nivel de riesgo mencionado en la respuesta y lo persiste."""
        texto_upper = texto.upper()
        if "PROHIBIDO" in texto_upper or "RIESGO INACEPTABLE" in texto_upper:
            self.nivel_riesgo = "PROHIBIDO"
        elif "ALTO RIESGO" in texto_upper or "DE ALTO RIESGO" in texto_upper:
            self.nivel_riesgo = "ALTO"
        elif "RIESGO LIMITADO" in texto_upper:
            self.nivel_riesgo = "LIMITADO"
        elif "RIESGO MINIMO" in texto_upper or "RIESGO MÍNIMO" in texto_upper:
            self.nivel_riesgo = "MINIMO"

    def generar_resumen_conversacion(self) -> str:
        """Genera un resumen estructurado en JSON de la conversación para el informe."""
        if len(self.historial) < 2:
            return "{}"

        prompt_resumen = """Basándote en la conversación anterior, genera un resumen estructurado en JSON con:
{
  "nombre_sistema": "nombre o descripción del sistema de IA",
  "sector": "sector de la empresa",
  "proposito": "propósito principal del sistema",
  "nivel_riesgo": "PROHIBIDO|ALTO|LIMITADO|MINIMO",
  "articulos_aplicables": ["Art. X", "Art. Y"],
  "caracteristicas_clave": ["característica 1", "característica 2"],
  "obligaciones_identificadas": ["obligación 1", "obligación 2"]
}

Devuelve únicamente el JSON, sin texto adicional ni bloques de código markdown."""

        respuesta = self.client.messages.create(
            model=MODEL,
            max_tokens=1024,
            system=SYSTEM_PROMPT_CHATBOT,
            messages=self.historial + [{"role": "user", "content": prompt_resumen}],
        )

        try:
            texto = respuesta.content[0].text.strip()
            if texto.startswith("```"):
                texto = texto.split("```")[1]
                if texto.startswith("json"):
                    texto = texto[4:]
            json.loads(texto)
            return texto
        except Exception:
            return "{}"

    def resetear(self) -> None:
        """Reinicia la conversación y el estado de la sesión."""
        self.historial = []
        self.contexto_empresa = {}
        self.nivel_riesgo = None

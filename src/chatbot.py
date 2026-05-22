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
from typing import Generator

from prompts.system_prompts import SYSTEM_PROMPT_CHATBOT
from src.llm.provider import LLMProvider
from src.rag.retriever import formatear_contexto_rag

_PROMPT_RESUMEN = """Basándote en la conversación anterior, genera un resumen estructurado en JSON con:
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


class AIComplyChat:
    """Gestiona la conversación con el LLM para el análisis de cumplimiento del AI Act."""

    def __init__(self, provider: LLMProvider):
        self.provider = provider
        self.historial: list[dict] = []
        self.nivel_riesgo: str | None = None

    def _system_con_rag(self, mensaje: str) -> str:
        """Enriquece el system prompt con artículos relevantes recuperados por RAG."""
        contexto = formatear_contexto_rag(mensaje, top_k=3)
        if contexto:
            return f"{SYSTEM_PROMPT_CHATBOT}\n\n{contexto}"
        return SYSTEM_PROMPT_CHATBOT

    def chat_stream(self, mensaje_usuario: str) -> Generator[str, None, None]:
        """Envía un mensaje y produce la respuesta en streaming, actualizando el historial."""
        self.historial.append({"role": "user", "content": mensaje_usuario})
        system = self._system_con_rag(mensaje_usuario)

        respuesta_completa = ""
        for fragmento in self.provider.chat_stream(self.historial, system_prompt=system):
            respuesta_completa += fragmento
            yield fragmento

        self.historial.append({"role": "assistant", "content": respuesta_completa})
        self._extraer_nivel_riesgo(respuesta_completa)

    def chat_completo(self, mensaje_usuario: str) -> str:
        """Envía un mensaje y devuelve la respuesta completa (sin streaming)."""
        self.historial.append({"role": "user", "content": mensaje_usuario})
        system = self._system_con_rag(mensaje_usuario)

        respuesta = self.provider.chat(self.historial, system_prompt=system)
        self.historial.append({"role": "assistant", "content": respuesta})
        self._extraer_nivel_riesgo(respuesta)
        return respuesta

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

        mensajes = self.historial + [{"role": "user", "content": _PROMPT_RESUMEN}]
        texto = self.provider.chat(mensajes, system_prompt=SYSTEM_PROMPT_CHATBOT)

        try:
            texto = texto.strip()
            if texto.startswith("```"):
                partes = texto.split("```")
                texto = partes[1]
                if texto.startswith("json"):
                    texto = texto[4:]
                texto = texto.strip()
            json.loads(texto)
            return texto
        except Exception:
            return "{}"

    def resetear(self) -> None:
        """Reinicia la conversación manteniendo el provider configurado."""
        self.historial = []
        self.nivel_riesgo = None

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

# El LLM emite esta cadena al final de su respuesta cuando el árbol de decisión llega a FIN.
# La app la detecta para mostrar el botón de completar evaluación. Se elimina del historial
# persistido para que no contamine futuras llamadas al modelo.

_PROMPT_EXTRAER_CLASIFICACION = """Basándote en toda la conversación de evaluación anterior, extrae la información estructurada. Devuelve ÚNICAMENTE el siguiente JSON, sin texto adicional ni bloques de código markdown:
{
  "clasificacion": "ALTO|LIMITADO|MINIMO|PROHIBIDO|FUERA_AMBITO|PENDIENTE",
  "estados_adicionales": ["Notificar a la NCA", "Convertirse en proveedor", "GPAI con Riesgo Sistémico"],
  "rol": "proveedor|implementador|distribuidor|importador|fabricante|representante_autorizado",
  "roles_multiples": [],
  "nodos_recorridos": [
    {"nodo": "#E1", "respuesta": "Implementador", "origen": "respuesta directa|inferencia confirmada|INDETERMINADO"}
  ],
  "puntos_indeterminados": ["descripción del nodo indeterminado y qué cambiaría según la respuesta"],
  "descripcion_sistema": "descripción del sistema evaluado en 2-3 frases",
  "sector": "sector de la empresa",
  "obligaciones_preliminares": ["obligación ya identificada (Art. X)"]
}
Si la evaluación no ha llegado a una clasificación definitiva, usa "clasificacion": "PENDIENTE"."""

_PROMPT_EXTRAER_CUMPLIMIENTO = """Basándote en toda la conversación de cumplimiento anterior, extrae la información estructurada. Devuelve ÚNICAMENTE el siguiente JSON, sin texto adicional ni bloques de código markdown:
{
  "obligaciones": [
    {
      "articulo": "Art. X",
      "titulo": "nombre de la obligación",
      "descripcion": "descripción concreta para esta organización",
      "estado": "cubierta|parcial|carencia|no_evaluada"
    }
  ],
  "carencias_detectadas": ["descripción de la carencia 1", "descripción de la carencia 2"],
  "puntos_revision_profesional": ["punto que requiere revisión profesional 1"],
  "resumen_cumplimiento": "resumen ejecutivo del análisis de cumplimiento en 2-3 frases"
}"""

_SENAL_COMPLETA = "[EVALUACION_COMPLETA]"


class AIComplyChat:
    """Gestiona la conversación con el LLM para el árbol de decisión o el análisis de cumplimiento."""

    def __init__(self, provider: LLMProvider, system_prompt_override: str | None = None):
        self.provider = provider
        self.historial: list[dict] = []
        self.nivel_riesgo: str | None = None
        self.evaluacion_completa: bool = False
        self._system_prompt_override = system_prompt_override

    @property
    def _system_base(self) -> str:
        return self._system_prompt_override or SYSTEM_PROMPT_CHATBOT

    def _system_con_rag(self, mensaje: str) -> str:
        """Enriquece el system prompt base con artículos relevantes recuperados por RAG."""
        if self._system_prompt_override:
            # En el modo cumplimiento, el contexto de clasificación ya está embebido
            # en el system prompt; añadir RAG duplicaría información y diluiría el foco.
            return self._system_prompt_override
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

        # Detectar señal de evaluación completa y limpiarla del historial persistido.
        # Solo se acepta si va acompañada de un informe real (≥150 caracteres).
        # Si llega sola o con texto insignificante, se descarta para evitar
        # que el LLM "congele" el chat al emitirla prematuramente en mitad del árbol.
        if _SENAL_COMPLETA in respuesta_completa:
            texto_sin_senal = respuesta_completa.replace(_SENAL_COMPLETA, "").strip()
            if len(texto_sin_senal) >= 150:
                self.evaluacion_completa = True
            respuesta_completa = texto_sin_senal

        self.historial.append({"role": "assistant", "content": respuesta_completa})
        self._extraer_nivel_riesgo(respuesta_completa)

    def chat_completo(self, mensaje_usuario: str) -> str:
        """Envía un mensaje y devuelve la respuesta completa (sin streaming)."""
        self.historial.append({"role": "user", "content": mensaje_usuario})
        system = self._system_con_rag(mensaje_usuario)

        respuesta = self.provider.chat(self.historial, system_prompt=system)

        if _SENAL_COMPLETA in respuesta:
            self.evaluacion_completa = True
            respuesta = respuesta.replace(_SENAL_COMPLETA, "").strip()

        self.historial.append({"role": "assistant", "content": respuesta})
        self._extraer_nivel_riesgo(respuesta)
        return respuesta

    def _extraer_nivel_riesgo(self, texto: str) -> None:
        """Detecta el nivel de riesgo mencionado en la respuesta y lo persiste."""
        texto_upper = texto.upper()
        if "PROHIBIDO" in texto_upper:
            self.nivel_riesgo = "PROHIBIDO"
        elif "ALTO RIESGO" in texto_upper or "DE ALTO RIESGO" in texto_upper:
            self.nivel_riesgo = "ALTO"
        elif "RIESGO LIMITADO" in texto_upper:
            self.nivel_riesgo = "LIMITADO"
        elif "RIESGO MINIMO" in texto_upper or "RIESGO MÍNIMO" in texto_upper:
            self.nivel_riesgo = "MINIMO"

    def extraer_clasificacion(self) -> dict:
        """Extrae la clasificación estructurada de la conversación de evaluación."""
        if len(self.historial) < 2:
            return {"clasificacion": "PENDIENTE"}

        mensajes = self.historial + [{"role": "user", "content": _PROMPT_EXTRAER_CLASIFICACION}]
        texto = self.provider.chat(mensajes, system_prompt=SYSTEM_PROMPT_CHATBOT)
        return self._parsear_json(texto, {"clasificacion": "PENDIENTE"})

    def extraer_cumplimiento(self) -> dict:
        """Extrae las obligaciones y gaps de la conversación de cumplimiento."""
        if len(self.historial) < 2:
            return {"obligaciones": [], "gaps_detectados": [], "puntos_revision_profesional": []}

        mensajes = self.historial + [{"role": "user", "content": _PROMPT_EXTRAER_CUMPLIMIENTO}]
        texto = self.provider.chat(mensajes, system_prompt=self._system_base)
        return self._parsear_json(texto, {"obligaciones": [], "gaps_detectados": []})

    def _parsear_json(self, texto: str, fallback: dict) -> dict:
        texto = texto.strip()
        if texto.startswith("```"):
            partes = texto.split("```")
            if len(partes) >= 2:
                texto = partes[1]
                if texto.startswith("json"):
                    texto = texto[4:]
        try:
            return json.loads(texto.strip())
        except Exception:
            return fallback

    def resetear(self) -> None:
        """Reinicia la conversación manteniendo el provider configurado."""
        self.historial = []
        self.nivel_riesgo = None
        self.evaluacion_completa = False

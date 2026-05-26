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

import json
import logging
import re
import time
from typing import Generator

_BACKOFF_MAX = 5.0  # cap del backoff tras 429 en segundos


def _backoff_rate_limit(exc: Exception) -> float:
    """Lee Retry-After del header de la excepción; devuelve máximo _BACKOFF_MAX."""
    try:
        valor = getattr(getattr(exc, "response", None), "headers", {}).get("retry-after")
        if valor:
            return min(float(valor), _BACKOFF_MAX)
    except Exception:
        pass
    return _BACKOFF_MAX

from prompts.system_prompts import SYSTEM_PROMPT_CHATBOT
from prompts.system_prompts_local import SYSTEM_PROMPT_CHATBOT_LOCAL
from src.conversation_state import EvalState, construir_bloque_estado, procesar_respuesta
from src.llm.provider import LLMProvider
from src.rag.retriever import formatear_contexto_rag

logger = logging.getLogger(__name__)

# El LLM emite esta cadena al final de su respuesta cuando el árbol de decisión llega a FIN.
# La app la detecta para mostrar el botón de completar evaluación. Se elimina del historial
# persistido para que no contamine futuras llamadas al modelo.

_SYSTEM_EXTRACTION = (
    "Eres un extractor de información estructurada. "
    "Lee la conversación y devuelve ÚNICAMENTE JSON válido, sin texto adicional ni bloques de código markdown."
)

_PROMPT_EXTRAER_CLASIFICACION = """Basándote en toda la conversación de evaluación anterior, extrae la información estructurada. Devuelve ÚNICAMENTE el siguiente JSON, sin texto adicional ni bloques de código markdown:
{
  "clasificacion": "ALTO|LIMITADO|MINIMO|PROHIBIDO|NO CUMPLE LA DEFINICIÓN DE SISTEMA DE IA|EXCLUIDO|PENDIENTE",
  "estados_adicionales": ["Notificar a la NCA", "Convertirse en proveedor", "GPAI con Riesgo Sistémico"],
  "rol": "proveedor|implementador|distribuidor|importador|fabricante|representante_autorizado",
  "roles_multiples": [],
  "nodos_recorridos": [
    {"pregunta": "Tipo de entidad", "respuesta": "Implementador", "origen": "respuesta directa|inferencia confirmada|INDETERMINADO"}
  ],
  "puntos_indeterminados": ["descripción del punto indeterminado y qué cambiaría según la respuesta"],
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

    def __init__(
        self,
        provider: LLMProvider,
        system_prompt_override: str | None = None,
        max_historial: int = 10,
    ):
        self.provider = provider
        self.historial: list[dict] = []
        self.nivel_riesgo: str | None = None
        self.evaluacion_completa: bool = False
        self._system_prompt_override = system_prompt_override
        self._max_historial = max_historial
        # Solo para el evaluador (sin override). El chatbot de cumplimiento no usa estado.
        self._eval_state: EvalState | None = EvalState() if system_prompt_override is None else None

    @property
    def _system_base(self) -> str:
        return self._system_prompt_override or SYSTEM_PROMPT_CHATBOT

    def _system_con_rag(self, mensaje: str) -> str:
        """Devuelve el system prompt adecuado al provider.

        - Con override (cumplimiento): usa el override siempre, sin RAG.
        - Sin override (evaluador): enriquece el prompt base con el contexto
          RAG recuperado para el mensaje actual. Si el RAG devuelve vacío o
          lanza una excepción, usa el prompt base sin modificar.
        - Con Ollama (local): usa el prompt compacto para reducir tokens.
        - Con APIs en la nube: usa el prompt completo.
        """
        if self._system_prompt_override:
            return self._system_prompt_override

        base = SYSTEM_PROMPT_CHATBOT_LOCAL if self.provider.es_local else SYSTEM_PROMPT_CHATBOT

        try:
            contexto = formatear_contexto_rag(mensaje, top_k=3)
        except Exception:
            logger.warning("Error al recuperar contexto RAG; continuando sin él.", exc_info=True)
            contexto = ""

        if contexto:
            prompt = (
                base
                + "\n\n---\nCONTEXTO NORMATIVO RECUPERADO PARA ESTA CONSULTA:\n"
                + contexto
                + "\n---\nUsa este contexto cuando respondas sobre artículos concretos, "
                "pero NO copies literalmente: cítalo como referencia y mantén el "
                "lenguaje accesible para PYME."
            )
        else:
            prompt = base

        if self._eval_state is not None:
            prompt += "\n\n" + construir_bloque_estado(self._eval_state)

        return prompt

    def _historial_truncado(self, max_mensajes: int | None = None) -> list[dict]:
        """Recorta el historial para no superar el límite de tokens de la API.

        Conserva siempre los dos primeros mensajes (descripción inicial del sistema)
        y los (max_mensajes-2) más recientes para mantener el contexto inmediato.
        """
        limite = max_mensajes if max_mensajes is not None else self._max_historial
        if len(self.historial) <= limite:
            return self.historial
        primeros = self.historial[:2]
        resto = self.historial[-(limite - 2):]
        # Garantizar que el primer mensaje del bloque reciente sea del usuario
        while resto and resto[0]["role"] != "user":
            resto = resto[1:]
        return primeros + resto

    def chat_stream(self, mensaje_usuario: str) -> Generator[str, None, None]:
        """Envía un mensaje y produce la respuesta en streaming, actualizando el historial."""
        self.historial.append({"role": "user", "content": mensaje_usuario})
        system = self._system_con_rag(mensaje_usuario)

        respuesta_completa = ""
        _completado = False
        try:
            for fragmento in self.provider.chat_stream(self._historial_truncado(), system_prompt=system):
                respuesta_completa += fragmento
                yield fragmento
            _completado = True
        except Exception as exc:
            # Retry automático tras 429 (rate limit): respetar Retry-After, máx 5 s.
            if "429" in str(exc) or "rate_limit" in str(exc).lower():
                time.sleep(_backoff_rate_limit(exc))
                respuesta_completa = self.provider.chat(
                    self._historial_truncado(), system_prompt=system
                )
                yield respuesta_completa
                _completado = True
            else:
                # Rollback: el historial no debe quedar con un user sin assistant.
                self.historial.pop()
                raise
        finally:
            # Si el stream fue interrumpido (StopException, GeneratorExit, etc.)
            # antes de completarse, limpiar el historial para evitar dos mensajes
            # de usuario consecutivos en la siguiente llamada a la API.
            if not _completado and self.historial and self.historial[-1]["role"] == "user":
                if respuesta_completa:
                    # Guardar la respuesta parcial para no perder el contexto
                    self.historial.append({"role": "assistant", "content": respuesta_completa})
                    self._extraer_nivel_riesgo(respuesta_completa)
                else:
                    # Sin respuesta parcial: rollback del mensaje de usuario
                    self.historial.pop()

        if not _completado:
            return

        # Detectar señal de evaluación completa y limpiarla del historial persistido.
        # Solo se acepta si va acompañada de un informe real (≥150 caracteres).
        # Si llega sola o con texto insignificante, se descarta para evitar
        # que el LLM "congele" el chat al emitirla prematuramente en mitad del árbol.
        if self._eval_state is not None:
            respuesta_completa, self._eval_state = procesar_respuesta(respuesta_completa, self._eval_state)
            if self._eval_state.evaluacion_completa:
                self.evaluacion_completa = True
        elif _SENAL_COMPLETA in respuesta_completa:
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

        try:
            respuesta = self.provider.chat(self._historial_truncado(), system_prompt=system)
        except Exception:
            self.historial.pop()
            raise

        if self._eval_state is not None:
            respuesta, self._eval_state = procesar_respuesta(respuesta, self._eval_state)
            if self._eval_state.evaluacion_completa:
                self.evaluacion_completa = True
        elif _SENAL_COMPLETA in respuesta:
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
        texto = self.provider.chat(mensajes, system_prompt=_SYSTEM_EXTRACTION)
        return self._parsear_json(texto, {"clasificacion": "PENDIENTE"})

    def extraer_cumplimiento(self) -> dict:
        """Extrae las obligaciones y gaps de la conversación de cumplimiento."""
        if len(self.historial) < 2:
            return {"obligaciones": [], "carencias_detectadas": [], "puntos_revision_profesional": []}

        mensajes = self.historial + [{"role": "user", "content": _PROMPT_EXTRAER_CUMPLIMIENTO}]
        texto = self.provider.chat(mensajes, system_prompt=_SYSTEM_EXTRACTION)
        return self._parsear_json(texto, {"obligaciones": [], "carencias_detectadas": []})

    def _parsear_json(self, texto: str, fallback: dict) -> dict:
        texto = texto.strip()
        # Strip markdown code fences
        if texto.startswith("```"):
            partes = texto.split("```")
            if len(partes) >= 2:
                texto = partes[1]
                if texto.startswith("json"):
                    texto = texto[4:]
        texto = texto.strip()
        try:
            return json.loads(texto)
        except Exception:
            # Last resort: find the first JSON object anywhere in the response
            match = re.search(r"\{[\s\S]*\}", texto)
            if match:
                try:
                    return json.loads(match.group())
                except Exception:
                    pass
            return fallback

    def resetear(self) -> None:
        """Reinicia la conversación manteniendo el provider configurado."""
        self.historial = []
        self.nivel_riesgo = None
        self.evaluacion_completa = False
        if self._eval_state is not None:
            self._eval_state = EvalState()

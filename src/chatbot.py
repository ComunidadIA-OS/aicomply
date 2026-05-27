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
  "rol": "todos los roles identificados, separados por ' / ' cuando hay varios (p. ej. 'proveedor / implementador')",
  "roles_multiples": ["proveedor", "implementador"],
  "nodos_recorridos": [
    {"pregunta": "Tipo de entidad", "respuesta": "Implementador", "origen": "respuesta directa|inferencia confirmada|INDETERMINADO"}
  ],
  "puntos_indeterminados": ["descripción del punto indeterminado y qué cambiaría según la respuesta"],
  "descripcion_sistema": "descripción del sistema evaluado en 2-3 frases",
  "sector": "sector de la empresa",
  "obligaciones_preliminares": ["obligación ya identificada (Art. X)"]
}
REGLA OBLIGATORIA PARA roles_multiples: Lista TODOS los roles identificados como array.
- Si la organización ha desarrollado o encargado el sistema Y lo utiliza internamente bajo su propia autoridad, incluye AMBOS: ["proveedor", "implementador"]. El campo "rol" debe reflejar los mismos roles: "proveedor / implementador".
- Si solo aplica un rol, incluye únicamente ese: p. ej. ["implementador"]. El campo "rol" = "implementador".
- NUNCA dejes roles_multiples vacío; como mínimo contiene el rol identificado.
Si la evaluación no ha llegado a una clasificación definitiva, usa "clasificacion": "PENDIENTE"."""

_PROMPT_EXTRAER_CUMPLIMIENTO = """Basándote en toda la conversación de cumplimiento anterior, extrae la información estructurada. Devuelve ÚNICAMENTE el siguiente JSON, sin texto adicional ni bloques de código markdown:
{
  "obligaciones": [
    {
      "articulo": "Art. X",
      "titulo": "nombre de la obligación",
      "descripcion": "descripción concreta para esta organización",
      "estado": "cubierta|parcial|carencia|no_aplica",
      "tipo": "obligacion|recomendacion|vigilancia"
    }
  ],
  "carencias_detectadas": ["descripción de la carencia 1"],
  "puntos_revision_profesional": ["punto que requiere revisión profesional 1"],
  "resumen_cumplimiento": "resumen ejecutivo del análisis de cumplimiento en 2-3 frases"
}
El campo "tipo" es obligatorio en cada elemento:
- "obligacion": exigible legalmente por el AI Act u otra normativa aplicable (p. ej. Art. 4, Art. 9-17, Art. 26, Art. 50.1).
- "recomendacion": voluntaria, no exigible (p. ej. Art. 95 — adhesión a códigos de conducta, documentación interna voluntaria).
- "vigilancia": medida prudencial de seguimiento, no es obligación autónoma (p. ej. vigilar cambios de uso que puedan elevar el nivel de riesgo).
Solo las obligaciones de tipo "obligacion" computan en el porcentaje de cumplimiento legal.
Para elementos de tipo "recomendacion" o "vigilancia" no adoptados usa estado "carencia", pero no los incluyas en "carencias_detectadas"."""

_SENAL_COMPLETA = "[EVALUACION_COMPLETA]"

_RE_BLOQUE_OBLIGACION = re.compile(r"<<<OBLIGACION>>>(.+?)<<<FIN>>>", re.DOTALL)
_RE_BLOQUE_CIERRE     = re.compile(r"<<<CIERRE>>>(.+?)<<<FIN>>>",     re.DOTALL)
_RE_REGISTRADO = re.compile(
    r"Registrado:\s*(?P<art>Art\.?\s*[\w.\-]+)\s*[—\-:]\s*(?P<titulo>[^:]+?):\s*"
    r"(?P<estado>CUBIERTA|PARCIAL|CARENCIA|NO[_ ]?CUBIERTA|NO[_ ]?APLICA)",
    re.IGNORECASE,
)
_NORM_ESTADO = {
    "cubierta": "cubierta",
    "parcial": "parcial",
    "carencia": "carencia",
    "no cubierta": "carencia",
    "no_cubierta": "carencia",
    "no aplica": "no_aplica",
    "no_aplica": "no_aplica",
}


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
        self.obligaciones_registradas: list[dict] = []
        self.carencias_registradas: list[str] = []
        self.puntos_revision_registrados: list[str] = []
        self.resumen_cumplimiento_registrado: str = ""

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
            return base

        if not contexto:
            return base

        return (
            base
            + "\n\n---\nCONTEXTO NORMATIVO RECUPERADO PARA ESTA CONSULTA:\n"
            + contexto
            + "\n---\nUsa este contexto cuando respondas sobre artículos concretos, "
            "pero NO copies literalmente: cítalo como referencia y mantén el "
            "lenguaje accesible para PYME."
        )

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

    def _procesar_bloques(self, texto: str) -> str:
        """Extrae bloques machine-readable del texto, persiste su contenido y devuelve texto limpio."""
        for m in _RE_BLOQUE_OBLIGACION.finditer(texto):
            try:
                obl = json.loads(m.group(1))
                if "articulo" not in obl or "estado" not in obl:
                    continue
                key = (obl.get("articulo", ""), obl.get("titulo", ""))
                self.obligaciones_registradas = [
                    o for o in self.obligaciones_registradas
                    if (o.get("articulo", ""), o.get("titulo", "")) != key
                ]
                self.obligaciones_registradas.append(obl)
            except Exception:
                logger.warning("Bloque OBLIGACION malformado; ignorado.", exc_info=True)

        for m in _RE_BLOQUE_CIERRE.finditer(texto):
            try:
                cierre = json.loads(m.group(1))
                self.resumen_cumplimiento_registrado = (
                    cierre.get("resumen") or self.resumen_cumplimiento_registrado
                )
                for c in cierre.get("carencias", []):
                    if c and c not in self.carencias_registradas:
                        self.carencias_registradas.append(c)
                for p in cierre.get("puntos_revision", []):
                    if p and p not in self.puntos_revision_registrados:
                        self.puntos_revision_registrados.append(p)
                break
            except Exception:
                logger.warning("Bloque CIERRE malformado; ignorado.", exc_info=True)

        texto_limpio = _RE_BLOQUE_OBLIGACION.sub("", texto)
        texto_limpio = _RE_BLOQUE_CIERRE.sub("", texto_limpio)
        return texto_limpio.rstrip()

    def chat_stream(self, mensaje_usuario: str) -> Generator[str, None, None]:
        """Envía un mensaje y produce la respuesta en streaming, actualizando el historial."""
        self.historial.append({"role": "user", "content": mensaje_usuario})
        system = self._system_con_rag(mensaje_usuario)

        respuesta_completa = ""
        try:
            for fragmento in self.provider.chat_stream(self._historial_truncado(), system_prompt=system):
                respuesta_completa += fragmento
                yield fragmento
        except Exception as exc:
            # Retry automático tras 429 (rate limit): respetar Retry-After, máx 5 s.
            if "429" in str(exc) or "rate_limit" in str(exc).lower():
                time.sleep(_backoff_rate_limit(exc))
                respuesta_completa = self.provider.chat(
                    self._historial_truncado(), system_prompt=system
                )
                yield respuesta_completa
            else:
                # Rollback: el historial no debe quedar con un user sin assistant.
                self.historial.pop()
                raise

        respuesta_completa = self._procesar_bloques(respuesta_completa)

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

        try:
            respuesta = self.provider.chat(self._historial_truncado(), system_prompt=system)
        except Exception:
            self.historial.pop()
            raise

        respuesta = self._procesar_bloques(respuesta)

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

    _ROLES_VALIDOS = frozenset({
        "proveedor", "implementador", "distribuidor",
        "importador", "fabricante", "representante_autorizado",
    })
    _ALIAS_ROLES = {"provider": "proveedor", "deployer": "implementador"}
    _SEP_ROLES = re.compile(r"\s*/\s*|\s+[ey]\s+|\s*,\s*|_")

    @classmethod
    def _normalizar_clasificacion_data(cls, datos: dict) -> dict:
        """Garantiza coherencia entre 'rol' y 'roles_multiples'.

        - Detecta roles combinados en el campo 'rol' (p. ej. "proveedor / implementador")
          y los expande en 'roles_multiples' si este viene vacío.
        - Asegura que 'roles_multiples' contiene como mínimo el rol indicado en 'rol'.
        - Deduplica 'roles_multiples' preservando el orden.
        - NO reduce 'rol' a un único valor: si el LLM emitió "proveedor / implementador",
          se conserva así para que los renderers de UI e informe muestren todos los roles.
        """
        rol_raw = (datos.get("rol") or "").strip()
        partes = [
            cls._ALIAS_ROLES.get(p, p)
            for p in cls._SEP_ROLES.split(rol_raw.lower())
            if p.strip()
        ]
        partes_validas = [p for p in partes if p in cls._ROLES_VALIDOS]

        roles_m = [r.strip().lower() for r in datos.get("roles_multiples", []) if r.strip()]
        roles_m_validos = [r for r in roles_m if r in cls._ROLES_VALIDOS]

        if not roles_m_validos:
            # Poblar desde 'rol' si no vino lista
            roles_m_validos = partes_validas if partes_validas else roles_m

        # Deduplicar preservando orden
        seen: set[str] = set()
        roles_dedup = []
        for r in roles_m_validos:
            if r not in seen:
                seen.add(r)
                roles_dedup.append(r)

        # Si 'rol' venía como valor único pero roles_dedup tiene varios, reconstruir 'rol'
        if len(roles_dedup) > 1 and len(partes_validas) <= 1:
            datos = {**datos, "rol": " / ".join(roles_dedup)}

        datos["roles_multiples"] = roles_dedup
        return datos

    def extraer_clasificacion(self) -> dict:
        """Extrae la clasificación estructurada de la conversación de evaluación."""
        if len(self.historial) < 2:
            return {"clasificacion": "PENDIENTE"}

        mensajes = self.historial + [{"role": "user", "content": _PROMPT_EXTRAER_CLASIFICACION}]
        texto = self.provider.chat(mensajes, system_prompt=_SYSTEM_EXTRACTION)
        datos = self._parsear_json(texto, {"clasificacion": "PENDIENTE"})
        return self._normalizar_clasificacion_data(datos)

    def extraer_cumplimiento(self) -> dict:
        """Devuelve la estructura de cumplimiento construida incrementalmente.

        La fuente de verdad son los bloques <<<OBLIGACION>>> y <<<CIERRE>>> capturados
        turno a turno por _procesar_bloques. Solo llama al LLM si no hay registros.
        """
        if self.obligaciones_registradas:
            return {
                "obligaciones": list(self.obligaciones_registradas),
                "carencias_detectadas": list(self.carencias_registradas),
                "puntos_revision_profesional": list(self.puntos_revision_registrados),
                "resumen_cumplimiento": self.resumen_cumplimiento_registrado or "",
            }

        resultado_fallback = self._extraer_cumplimiento_legacy()
        if not resultado_fallback.get("obligaciones"):
            reconstruido = self._reconstruir_obligaciones_desde_historial()
            if reconstruido:
                resultado_fallback["obligaciones"] = reconstruido
        return resultado_fallback

    def _extraer_cumplimiento_legacy(self) -> dict:
        """Extracción clásica: pide al LLM que derife el JSON del historial completo."""
        if len(self.historial) < 2:
            return {"obligaciones": [], "carencias_detectadas": [], "puntos_revision_profesional": []}

        mensajes = self.historial + [{"role": "user", "content": _PROMPT_EXTRAER_CUMPLIMIENTO}]
        texto = self.provider.chat(mensajes, system_prompt=_SYSTEM_EXTRACTION)
        return self._parsear_json(texto, {"obligaciones": [], "carencias_detectadas": []})

    def _reconstruir_obligaciones_desde_historial(self) -> list[dict]:
        """Último recurso: busca en el historial líneas 'Registrado: Art. X — Título: ESTADO'."""
        reconstruidas: dict[tuple, dict] = {}
        for msg in self.historial:
            if msg.get("role") != "assistant":
                continue
            for m in _RE_REGISTRADO.finditer(msg.get("content", "")):
                estado_raw = m.group("estado").lower().replace(" ", "_")
                estado = _NORM_ESTADO.get(estado_raw.replace("_", " "), estado_raw)
                art = m.group("art").strip()
                titulo = m.group("titulo").strip()
                key = (art, titulo)
                reconstruidas[key] = {
                    "articulo": art,
                    "titulo": titulo,
                    "estado": estado,
                    "tipo": "obligacion",
                    "descripcion": "",
                    "rol": "",
                }
        return list(reconstruidas.values())

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
        self.obligaciones_registradas = []
        self.carencias_registradas = []
        self.puntos_revision_registrados = []
        self.resumen_cumplimiento_registrado = ""

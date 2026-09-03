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

from __future__ import annotations

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
from src.calendario import aplicar_calendario
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
  "rol": "los roles confirmados en la conversación, separados por ' / ' cuando hay más de uno",
  "roles_multiples": ["implementador"],
  "nodos_recorridos": [
    {"pregunta": "Tipo de entidad", "respuesta": "Implementador", "origen": "respuesta directa|inferencia confirmada|INDETERMINADO"}
  ],
  "puntos_indeterminados": ["descripción del punto indeterminado y qué cambiaría según la respuesta"],
  "descripcion_sistema": "descripción del sistema evaluado en 2-3 frases",
  "sector": "sector de la empresa",
  "obligaciones_preliminares": ["obligación ya identificada (Art. X)"]
}
REGLA OBLIGATORIA PARA obligaciones_preliminares: cita el ARTÍCULO, nunca el apartado. Escribe "(Art. 26)", nunca "(Art. 26.1)" ni "(Art. 26.3)". Esta lista es preliminar; la precisión de apartado la aporta después el análisis de cumplimiento, y un apartado equivocado aquí contradice ese análisis dentro del mismo informe.
REGLA OBLIGATORIA PARA roles_multiples: lista los roles que la conversación CONFIRMÓ, y solo esos. Tienes la conversación entera delante: un rol cuenta como confirmado cuando la persona lo respondió o aceptó una inferencia sobre él, no cuando resulte plausible por el sector, por la clasificación o por el tipo de sistema.
- Si la organización ha desarrollado o encargado el sistema Y lo utiliza internamente bajo su propia autoridad, incluye AMBOS: ["proveedor", "implementador"]. El campo "rol" debe reflejar los mismos roles: "proveedor / implementador". Las dos condiciones tienen que constar en la conversación; una sola no basta.
- Si solo consta un rol, incluye únicamente ese: p. ej. ["implementador"]. El campo "rol" = "implementador".
- NO AÑADAS un rol que la conversación no confirmara. En particular, si la persona dijo que adquirió el sistema de un tercero y que no lo modifica, "proveedor" NO va en la lista: el rol es el que se determinó al preguntar por el tipo de entidad, y las modificaciones del Art. 25 se cerraron sin activarlo.
- Ante la duda entre uno y dos roles, emite el que la conversación confirme. Añadir un rol de más multiplica las obligaciones que se atribuyen a la organización; quedarse corto es un error menor que pasarse.
- NUNCA dejes roles_multiples vacío; como mínimo contiene el rol identificado.
REGLA OBLIGATORIA PARA nodos_recorridos: la "respuesta" de cada fila reproduce lo que la persona respondió en esa pregunta. No escribas en ella una justificación de un rol que la conversación no dé, ni añadas a la fila de las modificaciones del Art. 25 un motivo que respalde un rol distinto del registrado en "Tipo de entidad".
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

_ESTADOS_VALIDOS = frozenset({"cubierta", "parcial", "carencia", "no_aplica"})

MARCADOR_OBLIGACIONES = "{OBLIGACIONES_REGISTRADAS}"

# Estados ordenados de menor a mayor cumplimiento aparente. Solo se usa para clasificar
# la dirección de una recalificación; ver _registrar_conflicto.
_ORDEN_ESTADO = {"carencia": 0, "parcial": 1, "cubierta": 2, "no_aplica": 3}


def _normalizar_estado(valor: object) -> str | None:
    """Devuelve el estado en su forma canónica, o None si no es reconocible.

    Tolera las variantes contra las que advierte el prompt (mayúsculas, "no_cubierta",
    espacios en vez de guiones bajos). Un estado sin normalizar no es inocuo: el informe
    mete cualquier valor desconocido en "no aplica" y lo saca del denominador, así que
    una sola CARENCIA en mayúsculas sube el grado de cumplimiento de portada en silencio.
    """
    bruto = str(valor).strip().lower().replace("_", " ")
    estado = _NORM_ESTADO.get(bruto)
    return estado if estado in _ESTADOS_VALIDOS else None


def _clave_obligacion(obl: dict) -> tuple[str, str, str]:
    """Identidad de una obligación: artículo, título y rol.

    El rol forma parte de la clave porque el catálogo repite artículos entre roles: el
    Art. 49 aparece bajo Proveedor y bajo Implementador, y el "titulo" que emite el modelo
    es un nombre breve que puede coincidir en ambos. Sin el rol, en un caso de doble rol la
    segunda entrada machacaría a la primera y la diferencia de estado entre roles se leería
    como una recalificación que no ha ocurrido.
    """
    return (obl.get("articulo", ""), obl.get("titulo", ""), obl.get("rol", ""))


def formatear_obligaciones_registradas(obligaciones: list[dict]) -> str:
    """Formatea el registro de obligaciones ya evaluadas para inyectarlo en el prompt.

    Es la memoria del análisis, y sobrevive a la truncación del historial. Sin ella el
    modelo solo dispone de la ventana que le deja _historial_truncado(), que en un recorrido
    de 22 obligaciones deja fuera las primeras: creía no haberlas evaluado y las repreguntaba.
    """
    if not obligaciones:
        return (
            "REGISTRO DE OBLIGACIONES YA EVALUADAS EN ESTE ANÁLISIS:\n"
            "Todavía no se ha registrado ninguna obligación; el análisis empieza por la primera."
        )

    lineas = [
        f"REGISTRO DE OBLIGACIONES YA EVALUADAS EN ESTE ANÁLISIS "
        f"({len(obligaciones)} registradas):"
    ]
    for i, obl in enumerate(obligaciones, start=1):
        rol = obl.get("rol", "")
        etiqueta_rol = f" [{rol}]" if rol else ""
        lineas.append(
            f"{i:2d}. {obl.get('articulo', '?')} — {obl.get('titulo', '')}{etiqueta_rol}: "
            f"{str(obl.get('estado', '')).upper()}"
        )
    lineas += [
        "",
        "Esta lista la mantiene la aplicación a partir de los bloques <<<OBLIGACION>>> que has "
        "emitido: es completa y fiable. El historial de la conversación puede estar recortado; "
        "esta lista no.",
    ]
    return "\n".join(lineas)


def aplicar_obligaciones_registradas(texto: str, obligaciones: list[dict]) -> str:
    """Sustituye el marcador {OBLIGACIONES_REGISTRADAS} por el registro formateado.

    Usa .replace() y NUNCA .format(), por la misma razón que aplicar_calendario: los prompts
    contienen llaves literales en el bloque machine-readable <<<OBLIGACION>>>{...}.
    """
    return texto.replace(MARCADOR_OBLIGACIONES, formatear_obligaciones_registradas(obligaciones))


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
        self.conflictos_registrados: list[dict] = []
        self.resumen_cumplimiento_registrado: str = ""
        self.ultima_respuesta_truncada: bool = False

    @property
    def _system_base(self) -> str:
        return aplicar_calendario(self._system_prompt_override or SYSTEM_PROMPT_CHATBOT)

    def _system_con_rag(self, mensaje: str) -> str:
        """Devuelve el system prompt adecuado al provider.

        - Con override (cumplimiento): usa el override siempre, sin RAG.
        - Sin override (evaluador): enriquece el prompt base con el contexto
          RAG recuperado para el mensaje actual. Si el RAG devuelve vacío o
          lanza una excepción, usa el prompt base sin modificar.
        - Con Ollama (local): usa el prompt compacto para reducir tokens.
        - Con APIs en la nube: usa el prompt completo.

        El calendario normativo se inyecta SIEMPRE y fuera del try/except del RAG:
        el contexto recuperado es opcional y su ausencia solo degrada la respuesta,
        pero un prompt sin fechas de aplicación produce información jurídica falsa.
        Si el calendario no se puede cargar, la excepción propaga.

        El registro de obligaciones se inyecta también en cada turno, y por eso el marcador
        va al final del prompt: es el único bloque que cambia turno a turno, así que dejarlo
        detrás mantiene estable todo el prefijo. Hoy no se usa prompt caching, pero si algún
        día se añade, ese es el orden que lo hace aprovechable.
        """
        if self._system_prompt_override:
            prompt = aplicar_calendario(self._system_prompt_override)
            return aplicar_obligaciones_registradas(prompt, self.obligaciones_registradas)

        base = SYSTEM_PROMPT_CHATBOT_LOCAL if self.provider.es_local else SYSTEM_PROMPT_CHATBOT
        base = aplicar_calendario(base)
        base = aplicar_obligaciones_registradas(base, self.obligaciones_registradas)

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

    def _registrar_conflicto(self, previa: dict, nueva: dict) -> None:
        """Anota la recalificación de una obligación ya registrada.

        Gana el estado más reciente: la última respuesta del usuario es su mejor respuesta, y
        bloquearla le impediría corregir al alza desde el chat. Lo que no puede ocurrir —y era
        el fallo— es que gane en silencio.

        "mejora" marca los conflictos que se escalan a revisión profesional: los que inflan el
        numerador o alteran el denominador del grado de cumplimiento que calcula
        src/report_generator.py. No equivale a "sube el porcentaje": cubierta → no_aplica lo
        baja, porque retira del cálculo una obligación con crédito completo, y aun así se
        escala, porque reclasificar algo como no aplicable es un juicio jurídico. Un cambio a
        peor es el usuario admitiendo una laguna y no necesita revisión: escalarlos todos
        llenaría la sección de avisos inocuos hasta dejarla sin significado.
        """
        anterior = str(previa.get("estado", ""))
        nuevo = str(nueva.get("estado", ""))
        if anterior == nuevo:
            return
        self.conflictos_registrados.append({
            "articulo": nueva.get("articulo", ""),
            "titulo": nueva.get("titulo", ""),
            "rol": nueva.get("rol", ""),
            "estado_anterior": anterior,
            "estado_nuevo": nuevo,
            "turno": sum(1 for m in self.historial if m.get("role") == "assistant") + 1,
            "mejora": _ORDEN_ESTADO.get(nuevo, -1) > _ORDEN_ESTADO.get(anterior, -1),
        })

    def _procesar_bloques(self, texto: str) -> str:
        """Extrae bloques machine-readable del texto, persiste su contenido y devuelve texto limpio."""
        for m in _RE_BLOQUE_OBLIGACION.finditer(texto):
            try:
                obl = json.loads(m.group(1))
                if "articulo" not in obl or "estado" not in obl:
                    continue
                # Un estado que el informe no sabe interpretar es peor que una obligación
                # ausente: la ausencia se nota, el estado inválido infla el porcentaje.
                estado = _normalizar_estado(obl["estado"])
                if estado is None:
                    logger.warning(
                        "Bloque OBLIGACION con estado no reconocido (%r); ignorado.",
                        obl.get("estado"),
                    )
                    continue
                obl["estado"] = estado
                clave = _clave_obligacion(obl)
                previa = next(
                    (o for o in self.obligaciones_registradas if _clave_obligacion(o) == clave),
                    None,
                )
                if previa is not None:
                    self._registrar_conflicto(previa, obl)
                    self.obligaciones_registradas = [
                        o for o in self.obligaciones_registradas
                        if _clave_obligacion(o) != clave
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

    def _leer_truncacion(self) -> None:
        """Recoge del provider si la última respuesta se cortó por agotar max_tokens.

        getattr con retroceso porque los providers de test son duck-typed y no heredan del ABC.
        """
        self.ultima_respuesta_truncada = bool(
            getattr(self.provider, "ultima_respuesta_truncada", False)
        )

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

        self._leer_truncacion()
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

        self._leer_truncacion()
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

    # Recorta el apartado SOLO del Art. 26: "Art. 26.3" → "Art. 26".
    _RE_APARTADO_ART_26 = re.compile(r"(Art\.?\s*26)(?:\.\d+)+", re.IGNORECASE)

    @classmethod
    def _normalizar_obligaciones_preliminares(cls, datos: dict) -> dict:
        """Quita el apartado a las obligaciones preliminares del Art. 26.

        El evaluador citaba apartados equivocados —supervisión humana como Art. 26.1
        cuando es 26.2, conservación de registros como 26.5 cuando es 26.6— y el informe
        acababa con dos numeraciones distintas para las mismas obligaciones: la de esta
        lista y la del análisis de cumplimiento, que sí las cita bien. Además la lista se
        inyecta en el prompt de esa fase siguiente (_formatear_contexto_evaluacion), así
        que el error no solo se imprimía: se propagaba.

        El recorte es SELECTIVO a propósito, no lo generalices:
        - El Art. 26 tiene once apartados parecidos entre sí, es donde se observó el fallo,
          y su precisión aquí es redundante porque el análisis de cumplimiento la da bien.
        - "Art. 50.1" → "Art. 50" perdería información real: los cuatro apartados del
          Art. 50 son obligaciones distintas y de roles distintos.
        - "Art. 5.1.g" → "Art. 5" sería peor todavía: en un informe PROHIBIDO, qué letra
          del Art. 5 aplica es el dato más importante del documento.

        El prompt de extracción ya pide citar solo el artículo; esto es la red, porque una
        instrucción al modelo es orientativa y el código es determinista.
        """
        preliminares = datos.get("obligaciones_preliminares")
        if not isinstance(preliminares, list):
            return datos
        datos["obligaciones_preliminares"] = [
            cls._RE_APARTADO_ART_26.sub(r"\1", ob) if isinstance(ob, str) else ob
            for ob in preliminares
        ]
        return datos

    @classmethod
    def _reconciliar_rol(
        cls, rol_raw: str, partes_validas: list[str], roles: list[str]
    ) -> str | None:
        """Corrige 'rol' cuando trae roles que 'roles_multiples' no tiene. None si coinciden.

        Los dos campos alimentan partes distintas del informe: la cabecera y la portada del
        PDF se imprimen desde 'rol', y las obligaciones se construyen desde 'roles_multiples'
        (_roles_plan, en report_generator, prefiere el array). Sin reconciliar, un desacuerdo
        produce un documento que se contradice a sí mismo: encabezado con dos roles y un solo
        bloque de obligaciones.

        Se estrecha hacia 'roles_multiples' —el array explícito que gobierna la regla del
        prompt de extracción— y no al revés: ensanchar codificaría en el código el fallo B15,
        que es añadir un rol ante la duda. El ensanchado que sí se conserva en la función
        llamante es otro caso, el de 'rol' simple con un array más ancho, donde los campos no
        se contradicen porque 'rol' no afirma nada que el array niegue.

        La discrepancia no se estrecha en silencio: que los dos campos no coincidan significa
        que el modelo se ha contradicho sobre el dato más consecuente de la evaluación —el rol
        determina el catálogo entero—, y hoy no sabemos con qué frecuencia ocurre. Se registra
        como warning y no como punto de revisión profesional del informe: al usuario "los dos
        campos internos de rol no coincidían" no le dice nada accionable.
        """
        sobrantes = [p for p in partes_validas if p not in roles]
        if not sobrantes or not roles:
            return None
        rol_estrecho = " / ".join(roles)
        logger.warning(
            "Discrepancia de rol en la extracción: 'rol'=%r aporta %s que no está en "
            "'roles_multiples'=%s. Se conserva 'roles_multiples' y 'rol' pasa a %r.",
            rol_raw, sobrantes, roles, rol_estrecho,
        )
        return rol_estrecho

    @classmethod
    def _normalizar_clasificacion_data(cls, datos: dict) -> dict:
        """Garantiza coherencia entre 'rol' y 'roles_multiples'.

        - Detecta roles combinados en el campo 'rol' (p. ej. "proveedor / implementador")
          y los expande en 'roles_multiples' si este viene vacío.
        - Asegura que 'roles_multiples' contiene como mínimo el rol indicado en 'rol'.
        - Deduplica 'roles_multiples' preservando el orden.
        - NO reduce 'rol' a un único valor cuando los dos campos concuerdan: si el LLM emitió
          "proveedor / implementador" y el array dice lo mismo, se conserva así para que los
          renderers de UI e informe muestren todos los roles.
        - Reconcilia los dos campos cuando SÍ discrepan: 'rol' pasa a contener exactamente los
          roles de 'roles_multiples'. Ver _reconciliar_rol.
        - Delega en _normalizar_obligaciones_preliminares el recorte del apartado del
          Art. 26 en 'obligaciones_preliminares'.

        Lo que esta función NO hace, deliberadamente: comprobar si el modelo se ha inventado
        un rol (hallazgo B15). No hay señal fiable para ello y no debe añadirse una. La única
        traza que llega hasta aquí es 'nodos_recorridos', que emite el mismo modelo en la
        misma llamada: en B15 ya venía contaminada ("Tipo de entidad: Proveedor e
        Implementador"), así que contrastar contra ella no habría saltado. Y el doble rol
        legítimo tiene firma idéntica al inventado —#E2 respondido "ninguna de las anteriores"
        y sin "Convertirse en proveedor" en estados_adicionales—, de modo que cualquier regla
        que marcase uno marcaría también el otro. El contrapeso vive en los prompts.
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

        # Si 'rol' trae roles que roles_dedup no tiene, estrechar hacia roles_dedup (B15)
        rol_estrecho = cls._reconciliar_rol(rol_raw, partes_validas, roles_dedup)
        if rol_estrecho is not None:
            datos = {**datos, "rol": rol_estrecho}
        # Si 'rol' venía como valor único pero roles_dedup tiene varios, reconstruir 'rol'
        elif len(roles_dedup) > 1 and len(partes_validas) <= 1:
            datos = {**datos, "rol": " / ".join(roles_dedup)}

        datos["roles_multiples"] = roles_dedup
        return cls._normalizar_obligaciones_preliminares(datos)

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
                "puntos_revision_profesional": self._puntos_revision_con_conflictos(),
                "resumen_cumplimiento": self.resumen_cumplimiento_registrado or "",
            }

        resultado_fallback = self._extraer_cumplimiento_legacy()
        if not resultado_fallback.get("obligaciones"):
            reconstruido = self._reconstruir_obligaciones_desde_historial()
            if reconstruido:
                resultado_fallback["obligaciones"] = reconstruido
        return resultado_fallback

    def _puntos_revision_con_conflictos(self) -> list[str]:
        """Puntos de revisión registrados más las recalificaciones que exigen verificación.

        Solo se escalan los conflictos con mejora=True (ver _registrar_conflicto). No muta
        self.puntos_revision_registrados: la lista devuelta es una vista, no la fuente.
        """
        puntos = list(self.puntos_revision_registrados)
        for c in self.conflictos_registrados:
            if not c.get("mejora"):
                continue
            rol = f" [{c['rol']}]" if c.get("rol") else ""
            punto = (
                f"Verificar la recalificación de {c['articulo']} — {c['titulo']}{rol}: "
                f"se registró como {str(c['estado_anterior']).upper()} y después se cambió a "
                f"{str(c['estado_nuevo']).upper()} (turno {c['turno']})."
            )
            if punto not in puntos:
                puntos.append(punto)
        return puntos

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
                estado = _normalizar_estado(m.group("estado"))
                if estado is None:
                    continue
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
        self.conflictos_registrados = []
        self.resumen_cumplimiento_registrado = ""
        self.ultima_respuesta_truncada = False

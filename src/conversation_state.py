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

"""Estado de la evaluación del árbol de decisión, mantenido por la aplicación.

PROBLEMA QUE RESUELVE
---------------------
El LLM olvida el rol a partir del turno ~13 porque la confirmación desaparece
del historial truncado y el bloque de ESTADO contradice al historial restante.
La causa raíz era pedirle al LLM emitir tokens estructurados ([ROL_DETERMINADO])
dentro de prosa libre, lo que falla de forma sistemática.

SOLUCIÓN
--------
El LLM principal solo genera prosa natural. Una llamada JSON separada y barata,
no-streaming, ejecutada DESPUÉS de cada turno (extraer_roles_confirmados),
detecta si en ese intercambio se confirmó algún rol y actualiza EvalState.
Los intercambios donde se confirma el rol se pinean (mensajes_pinneados) para
sobrevivir al truncado del historial.

En cada turno:
  1. Se antepone un bloque de ESTADO informativo con lo que ya se sabe.
  2. Tras recibir la respuesta, se procesa la señal [EVALUACION_COMPLETA]
     y se limpia el texto visible.
  3. El extractor JSON detecta confirmaciones de rol y actualiza EvalState.

NOTA LEGAL: este módulo NO toma ni altera ninguna decisión de clasificación del
AI Act. Solo transporta, sin modificarlo, lo que el modelo ha determinado
(rol, progreso). La lógica del árbol vive íntegra en el system prompt.
"""

from __future__ import annotations

import json
import logging
import re
from dataclasses import dataclass, field, asdict
from typing import Optional

logger = logging.getLogger(__name__)

# --------------------------------------------------------------------------- #
# Patrones de señales de control                                              #
# --------------------------------------------------------------------------- #

_RE_EVAL_COMPLETA = re.compile(r"\[\s*EVALUACION_COMPLETA\s*\]", re.IGNORECASE)

# Conserva las tres señales antiguas para limpiar texto de conversaciones que
# pudieran contener tokens legacy (compatibilidad retro).
_RE_TODAS_LAS_SENALES = re.compile(
    r"\[\s*(?:ROL_DETERMINADO\s*:[^\]]*|ROL_COMPLETADO\s*:[^\]]*|EVALUACION_COMPLETA)\s*\]",
    re.IGNORECASE,
)

# --------------------------------------------------------------------------- #
# Roles canónicos                                                              #
# --------------------------------------------------------------------------- #

_ROLES_CANONICOS = {
    "proveedor": "Proveedor",
    "implementador": "Implementador",
    "responsable del despliegue": "Implementador",
    "distribuidor": "Distribuidor",
    "importador": "Importador",
    "fabricante de producto": "Fabricante de producto",
    "fabricante": "Fabricante de producto",
    "representante autorizado": "Representante autorizado",
}


def _normalizar_rol(bruto: str) -> Optional[str]:
    """Normaliza un nombre de rol al canónico; None si no se reconoce."""
    clave = bruto.strip().lower()
    if clave in _ROLES_CANONICOS:
        return _ROLES_CANONICOS[clave]
    for k, v in _ROLES_CANONICOS.items():
        if k in clave:
            return v
    return None


# --------------------------------------------------------------------------- #
# Estado de la evaluación                                                     #
# --------------------------------------------------------------------------- #

@dataclass
class EvalState:
    """Estado del recorrido del árbol, persistido en st.session_state."""

    es_sistema_ia: Optional[bool] = None
    roles_declarados: list[str] = field(default_factory=list)
    roles_completados: list[str] = field(default_factory=list)
    estados_obligacion: list[str] = field(default_factory=list)
    evaluacion_completa: bool = False
    # Índices del chatbot.historial que el truncado no debe descartar.
    # Contienen los intercambios donde se confirmó información crítica (rol).
    mensajes_pinneados: list[int] = field(default_factory=list)

    @property
    def rol_en_curso(self) -> Optional[str]:
        """Primer rol declarado que aún no se ha completado."""
        for r in self.roles_declarados:
            if r not in self.roles_completados:
                return r
        return None

    @property
    def todos_los_roles_completados(self) -> bool:
        return bool(self.roles_declarados) and all(
            r in self.roles_completados for r in self.roles_declarados
        )

    def to_dict(self) -> dict:
        return asdict(self)

    @classmethod
    def from_dict(cls, d: dict) -> "EvalState":
        return cls(
            es_sistema_ia=d.get("es_sistema_ia"),
            roles_declarados=list(d.get("roles_declarados", [])),
            roles_completados=list(d.get("roles_completados", [])),
            estados_obligacion=list(d.get("estados_obligacion", [])),
            evaluacion_completa=bool(d.get("evaluacion_completa", False)),
            mensajes_pinneados=list(d.get("mensajes_pinneados", [])),
        )


# --------------------------------------------------------------------------- #
# Procesado de la respuesta del LLM principal                                 #
# --------------------------------------------------------------------------- #

def procesar_respuesta(texto_llm: str, estado: EvalState) -> tuple[str, EvalState]:
    """Procesa la señal de cierre y limpia el texto visible.

    A diferencia de la versión anterior, esta función ya NO intenta extraer
    roles del texto del modelo principal. La detección de roles se hace en
    extraer_roles_confirmados(), que se llama por separado tras cada turno.
    """
    if _RE_EVAL_COMPLETA.search(texto_llm):
        if not estado.roles_declarados or estado.todos_los_roles_completados:
            estado.evaluacion_completa = True

    texto_limpio = _RE_TODAS_LAS_SENALES.sub("", texto_llm)
    texto_limpio = re.sub(r"\n{3,}", "\n\n", texto_limpio).strip()
    return texto_limpio, estado


# --------------------------------------------------------------------------- #
# Bloque de ESTADO informativo                                                #
# --------------------------------------------------------------------------- #

def construir_bloque_estado(estado: EvalState) -> str:
    """Genera el bloque de ESTADO (informativo) para anteponer al turno.

    Tono neutro: la aplicación informa de lo que sabe; no amenaza ni
    bloquea. La continuidad del árbol depende del propio LLM leyendo este
    bloque y siguiendo la lógica del system prompt.
    """
    if estado.es_sistema_ia is True:
        es_ia = "sí"
    elif estado.es_sistema_ia is False:
        es_ia = "no (no cumple la definición del Art. 3.1)"
    else:
        es_ia = "aún no confirmado"

    roles = ", ".join(estado.roles_declarados) if estado.roles_declarados else "aún no determinado"
    completados = ", ".join(estado.roles_completados) if estado.roles_completados else "ninguno todavía"
    obligaciones = ", ".join(estado.estados_obligacion) if estado.estados_obligacion else "ninguno"
    en_curso = estado.rol_en_curso or "—"

    return (
        "═══ ESTADO ACTUAL DE LA EVALUACIÓN (mantenido por la aplicación) ═══\n"
        "Esta información la mantiene la aplicación a partir de la conversación.\n"
        "Tómala como punto de partida del turno; no la cuestiones ni la repreguntes.\n"
        f"- ¿Es sistema de IA? {es_ia}\n"
        f"- Rol(es) de la organización: {roles}\n"
        f"- Rol que se está evaluando ahora: {en_curso}\n"
        f"- Roles ya completados: {completados}\n"
        f"- Estados de obligación adquiridos (p. ej. Art. 25): {obligaciones}\n"
        "Si el rol ya figura aquí, no lo vuelvas a preguntar: continúa por el\n"
        "siguiente nodo pendiente del árbol.\n"
        "═══════════════════════════════════════════════════════════════════════"
    )


# --------------------------------------------------------------------------- #
# Extractor JSON de roles confirmados                                         #
# --------------------------------------------------------------------------- #

_EXTRACTOR_SYSTEM = (
    "Eres un extractor de información estructurada. Lees un fragmento de "
    "conversación y devuelves ÚNICAMENTE un objeto JSON válido. Sin "
    "preámbulo, sin markdown, sin texto adicional."
)

_EXTRACTOR_PROMPT_TMPL = """Lee este intercambio entre un usuario (organización
evaluada bajo la Ley de IA de la UE) y un asistente:

USUARIO: {user_msg}

ASISTENTE: {assistant_msg}

¿En este turno el asistente CONFIRMA el rol o roles de la organización en
sentido del AI Act? Roles posibles (canónicos):
"Proveedor", "Implementador", "Distribuidor", "Importador",
"Fabricante de producto", "Representante autorizado".

"Confirmar" significa afirmar el rol de la organización evaluada (ej.: "su
organización es Implementador", "queda confirmado como Proveedor",
"actuáis como Distribuidor"). NO cuenta:
- Listar las opciones sin asignarlas.
- Mencionar un rol en una explicación general.
- Preguntar al usuario qué rol tiene.

Devuelve EXCLUSIVAMENTE:
{{"confirmado": true|false, "roles": ["..."]}}

Si "confirmado" es false, "roles" debe ser []."""


def extraer_roles_confirmados(provider, user_msg: str, assistant_msg: str) -> list[str]:
    """Llama al provider en modo no-streaming para detectar roles confirmados.

    Devuelve la lista de roles canónicos confirmados en el intercambio, o
    lista vacía si no hay confirmación o si la extracción falla. Esta función
    nunca lanza: cualquier error se loggea y devuelve [].
    """
    prompt = _EXTRACTOR_PROMPT_TMPL.format(
        user_msg=(user_msg or "").strip()[:2000],
        assistant_msg=(assistant_msg or "").strip()[:4000],
    )
    try:
        texto = provider.chat(
            [{"role": "user", "content": prompt}],
            system_prompt=_EXTRACTOR_SYSTEM,
        )
    except Exception:
        logger.warning("Extractor de roles: fallo en la llamada al provider.", exc_info=True)
        return []

    texto = (texto or "").strip()
    if texto.startswith("```"):
        partes = texto.split("```")
        if len(partes) >= 2:
            texto = partes[1]
            if texto.lstrip().lower().startswith("json"):
                texto = texto.lstrip()[4:]
    texto = texto.strip()

    try:
        data = json.loads(texto)
    except Exception:
        m = re.search(r"\{[\s\S]*\}", texto)
        if not m:
            logger.warning("Extractor de roles: respuesta no es JSON: %r", texto[:200])
            return []
        try:
            data = json.loads(m.group())
        except Exception:
            logger.warning("Extractor de roles: JSON inválido: %r", texto[:200])
            return []

    if not data.get("confirmado"):
        return []
    roles_brutos = data.get("roles") or []
    if not isinstance(roles_brutos, list):
        return []
    salida: list[str] = []
    for bruto in roles_brutos:
        if not isinstance(bruto, str):
            continue
        canon = _normalizar_rol(bruto)
        if canon and canon not in salida:
            salida.append(canon)
    return salida

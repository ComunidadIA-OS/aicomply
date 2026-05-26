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
El LLM no tiene memoria entre turnos: en cada mensaje reconstruye desde cero en
qué punto del árbol está. Cuando la conversación crece, pierde la posición y
vuelve a anclarse en #E1 (la pregunta del rol), de modo que re-pregunta el tipo
de entidad o no llega a terminar la evaluación. Añadir más prohibiciones al
prompt no lo arregla porque la causa es la falta de estado persistente.

Este módulo saca el estado del historial y lo mantiene en `st.session_state`,
igual que ya se hace con la señal [EVALUACION_COMPLETA]. En cada turno:

  1. Antes de llamar al LLM, se ANTEPONE un bloque de ESTADO (fuente de verdad)
     con el rol o roles ya determinados, la pasada en curso, los roles
     completados y el siguiente nodo pendiente.
  2. Tras recibir la respuesta, se PARSEAN las señales de control que el modelo
     emite ([ROL_DETERMINADO], [ROL_COMPLETADO], [EVALUACION_COMPLETA]), se
     actualiza el estado y se ELIMINAN del texto antes de mostrarlo al usuario.

Las señales son invisibles para el usuario; este módulo las quita siempre.

NOTA LEGAL: este módulo NO toma ni altera ninguna decisión de clasificación del
AI Act. Solo transporta, sin modificarlo, lo que el modelo ya ha determinado
(rol, progreso). La lógica del árbol vive íntegra en el system prompt.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field, asdict
from typing import Optional


# --------------------------------------------------------------------------- #
# Patrones de las señales de control                                          #
# --------------------------------------------------------------------------- #
# Tolerantes a may/min y espacios. Capturan el contenido entre corchetes.
_RE_ROL_DETERMINADO = re.compile(
    r"\[\s*ROL_DETERMINADO\s*:\s*(?P<roles>[^\]]+)\]", re.IGNORECASE
)
_RE_ROL_COMPLETADO = re.compile(
    r"\[\s*ROL_COMPLETADO\s*:\s*(?P<rol>[^\]]+)\]", re.IGNORECASE
)
_RE_EVAL_COMPLETA = re.compile(r"\[\s*EVALUACION_COMPLETA\s*\]", re.IGNORECASE)

# Cualquiera de las tres, para limpiar de una pasada el texto visible.
_RE_TODAS_LAS_SENALES = re.compile(
    r"\[\s*(?:ROL_DETERMINADO\s*:[^\]]*|ROL_COMPLETADO\s*:[^\]]*|EVALUACION_COMPLETA)\s*\]",
    re.IGNORECASE,
)

# Roles canónicos reconocidos (para normalizar lo que escriba el modelo).
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

# Frases que indican que el LLM está CONFIRMANDO el rol (no solo describiendo opciones).
_RE_TRIGGER_CONFIRMACION = re.compile(
    r"(?:"
    # formal/informal sing-plur: "su/vuestra/tu organización/asesoría/empresa es [entonces]"
    r"(?:su|vuestra?|tu)\s+(?:organización|asesoría|empresa|entidad|caso)\s+es(?:\s+entonces)?|"
    # "queda claro/confirmado/establecido/fijado …"
    r"queda\s+(?:claro|confirmado|establecido|fijado)|"
    # "su/vuestro/tu rol como/es/de/queda"
    r"(?:su|vuestro?|tu)\s+rol\s+(?:como|es|de|queda)\b|"
    # "confirmado el rol"
    r"confirmado\s+(?:el\s+)?rol(?:\s+(?:como|de))?|"
    # "sois [opcionalmente (b)] [el] Implementador"
    r"\bsois\s+(?:\(?[a-f]\)?\s+)?(?:el\s+|la\s+|un\s+|una\s+)?(?:entonces\s+)?|"
    # "actuáis como" / "estáis actuando como"
    r"(?:act[uú][aá]is|est[aá]is\s+actuando)\s+como|"
    # "os/le corresponde el rol de"
    r"(?:os|le)\s+corresponde\s+el\s+rol\s+de|"
    # "os identifico como" / "os posiciono como"
    r"os\s+(?:identifico|posiciono|clasifico)\s+como|"
    # "estáis en la categoría de"
    r"est[aá]is\s+en\s+la\s+categor[ií]a\s+de"
    r")",
    re.IGNORECASE,
)


def _normalizar_rol(bruto: str) -> Optional[str]:
    """Normaliza un nombre de rol al canónico; None si no se reconoce."""
    clave = bruto.strip().lower()
    if clave in _ROLES_CANONICOS:
        return _ROLES_CANONICOS[clave]
    # Coincidencia parcial tolerante (p. ej. "proveedor de IA").
    for k, v in _ROLES_CANONICOS.items():
        if k in clave:
            return v
    return None


def _inferir_roles_del_texto(texto: str) -> list[str]:
    """Fallback: extrae todos los roles cuando el LLM confirmó verbalmente pero olvidó la señal.

    Busca frases de confirmación («queda confirmado su rol como X», «su organización
    es entonces (b) Implementador»…) y extrae TODOS los roles canónicos encontrados
    en la ventana de contexto siguiente al trigger (soporta roles múltiples).
    Devuelve lista vacía si no hay indicios claros de confirmación.
    """
    encontrados: list[str] = []
    for m in _RE_TRIGGER_CONFIRMACION.finditer(texto):
        fragmento = texto[m.start(): m.start() + 200]
        for clave, canon in _ROLES_CANONICOS.items():
            if canon not in encontrados and re.search(
                r"\b" + re.escape(clave) + r"\b", fragmento, re.IGNORECASE
            ):
                encontrados.append(canon)
    return encontrados


# --------------------------------------------------------------------------- #
# Estado de la evaluación                                                     #
# --------------------------------------------------------------------------- #
@dataclass
class EvalState:
    """Estado del recorrido del árbol, persistido en st.session_state."""

    es_sistema_ia: Optional[bool] = None          # None = aún sin confirmar
    roles_declarados: list[str] = field(default_factory=list)
    roles_completados: list[str] = field(default_factory=list)
    estados_obligacion: list[str] = field(default_factory=list)  # p. ej. Art. 25
    evaluacion_completa: bool = False

    # -- helpers de progreso ------------------------------------------------ #
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
        )


# --------------------------------------------------------------------------- #
# Parseo de señales + limpieza del texto visible                              #
# --------------------------------------------------------------------------- #
def procesar_respuesta(texto_llm: str, estado: EvalState) -> tuple[str, EvalState]:
    """Actualiza `estado` con las señales del modelo y devuelve el texto limpio.

    Devuelve (texto_visible_sin_senales, estado_actualizado).

    SALVAGUARDA ANTI-TERMINACIÓN PREMATURA: si el modelo emite
    [EVALUACION_COMPLETA] pero aún quedan roles declarados sin completar, NO se
    marca la evaluación como completa. La señal se elimina igualmente del texto
    y el bloque de ESTADO del siguiente turno seguirá mostrando los roles
    pendientes, empujando al modelo a continuar en lugar de detenerse.
    """
    # 1) [ROL_DETERMINADO: a, b, ...] — solo la primera vez fija los roles.
    m = _RE_ROL_DETERMINADO.search(texto_llm)
    if m and not estado.roles_declarados:
        for bruto in m.group("roles").split(","):
            rol = _normalizar_rol(bruto)
            if rol and rol not in estado.roles_declarados:
                estado.roles_declarados.append(rol)

    # 1b) Fallback: si el LLM no emitió la señal pero confirmó el rol en texto,
    #     extraer todos los roles para que el bloque de ESTADO no siga mostrando «pendiente».
    #     Soporta roles múltiples (Considerando 83): p. ej. Proveedor + Implementador.
    if not estado.roles_declarados:
        for rol in _inferir_roles_del_texto(texto_llm):
            if rol not in estado.roles_declarados:
                estado.roles_declarados.append(rol)

    # 2) [ROL_COMPLETADO: x] — puede aparecer varias veces.
    for mc in _RE_ROL_COMPLETADO.finditer(texto_llm):
        rol = _normalizar_rol(mc.group("rol"))
        if rol and rol not in estado.roles_completados:
            estado.roles_completados.append(rol)

    # 3) [EVALUACION_COMPLETA] — solo válida si todos los roles están cerrados.
    if _RE_EVAL_COMPLETA.search(texto_llm):
        if not estado.roles_declarados or estado.todos_los_roles_completados:
            estado.evaluacion_completa = True
        # si es prematura, se ignora el flag pero igualmente se limpia abajo.

    # 4) Eliminar TODAS las señales del texto visible para el usuario.
    texto_limpio = _RE_TODAS_LAS_SENALES.sub("", texto_llm)
    # Compactar líneas en blanco que pudieran quedar al quitar una señal sola.
    texto_limpio = re.sub(r"\n{3,}", "\n\n", texto_limpio).strip()

    return texto_limpio, estado


# --------------------------------------------------------------------------- #
# Construcción del bloque de ESTADO que se inyecta cada turno                  #
# --------------------------------------------------------------------------- #
def construir_bloque_estado(estado: EvalState) -> str:
    """Genera el bloque de ESTADO (fuente de verdad) para anteponer al turno.

    El system prompt instruye al modelo a leer este bloque primero y a no
    re-preguntar nada que ya figure resuelto aquí.
    """
    if estado.es_sistema_ia is True:
        es_ia = "SÍ (confirmado)"
    elif estado.es_sistema_ia is False:
        es_ia = "NO (no cumple la definición del Art. 3.1)"
    else:
        es_ia = "pendiente de confirmar"

    if estado.roles_declarados:
        roles = ", ".join(estado.roles_declarados)
        rol_linea = f"{roles}  [BLOQUEADO — no volver a preguntar]"
    else:
        rol_linea = (
            "pendiente de registro — "
            "ACCIÓN REQUERIDA: si el rol ya fue determinado en la conversación, "
            "añade [ROL_DETERMINADO: <rol>] al final de tu respuesta actual para registrarlo. "
            "Si aún no fue determinado, resuélvelo ahora y emite la señal."
        )

    estados_obl = (
        ", ".join(estado.estados_obligacion)
        if estado.estados_obligacion
        else "ninguno"
    )

    completados = (
        ", ".join(estado.roles_completados)
        if estado.roles_completados
        else "ninguno"
    )

    en_curso = estado.rol_en_curso or "—"
    if estado.roles_declarados:
        total = len(estado.roles_declarados)
        hechos = len(
            [r for r in estado.roles_declarados if r in estado.roles_completados]
        )
        pasada = f"rol «{en_curso}» ({hechos + 1 if en_curso != '—' else hechos} de {total})"
        if en_curso == "—":
            pasada = f"todas las pasadas completadas ({total} de {total})"
    else:
        pasada = "recorrido único (rol aún sin determinar)"

    return (
        "═══ ESTADO DE LA EVALUACIÓN (mantenido por la aplicación — FUENTE DE VERDAD) ═══\n"
        "Este bloque lo mantiene la aplicación, no tú. NO lo cuestiones ni lo contradigas.\n"
        "NO vuelvas a preguntar nada que ya figure resuelto aquí.\n"
        f"- ¿Es sistema de IA?: {es_ia}\n"
        f"- Rol(es) declarado(s): {rol_linea}\n"
        f"- Estados de obligación adquiridos (p. ej. Art. 25): {estados_obl}\n"
        f"- Pasada de rol en curso: {pasada}\n"
        f"- Roles ya completados: {completados}\n"
        "Continúa desde el siguiente nodo pendiente. El rol está fijado: bajo ninguna\n"
        "circunstancia lo preguntes de nuevo ni reinicies el árbol.\n"
        "═══════════════════════════════════════════════════════════════════════════"
    )

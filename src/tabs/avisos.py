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

"""Avisos de interfaz compartidos entre pestañas."""

from __future__ import annotations

import logging

import streamlit as st

logger = logging.getLogger(__name__)

TEXTO_RESPUESTA_TRUNCADA = (
    "**La respuesta quedó incompleta.** Alcanzó el límite de longitud del modelo "
    "(`LLM_MAX_TOKENS`) y se cortó antes de terminar. Escriba «continúa» para que el "
    "asistente siga desde donde se quedó, o suba `LLM_MAX_TOKENS` en su fichero `.env`."
)


def marcar_truncada(clave: str, truncada: bool) -> None:
    """Recuerda si la última respuesta de esta pestaña se cortó por el límite de tokens."""
    st.session_state[clave] = bool(truncada)


def avisar_si_truncada(clave: str) -> None:
    """Muestra el aviso de respuesta incompleta si la última respuesta se cortó.

    Se avisa de forma visible en lugar de dejar un texto cortado a media frase: una respuesta
    truncada tampoco llega a emitir [EVALUACION_COMPLETA], así que sin este aviso el usuario
    solo percibe que el botón de continuar no aparece, sin saber por qué.
    """
    if st.session_state.get(clave):
        st.warning(TEXTO_RESPUESTA_TRUNCADA)


# ── Documentación técnica recortada ───────────────────────────────────────────

CLAVE_DOC_RECORTADA = "documentacion_recortada"

TEXTO_DOCUMENTACION_RECORTADA = (
    "**La documentación técnica no cabe entera.** Se han conservado los primeros "
    "{conservados} caracteres de los {originales} aportados. El asistente no tendrá en "
    "cuenta la parte final del documento, así que puede preguntarle por algo que solo "
    "esté ahí. Si lo importante está al final, péguelo en el área de texto o suba un "
    "documento más corto."
)


def formatear_miles(n: int) -> str:
    """Formato español de millares: 6.000, no 6,000."""
    return f"{n:,}".replace(",", ".")


def marcar_documentacion_recortada(originales: int, conservados: int) -> None:
    """Recuerda que la documentación aportada no cupo entera en el prompt, y lo registra.

    El recorte importa desde que la documentación se inyecta en cada turno del árbol de
    decisión: lo que queda fuera son respuestas que el modelo no encontrará y volverá a
    preguntar, que es justo lo que la inyección venía a evitar. El límite no se sube —6.000
    caracteres ya son unos 1.500 tokens por turno—, así que lo que toca es decirlo.
    """
    if originales <= conservados:
        st.session_state.pop(CLAVE_DOC_RECORTADA, None)
        return

    st.session_state[CLAVE_DOC_RECORTADA] = (originales, conservados)
    logger.warning(
        "Documentación técnica recortada: %d caracteres aportados, %d inyectados en el "
        "prompt. El árbol de decisión no verá el resto y puede repreguntar lo que solo "
        "estuviera en la parte descartada.",
        originales, conservados,
    )


def avisar_si_documentacion_recortada() -> None:
    """Muestra el aviso de documentación recortada mientras la sesión la siga usando.

    Va en las dos pestañas que inyectan el documento —Evaluador y Cumplimiento—, no solo en
    la que hace el recorte: quien lee un turno del análisis de cumplimiento necesita saber
    que el asistente no tiene delante el documento entero tanto como quien lo subió.
    """
    datos = st.session_state.get(CLAVE_DOC_RECORTADA)
    if not datos:
        return
    originales, conservados = datos
    st.warning(
        TEXTO_DOCUMENTACION_RECORTADA.format(
            conservados=formatear_miles(conservados), originales=formatear_miles(originales)
        )
    )

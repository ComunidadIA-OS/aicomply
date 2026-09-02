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

import streamlit as st

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

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

"""Estado de la pestaña Evaluador (src/tabs/evaluador.py).

Solo se prueba _inicializar_estado, que toca session_state y construye el chatbot: el resto
de la pestaña dibuja widgets y necesita `streamlit run`. Lo que se comprueba aquí es que una
sesión que ya traía documentación técnica se la pase al chatbot al reconstruirlo —el caso de
la recarga de página—, porque el prompt es ahora el único sitio donde esa documentación
sobrevive al recorte del historial.
"""

import pytest
import streamlit as st

from src.tabs.evaluador import _inicializar_estado

_CLAVES = (
    "intro_vista",
    "mensajes_evaluador",
    "chatbot_evaluador",
    "evaluacion_completada",
    "clasificacion_data",
    "readme_tecnico",
)


@pytest.fixture(autouse=True)
def _sesion_limpia():
    for clave in _CLAVES:
        st.session_state.pop(clave, None)
    yield
    for clave in _CLAVES:
        st.session_state.pop(clave, None)


def test_sin_documentacion_el_chatbot_arranca_sin_ella(mock_provider):
    _inicializar_estado(mock_provider)
    assert st.session_state.chatbot_evaluador.documentacion_aportada == ""


def test_una_sesion_con_documentacion_se_la_pasa_al_chatbot(mock_provider):
    """Recarga de página: readme_tecnico sigue en la sesión y el chatbot se reconstruye."""
    st.session_state.readme_tecnico = "Red neuronal entrenada con imágenes térmicas."
    _inicializar_estado(mock_provider)
    assert (
        st.session_state.chatbot_evaluador.documentacion_aportada
        == "Red neuronal entrenada con imágenes térmicas."
    )

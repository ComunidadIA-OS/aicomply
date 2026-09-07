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

from src.tabs.avisos import CLAVE_DOC_RECORTADA
from src.tabs.evaluador import (
    _MAX_DOC_CARACTERES,
    _inicializar_estado,
    _preparar_documentacion,
)

_CLAVES = (
    "intro_vista",
    "mensajes_evaluador",
    "chatbot_evaluador",
    "evaluacion_completada",
    "clasificacion_data",
    "readme_tecnico",
    CLAVE_DOC_RECORTADA,
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


class TestPrepararDocumentacion:
    """El recorte de 6.000 caracteres dejó de ser inofensivo cuando la documentación pasó a
    consultarse antes de cada pregunta del árbol: lo que se corta son respuestas que el
    modelo no encontrará y volverá a preguntar."""

    def test_lo_que_cabe_pasa_entero_y_sin_aviso(self):
        texto = "ficha corta"
        assert _preparar_documentacion(texto) == texto
        assert CLAVE_DOC_RECORTADA not in st.session_state

    def test_lo_que_no_cabe_se_recorta_al_limite(self):
        recortado = _preparar_documentacion("x" * 20_000)
        assert len(recortado) == _MAX_DOC_CARACTERES

    def test_el_recorte_no_es_silencioso(self):
        """El punto del arreglo: el corte ya existía, el aviso no."""
        _preparar_documentacion("x" * 20_000)
        assert st.session_state[CLAVE_DOC_RECORTADA] == (20_000, _MAX_DOC_CARACTERES)

    def test_el_aviso_cuenta_los_caracteres_del_documento_entero(self):
        """No los del recortado: la cifra que le falta al usuario es la que aportó."""
        _preparar_documentacion("x" * 18_432)
        originales, _ = st.session_state[CLAVE_DOC_RECORTADA]
        assert originales == 18_432

    def test_el_limite_del_aviso_es_el_del_recorte(self):
        """Si alguien mueve uno y no el otro, el aviso miente sobre lo que se ha guardado."""
        recortado = _preparar_documentacion("x" * 20_000)
        _, conservados = st.session_state[CLAVE_DOC_RECORTADA]
        assert conservados == len(recortado)

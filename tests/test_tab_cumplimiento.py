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

"""La pestaña Cumplimiento cerrada para PROHIBIDO (src/tabs/cumplimiento.py).

Un sistema del Art. 5 no pasa por el análisis de cumplimiento: no hay nada que evaluar. Lo
que se prueba aquí es que la pestaña se detiene ANTES de `_inicializar_estado`, que es donde
se construye el chatbot de cumplimiento. Recorrer obligaciones sobre un sistema prohibido es
lo que produjo B34, y además gasta clave: cada turno de ese chatbot es una llamada al modelo.

La pestaña dibuja widgets, así que estos tests la llaman fuera de `streamlit run`: los
widgets no pintan nada y devuelven sus valores por defecto, que es justo lo que hace falta
para ver por qué rama pasa.
"""

import pytest
import streamlit as st

from src.clasificaciones import TEXTO_CUMPLIMIENTO_PROHIBIDO
from src.tabs.cumplimiento import mostrar_tab_cumplimiento

_CLAVES = (
    "evaluacion_completada",
    "acceso_directo_cumplimiento",
    "clasificacion_data",
    "chatbot_cumplimiento",
    "mensajes_cumplimiento",
    "cumplimiento_completado",
    "cumplimiento_data",
    "readme_tecnico",
)


@pytest.fixture(autouse=True)
def _sesion_limpia():
    for clave in _CLAVES:
        st.session_state.pop(clave, None)
    yield
    for clave in _CLAVES:
        st.session_state.pop(clave, None)


def _clasificacion(nivel: str) -> dict:
    return {
        "clasificacion": nivel,
        "rol": "implementador",
        "roles_multiples": ["implementador"],
        "descripcion_sistema": (
            "Análisis de la voz de los agentes durante las llamadas para inferir su estado "
            "emocional"
        ),
        "sector": "Contact center",
        "obligaciones_preliminares": [],
        "puntos_indeterminados": [],
        "estados_adicionales": [],
    }


class TestProhibidoNoArrancaElChatbotDeCumplimiento:
    """Las dos vías por las que se llega a la pestaña con una clasificación ya hecha. La del
    acceso directo importa tanto como la otra: es la única en la que el usuario elige
    «Prohibido» a mano, y por ahí es por donde volvería el 83 % de B34."""

    def test_por_la_via_normal_no_se_crea_el_chatbot(self, mock_provider):
        st.session_state.evaluacion_completada = True
        st.session_state.clasificacion_data = _clasificacion("PROHIBIDO")

        mostrar_tab_cumplimiento(mock_provider)

        assert st.session_state.get("chatbot_cumplimiento") is None
        assert mock_provider.llamadas_chat == 0
        assert mock_provider.llamadas_stream == 0

    def test_por_el_acceso_directo_tampoco(self, mock_provider):
        """El formulario de acceso directo escribe la clasificación en la sesión y marca
        `acceso_directo_cumplimiento`: no hay evaluación previa, así que la rama no puede
        depender de `evaluacion_completada`."""
        st.session_state.acceso_directo_cumplimiento = True
        st.session_state.clasificacion_data = _clasificacion("PROHIBIDO")

        mostrar_tab_cumplimiento(mock_provider)

        assert st.session_state.get("chatbot_cumplimiento") is None
        assert mock_provider.llamadas_chat == 0
        assert mock_provider.llamadas_stream == 0

    def test_la_pestana_ni_siquiera_inicializa_su_estado(self, mock_provider):
        """`_inicializar_estado` crea el chatbot, pero también las claves de la conversación.
        Que no aparezca ninguna es la señal de que se ha salido antes de llegar."""
        st.session_state.evaluacion_completada = True
        st.session_state.clasificacion_data = _clasificacion("PROHIBIDO")

        mostrar_tab_cumplimiento(mock_provider)

        assert "mensajes_cumplimiento" not in st.session_state
        assert "cumplimiento_data" not in st.session_state

    def test_una_clasificacion_en_minusculas_tambien_se_detiene(self, mock_provider):
        """La comparación la hace `es_prohibido`, que normaliza. Un valor sin canonizar por
        una sesión importada no puede reabrir el análisis."""
        st.session_state.evaluacion_completada = True
        st.session_state.clasificacion_data = _clasificacion("prohibido")

        mostrar_tab_cumplimiento(mock_provider)

        assert st.session_state.get("chatbot_cumplimiento") is None

    def test_alto_si_arranca_el_chatbot(self, mock_provider):
        """El control del test anterior: si la pestaña no arrancara el chatbot para nadie,
        los tres tests de arriba pasarían sin probar nada."""
        st.session_state.evaluacion_completada = True
        st.session_state.clasificacion_data = _clasificacion("ALTO")

        mostrar_tab_cumplimiento(mock_provider)

        assert st.session_state.get("chatbot_cumplimiento") is not None
        assert "mensajes_cumplimiento" in st.session_state


class TestElTextoDeLaPestanaParaProhibido:
    """Cuatro cosas, en este orden: qué es el sistema, por qué no hay análisis, qué sigue
    obligando pese a la prohibición y dónde está el detalle."""

    def test_dice_que_es_una_practica_prohibida_del_art_5(self):
        assert "práctica prohibida" in TEXTO_CUMPLIMIENTO_PROHIBIDO
        assert "Art. 5" in TEXTO_CUMPLIMIENTO_PROHIBIDO

    def test_dice_por_que_no_procede_el_analisis(self):
        assert "No procede un análisis de cumplimiento" in TEXTO_CUMPLIMIENTO_PROHIBIDO
        assert "no admite grados" in TEXTO_CUMPLIMIENTO_PROHIBIDO
        assert "no existe una versión conforme" in TEXTO_CUMPLIMIENTO_PROHIBIDO

    def test_dice_que_el_art_4_obliga_a_la_organizacion_y_no_al_sistema(self):
        assert "Art. 4" in TEXTO_CUMPLIMIENTO_PROHIBIDO
        assert "responsable del despliegue de sistemas de IA" in TEXTO_CUMPLIMIENTO_PROHIBIDO
        assert "no por este sistema en concreto" in TEXTO_CUMPLIMIENTO_PROHIBIDO

    def test_remite_al_informe_de_evaluacion(self):
        assert "Informe de evaluación" in TEXTO_CUMPLIMIENTO_PROHIBIDO
        assert "pestaña **Informe**" in TEXTO_CUMPLIMIENTO_PROHIBIDO

    def test_el_orden_es_el_del_razonamiento(self):
        posiciones = [
            TEXTO_CUMPLIMIENTO_PROHIBIDO.index("práctica prohibida"),
            TEXTO_CUMPLIMIENTO_PROHIBIDO.index("No procede un análisis"),
            TEXTO_CUMPLIMIENTO_PROHIBIDO.index("Art. 4"),
            TEXTO_CUMPLIMIENTO_PROHIBIDO.index("Informe de evaluación"),
        ]
        assert posiciones == sorted(posiciones)

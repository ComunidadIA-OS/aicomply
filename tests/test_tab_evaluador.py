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

Se prueban las funciones que tocan session_state y construyen el chatbot; el resto de la
pestaña dibuja widgets y necesita `streamlit run`. Lo que hay detrás de cada bloque:

- _inicializar_estado: una sesión que ya traía documentación técnica se la pasa al chatbot al
  reconstruirlo (recarga de página), porque el prompt es el único sitio donde esa
  documentación sobrevive al recorte del historial.
- _preparar_documentacion: el recorte al límite del prompt, que dejó de ser inofensivo cuando
  la documentación pasó a consultarse antes de cada pregunta.
- _cargar_documentacion: el orden entre recortar y analizar, y que un fallo del proveedor no
  deje la sesión a medias.
"""

import pytest
import streamlit as st

from src.chatbot import AIComplyChat
from src.security import envolver_contenido_no_confiable
from src.tabs.avisos import CLAVE_DOC_RECORTADA
from src.tabs.evaluador import (
    _MAX_DOC_CARACTERES,
    _MAX_PEGADO_CARACTERES,
    _MAX_UPLOAD_BYTES,
    _cargar_documentacion,
    _error_texto_pegado,
    _inicializar_estado,
    _preparar_documentacion,
)


class SpyProvider:
    """Provider de test (duck typing) que captura el contenido del mensaje enviado."""

    es_local = False

    def __init__(self, respuesta: str = "Resumen del sistema."):
        self.respuesta = respuesta
        self.ultimo_contenido: str = ""

    def chat(self, messages, system_prompt: str = "") -> str:
        self.ultimo_contenido = messages[0]["content"]
        return self.respuesta

    def chat_stream(self, messages, system_prompt: str = ""):
        yield self.respuesta


class ProviderQueFalla:
    """El proveedor cae en mitad del análisis: ni resumen ni documentación cargada."""

    es_local = False

    def chat(self, messages, system_prompt: str = "") -> str:
        raise RuntimeError("503 Service Unavailable")

    def chat_stream(self, messages, system_prompt: str = ""):
        raise RuntimeError("503 Service Unavailable")

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


class TestCargarDocumentacion:
    """El resumen inicial y la documentación inyectada tienen que ser el mismo documento.

    Había dos recortes con dos límites distintos —_analizar_readme leía 8.000 caracteres y se
    guardaban 6.000—, y además se analizaba el original antes de recortar. Con un documento
    de entre 6.000 y 8.000 caracteres, el usuario confirmaba un resumen escrito sobre
    párrafos que el árbol ya no tenía delante: un hecho aceptado de la conversación que la
    documentación inyectada no respalda, y que el modelo puede repreguntar o contradecir.
    """

    def _chatbot(self) -> AIComplyChat:
        return AIComplyChat(SpyProvider())

    def test_se_analiza_exactamente_lo_que_queda_en_sesion(self):
        """El invariante del arreglo, en el caso que lo destapaba: 7.000 caracteres."""
        spy = SpyProvider()
        chatbot = self._chatbot()

        _cargar_documentacion(spy, chatbot, "x" * 7_000)

        guardado = st.session_state.readme_tecnico
        assert len(guardado) == _MAX_DOC_CARACTERES
        assert envolver_contenido_no_confiable(guardado) in spy.ultimo_contenido

    def test_al_proveedor_no_le_llega_nada_que_no_se_guarde(self):
        """El texto sobrante del documento no puede colarse en el análisis.

        El marcador es una cadena que no aparece en el prompt de análisis: buscar una letra
        suelta daba falsos positivos contra su propia redacción.
        """
        spy = SpyProvider()
        cola = "SOLO_EN_LA_PARTE_DESCARTADA"
        _cargar_documentacion(spy, self._chatbot(), "a" * _MAX_DOC_CARACTERES + cola)

        assert cola not in spy.ultimo_contenido
        assert cola not in st.session_state.readme_tecnico

    def test_el_chatbot_recibe_lo_mismo_que_la_sesion(self):
        spy = SpyProvider()
        chatbot = self._chatbot()

        _cargar_documentacion(spy, chatbot, "Ficha técnica del sistema.")

        assert chatbot.documentacion_aportada == st.session_state.readme_tecnico
        assert envolver_contenido_no_confiable(chatbot.documentacion_aportada) in spy.ultimo_contenido

    def test_un_documento_que_cabe_llega_entero_al_analisis(self):
        """Regresión del caso normal: sin recorte, nada cambia."""
        spy = SpyProvider()
        ficha = "Red neuronal de detección de objetos entrenada con imágenes térmicas."

        _cargar_documentacion(spy, self._chatbot(), ficha)

        assert st.session_state.readme_tecnico == ficha
        assert ficha in spy.ultimo_contenido

    def test_la_documentacion_sigue_yendo_envuelta_al_proveedor(self):
        """Condición que no se negocia: es dato, no instrucción."""
        spy = SpyProvider()
        _cargar_documentacion(spy, self._chatbot(), "ficha")

        assert "<<<DOCUMENTO_DEL_USUARIO_INICIO>>>" in spy.ultimo_contenido
        assert "<<<DOCUMENTO_DEL_USUARIO_FIN>>>" in spy.ultimo_contenido

    def test_devuelve_el_resumen_del_proveedor(self):
        resumen = _cargar_documentacion(
            SpyProvider("Sistema de visión artificial."), self._chatbot(), "ficha"
        )
        assert resumen == "Sistema de visión artificial."

    def test_un_fallo_del_proveedor_no_carga_documentacion(self):
        chatbot = self._chatbot()
        with pytest.raises(RuntimeError):
            _cargar_documentacion(ProviderQueFalla(), chatbot, "x" * 20_000)

        assert "readme_tecnico" not in st.session_state
        assert chatbot.documentacion_aportada == ""

    def test_un_texto_pegado_enorme_avisa_con_la_cifra_real(self):
        """La cifra del aviso es la que aportó el usuario, no la de ningún tope intermedio.

        Con el `max_chars=8000` que llevaba el área de texto, quien pegaba 20.000 caracteres
        leía «se han conservado los primeros 6.000 de los 8.000 aportados»: Streamlit
        recortaba antes, en silencio, y la aplicación presentaba como aportado un número que
        se había fabricado ella con su propio recorte.
        """
        _cargar_documentacion(SpyProvider(), self._chatbot(), "x" * 20_000)

        originales, conservados = st.session_state[CLAVE_DOC_RECORTADA]
        assert originales == 20_000
        assert conservados == _MAX_DOC_CARACTERES

    def test_un_fallo_del_proveedor_no_deja_el_aviso_puesto(self):
        """El aviso se marca al recortar, antes de llamar al modelo: si la llamada falla,
        anunciaría el recorte de una documentación que no está en sesión."""
        with pytest.raises(RuntimeError):
            _cargar_documentacion(ProviderQueFalla(), self._chatbot(), "x" * 20_000)

        assert CLAVE_DOC_RECORTADA not in st.session_state


class TestTechoDelTextoPegado:
    """Las dos vías de entrada se comportan igual ante un documento demasiado grande: la de
    fichero ya fallaba ruidosamente por encima de 500 KB, la de pegado callaba."""

    def test_lo_normal_no_da_error(self):
        assert _error_texto_pegado(6_000) is None

    def test_muy_por_encima_del_limite_del_prompt_tampoco(self):
        """El techo de entrada no es el del prompt: 20.000 caracteres entran, se recortan
        para el prompt y el aviso lo dice. Lo que no puede es rechazarlos en silencio."""
        assert _error_texto_pegado(20_000) is None

    def test_justo_en_el_techo_entra(self):
        assert _error_texto_pegado(_MAX_PEGADO_CARACTERES) is None

    def test_por_encima_del_techo_hay_error(self):
        error = _error_texto_pegado(_MAX_PEGADO_CARACTERES + 1)
        assert error is not None

    def test_el_error_dice_el_techo_y_lo_que_se_pego(self):
        error = _error_texto_pegado(812_430)
        assert "500.000" in error
        assert "812.430" in error

    def test_el_techo_de_pegado_acompana_al_de_subida(self):
        """Mismo orden de magnitud: la vía de entrada no debería decidir cuánto cabe."""
        assert _MAX_PEGADO_CARACTERES == _MAX_UPLOAD_BYTES

    def test_el_techo_deja_sitio_de_sobra_al_recorte_del_prompt(self):
        """Si el techo bajara hasta el límite del prompt, len(contenido) valdría exactamente
        el límite, marcar_documentacion_recortada no vería recorte y el aviso no saltaría
        nunca. El techo rechaza; el que recorta es _preparar_documentacion."""
        assert _MAX_PEGADO_CARACTERES > _MAX_DOC_CARACTERES

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

"""Avisos compartidos entre pestañas (src/tabs/avisos.py).

El aviso de documentación recortada existe desde que la documentación se inyecta en cada
turno del árbol de decisión: lo que el recorte deja fuera son respuestas que el modelo no
encontrará y volverá a preguntar. El límite se queda en 6.000 caracteres —unos 1.500 tokens
por turno—, así que lo que cambia es que se diga.
"""

import logging

import pytest
import streamlit as st

from src.tabs.avisos import (
    CLAVE_DOC_RECORTADA,
    TEXTO_DOCUMENTACION_RECORTADA,
    avisar_si_documentacion_recortada,
    marcar_documentacion_recortada,
)


@pytest.fixture(autouse=True)
def _sesion_limpia():
    st.session_state.pop(CLAVE_DOC_RECORTADA, None)
    yield
    st.session_state.pop(CLAVE_DOC_RECORTADA, None)


class TestMarcarDocumentacionRecortada:
    def test_un_documento_que_cabe_no_deja_aviso(self):
        marcar_documentacion_recortada(4_200, 6_000)
        assert CLAVE_DOC_RECORTADA not in st.session_state

    def test_uno_que_cabe_justo_tampoco(self):
        """El límite es inclusivo: 6.000 de 6.000 no se ha perdido nada."""
        marcar_documentacion_recortada(6_000, 6_000)
        assert CLAVE_DOC_RECORTADA not in st.session_state

    def test_uno_que_no_cabe_guarda_las_dos_cifras(self):
        marcar_documentacion_recortada(18_432, 6_000)
        assert st.session_state[CLAVE_DOC_RECORTADA] == (18_432, 6_000)

    def test_un_documento_nuevo_que_cabe_borra_el_aviso_anterior(self):
        """Reiniciar la evaluación y subir otro documento no puede dejar el aviso viejo."""
        marcar_documentacion_recortada(18_432, 6_000)
        marcar_documentacion_recortada(900, 6_000)
        assert CLAVE_DOC_RECORTADA not in st.session_state

    def test_el_recorte_queda_en_el_log(self, caplog):
        """Streamlit avisa en su propio logger al correr en bare mode: se filtra por el
        nuestro, o el test comprueba el ruido ajeno."""
        with caplog.at_level(logging.WARNING, logger="src.tabs.avisos"):
            marcar_documentacion_recortada(18_432, 6_000)
        propios = [r.getMessage() for r in caplog.records if r.name == "src.tabs.avisos"]
        assert len(propios) == 1
        assert "18432" in propios[0] and "6000" in propios[0]
        assert "repreguntar" in propios[0]

    def test_lo_que_si_cabe_no_ensucia_el_log(self, caplog):
        with caplog.at_level(logging.WARNING, logger="src.tabs.avisos"):
            marcar_documentacion_recortada(900, 6_000)
        assert [r for r in caplog.records if r.name == "src.tabs.avisos"] == []


class TestAvisoDeDocumentacionRecortada:
    def test_el_texto_dice_cuanto_se_conserva_de_cuanto(self):
        texto = TEXTO_DOCUMENTACION_RECORTADA.format(conservados="6.000", originales="18.432")
        assert "6.000" in texto and "18.432" in texto

    def test_el_texto_avisa_de_que_el_final_del_documento_no_cuenta(self):
        texto = TEXTO_DOCUMENTACION_RECORTADA.format(conservados="6.000", originales="18.432")
        assert "parte final del documento" in texto

    def test_sin_marca_no_se_muestra_nada(self, monkeypatch):
        import src.tabs.avisos  # noqa: PLC0415
        mostrados: list[str] = []
        monkeypatch.setattr(src.tabs.avisos.st, "warning", mostrados.append)

        avisar_si_documentacion_recortada()
        assert mostrados == []

    def test_con_marca_se_muestra_con_las_cifras_en_formato_espanol(self, monkeypatch):
        import src.tabs.avisos  # noqa: PLC0415
        mostrados: list[str] = []
        monkeypatch.setattr(src.tabs.avisos.st, "warning", mostrados.append)

        marcar_documentacion_recortada(18_432, 6_000)
        avisar_si_documentacion_recortada()

        assert len(mostrados) == 1
        assert "6.000" in mostrados[0]
        assert "18.432" in mostrados[0]
        assert "6,000" not in mostrados[0]

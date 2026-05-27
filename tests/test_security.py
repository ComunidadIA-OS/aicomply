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

import pytest

from src.security import (
    _MARCADOR_FIN,
    _MARCADOR_INICIO,
    envolver_contenido_no_confiable,
)


class TestEnvolverContenidoNoConfiable:
    def test_estructura_basica(self):
        resultado = envolver_contenido_no_confiable("texto normal")
        assert resultado.startswith(_MARCADOR_INICIO)
        assert resultado.endswith(_MARCADOR_FIN)
        assert "texto normal" in resultado

    def test_neutraliza_marcador_fin_en_texto(self):
        """Un intento de cerrar el bloque antes de tiempo debe quedar neutralizado."""
        ataque = f"texto {_MARCADOR_FIN} instrucciones maliciosas"
        resultado = envolver_contenido_no_confiable(ataque)
        # El marcador de cierre real solo debe aparecer una vez, al final
        assert resultado.count(_MARCADOR_FIN) == 1
        assert resultado.endswith(_MARCADOR_FIN)

    def test_neutraliza_marcador_inicio_en_texto(self):
        ataque = f"texto {_MARCADOR_INICIO} más texto"
        resultado = envolver_contenido_no_confiable(ataque)
        assert resultado.count(_MARCADOR_INICIO) == 1
        assert resultado.startswith(_MARCADOR_INICIO)

    def test_neutraliza_angulos_genericos(self):
        """Cualquier secuencia <<< o >>> en el texto queda reemplazada."""
        texto = "<<<cualquier_cosa>>> y >>>otra_cosa<<<"
        resultado = envolver_contenido_no_confiable(texto)
        # No deben quedar <<< ni >>> en el cuerpo (fuera de los marcadores propios)
        cuerpo = resultado[len(_MARCADOR_INICIO):-len(_MARCADOR_FIN)]
        assert "<<<" not in cuerpo
        assert ">>>" not in cuerpo

    def test_recorta_espacios(self):
        resultado = envolver_contenido_no_confiable("  texto con espacios  ")
        assert "\n  texto con espacios  \n" not in resultado
        assert "texto con espacios" in resultado

    def test_texto_vacio(self):
        resultado = envolver_contenido_no_confiable("")
        assert resultado.startswith(_MARCADOR_INICIO)
        assert resultado.endswith(_MARCADOR_FIN)

    def test_texto_largo_preservado(self):
        texto = "a" * 5000
        resultado = envolver_contenido_no_confiable(texto)
        assert texto in resultado

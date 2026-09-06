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

"""Guardianes de texto sobre el catálogo de obligaciones (prompts/system_prompt_cumplimiento.py).

Fichero aparte de test_calendario.py a propósito: allí las comprobaciones sobre el catálogo
existen porque las etiquetas de fecha son texto literal y pueden desincronizarse de
data/calendario.json. Lo que se comprueba aquí no tiene que ver con fechas, sino con la forma
de las obligaciones condicionales, y meterlo en el fichero del calendario haría que la próxima
persona lo buscara donde no está.

Como en test_prompt_evaluador.py: esto NO prueba que el modelo obedezca la regla —eso exige
una llamada real y no es determinista—, solo que la regla sigue escrita con la forma que en
los recorridos funcionó.

  B17 - el Art. 27 se declaraba carencia de una PYME privada contra la condición que el propio
        informe imprimía dos páginas después
"""

from prompts.system_prompt_cumplimiento import SYSTEM_PROMPT_CUMPLIMIENTO


class TestArt27Condicional:
    """B17. El catálogo ya enunciaba la condición correcta y el modelo la ignoró. Con el Art. 49
    no la ignoró, porque allí el prompt no se limita a enunciarla: ordena preguntar y prohíbe
    la carencia. La entrada del Art. 27 recibe ahora esa misma forma.
    """

    def test_el_art_27_sigue_una_sola_vez_bajo_implementador(self):
        assert len(_lineas_del_implementador("- Art. 27:")) == 1

    def test_ordena_preguntar_antes_de_etiquetar(self):
        """La lección de B11: enunciar la condición no basta, hay que ordenar preguntarla."""
        linea = _linea_del_art_27()
        assert "PREGUNTA" in linea
        assert "organismos de Derecho público" in linea
        assert "entidades privadas que prestan servicios públicos" in linea
        assert "Anexo III punto 5(b)" in linea and "5(c)" in linea

    def test_prohibe_la_carencia_ademas_de_condicionar(self):
        """Prohibición simétrica: la lección de B15 y B19 es que una regla escrita en una sola
        dirección se aplica de más."""
        linea = _linea_del_art_27()
        assert '"estado": "no_aplica"' in linea
        assert "NUNCA como carencia" in linea
        assert "no computa en el porcentaje de cumplimiento legal" in linea
        assert 'ni entra en "carencias"' in linea

    def test_descarta_el_empleo_por_su_punto_del_anexo_iii(self):
        """El caso real que falló: cribado de currículums es el punto 4, no el 5(b) ni el 5(c).
        Sin nombrarlo, "sistema de alto riesgo del Anexo III" se lee como supuesto suficiente."""
        linea = _linea_del_art_27()
        assert "el empleo es el punto 4" in linea
        assert "no basta" in linea

    def test_conserva_la_clave_estable(self):
        """Las obligaciones se reconcilian por clave: cambiarla parte el registro ya guardado."""
        assert "[clave: 27-evaluacion-derechos-fundamentales]" in _linea_del_art_27()

    def test_mantiene_la_etiqueta_de_aplicabilidad(self):
        assert "[Aplicable próximamente — 2 dic 2027]" in _linea_del_art_27()

    def test_tiene_la_misma_forma_que_el_art_49(self):
        """El hallazgo era exactamente ese: el arreglo existía en el artículo de al lado y no se
        había replicado. Si alguien afloja una de las dos entradas, que salte aquí."""
        art_27 = _linea_del_art_27()
        art_49 = _lineas_del_implementador("- Art. 49:")[0]
        for marca in ("obligación condicional", "PREGUNTA", '"estado": "no_aplica"',
                      "NUNCA como carencia", 'ni entra en "carencias"'):
            assert marca in art_27 and marca in art_49, f"falta {marca!r} en una de las dos"


def _lineas_del_implementador(prefijo: str) -> list[str]:
    bloque = SYSTEM_PROMPT_CUMPLIMIENTO.split("ALTO RIESGO — Rol Implementador (Art. 26):")[1]
    bloque = bloque.split("ALTO RIESGO — Rol Distribuidor")[0]
    return [ln for ln in bloque.splitlines() if ln.startswith(prefijo)]


def _linea_del_art_27() -> str:
    lineas = _lineas_del_implementador("- Art. 27:")
    assert len(lineas) == 1, f"se esperaba una sola entrada del Art. 27, hay {len(lineas)}"
    return lineas[0]

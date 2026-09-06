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

"""Guardianes de texto sobre el prompt del evaluador (prompts/system_prompts.py).

El árbol de decisión no está en código y ningún test lo ejecuta: estas comprobaciones NO
prueban que el modelo obedezca las reglas —eso exige una llamada real y no es determinista—,
solo que las reglas siguen escritas. No sustituyen al recorrido manual.

Los dos hallazgos que las motivan son la misma historia: un arreglo que se aplicó al prompt de
cumplimiento y no a este, de modo que el usuario recibía respuestas opuestas sobre el mismo
artículo en dos pestañas consecutivas.

  B19 - el evaluador atribuía al implementador el registro en la base de datos de la UE
  B21 - el evaluador se inventaba los apartados del Art. 26
"""

from prompts.system_prompts import SYSTEM_PROMPT_CHATBOT


class TestArt49NoEsDelImplementador:
    """B19. En el recorrido del 6 de septiembre, con rol implementador único y confirmado, el
    evaluador dijo «debéis solicitárselo o, en su defecto, gestionarlo vosotros», y dos
    pantallas después Cumplimiento concluyó «no aplica».
    """

    def test_la_regla_del_art_49_sigue_en_el_prompt(self):
        assert (
            "REGLA — El registro en la base de datos de la UE (Art. 49) NO es obligación "
            "del implementador:"
        ) in SYSTEM_PROMPT_CHATBOT

    def test_la_regla_ordena_preguntar_antes_de_afirmar(self):
        """La lección de B11: enunciar la condición no basta, hay que ordenar preguntarla.

        Es la forma que ya tenía la entrada del Art. 49 en el catálogo de cumplimiento, y la
        que allí sí funcionó en este mismo recorrido.
        """
        bloque = _bloque_regla_art_49()
        assert "PREGUNTA" in bloque
        assert "autoridad pública" in bloque and "organismo público" in bloque
        assert "Art. 26.8" in bloque

    def test_la_regla_prohibe_ademas_de_condicionar(self):
        """Prohibición simétrica: la lección de B15 y B17 es que una regla escrita en una sola
        dirección se aplica de más."""
        bloque = _bloque_regla_art_49()
        assert "NO le aplica" in bloque
        assert "no lo presentes como carencia" in bloque.lower()
        assert "gestione por su cuenta" in bloque, (
            "debe desactivar explícitamente la salida que se vio en el recorrido"
        )

    def test_la_notificacion_a_la_nca_esta_condicionada_al_proveedor(self):
        """La línea del catálogo que el modelo leía sin rol y aplicaba a quien fuera.

        Se busca por "Notificar a la NCA (Art." y no por el nombre a secas: el nombre también
        es un estado del árbol (#S1), y esa línea sí es correcta sin rol.
        """
        linea = _linea_que_contiene("Notificar a la NCA (Art.")
        assert "OBLIGACIÓN DEL PROVEEDOR" in linea
        assert "no se la atribuyas al implementador" in linea

    def test_el_art_71_tambien_queda_cubierto(self):
        """El recorrido citó «Art. 49 y Art. 71»: si la regla no lo nombra, se cuela por ahí."""
        assert "Arts. 49 y 71" in _bloque_regla_art_49()


def _bloque_regla_art_49() -> str:
    bloque = SYSTEM_PROMPT_CHATBOT.split("REGLA — El registro en la base de datos de la UE")[1]
    return bloque.split("Obligaciones por tipo de sistema:")[0]


def _linea_que_contiene(fragmento: str) -> str:
    lineas = [ln for ln in SYSTEM_PROMPT_CHATBOT.splitlines() if fragmento in ln]
    assert len(lineas) == 1, f"se esperaba una sola línea con {fragmento!r}, hay {len(lineas)}"
    return lineas[0]

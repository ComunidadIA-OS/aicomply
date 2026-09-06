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

import re

from prompts.system_prompts import SYSTEM_PROMPT_CHATBOT

_RE_APARTADO_26 = re.compile(r"Art\.?\s*26\.\d")


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


class TestArt26SinApartados:
    """B21. El evaluador citó «Art. 26.2» para la pertinencia de los datos de entrada (es el
    26.4) y «Art. 26.4» para los incidentes graves (es el 26.5).

    Este prompt no tiene el catálogo del Art. 26 apartado por apartado y no debe tenerlo:
    duplicarlo crearía una segunda fuente que se desincronizaría de
    system_prompt_cumplimiento.py, que es donde vive verificado contra el consolidado. La
    salida barata es la de B10: citar el artículo y nunca el apartado.
    """

    def test_el_catalogo_de_entidades_prohibe_los_apartados(self):
        linea = _linea_que_contiene("- Implementador (Art. 26):")
        assert 'Cita SIEMPRE "Art. 26" a secas, NUNCA un apartado' in linea
        assert "sin añadirle número de apartado" in linea

    def test_el_formato_del_informe_prohibe_los_apartados(self):
        linea = _linea_que_contiene("2. Tus obligaciones:")
        assert "Para el Art. 26, sin apartado" in linea
        assert '"(Art. 26)"' in linea

    def test_la_prohibicion_esta_en_los_dos_sitios(self):
        """Que no dependa solo del formato del informe: la conversación es lo que el usuario lee
        en pantalla, y es donde se vieron los apartados inventados."""
        assert SYSTEM_PROMPT_CHATBOT.count('nunca "(Art. 26.2)"') == 2

    def test_no_se_cita_ningun_apartado_del_art_26_fuera_de_las_reglas(self):
        """El guardián de verdad: si alguien añade un "Art. 26.3" al árbol en una edición
        futura, salta aquí.

        Se excluyen los tres contextos donde un apartado sí es deliberado: las dos
        prohibiciones, que citan apartados como ejemplo de lo que NO hay que escribir, y la
        regla del Art. 49, que cita el 26.8 como base legal de cuándo el implementador sí
        registra. Fuera de ahí, el prompt no numera apartados del Art. 26.
        """
        sancionadas = (
            "- Implementador (Art. 26):",
            "2. Tus obligaciones:",
            "El responsable del despliegue solo registra",
        )
        resto = [
            ln for ln in SYSTEM_PROMPT_CHATBOT.splitlines()
            if not any(marca in ln for marca in sancionadas)
        ]
        intrusos = [ln for ln in resto if _RE_APARTADO_26.search(ln)]
        assert not intrusos, f"apartados del Art. 26 fuera de las reglas: {intrusos}"

    def test_el_catalogo_del_art_26_no_se_ha_duplicado_aqui(self):
        """Duplicarlo crea una segunda fuente que se desincroniza; vive en cumplimiento."""
        assert "26.11" not in SYSTEM_PROMPT_CHATBOT
        assert "26.12" not in SYSTEM_PROMPT_CHATBOT


def _bloque_regla_art_49() -> str:
    bloque = SYSTEM_PROMPT_CHATBOT.split("REGLA — El registro en la base de datos de la UE")[1]
    return bloque.split("Obligaciones por tipo de sistema:")[0]


def _linea_que_contiene(fragmento: str) -> str:
    lineas = [ln for ln in SYSTEM_PROMPT_CHATBOT.splitlines() if fragmento in ln]
    assert len(lineas) == 1, f"se esperaba una sola línea con {fragmento!r}, hay {len(lineas)}"
    return lineas[0]

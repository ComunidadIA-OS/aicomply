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
  B22 - el Art. 49 desapareció entero del recorrido: la conclusión del evaluador llegó en
        {contexto_evaluacion} y el modelo la leyó como asunto cerrado
"""

from pathlib import Path

import pytest

from prompts.system_prompt_cumplimiento import SYSTEM_PROMPT_CUMPLIMIENTO

_RAIZ = Path(__file__).resolve().parent.parent


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


class TestCatalogoUnicaLista:
    """B22. El evaluador concluyó bien que el Art. 49 no alcanza a un implementador privado, la
    frase viajó a {contexto_evaluacion} y el modelo dejó de presentar la obligación: once
    obligaciones donde por la mañana hubo doce. La reconciliación no puede verlo —narradas y
    registradas coinciden— porque la aplicación no sabe cuántas le tocan a cada rol. El único
    sitio donde la regla puede vivir es el prompt, y aquí se comprueba que sigue escrita.
    """

    def test_la_regla_existe_en_el_bloque_de_comportamiento(self):
        assert "9. EL CATÁLOGO ES LA ÚNICA LISTA DEL RECORRIDO" in SYSTEM_PROMPT_CUMPLIMIENTO
        # La regla va donde el modelo lee el resto del procedimiento, no en el catálogo.
        assert SYSTEM_PROMPT_CUMPLIMIENTO.index("9. EL CATÁLOGO ES LA ÚNICA LISTA") < (
            SYSTEM_PROMPT_CUMPLIMIENTO.index("CATÁLOGO DE OBLIGACIONES POR CLASIFICACIÓN:")
        )

    def test_el_contexto_de_la_evaluacion_no_recorta_el_catalogo(self):
        """El mecanismo exacto de B22: lo que llega de la evaluación informa, no decide la lista."""
        regla = _regla_del_catalogo_unico()
        assert "Obligaciones ya identificadas en la evaluación" in regla
        assert "no sustituyen al catálogo" in regla.lower()
        assert "no lo recortan y no lo amplían" in regla
        assert "responde la PREGUNTA" in regla
        assert "nunca retira la OBLIGACIÓN" in regla

    def test_las_condicionales_se_registran_no_aplica_y_no_se_omiten(self):
        regla = _regla_del_catalogo_unico()
        assert "NO se omite" in regla
        assert '"estado": "no_aplica"' in regla
        assert "La condición decide el ESTADO" in regla
        assert "nunca si la obligación entra en el recorrido" in regla

    def test_lo_ya_resuelto_se_presenta_y_se_registra_sin_repreguntar(self):
        """La otra mitad: no basta con no omitirla, hay que no pagar otra vez el turno."""
        regla = _regla_del_catalogo_unico()
        assert "NO vuelvas a preguntar" in regla
        assert "quedó resuelto en la evaluación" in regla
        assert "Art. 49" in regla

    def test_recuerda_que_la_m_es_el_total_del_catalogo(self):
        """Si M encogiera con lo ya resuelto, el recuento volvería a cuadrar sobre una lista corta."""
        regla = _regla_del_catalogo_unico()
        assert '"Obligación N de M"' in regla
        assert "TOTAL de obligaciones del catálogo" in regla
        assert "no cambia" in regla

    def test_no_contradice_las_decisiones_9_y_10_de_spec_art_111(self):
        """El traspaso entre pestañas se fijó allí para el Art. 50.2 y aquí para el Art. 49: es el
        mismo mecanismo, así que las dos redacciones tienen que decir lo mismo. Se comprueba por
        frases clave compartidas, que es lo que un texto puede comprobar de otro texto.

        SPEC-ART-111.md vive en _trabajo/, que está excluido del repositorio: el test se salta
        donde el documento no existe en lugar de fallar en un clon limpio.
        """
        spec = _RAIZ / "_trabajo" / "SPEC-ART-111.md"
        if not spec.exists():
            pytest.skip("_trabajo/SPEC-ART-111.md no está en este árbol de trabajo")
        decisiones = _normalizar(_decisiones_9_y_10(spec.read_text(encoding="utf-8")))
        regla = _normalizar(_regla_del_catalogo_unico())
        for frase in ("responde la PREGUNTA", "nunca retira la OBLIGACIÓN",
                      "quedó resuelto en la evaluación"):
            assert frase in regla and frase in decisiones, (
                f"{frase!r} no aparece en las dos redacciones del mismo traspaso"
            )
        # La decisión 10 explica por qué la prosa de obligaciones_preliminares no manda:
        # es literalmente el canal que produjo B22.
        assert "obligaciones_preliminares" in decisiones


def _regla_del_catalogo_unico() -> str:
    bloque = SYSTEM_PROMPT_CUMPLIMIENTO.split("9. EL CATÁLOGO ES LA ÚNICA LISTA DEL RECORRIDO")[1]
    return bloque.split("\n10. ")[0]


def _normalizar(texto: str) -> str:
    """Colapsa saltos de línea y sangrías: el SPEC va a 100 columnas y el prompt en párrafos
    largos, así que una frase compartida cruza el salto en uno y no en el otro."""
    return " ".join(texto.replace("*", "").split())


def _decisiones_9_y_10(texto_spec: str) -> str:
    bloque = texto_spec.split("## 4. Decisiones")[1]
    return bloque.split("\n9. ")[1].split("\n11. ")[0]


def _lineas_del_implementador(prefijo: str) -> list[str]:
    bloque = SYSTEM_PROMPT_CUMPLIMIENTO.split("ALTO RIESGO — Rol Implementador (Art. 26):")[1]
    bloque = bloque.split("ALTO RIESGO — Rol Distribuidor")[0]
    return [ln for ln in bloque.splitlines() if ln.startswith(prefijo)]


def _linea_del_art_27() -> str:
    lineas = _lineas_del_implementador("- Art. 27:")
    assert len(lineas) == 1, f"se esperaba una sola entrada del Art. 27, hay {len(lineas)}"
    return lineas[0]

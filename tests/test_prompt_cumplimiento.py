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
  B25 - el bloque de LIMITADO listaba los cuatro apartados del Art. 50 sin rol y sin clave, y el
        modelo los atribuyó a quien tenía delante: a una agencia de viajes implementadora se le
        declaró carencia legal el Art. 50.2, que obliga al proveedor
"""

import re
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


class TestArt50PartidoPorRol:
    """B25. El Art. 50 reparte sus apartados entre dos roles: 50.1 y 50.2 obligan al proveedor,
    50.3 y 50.4 al responsable del despliegue. El bloque de LIMITADO los listaba en una sola
    lista sin rol, al contrario que el de ALTO, partido por rol desde B9/B14, y el modelo se los
    atribuía al rol que tuviera delante. Como en el resto del fichero: esto no prueba que el
    modelo obedezca, solo que el bloque conserva la forma que hace posible obedecerlo.
    """

    def test_el_bloque_esta_partido_por_rol_como_el_de_alto(self):
        assert "RIESGO LIMITADO — Transparencia (Art. 50) — Rol Proveedor:" in (
            SYSTEM_PROMPT_CUMPLIMIENTO
        )
        assert (
            "RIESGO LIMITADO — Transparencia (Art. 50) — Rol Responsable del despliegue"
            " (implementador):"
        ) in SYSTEM_PROMPT_CUMPLIMIENTO

    def test_cada_entrada_lleva_clave(self):
        """Sin clave, dos entradas del mismo apartado —el 50.2 obligación y el 50.2 vigilancia—
        se pisan la una a la otra en el registro, igual que pasaba con el Art. 26.5."""
        entradas = _entradas_de_limitado()
        assert entradas, "el bloque de LIMITADO debería seguir teniendo entradas"
        for entrada in entradas:
            assert re.search(r"\[clave: [^\]]+\]$", entrada.rstrip()), f"sin clave: {entrada!r}"

    def test_las_claves_no_se_repiten(self):
        claves = [re.search(r"\[clave: ([^\]]+)\]", e).group(1) for e in _entradas_de_limitado()]
        assert len(claves) == len(set(claves)), f"claves duplicadas en LIMITADO: {claves}"

    def test_el_50_1_y_el_50_2_son_del_proveedor(self):
        proveedor = _bloque_de_limitado("Rol Proveedor:")
        assert "- Art. 50.1:" in proveedor and "- Art. 50.2:" in proveedor
        assert "- Art. 50.3:" not in proveedor and "- Art. 50.4:" not in proveedor

    def test_el_50_3_y_el_50_4_son_del_responsable_del_despliegue(self):
        despliegue = _bloque_de_limitado("Rol Responsable del despliegue (implementador):")
        assert "- Art. 50.3:" in despliegue and "- Art. 50.4:" in despliegue

    def test_el_50_1_y_el_50_2_siguen_a_la_vista_del_implementador_como_vigilancia(self):
        """La doctrina de SPEC-ART-111.md: la herramienta no concede exenciones, informa. No se
        retiran de la vista; se presentan como obligación del proveedor y punto de vigilancia."""
        despliegue = _bloque_de_limitado("Rol Responsable del despliegue (implementador):")
        for entrada in ("- Art. 50.1 (vigilancia):", "- Art. 50.2 (vigilancia):"):
            assert entrada in despliegue
        for linea in _entradas_de_limitado():
            if "(vigilancia)" not in linea:
                continue
            assert "OBLIGACIÓN DEL PROVEEDOR" in linea, f"no dice de quién es: {linea!r}"
            assert 'tipo="vigilancia"' in linea
            assert "NUNCA como carencia legal" in linea
            assert "fuera del cómputo del porcentaje" in linea

    def test_el_50_4_no_es_marcado_legible_por_maquina(self):
        """El segundo defecto de B25: la línea del 50.4 describía la obligación del 50.2. El
        50.4 exige hacer público que el contenido es artificial, no marcarlo."""
        linea = _entrada_de_limitado("- Art. 50.4:")
        assert "legible por máquina" not in linea
        assert "HACER PÚBLICO" in linea
        assert "generado o manipulado de manera artificial" in linea

    def test_el_50_4_recoge_sus_dos_supuestos(self):
        """Son los que deciden si aplica: sin ellos, publicidad comercial sin ultrasuplantaciones
        se lee como supuesto cubierto."""
        linea = _entrada_de_limitado("- Art. 50.4:")
        assert "ULTRASUPLANTACIÓN" in linea
        assert "interés público" in linea
        assert 'estado": "no_aplica"' in linea and "NUNCA como carencia" in linea

    def test_el_50_2_conserva_su_etiqueta_condicional_por_fecha_de_mercado(self):
        """Verificado en el recorrido del 7 de septiembre: esta parte funciona y no se toca.
        Vale para las dos entradas, la del proveedor y la de vigilancia."""
        for prefijo in ("- Art. 50.2:", "- Art. 50.2 (vigilancia):"):
            linea = _entrada_de_limitado(prefijo)
            assert "etiqueta condicional" in linea
            assert "PREGUNTA primero si el sistema estaba en el mercado antes del 2 ago 2026" in (
                linea
            )
            assert "[Aplicable próximamente — 2 dic 2026]" in linea
            assert "[Aplicable actualmente — desde 2 ago 2026]" in linea


def _bloque_de_limitado(cabecera_rol: str = "") -> str:
    """El bloque de LIMITADO entero, o solo el de un rol. Termina en 'MÍNIMO:', que es la
    siguiente clasificación del catálogo."""
    bloque = SYSTEM_PROMPT_CUMPLIMIENTO.split("RIESGO LIMITADO — Transparencia (Art. 50):")[1]
    bloque = bloque.split("\nMÍNIMO:")[0]
    if not cabecera_rol:
        return bloque
    trozos = bloque.split(f"RIESGO LIMITADO — Transparencia (Art. 50) — {cabecera_rol}")
    assert len(trozos) == 2, f"no hay una sola cabecera {cabecera_rol!r} en LIMITADO"
    return trozos[1].split("\nRIESGO LIMITADO —")[0]


def _entradas_de_limitado() -> list[str]:
    return [ln for ln in _bloque_de_limitado().splitlines() if ln.startswith("- Art. 50")]


def _entrada_de_limitado(prefijo: str) -> str:
    lineas = [ln for ln in _entradas_de_limitado() if ln.startswith(prefijo)]
    assert len(lineas) == 1, f"se esperaba una sola entrada {prefijo!r}, hay {len(lineas)}"
    return lineas[0]


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

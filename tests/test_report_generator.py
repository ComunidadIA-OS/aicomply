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

import re

import pytest

from src.report_generator import GeneradorInforme, _limpiar

# ── Fixtures de datos ──────────────────────────────────────────────────────────

_CLASIFICACION = {
    "clasificacion": "ALTO",
    "rol": "proveedor",
    "roles_multiples": [],
    "descripcion_sistema": "Sistema de reconocimiento facial en entornos industriales",
    "sector": "Seguridad industrial",
    "estados_adicionales": [],
    "obligaciones_preliminares": [],
    "puntos_indeterminados": ["¿El sistema se usa en infraestructura crítica?"],
}

_CUMPLIMIENTO = {
    "obligaciones": [
        {
            "articulo": "Art. 9",
            "titulo": "Gestión de riesgos",
            "descripcion": "Requiere sistema documentado de gestión de riesgos.",
            "estado": "cubierta",
        },
        {
            "articulo": "Art. 10",
            "titulo": "Gobernanza de datos",
            "descripcion": "Requiere políticas de datos de entrenamiento.",
            "estado": "carencia",
        },
    ],
    "carencias_detectadas": ["Falta documentación técnica (Anexo IV)", "Sin registro de actividad (Art. 12)"],
    "puntos_revision_profesional": ["Revisar si aplica Art. 6.2"],
    "resumen_cumplimiento": "Cumplimiento parcial. Dos áreas críticas pendientes.",
}


def _nums_seccion(texto: str) -> list[int]:
    """Extrae los números de las secciones ## N. del Markdown."""
    return [int(m) for m in re.findall(r"^## (\d+)\.", texto, re.MULTILINE)]


# ── Tests de numeración (regresión issue #12) ─────────────────────────────────

class TestNumeracionSecciones:
    def test_clasificacion_numeracion_consecutiva(self):
        md = GeneradorInforme().generar_informe_clasificacion(_CLASIFICACION)
        nums = _nums_seccion(md)
        assert len(nums) >= 3
        assert nums == list(range(1, len(nums) + 1)), f"Numeración no consecutiva: {nums}"

    def test_cumplimiento_numeracion_consecutiva(self):
        md = GeneradorInforme().generar_informe_cumplimiento(_CLASIFICACION, _CUMPLIMIENTO)
        nums = _nums_seccion(md)
        assert len(nums) >= 4
        assert nums == list(range(1, len(nums) + 1)), f"Numeración no consecutiva: {nums}"

    def test_completo_numeracion_consecutiva(self):
        md = GeneradorInforme().generar_informe_completo(_CLASIFICACION, _CUMPLIMIENTO)
        nums = _nums_seccion(md)
        assert len(nums) >= 6
        assert nums == list(range(1, len(nums) + 1)), f"Numeración no consecutiva: {nums}"

    def test_completo_tiene_7_secciones(self):
        md = GeneradorInforme().generar_informe_completo(_CLASIFICACION, _CUMPLIMIENTO)
        assert _nums_seccion(md) == list(range(1, 8))

    def test_clasificacion_empieza_en_1(self):
        md = GeneradorInforme().generar_informe_clasificacion(_CLASIFICACION)
        nums = _nums_seccion(md)
        assert nums[0] == 1

    def test_sin_salto_en_numeracion(self):
        md = GeneradorInforme().generar_informe_completo(_CLASIFICACION, _CUMPLIMIENTO)
        nums = _nums_seccion(md)
        for i in range(len(nums) - 1):
            assert nums[i + 1] == nums[i] + 1, f"Salto entre sección {nums[i]} y {nums[i+1]}"


# ── Tests de transliteración _limpiar() (regresión issue #13) ─────────────────

class TestLimpiar:
    def test_bullet_a_guion(self):
        assert _limpiar("• item") == "- item"

    def test_em_dash_a_guion(self):
        assert _limpiar("A — B") == "A - B"

    def test_en_dash_a_guion(self):
        assert _limpiar("A – B") == "A - B"

    def test_comilla_doble_izquierda(self):
        assert _limpiar("“Hola”") == '"Hola"'

    def test_comilla_simple_curva(self):
        assert _limpiar("‘Hola’") == "'Hola'"

    def test_puntos_suspensivos_unicode(self):
        assert _limpiar("texto…") == "texto..."

    def test_guillemets_a_comillas(self):
        assert _limpiar("«Ejemplo»") == '"Ejemplo"'

    def test_texto_ascii_sin_cambios(self):
        texto = "Texto normal sin caracteres especiales."
        assert _limpiar(texto) == texto

    def test_espanol_latino_sin_cambios(self):
        # Tildes y eñe son válidos en latin-1, deben pasar intactos
        texto = "El sistema tiene obligaciones según el reglamento de la UE."
        assert _limpiar(texto) == texto

    def test_resultado_codificable_latin1(self):
        # El resultado nunca debe fallar al codificarse en latin-1
        texto = "Texto con • bullets — guiones “citas” y más"
        resultado = _limpiar(texto)
        resultado.encode("latin-1")  # no debe lanzar UnicodeEncodeError


# ── Tests de exportar_texto_plano() ──────────────────────────────────────────

class TestExportarTextoPlano:
    def test_elimina_encabezados_h1(self):
        resultado = GeneradorInforme().exportar_texto_plano("# Título principal\ncontenido")
        assert "# " not in resultado
        assert "Título principal" in resultado

    def test_elimina_encabezados_h2(self):
        resultado = GeneradorInforme().exportar_texto_plano("## Sección 2\ncontenido")
        assert "## " not in resultado
        assert "Sección 2" in resultado

    def test_elimina_negrita(self):
        resultado = GeneradorInforme().exportar_texto_plano("Texto **negrita** aquí")
        assert "**" not in resultado
        assert "negrita" in resultado

    def test_elimina_cursiva(self):
        resultado = GeneradorInforme().exportar_texto_plano("Texto *cursiva* aquí")
        assert "*cursiva*" not in resultado
        assert "cursiva" in resultado

    def test_elimina_blockquotes(self):
        resultado = GeneradorInforme().exportar_texto_plano("> Aviso importante")
        assert resultado == "Aviso importante"

    def test_no_lineas_en_blanco_excesivas(self):
        resultado = GeneradorInforme().exportar_texto_plano("p1\n\n\n\n\np2")
        assert "\n\n\n" not in resultado

    def test_informe_completo_sin_marcas_markdown(self):
        md = GeneradorInforme().generar_informe_completo(_CLASIFICACION, _CUMPLIMIENTO)
        txt = GeneradorInforme().exportar_texto_plano(md)
        assert "##" not in txt
        assert "**" not in txt
        assert len(txt) > 100  # tiene contenido real


# ── Tests de _seccion_carencias siempre devuelve contenido (regresión #12) ────

class TestSeccionCarenciasContenido:
    def test_sin_carencias_devuelve_seccion(self):
        g = GeneradorInforme()
        resultado = g._seccion_carencias(3, [])
        assert resultado.startswith("## 3.")
        assert "No se identificaron" in resultado

    def test_con_carencias_lista_completa(self):
        g = GeneradorInforme()
        resultado = g._seccion_carencias(5, ["Carencia A", "Carencia B"])
        assert "Carencia A" in resultado
        assert "Carencia B" in resultado


# ── Tests de exportar_pdf() ───────────────────────────────────────────────────

class TestExportarPdf:
    def _informe(self) -> str:
        return GeneradorInforme().generar_informe_completo(_CLASIFICACION, _CUMPLIMIENTO)

    def test_pdf_devuelve_bytes(self):
        pdf = GeneradorInforme().exportar_pdf(self._informe())
        assert isinstance(pdf, bytes)

    def test_pdf_no_vacio(self):
        pdf = GeneradorInforme().exportar_pdf(self._informe())
        assert len(pdf) > 500

    def test_pdf_empieza_con_cabecera_pdf(self):
        pdf = GeneradorInforme().exportar_pdf(self._informe())
        assert pdf[:4] == b"%PDF"

    def test_pdf_con_titulo_personalizado(self):
        pdf = GeneradorInforme().exportar_pdf(self._informe(), titulo="Informe de Prueba")
        assert isinstance(pdf, bytes) and len(pdf) > 500

    def test_pdf_markdown_con_todos_los_formatos(self):
        md = (
            "# Título H1\n## Sección H2\n### Subsección H3\n#### Sub-sub H4\n"
            "> Blockquote de aviso\n"
            "- item de lista\n"
            "**negrita** y texto normal\n"
            "---\n"
            "Párrafo final.\n"
        )
        pdf = GeneradorInforme().exportar_pdf(md)
        assert pdf[:4] == b"%PDF"

    def test_pdf_informe_clasificacion(self):
        md = GeneradorInforme().generar_informe_clasificacion(_CLASIFICACION)
        pdf = GeneradorInforme().exportar_pdf(md)
        assert pdf[:4] == b"%PDF"

    def test_pdf_informe_cumplimiento(self):
        md = GeneradorInforme().generar_informe_cumplimiento(_CLASIFICACION, _CUMPLIMIENTO)
        pdf = GeneradorInforme().exportar_pdf(md)
        assert pdf[:4] == b"%PDF"


# ── Tests de tipo obligacion/recomendacion/vigilancia ────────────────────────

def _obl(art, titulo, estado, tipo="obligacion"):
    return {"articulo": art, "titulo": titulo, "descripcion": "", "estado": estado, "tipo": tipo}


_MINIMO_CLASIF = {
    "clasificacion": "MINIMO",
    "rol": "proveedor",
    "roles_multiples": [],
    "descripcion_sistema": "Sistema de recomendación interno",
    "sector": "Industria",
    "estados_adicionales": [],
    "obligaciones_preliminares": [],
    "puntos_indeterminados": [],
}


class TestCumplimientoLegalVsRecomendaciones:
    """Garantiza que las recomendaciones no reducen el porcentaje de cumplimiento legal."""

    def test_minimo_sin_legales_solo_recomendaciones(self):
        """Caso B: sin obligaciones legales — debe decir 'No aplicable', no 0 %."""
        cumpl = {
            "obligaciones": [
                _obl("Art. 95", "Códigos de conducta", "carencia", "recomendacion"),
                _obl("Vigilancia", "Cambios de uso", "carencia", "vigilancia"),
            ],
            "carencias_detectadas": [],
            "puntos_revision_profesional": [],
            "resumen_cumplimiento": "",
        }
        md = GeneradorInforme().generar_informe_cumplimiento(_MINIMO_CLASIF, cumpl)
        assert "No aplicable" in md
        assert "0 %" not in md
        assert "100 %" not in md

    def test_minimo_una_legal_cubierta_y_dos_recomendaciones(self):
        """Caso A: 1 obligación cubierta + 2 recomendaciones pendientes → 100 %."""
        cumpl = {
            "obligaciones": [
                _obl("Art. 4", "Alfabetización IA", "cubierta", "obligacion"),
                _obl("Art. 95", "Códigos de conducta", "carencia", "recomendacion"),
                _obl("Vigilancia", "Cambios de uso", "carencia", "vigilancia"),
            ],
            "carencias_detectadas": [],
            "puntos_revision_profesional": [],
            "resumen_cumplimiento": "",
        }
        md = GeneradorInforme().generar_informe_cumplimiento(_MINIMO_CLASIF, cumpl)
        assert "100 %" in md
        assert "33 %" not in md

    def test_minimo_una_legal_parcial_y_recomendaciones(self):
        """Caso C: 1 obligación parcial + recomendaciones → 50 %, no 33 %."""
        cumpl = {
            "obligaciones": [
                _obl("Art. 4", "Alfabetización IA", "parcial", "obligacion"),
                _obl("Art. 95", "Códigos de conducta", "carencia", "recomendacion"),
                _obl("Vigilancia", "Cambios de uso", "carencia", "vigilancia"),
            ],
            "carencias_detectadas": [],
            "puntos_revision_profesional": [],
            "resumen_cumplimiento": "",
        }
        md = GeneradorInforme().generar_informe_cumplimiento(_MINIMO_CLASIF, cumpl)
        assert "50 %" in md
        assert "33 %" not in md

    def test_alto_riesgo_recomendaciones_no_bajan_porcentaje(self):
        """Recomendaciones en alto riesgo no reducen el porcentaje de cumplimiento legal."""
        cumpl = {
            "obligaciones": [
                _obl("Art. 9", "Gestión de riesgos", "cubierta", "obligacion"),
                _obl("Art. 10", "Gobernanza de datos", "cubierta", "obligacion"),
                _obl("Art. 95", "Códigos de conducta", "carencia", "recomendacion"),
            ],
            "carencias_detectadas": [],
            "puntos_revision_profesional": [],
            "resumen_cumplimiento": "",
        }
        md = GeneradorInforme().generar_informe_cumplimiento(_CLASIFICACION, cumpl)
        assert "100 %" in md
        assert "67 %" not in md

    def test_recomendaciones_aparecen_en_seccion_b(self):
        """Las recomendaciones deben aparecer en la sección B, no en obligaciones legales."""
        cumpl = {
            "obligaciones": [
                _obl("Art. 4", "Alfabetización IA", "cubierta", "obligacion"),
                _obl("Art. 95", "Códigos de conducta", "carencia", "recomendacion"),
            ],
            "carencias_detectadas": [],
            "puntos_revision_profesional": [],
            "resumen_cumplimiento": "",
        }
        md = GeneradorInforme().generar_informe_cumplimiento(_MINIMO_CLASIF, cumpl)
        assert "B. Recomendaciones" in md
        assert "Recomendación pendiente" in md

    def test_vigilancia_aparece_en_seccion_c(self):
        """Las medidas prudenciales deben aparecer en la sección C."""
        cumpl = {
            "obligaciones": [
                _obl("Vigilancia", "Cambios de uso", "carencia", "vigilancia"),
            ],
            "carencias_detectadas": [],
            "puntos_revision_profesional": [],
            "resumen_cumplimiento": "",
        }
        md = GeneradorInforme().generar_informe_cumplimiento(_MINIMO_CLASIF, cumpl)
        assert "C. Medidas prudenciales" in md
        assert "Medida prudencial pendiente" in md

    def test_retrocompatibilidad_sin_campo_tipo(self):
        """Obligaciones sin campo tipo se tratan como obligacion (retrocompatibilidad)."""
        cumpl = {
            "obligaciones": [
                {"articulo": "Art. 9", "titulo": "Gestión de riesgos",
                 "descripcion": "", "estado": "cubierta"},  # sin tipo
            ],
            "carencias_detectadas": [],
            "puntos_revision_profesional": [],
            "resumen_cumplimiento": "",
        }
        md = GeneradorInforme().generar_informe_cumplimiento(_CLASIFICACION, cumpl)
        assert "100 %" in md

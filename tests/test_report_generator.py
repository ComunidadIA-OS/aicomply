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

from src.calendario import obtener_version
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


class TestPorcentajeSinEvaluar:
    """Las obligaciones 'no aplica' (no_evaluada) no deben reducir el porcentaje."""

    def test_sin_evaluar_no_penaliza(self):
        """2 cubiertas + 3 no aplica → 100 %, no 40 %."""
        cumpl = {
            "obligaciones": [
                _obl("Art. 9",  "Gestión de riesgos",    "cubierta"),
                _obl("Art. 10", "Gobernanza de datos",    "cubierta"),
                _obl("Art. 11", "Documentación técnica",  "no_aplica"),
                _obl("Art. 12", "Registro de actividad",  "no_aplica"),
                _obl("Art. 13", "Instrucciones de uso",   "no_aplica"),
            ],
            "carencias_detectadas": [],
            "puntos_revision_profesional": [],
            "resumen_cumplimiento": "",
        }
        md = GeneradorInforme().generar_informe_cumplimiento(_CLASIFICACION, cumpl)
        assert "100 %" in md
        assert "40 %" not in md

    def test_sin_evaluar_mixto(self):
        """1 cubierta + 1 carencia + 2 no aplica → 50 %, no 25 %."""
        cumpl = {
            "obligaciones": [
                _obl("Art. 9",  "Gestión de riesgos",    "cubierta"),
                _obl("Art. 10", "Gobernanza de datos",    "carencia"),
                _obl("Art. 11", "Documentación técnica",  "no_aplica"),
                _obl("Art. 12", "Registro de actividad",  "no_aplica"),
            ],
            "carencias_detectadas": [],
            "puntos_revision_profesional": [],
            "resumen_cumplimiento": "",
        }
        md = GeneradorInforme().generar_informe_cumplimiento(_CLASIFICACION, cumpl)
        assert "50 %" in md
        assert "25 %" not in md

    def test_todos_sin_evaluar_muestra_cero(self):
        """Si todas las legales están no aplica, el porcentaje es 0 %."""
        cumpl = {
            "obligaciones": [
                _obl("Art. 9",  "Gestión de riesgos",   "no_aplica"),
                _obl("Art. 10", "Gobernanza de datos",   "no_aplica"),
            ],
            "carencias_detectadas": [],
            "puntos_revision_profesional": [],
            "resumen_cumplimiento": "",
        }
        md = GeneradorInforme().generar_informe_cumplimiento(_CLASIFICACION, cumpl)
        assert "0 %" in md


# ── Calendario normativo en el informe (regresión A1, A2, A3) ─────────────────

class TestCalendarioEnElInforme:
    """El informe es lo que se lleva la PYME: no puede citar fechas caducadas."""

    def test_alto_riesgo_cita_las_fechas_firmes_del_omnibus(self):
        md = GeneradorInforme().generar_informe_completo(_CLASIFICACION, _CUMPLIMIENTO)
        assert "2 de diciembre de 2027" in md
        assert "2 de agosto de 2028" in md
        assert "Reglamento (UE) 2026/1744" in md

    def test_alto_riesgo_no_presenta_el_calendario_como_provisional(self):
        md = GeneradorInforme().generar_informe_completo(_CLASIFICACION, _CUMPLIMIENTO)
        for frase in ("pendiente de publicacion", "pendiente de publicación",
                      "plazo provisional", "acuerdo Omnibus", "calendario final"):
            assert frase not in md

    def test_limitado_corrige_la_fecha_del_art_50_1(self):
        """A2: decía «en vigor desde agosto de 2025», que es la fecha de GPAI."""
        clas = dict(_CLASIFICACION, clasificacion="LIMITADO")
        md = GeneradorInforme().generar_informe_completo(clas, _CUMPLIMIENTO)
        assert "2 de agosto de 2026" in md
        assert "agosto de 2025" not in md

    def test_limitado_distingue_los_dos_casos_del_art_50_2(self):
        """A3: el 2 dic 2026 solo cubre sistemas ya en el mercado antes del 2 ago 2026."""
        clas = dict(_CLASIFICACION, clasificacion="LIMITADO")
        md = GeneradorInforme().generar_informe_completo(clas, _CUMPLIMIENTO)
        assert "2 de diciembre de 2026" in md
        assert "ya estaba en el mercado antes de esa fecha" in md

    def test_el_pie_declara_la_version_del_calendario(self):
        """Tocar una fecha ya no mueve PROMPT_VERSION: el informe debe declarar
        con qué calendario se generó."""
        md = GeneradorInforme().generar_informe_completo(_CLASIFICACION, _CUMPLIMIENTO)
        assert f"Calendario v{obtener_version()}" in md

    def test_el_pdf_se_genera_con_las_tildes_reintroducidas(self):
        """C1: _limpiar() codifica a latin-1, que admite tildes y ñ."""
        pdf = GeneradorInforme().exportar_pdf(
            GeneradorInforme().generar_informe_completo(_CLASIFICACION, _CUMPLIMIENTO)
        )
        assert pdf.startswith(b"%PDF")


# ── Plan de acción de ALTO por rol (regresión B9) ─────────────────────────────

def _plan_de_accion(md: str) -> str:
    """Recorta la sección «Plan de acción recomendado» del informe completo.

    El recorte aísla la sección que se está comprobando. Nació porque la sección 3
    imprimía su lista por defecto de ALTO —toda de proveedor— fuese cual fuese el rol,
    y sin recortar «el implementador no ve el Art. 43» fallaba por ese otro defecto
    (B14) y no por el plan. B14 ya está corregido; el recorte se conserva para que cada
    test siga hablando de una sola sección.
    """
    m = re.search(r"^## \d+\. Plan de acción recomendado$(.*?)(?=^## \d+\.)",
                  md, re.MULTILINE | re.DOTALL)
    assert m, "El informe no contiene la sección de plan de acción"
    return m.group(1)


def _plan_para(**campos) -> str:
    """Plan de acción del informe completo de ALTO con los roles indicados."""
    clas = dict(_CLASIFICACION, **campos)
    return _plan_de_accion(GeneradorInforme().generar_informe_completo(clas, _CUMPLIMIENTO))


class TestPlanAccionPorRol:
    """B9: el plan de ALTO no puede pedirle a un implementador obligaciones del proveedor."""

    def test_implementador_no_recibe_obligaciones_del_proveedor(self):
        plan = _plan_para(rol="implementador", roles_multiples=["implementador"])
        assert "marcado CE" not in plan
        assert "Art. 43" not in plan
        assert "Art. 17" not in plan
        assert "Art. 11" not in plan  # documentación técnica del Anexo IV

    def test_implementador_recibe_las_obligaciones_del_art_26(self):
        plan = _plan_para(rol="implementador", roles_multiples=["implementador"])
        assert "Obligaciones como implementador (Art. 26)" in plan
        for apartado in ("Art. 26.1", "Art. 26.2", "Art. 26.3", "Art. 26.5",
                         "Art. 26.6", "Art. 26.7", "Art. 26.10", "Art. 26.11"):
            assert apartado in plan, f"Falta el {apartado} en el plan del implementador"
        assert "Art. 27" in plan  # evaluación de impacto, cuando proceda

    def test_proveedor_si_recibe_las_obligaciones_del_proveedor(self):
        plan = _plan_para(rol="proveedor", roles_multiples=["proveedor"])
        assert "Obligaciones como proveedor (Art. 16)" in plan
        assert "marcado CE" in plan
        assert "Art. 43" in plan
        assert "Art. 17" in plan
        assert "Obligaciones como implementador" not in plan

    def test_doble_rol_recibe_los_dos_bloques_y_un_solo_bloque_comun(self):
        plan = _plan_para(rol="proveedor / implementador",
                          roles_multiples=["proveedor", "implementador"])
        assert "Obligaciones como proveedor (Art. 16)" in plan
        assert "Obligaciones como implementador (Art. 26)" in plan
        assert plan.count("### Acciones comunes a cualquier rol") == 1

    def test_los_roles_se_deducen_del_campo_rol_si_no_hay_lista(self):
        """El campo 'rol' puede traer varios roles separados por '/'."""
        plan = _plan_para(rol="proveedor / implementador", roles_multiples=[])
        assert "Obligaciones como proveedor (Art. 16)" in plan
        assert "Obligaciones como implementador (Art. 26)" in plan

    def test_distribuidor_recibe_el_art_24_y_no_los_bloques_ajenos(self):
        plan = _plan_para(rol="distribuidor", roles_multiples=["distribuidor"])
        assert "Obligaciones como distribuidor (Art. 24)" in plan
        assert "Art. 16" not in plan
        assert "Art. 26" not in plan

    def test_importador_recibe_el_art_23(self):
        plan = _plan_para(rol="importador", roles_multiples=["importador"])
        assert "Obligaciones como importador (Art. 23)" in plan
        assert "Art. 16" not in plan
        assert "Art. 26" not in plan

    def test_representante_autorizado_recibe_los_arts_22_y_54(self):
        plan = _plan_para(rol="representante_autorizado",
                          roles_multiples=["representante_autorizado"])
        assert "Arts. 22 y 54" in plan
        assert "Art. 26" not in plan

    def test_fabricante_asume_las_obligaciones_del_proveedor(self):
        """Art. 25 en relación con el Anexo I: el fabricante recibe además el bloque de proveedor."""
        plan = _plan_para(rol="fabricante", roles_multiples=["fabricante"])
        assert "Art. 25" in plan
        assert "Obligaciones como proveedor (Art. 16)" in plan
        assert "marcado CE" in plan

    def test_rol_sin_determinar_presenta_los_bloques_como_alternativos(self):
        plan = _plan_para(rol="no especificado", roles_multiples=[])
        assert "Si su entidad es proveedora del sistema (Art. 16)" in plan
        assert "Si su entidad es implementadora del sistema (Art. 26)" in plan
        assert "No se ha podido determinar el rol" in plan
        assert "Evaluador y clasificador" in plan

    def test_el_plan_conserva_las_tildes_y_es_codificable_en_latin1(self):
        plan = _plan_para(rol="implementador", roles_multiples=["implementador"])
        assert "Preparación" in plan
        assert "supervisión" in plan
        _limpiar(plan).encode("latin-1")  # no debe lanzar UnicodeEncodeError

    def test_el_plan_sigue_listando_las_areas_de_mejora(self):
        plan = _plan_para(rol="implementador", roles_multiples=["implementador"])
        assert "Áreas de mejora detectadas (2):" in plan
        assert "Falta documentación técnica (Anexo IV)" in plan

    def test_el_pdf_se_genera_con_los_bloques_por_rol(self):
        md = GeneradorInforme().generar_informe_completo(
            dict(_CLASIFICACION, rol="implementador", roles_multiples=["implementador"]),
            _CUMPLIMIENTO,
        )
        assert GeneradorInforme().exportar_pdf(md).startswith(b"%PDF")


# ── Obligaciones preliminares de ALTO por rol (regresión B14) ─────────────────

_ARTS_PROVEEDOR = ("Art. 9", "Art. 10", "Art. 11", "Art. 12", "Art. 13",
                   "Art. 14", "Art. 15", "Art. 43", "Art. 49")


def _preliminares(md: str) -> str:
    """Recorta la sección «Obligaciones identificadas durante la evaluación»."""
    m = re.search(r"^## \d+\. Obligaciones identificadas durante la evaluación$(.*?)(?=^## \d+\.)",
                  md, re.MULTILINE | re.DOTALL)
    assert m, "El informe no contiene la sección de obligaciones preliminares"
    return m.group(1)


def _preliminares_para(**campos) -> str:
    """Sección 3 del informe completo de ALTO con los roles indicados.

    'obligaciones_preliminares' va vacío a propósito: es el caso en que el evaluador no
    extrajo nada de la conversación y la sección cae en la lista por defecto del catálogo.
    """
    clas = dict(_CLASIFICACION, obligaciones_preliminares=[], **campos)
    return _preliminares(GeneradorInforme().generar_informe_completo(clas, _CUMPLIMIENTO))


class TestObligacionesPreliminaresPorRol:
    """B14: la lista por defecto de ALTO no puede ser la del proveedor para todos los roles."""

    def test_implementador_no_recibe_obligaciones_del_proveedor(self):
        seccion = _preliminares_para(rol="implementador", roles_multiples=["implementador"])
        for art in _ARTS_PROVEEDOR:
            assert art not in seccion, f"El implementador no debe ver el {art} en la sección 3"
        assert "marcado CE" not in seccion

    def test_implementador_recibe_las_obligaciones_del_art_26(self):
        seccion = _preliminares_para(rol="implementador", roles_multiples=["implementador"])
        assert "Obligaciones como implementador (Art. 26)" in seccion
        for apartado in ("Art. 26.1", "Art. 26.2", "Art. 26.3", "Art. 26.5",
                         "Art. 26.6", "Art. 26.7", "Art. 26.10", "Art. 26.11"):
            assert apartado in seccion, f"Falta el {apartado} en la sección 3 del implementador"
        assert "Art. 27" in seccion  # evaluación de impacto, cuando proceda

    def test_proveedor_si_recibe_las_obligaciones_del_proveedor(self):
        seccion = _preliminares_para(rol="proveedor", roles_multiples=["proveedor"])
        assert "Obligaciones como proveedor (Art. 16)" in seccion
        for art in _ARTS_PROVEEDOR:
            assert art in seccion, f"El proveedor debe seguir viendo el {art}"
        assert "Obligaciones como implementador" not in seccion

    def test_doble_rol_recibe_los_dos_bloques(self):
        seccion = _preliminares_para(rol="proveedor / implementador",
                                     roles_multiples=["proveedor", "implementador"])
        assert "Obligaciones como proveedor (Art. 16)" in seccion
        assert "Obligaciones como implementador (Art. 26)" in seccion

    def test_distribuidor_recibe_el_art_24_y_no_los_bloques_ajenos(self):
        seccion = _preliminares_para(rol="distribuidor", roles_multiples=["distribuidor"])
        assert "Obligaciones como distribuidor (Art. 24)" in seccion
        assert "Art. 16" not in seccion
        assert "Art. 26" not in seccion
        assert "Art. 49" not in seccion

    def test_importador_recibe_el_art_23(self):
        seccion = _preliminares_para(rol="importador", roles_multiples=["importador"])
        assert "Obligaciones como importador (Art. 23)" in seccion
        assert "Art. 43" not in seccion

    def test_representante_autorizado_recibe_los_arts_22_y_54(self):
        seccion = _preliminares_para(rol="representante_autorizado",
                                     roles_multiples=["representante_autorizado"])
        assert "Arts. 22 y 54" in seccion
        assert "Art. 26" not in seccion

    def test_fabricante_asume_las_obligaciones_del_proveedor(self):
        seccion = _preliminares_para(rol="fabricante", roles_multiples=["fabricante"])
        assert "Art. 25" in seccion
        assert "Obligaciones como proveedor (Art. 16)" in seccion

    def test_rol_sin_determinar_presenta_los_bloques_como_alternativos(self):
        seccion = _preliminares_para(rol="no especificado", roles_multiples=[])
        assert "Si su entidad es proveedora del sistema (Art. 16)" in seccion
        assert "Si su entidad es implementadora del sistema (Art. 26)" in seccion
        assert "No se ha podido determinar el rol" in seccion

    def test_la_lista_extraida_por_el_evaluador_manda_sobre_la_del_catalogo(self):
        """Con obligaciones extraídas, la sección las imprime tal cual y no toca el catálogo."""
        clas = dict(_CLASIFICACION, rol="implementador", roles_multiples=["implementador"],
                    obligaciones_preliminares=["Supervisión humana (Art. 26)"])
        seccion = _preliminares(
            GeneradorInforme().generar_informe_completo(clas, _CUMPLIMIENTO)
        )
        assert "Supervisión humana (Art. 26)" in seccion
        assert "Obligaciones como implementador (Art. 26)" not in seccion

    def test_los_niveles_distintos_de_alto_no_cambian(self):
        """LIMITADO conserva su lista literal: el sesgo de rol del Art. 50 es B12."""
        seccion = _preliminares_para(clasificacion="LIMITADO", rol="implementador",
                                     roles_multiples=["implementador"])
        assert "Art. 50.1" in seccion
        assert "Obligaciones como implementador" not in seccion

    def test_el_pdf_se_genera_con_la_seccion_3_por_rol(self):
        md = GeneradorInforme().generar_informe_completo(
            dict(_CLASIFICACION, rol="implementador", roles_multiples=["implementador"],
                 obligaciones_preliminares=[]),
            _CUMPLIMIENTO,
        )
        assert GeneradorInforme().exportar_pdf(md).startswith(b"%PDF")

    def test_el_informe_de_clasificacion_tambien_construye_la_seccion_por_rol(self):
        """La sección 3 vive en los dos informes que la incluyen."""
        clas = dict(_CLASIFICACION, rol="implementador", roles_multiples=["implementador"],
                    obligaciones_preliminares=[])
        md = GeneradorInforme().generar_informe_clasificacion(clas)
        seccion = _preliminares(md)
        assert "Obligaciones como implementador (Art. 26)" in seccion
        assert "Art. 43" not in seccion

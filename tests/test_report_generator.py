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
import zlib
from pathlib import Path

import pytest

from prompts.system_prompt_cumplimiento import SYSTEM_PROMPT_CUMPLIMIENTO
from src.calendario import obtener_obligacion, obtener_version
from src.clasificaciones import CLASIFICACIONES_SIN_OBLIGACIONES
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


class TestEtiquetaDeLaMetrica:
    """B6: la cifra mide avance de trabajo, no conformidad jurídica.

    En el Anexo III no existe el cumplimiento parcial. Un «60 % de cumplimiento legal»
    en un informe que documenta tres carencias invita a leer «vamos bien» donde la
    lectura correcta es «faltan obligaciones por implementar».
    """

    _CON_CARENCIAS = {
        "obligaciones": [
            _obl("Art. 9",  "Gestión de riesgos",   "cubierta"),
            _obl("Art. 10", "Gobernanza de datos",  "parcial"),
            _obl("Art. 11", "Documentación técnica", "carencia"),
        ],
        "carencias_detectadas": [],
        "puntos_revision_profesional": [],
        "resumen_cumplimiento": "",
    }

    def test_la_metrica_se_llama_avance_de_implementacion(self):
        md = GeneradorInforme().generar_informe_cumplimiento(
            _CLASIFICACION, self._CON_CARENCIAS
        )
        assert "**Avance de implementación:** 50 %" in md
        assert "cumplimiento legal estimado" not in md

    def test_los_recuentos_siguen_debajo_de_la_cifra(self):
        """La etiqueta cambia; lo que hay debajo son hechos y no se toca."""
        md = GeneradorInforme().generar_informe_cumplimiento(
            _CLASIFICACION, self._CON_CARENCIAS
        )
        assert "Cubiertas: 1 | Parciales: 1 | No cubiertas: 1 | No aplica: 0" in md

    def test_el_pdf_se_exporta_con_la_nueva_etiqueta(self):
        """Humo: el PDF saca el porcentaje parseando esta línea del markdown, así que la
        exportación tiene que seguir recorriéndola sin romperse."""
        md = GeneradorInforme().generar_informe_cumplimiento(
            _CLASIFICACION, self._CON_CARENCIAS
        )
        assert GeneradorInforme().exportar_pdf(md).startswith(b"%PDF")


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


# B18: los apartados del Art. 26 que sí son del responsable del despliegue. El 26.3 (cláusula
# de «no afecta a otras obligaciones»), el 26.8 (registro del Art. 49, solo autoridades
# públicas), el 26.9 (EIDF) y el 26.10 (identificación biométrica remota posterior con fines
# policiales) NO son obligaciones a exigir a una PYME industrial.
_APARTADOS_ART_26_IMPLEMENTADOR = ("26.1", "26.2", "26.4", "26.5", "26.6", "26.7",
                                   "26.11", "26.12")
_APARTADOS_ART_26_AJENOS = ("26.3", "26.8", "26.9", "26.10")


def _cita_apartado(texto: str, apartado: str) -> bool:
    """¿Cita `texto` ese apartado exacto? '26.1' no puede casar dentro de '26.11'."""
    return re.search(rf"Art\. {re.escape(apartado)}(?!\d)", texto) is not None


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
        for apartado in _APARTADOS_ART_26_IMPLEMENTADOR:
            assert _cita_apartado(plan, apartado), (
                f"Falta el Art. {apartado} en el plan del implementador"
            )
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


# ── Plan de acción de LIMITADO por rol (regresión B12) ───────────────────────

def _plan_limitado_para(**campos) -> str:
    """Plan de acción del informe completo de LIMITADO con los roles indicados."""
    clas = dict(_CLASIFICACION, clasificacion="LIMITADO", **campos)
    return _plan_de_accion(GeneradorInforme().generar_informe_completo(clas, _CUMPLIMIENTO))


# Las instrucciones en primera persona del 50.1 y del 50.2: lo que un responsable del
# despliegue NO debe recibir, porque esos dos apartados obligan al proveedor.
_ORDENES_DEL_PROVEEDOR = (
    "Añadir aviso claro en la interfaz",
    "los resultados de salida deben quedar marcados",
)

# Los cinco casos de rol que el plan de LIMITADO distingue: cada uno de los dos roles del
# Art. 50 por separado, los dos juntos, el rol sin determinar y un rol al que el Art. 50 no
# dirige apartados (distribuidor), que cae en la misma rama que el indeterminado.
_TODOS_LOS_CASOS_DE_ROL = (
    {"rol": "implementador", "roles_multiples": ["implementador"]},
    {"rol": "proveedor", "roles_multiples": ["proveedor"]},
    {"rol": "proveedor/implementador", "roles_multiples": ["proveedor", "implementador"]},
    {"rol": "", "roles_multiples": []},
    {"rol": "distribuidor", "roles_multiples": ["distribuidor"]},
)


class TestPlanLimitadoPorRol:
    """B12, la misma familia que B9 pero en el Art. 50. `pasos_por_nivel["LIMITADO"]` era
    texto fijo por clasificación y no miraba el rol, así que a una agencia de viajes
    implementadora el informe le decía en la sección 2.C que el Art. 50.1 es obligación de su
    proveedor y que a ella le toca verificarlo, y tres párrafos más abajo le ordenaba «añadir
    aviso claro en la interfaz de que el sistema usa IA». El documento se contradecía a sí
    mismo en dos secciones consecutivas.

    La dirección del error importa: que un paso pase de «hágalo» a «verifique que su proveedor
    lo hace» es correcto; que desaparezca, no. Por eso cada test que comprueba una ausencia
    tiene al lado otro que comprueba que el contenido sigue estando en su forma de vigilancia.
    """

    def test_el_implementador_no_recibe_las_ordenes_del_50_1_ni_del_50_2(self):
        plan = _plan_limitado_para(rol="implementador", roles_multiples=["implementador"])
        for orden in _ORDENES_DEL_PROVEEDOR:
            assert orden not in plan, f"le ordena en primera persona algo del proveedor: {orden!r}"

    def test_el_implementador_si_recibe_los_dos_puntos_de_vigilancia(self):
        """La otra mitad, y la que impide que el arreglo se pase de frenada: el 50.1 y el 50.2
        no se le retiran de la vista, cambian de forma."""
        plan = _plan_limitado_para(rol="implementador", roles_multiples=["implementador"])
        assert "Puntos de vigilancia sobre su proveedor (Art. 50.1 y 50.2)" in plan
        assert "Art. 50.1 — obligación de su proveedor" in plan
        assert "Art. 50.2 — obligación de su proveedor" in plan
        assert plan.count("exigirlo por contrato") + plan.count("exigírselo por contrato") == 2

    def test_el_implementador_recibe_sus_apartados_propios(self):
        """El 50.3 y el 50.4 son suyos, y antes no aparecían en el plan de ningún rol."""
        plan = _plan_limitado_para(rol="implementador", roles_multiples=["implementador"])
        assert "Obligaciones como responsable del despliegue (Art. 50.3 y 50.4)" in plan
        assert "Art. 50.3" in plan
        assert "ultrasuplantación (deep fake)" in plan
        assert "interés público" in plan

    def test_el_proveedor_si_recibe_las_ordenes_del_50_1_y_del_50_2(self):
        plan = _plan_limitado_para(rol="proveedor", roles_multiples=["proveedor"])
        assert "Obligaciones como proveedor (Art. 50.1 y 50.2)" in plan
        for orden in _ORDENES_DEL_PROVEEDOR:
            assert orden in plan

    def test_el_proveedor_no_recibe_los_puntos_de_vigilancia(self):
        """Verificar que su proveedor cumple no tiene sentido para quien ES el proveedor."""
        plan = _plan_limitado_para(rol="proveedor", roles_multiples=["proveedor"])
        assert "Puntos de vigilancia sobre su proveedor" not in plan

    def test_el_doble_rol_no_duplica_el_50_1_ni_el_50_2(self):
        """La regla de doble rol del catálogo: si concurren los dos roles, el 50.1 y el 50.2 son
        obligaciones suyas en primera persona y la verificación sería decir dos veces lo mismo."""
        plan = _plan_limitado_para(rol="proveedor/implementador",
                                   roles_multiples=["proveedor", "implementador"])
        assert "Obligaciones como proveedor (Art. 50.1 y 50.2)" in plan
        assert "Obligaciones como responsable del despliegue (Art. 50.3 y 50.4)" in plan
        assert "Puntos de vigilancia sobre su proveedor" not in plan
        for orden in _ORDENES_DEL_PROVEEDOR:
            assert plan.count(orden) == 1

    def test_sin_rol_determinado_se_presentan_los_dos_bloques_como_alternativos(self):
        """Como en `_plan_alto`: sin rol no se elige por el usuario, se le dice que elija. La
        herramienta no concede exenciones, informa."""
        plan = _plan_limitado_para(rol="", roles_multiples=[])
        assert "Los bloques siguientes son alternativos" in plan
        assert "Si su entidad es proveedora del sistema (Art. 50.1 y 50.2)" in plan
        assert "Si su entidad es responsable del despliegue (Art. 50.3 y 50.4)" in plan
        for orden in _ORDENES_DEL_PROVEEDOR:
            assert orden in plan

    def test_ningun_rol_pierde_el_50_1_ni_el_50_2(self):
        """El guardián de la dirección del error. El plan viejo llevaba el 50.1 y el 50.2 para
        todo el mundo; el nuevo puede cambiar quién los ejecuta —orden para el proveedor,
        verificación para el responsable del despliegue— pero no puede hacerlos desaparecer del
        documento de ningún rol."""
        for campos in _TODOS_LOS_CASOS_DE_ROL:
            plan = _plan_limitado_para(**campos)
            for apartado in ("Art. 50.1", "Art. 50.2"):
                assert apartado in plan, f"{apartado} desaparece del plan con {campos}"

    def test_el_50_3_y_el_50_4_llegan_a_quien_los_tiene(self):
        """La mitad complementaria. Un proveedor puro NO los recibe, y es correcto: obligan al
        responsable del despliegue y ahí el proveedor no tiene ni siquiera un punto de
        vigilancia, al revés de lo que le pasa al implementador con el 50.1 y el 50.2."""
        for campos in _TODOS_LOS_CASOS_DE_ROL:
            plan = _plan_limitado_para(**campos)
            tiene_despliegue = "implementador" in (campos["roles_multiples"] or [])
            solo_proveedor = campos["roles_multiples"] == ["proveedor"]
            for apartado in ("Art. 50.3", "Art. 50.4"):
                if solo_proveedor:
                    assert apartado not in plan, f"{apartado} no es del proveedor: {campos}"
                elif tiene_despliegue or not campos["roles_multiples"]:
                    assert apartado in plan, f"falta {apartado} con {campos}"

    def test_el_condicional_de_la_fecha_del_50_2_sigue_en_los_dos_roles(self):
        """Verificado en el recorrido del 7 de septiembre y fuera del alcance de B12: el plazo
        del Art. 111.4 acompaña al 50.2 tanto si se ejecuta como si se verifica."""
        for campos in (
            {"rol": "implementador", "roles_multiples": ["implementador"]},
            {"rol": "proveedor", "roles_multiples": ["proveedor"]},
        ):
            plan = _plan_limitado_para(**campos)
            assert "La fecha depende de cuándo se introdujo el sistema en el mercado" in plan
            assert "2 de agosto de 2026" in plan
            assert "ya estaba en el mercado antes de esa fecha" in plan
            assert "2 de diciembre de 2026" in plan

    def test_el_plan_de_limitado_sigue_listando_las_areas_de_mejora(self):
        plan = _plan_limitado_para(rol="implementador", roles_multiples=["implementador"])
        assert "Áreas de mejora detectadas (2):" in plan

    def test_el_pdf_de_limitado_se_genera_con_los_bloques_por_rol(self):
        md = GeneradorInforme().generar_informe_completo(
            dict(_CLASIFICACION, clasificacion="LIMITADO",
                 rol="implementador", roles_multiples=["implementador"]),
            _CUMPLIMIENTO,
        )
        assert GeneradorInforme().exportar_pdf(md).startswith(b"%PDF")


# ── Informe de una clasificación sin obligaciones (regresión B33) ────────────

# Las dos clasificaciones que cierran el recorrido sin obligaciones del AI Act. Se toman de
# src/clasificaciones.py y no se escriben aquí a mano: si alguien añade una tercera, estos
# tests la cubren solos, que es justo lo que no pasó cuando se añadió la segunda.
_SIN_OBLIGACIONES = sorted(CLASIFICACIONES_SIN_OBLIGACIONES)


def _informes_sin_obligaciones(clasificacion: str) -> dict[str, str]:
    """Los dos informes que la aplicación genera para esa clasificación.

    'rol' llega como «No aplica» a propósito: es lo que la aplicación pone cuando el recorrido
    termina antes del Bloque #E, y es el valor que producía la frase rota.
    """
    clas = dict(_CLASIFICACION, clasificacion=clasificacion, rol="No aplica",
                roles_multiples=[], obligaciones_preliminares=[], estados_adicionales=[])
    generador = GeneradorInforme()
    return {
        "clasificación": generador.generar_informe_clasificacion(clas),
        "completo": generador.generar_informe_completo(clas, _CUMPLIMIENTO),
    }


class TestInformeSinObligaciones:
    """B33. El recorrido del ejemplo 00 terminó bien y el documento salió mal en dos sitios.

    El informe abría con «La entidad actúa como **No aplica**» —primera línea del resumen
    ejecutivo— porque la frase se armaba siempre, y ahí no había rol: la comprobación de la
    definición del Art. 3.1 es previa al Bloque #E. Y titulaba «Obligaciones identificadas
    durante la evaluación» una sección de la que colgaban una conclusión y tres
    recomendaciones, ninguna obligación. Misma familia que B28: un título que desmiente lo que
    tiene debajo.

    Los dos defectos estaban en el informe de clasificación y en el completo, así que todo se
    comprueba en los dos. El informe que el modelo escribe en el chat ya lo hacía mejor —«2. Sus
    obligaciones: Ninguna»—: el documento que se descarga era la versión peor de lo mismo.

    OJO con la condición: lo que decide la frase del rol es el ROL, no la clasificación. Las dos
    cosas no van juntas. EXCLUIDO tampoco tiene obligaciones y SÍ tiene rol, porque la exclusión
    se resuelve en #R2 o en #S1, después del Bloque #E. El primer arreglo condicionó la frase a
    `es_sin_obligaciones()` y con eso borraba «La entidad actúa como Proveedor» del informe del
    ejemplo 05, que está publicado en el repositorio y es correcto. El título de la sección 3 sí
    depende de la clasificación, y para EXCLUIDO también es el bueno: tampoco tiene obligaciones.
    """

    @pytest.mark.parametrize("clasificacion", _SIN_OBLIGACIONES)
    def test_no_dice_que_la_entidad_actua_como_no_aplica(self, clasificacion):
        for nombre, md in _informes_sin_obligaciones(clasificacion).items():
            assert "actúa como" not in md, (
                f"el informe {nombre} de {clasificacion} sigue construyendo la frase del rol"
            )
            assert "No aplica**" not in md

    @pytest.mark.parametrize("clasificacion", _SIN_OBLIGACIONES)
    def test_no_titula_obligaciones_una_seccion_sin_obligaciones(self, clasificacion):
        for nombre, md in _informes_sin_obligaciones(clasificacion).items():
            assert "Obligaciones identificadas durante la evaluación" not in md, (
                f"el informe {nombre} de {clasificacion} conserva el título que desmiente"
            )

    @pytest.mark.parametrize("clasificacion", _SIN_OBLIGACIONES)
    def test_el_titulo_describe_lo_que_cuelga_de_el(self, clasificacion):
        for md in _informes_sin_obligaciones(clasificacion).values():
            assert "Conclusión de la evaluación y acciones recomendadas" in md

    @pytest.mark.parametrize("clasificacion", _SIN_OBLIGACIONES)
    def test_responde_explicitamente_que_no_hay_obligaciones(self, clasificacion):
        """Lo que hacía bien el informe del chat y no el descargable: decirlo, no solo omitirlo."""
        for md in _informes_sin_obligaciones(clasificacion).values():
            assert "**Obligaciones del AI Act aplicables:** ninguna." in md

    @pytest.mark.parametrize("clasificacion", _SIN_OBLIGACIONES)
    def test_conserva_la_razon_y_la_clasificacion(self, clasificacion):
        """El guardián de la dirección del error: quitar la frase del rol y renombrar el título
        no puede llevarse por delante el contenido que sí era correcto."""
        for md in _informes_sin_obligaciones(clasificacion).values():
            assert clasificacion in md
            assert "Reglamento (UE) 2024/1689" in md
            assert "documentar esta evaluación" in md

    @pytest.mark.parametrize("clasificacion", _SIN_OBLIGACIONES)
    def test_los_dos_informes_coinciden_en_las_dos_secciones(self, clasificacion):
        """El defecto estaba en los dos y el arreglo tiene que estarlo también: si alguien
        corrige uno solo, vuelve la incoherencia entre el documento corto y el largo."""
        informes = _informes_sin_obligaciones(clasificacion)
        for marca in ("Conclusión de la evaluación y acciones recomendadas",
                      "**Obligaciones del AI Act aplicables:** ninguna."):
            faltan = [n for n, md in informes.items() if marca not in md]
            assert not faltan, f"{marca!r} falta en el informe {faltan}"

    def test_una_clasificacion_con_rol_conserva_la_frase(self):
        """La mitad simétrica: el arreglo no puede callar el rol cuando sí lo hay."""
        md = GeneradorInforme().generar_informe_completo(
            dict(_CLASIFICACION, rol="implementador", roles_multiples=["implementador"]),
            _CUMPLIMIENTO,
        )
        assert "La entidad actúa como **Implementador**." in md

    def test_excluido_con_rol_conserva_la_frase(self):
        """El caso que el simétrico de arriba NO cubre, porque aquel usa una clasificación CON
        obligaciones y por tanto pasa aunque la condición mire la clasificación en vez del rol.

        Es el ejemplo 05 tal como está publicado: PYME proveedora de un sistema de imagen
        térmica de uso exclusivamente militar, EXCLUIDO por el Art. 2.3 y con el rol determinado
        en el Bloque #E, mucho antes de la exclusión. Su informe dice «La entidad actúa como
        Proveedor», y regenerarlo no puede quitárselo.
        """
        clas = dict(_CLASIFICACION, clasificacion="EXCLUIDO", rol="proveedor",
                    roles_multiples=["proveedor"], obligaciones_preliminares=[],
                    estados_adicionales=[])
        generador = GeneradorInforme()
        for nombre, md in (("clasificación", generador.generar_informe_clasificacion(clas)),
                           ("completo", generador.generar_informe_completo(clas, _CUMPLIMIENTO))):
            assert "La entidad actúa como **Proveedor**." in md, (
                f"el informe {nombre} de un EXCLUIDO con rol ha perdido la frase"
            )
            # Y sigue sin llamar «obligaciones» a lo que no lo es: las dos cosas son
            # independientes, y este caso es el que lo demuestra.
            assert "Obligaciones identificadas durante la evaluación" not in md
            assert "Conclusión de la evaluación y acciones recomendadas" in md

    @pytest.mark.parametrize("clasificacion", _SIN_OBLIGACIONES)
    def test_el_pdf_se_genera_para_las_dos_clasificaciones(self, clasificacion):
        for md in _informes_sin_obligaciones(clasificacion).values():
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
        for apartado in _APARTADOS_ART_26_IMPLEMENTADOR:
            assert _cita_apartado(seccion, apartado), (
                f"Falta el Art. {apartado} en la sección 3 del implementador"
            )
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
        """La sección 3 de LIMITADO conserva su lista literal. B12 cerró el sesgo de rol del
        Art. 50 en el PLAN (sección 4/6, `_plan_limitado`), no aquí: esta lista sigue siendo
        plana y sin rol, que es el mismo defecto que B14 arregló para ALTO en esta sección."""
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


# ── Numeración de los apartados del Art. 26 (regresión B18) ───────────────────


class TestApartadosArt26:
    """B18: tres apartados citados con el número equivocado y el 26.11 real ausente.

    Contrastado con el Reglamento (UE) 2024/1689 consolidado a 27 de julio de 2026:
    la pertinencia de los datos de entrada es el 26.4 (no el 26.3), la notificación de
    incidentes graves es el 26.5 (no el 26.10, que es identificación biométrica remota
    posterior con fines policiales) y la cooperación con las autoridades es el 26.12
    (no el 26.11, que es informar a las personas físicas afectadas).
    """

    def test_el_plan_del_implementador_cita_los_apartados_correctos(self):
        plan = _plan_para(rol="implementador", roles_multiples=["implementador"])
        for apartado in _APARTADOS_ART_26_AJENOS:
            assert not _cita_apartado(plan, apartado), (
                f"El Art. {apartado} no es una obligación del implementador de este catálogo"
            )

    def test_la_seccion_3_del_implementador_cita_los_apartados_correctos(self):
        seccion = _preliminares_para(rol="implementador", roles_multiples=["implementador"])
        for apartado in _APARTADOS_ART_26_AJENOS:
            assert not _cita_apartado(seccion, apartado), (
                f"El Art. {apartado} no es una obligación del implementador de este catálogo"
            )

    def test_el_catalogo_del_prompt_cita_los_mismos_apartados_que_el_informe(self):
        """El prompt y el informe son dos copias a mano de la misma lista: deben coincidir."""
        bloque = SYSTEM_PROMPT_CUMPLIMIENTO.split(
            "ALTO RIESGO — Rol Implementador (Art. 26):")[1].split("ALTO RIESGO — Rol Distribuidor")[0]
        for apartado in _APARTADOS_ART_26_IMPLEMENTADOR:
            assert _cita_apartado(bloque, apartado), f"Falta el Art. {apartado} en el catálogo"
        for apartado in _APARTADOS_ART_26_AJENOS:
            assert not _cita_apartado(bloque, apartado), (
                f"El Art. {apartado} no debería estar en el catálogo del implementador"
            )

    def test_las_dos_caras_del_26_5_se_distinguen(self):
        """El 26.5 tiene dos obligaciones separables: vigilar el uso y notificar incidentes
        graves. Fundirlas en una haría que una PYME con auditorías periódicas y sin
        procedimiento del Art. 73 quedase registrada como cubierta."""
        plan = _plan_para(rol="implementador", roles_multiples=["implementador"])
        assert plan.count("(Art. 26.5)") == 2
        assert "Art. 73" in plan
        assert "incidentes graves" in plan.lower()

    def test_el_implementador_debe_informar_a_las_personas_afectadas(self):
        """El 26.11 real: para un sistema que criba currículums es la obligación más
        visible frente al candidato, y no estaba en el catálogo."""
        plan = _plan_para(rol="implementador", roles_multiples=["implementador"])
        assert _cita_apartado(plan, "26.11")
        assert "personas físicas" in plan
        assert "Anexo III" in plan

    def test_ningun_apartado_ajeno_sobrevive_en_prompts_ni_src(self):
        """Los apartados están escritos a mano en varios sitios; el fallo era una copia
        desincronizada. Este test recorre el código fuente entero, no solo el informe."""
        raiz = Path(__file__).resolve().parent.parent
        obsoletos = re.compile(r"Art\. 26\.3(?!\d)|Art\. 26\.10(?!\d)|Art\. 26\.11 — [Cc]ooperación")
        for fichero in [*(raiz / "prompts").rglob("*.py"), *(raiz / "src").rglob("*.py")]:
            if "__pycache__" in fichero.parts:
                continue
            texto = fichero.read_text(encoding="utf-8")
            assert not obsoletos.search(texto), (
                f"{fichero.relative_to(raiz)} sigue citando un apartado obsoleto del Art. 26"
            )


# ── PROHIBIDO: sin porcentaje (regresión B34) ─────────────────────────────────

_PROHIBIDO_CLASIF = {
    "clasificacion": "PROHIBIDO",
    "rol": "implementador",
    "roles_multiples": ["implementador"],
    "descripcion_sistema": (
        "Análisis de la voz de los agentes durante las llamadas para inferir su estado "
        "emocional y generar un indicador de engagement"
    ),
    "sector": "Contact center",
    "estados_adicionales": [],
    "obligaciones_preliminares": [],
    "puntos_indeterminados": [],
}


def _cumplimiento_prohibido(estado_prohibicion: str) -> dict:
    """El registro del ejemplo 04: la prohibición del Art. 5 y el Art. 4 transversal."""
    return {
        "obligaciones": [
            {
                "articulo": "Art. 5",
                "titulo": "Práctica de IA prohibida",
                "clave": "5-practica-prohibida",
                "descripcion": "Reconocimiento de emociones en el lugar de trabajo (Art. 5.1.f).",
                "estado": estado_prohibicion,
                "tipo": "obligacion",
            },
            {
                "articulo": "Art. 4",
                "titulo": "Alfabetización en IA",
                "clave": "4-alfabetizacion",
                "descripcion": "Formación anual del personal.",
                "estado": "cubierta",
                "tipo": "obligacion",
            },
        ],
        "carencias_detectadas": ["El sistema prohibido sigue en funcionamiento"],
        "puntos_revision_profesional": [],
        "resumen_cumplimiento": (
            "La organización se encuentra en situación de incumplimiento de una prohibición."
        ),
    }


def _seccion_de_obligaciones(md: str) -> str:
    """La sección «Análisis de obligaciones», que es donde vive la cifra.

    El plan de acción cita legítimamente el 7 % del Art. 99.3, así que la prohibición de
    porcentajes se comprueba donde la cifra significaba grado de cumplimiento y no donde
    significa una multa.
    """
    partes = re.split(r"^## \d+\. ", md, flags=re.MULTILINE)
    seccion = [p for p in partes if p.startswith("Análisis de obligaciones")]
    assert len(seccion) == 1, "el informe debería tener una sección de análisis de obligaciones"
    return seccion[0]


def _texto_del_pdf(pdf: bytes) -> str:
    """El texto de los flujos del PDF, descomprimido. fpdf2 los comprime por defecto; si
    algún día dejara de hacerlo, el flujo crudo ya es legible y sirve igual."""
    trozos = []
    for m in re.finditer(rb"stream\r?\n(.*?)endstream", pdf, re.S):
        try:
            trozos.append(zlib.decompress(m.group(1)))
        except zlib.error:
            trozos.append(m.group(1))
    return b"".join(trozos).decode("latin-1")


class TestProhibidoSinPorcentaje:
    """B34. Un contact center analizaba la voz de sus 90 agentes para inferir su estado
    emocional (Art. 5.1.f). El sistema seguía activo; el asistente registró la prohibición
    como PARCIAL —«existe una intención formal de cumplimiento»— y con dos obligaciones
    cubiertas sobre tres el informe abrió con «Avance de implementación: 83 %» sobre un
    sistema ilegal en funcionamiento, mientras su propio resumen decía lo contrario.

    En PROHIBIDO la cifra no es que esté mal calculada: es que no mide nada. Una prohibición
    no tiene grados. Se suprime con el mismo mecanismo que ya la suprime cuando el registro
    es incoherente, y en su lugar va el estado de la prohibición.

    El camino normal ya no pasa por aquí —PROHIBIDO no llega a la pestaña Cumplimiento y no
    produce registro—, pero la clase se conserva: sí llegan las sesiones guardadas antes de
    ese cambio y cualquier registro importado, y sin esta defensa el 83 % vuelve por ahí.
    """

    def test_el_informe_no_publica_porcentaje_con_la_prohibicion_incumplida(self):
        md = GeneradorInforme().generar_informe_cumplimiento(
            _PROHIBIDO_CLASIF, _cumplimiento_prohibido("carencia")
        )
        seccion = _seccion_de_obligaciones(md)
        assert not re.search(r"\d+\s*%", seccion), f"la sección publica una cifra:\n{seccion}"
        assert "Avance de implementación" not in md
        assert "Grado de cumplimiento" not in md

    def test_el_informe_no_publica_porcentaje_con_la_prohibicion_atendida(self):
        """El caso simétrico: sistema detenido. Tampoco entonces hay un grado que publicar,
        y un 100 % sería tan falso como el 83 %."""
        md = GeneradorInforme().generar_informe_cumplimiento(
            _PROHIBIDO_CLASIF, _cumplimiento_prohibido("cubierta")
        )
        seccion = _seccion_de_obligaciones(md)
        assert not re.search(r"\d+\s*%", seccion), f"la sección publica una cifra:\n{seccion}"
        assert "Avance de implementación" not in md

    def test_en_su_lugar_dice_si_la_prohibicion_esta_atendida(self):
        gen = GeneradorInforme()
        activo = gen.generar_informe_cumplimiento(
            _PROHIBIDO_CLASIF, _cumplimiento_prohibido("carencia")
        )
        detenido = gen.generar_informe_cumplimiento(
            _PROHIBIDO_CLASIF, _cumplimiento_prohibido("cubierta")
        )
        assert "**Estado de la prohibición (Art. 5):** No atendida" in activo
        assert "El sistema sigue en funcionamiento" in activo
        assert "**Estado de la prohibición (Art. 5):** Atendida" in detenido

    def test_un_parcial_que_llegue_igualmente_no_se_publica_como_parcial(self):
        """El catálogo lo prohíbe, pero el estado lo escribe el modelo y el informe no puede
        confiar en que la regla se haya seguido: era exactamente el estado que produjo B34."""
        md = GeneradorInforme().generar_informe_cumplimiento(
            _PROHIBIDO_CLASIF, _cumplimiento_prohibido("parcial")
        )
        assert "**Estado de la prohibición (Art. 5):** No atendida" in md
        assert not re.search(r"\d+\s*%", _seccion_de_obligaciones(md))

    def test_los_recuentos_siguen_debajo(self):
        """Lo que se suprime es la magnitud sin sentido; los recuentos son hechos."""
        md = GeneradorInforme().generar_informe_cumplimiento(
            _PROHIBIDO_CLASIF, _cumplimiento_prohibido("carencia")
        )
        assert "Cubiertas: 1 | Parciales: 0 | No cubiertas: 1 | No aplica: 0" in md

    def test_el_plan_de_remediacion_sigue_intacto(self):
        """La clasificación ya construía bien el plan: eso no se toca."""
        md = GeneradorInforme().generar_informe_cumplimiento(
            _PROHIBIDO_CLASIF, _cumplimiento_prohibido("carencia")
        )
        assert "**Pasos de remediación recomendados:**" in md
        assert "**Inmediato:** Suspender el desarrollo y despliegue del sistema" in md
        assert "**Revisión profesional:**" in md

    def test_el_pdf_tampoco_dibuja_la_barra_de_porcentaje(self):
        """El PDF saca la cifra parseando la línea del markdown. Sin reconocer la etiqueta
        nueva, el parser se quedaba en su 0 inicial y dibujaba una barra de «0 %», que es
        otra cifra falsa en vez de ninguna."""
        md = GeneradorInforme().generar_informe_cumplimiento(
            _PROHIBIDO_CLASIF, _cumplimiento_prohibido("carencia")
        )
        pdf = GeneradorInforme().exportar_pdf(md)
        assert pdf.startswith(b"%PDF")
        texto = _texto_del_pdf(pdf)
        # Los paréntesis van escapados dentro de las cadenas del PDF.
        assert r"Estado de la prohibición \(Art. 5\)" in texto
        assert "No atendida" in texto
        assert "Avance de implementación" not in texto
        # La cifra de la barra se dibuja en una celda propia: «(50 %) Tj». El 7 % del Art. 99.3
        # que cita el plan viaja dentro de una frase y no en una celda suya.
        assert not re.search(r"\(\d+ %\) Tj", texto), "el PDF sigue dibujando un porcentaje"

    def test_las_demas_clasificaciones_conservan_su_cifra(self):
        """La supresión es de PROHIBIDO, no general: en ALTO la cifra mide avance de trabajo
        y sigue siendo útil (B6)."""
        md = GeneradorInforme().generar_informe_cumplimiento(_CLASIFICACION, _CUMPLIMIENTO)
        assert "**Avance de implementación:**" in md


class TestEstadoDeLaProhibicionNoSeConfundeDeArticulo:
    """El estado de la prohibición se busca por la clave, y el respaldo por artículo no puede
    capturar el Art. 50.

    La entrada del Art. 5 lleva `[clave: 5-practica-prohibida]` desde el cierre de B34, pero
    los registros guardados antes no la tienen, y son exactamente aquellos en los que el
    modelo se traía el Art. 50.3 del bloque de LIMITADO y lo marcaba «cubierta». Un respaldo
    escrito como `startswith("Art. 5")` acepta «Art. 50.3», «Art. 50.1» y «Art. 54»: en un
    registro al que le falte la prohibición —omitida por el modelo, o vaciada— el informe
    publicaba «Estado de la prohibición (Art. 5): Atendida» sobre un sistema prohibido en
    funcionamiento. Es B34 otra vez, en la dirección peligrosa y sin ruido.

    Como la clase anterior: el camino normal ya no produce estos registros, pero los que
    llegan de una sesión guardada o importada siguen entrando por aquí.
    """

    def test_un_art_50_3_cubierta_no_ocupa_el_sitio_de_la_prohibicion_ausente(self):
        """La forma exacta del registro que produjo B34: sin Art. 5 y con el Art. 50.3 que el
        modelo trajo de LIMITADO, cubierta y sin clave."""
        cumplimiento = {
            "obligaciones": [
                {
                    "articulo": "Art. 50.3",
                    "titulo": "Informar del reconocimiento de emociones",
                    "descripcion": "Se informa a los agentes de que se analiza su voz.",
                    "estado": "cubierta",
                    "tipo": "obligacion",
                },
            ],
            "carencias_detectadas": [],
            "puntos_revision_profesional": [],
            "resumen_cumplimiento": "Registro incompleto.",
        }
        md = GeneradorInforme().generar_informe_cumplimiento(_PROHIBIDO_CLASIF, cumplimiento)
        assert "**Estado de la prohibición (Art. 5):** No consta" in md
        assert "**Estado de la prohibición (Art. 5):** Atendida" not in md

    def test_el_respaldo_por_articulo_sigue_cogiendo_el_art_5_1_f_sin_clave(self):
        """Acotar el respaldo no puede perder el caso legítimo: el registro antiguo en el que
        la prohibición está, sin clave, citada por su letra."""
        cumplimiento = {
            "obligaciones": [
                {
                    "articulo": "Art. 5.1.f",
                    "titulo": "Práctica de IA prohibida",
                    "descripcion": "Reconocimiento de emociones en el lugar de trabajo.",
                    "estado": "carencia",
                    "tipo": "obligacion",
                },
            ],
            "carencias_detectadas": ["El sistema prohibido sigue en funcionamiento"],
            "puntos_revision_profesional": [],
            "resumen_cumplimiento": "Incumplimiento de una prohibición.",
        }
        md = GeneradorInforme().generar_informe_cumplimiento(_PROHIBIDO_CLASIF, cumplimiento)
        assert "**Estado de la prohibición (Art. 5):** No atendida" in md

    def test_la_clave_manda_sobre_el_orden_del_registro(self):
        """El Art. 50.3 va ANTES que la prohibición en la lista. Buscar «la primera entrada
        que sirva» devolvería la de arriba; la clave es la identidad y no depende del orden."""
        cumplimiento = _cumplimiento_prohibido("carencia")
        cumplimiento["obligaciones"].insert(
            0,
            {
                "articulo": "Art. 50.3",
                "titulo": "Informar del reconocimiento de emociones",
                "descripcion": "Se informa a los agentes de que se analiza su voz.",
                "estado": "cubierta",
                "tipo": "obligacion",
            },
        )
        md = GeneradorInforme().generar_informe_cumplimiento(_PROHIBIDO_CLASIF, cumplimiento)
        assert "**Estado de la prohibición (Art. 5):** No atendida" in md

    def test_un_prohibido_sin_obligaciones_legales_no_dice_que_no_hay_nada_que_evaluar(self):
        """Con el registro legal vacío —todo anotado como vigilancia—, la rama de «no se
        identifican obligaciones legales evaluables» se colaba delante de la de PROHIBIDO y
        dejaba una frase tranquilizadora sobre un sistema prohibido. PROHIBIDO va primero, y
        el estado sale «No consta», que es ruidoso a propósito."""
        cumplimiento = {
            "obligaciones": [
                {
                    "articulo": "Art. 4",
                    "titulo": "Alfabetización en IA",
                    "descripcion": "Formación anual del personal.",
                    "estado": "cubierta",
                    "tipo": "vigilancia",
                },
            ],
            "carencias_detectadas": [],
            "puntos_revision_profesional": [],
            "resumen_cumplimiento": "Registro legal vacío.",
        }
        md = GeneradorInforme().generar_informe_cumplimiento(_PROHIBIDO_CLASIF, cumplimiento)
        assert "No se identifican obligaciones legales evaluables" not in md
        assert "**Estado de la prohibición (Art. 5):** No consta" in md


class TestLaSancionSeCitaComoLaCitaElReglamento:
    """El Art. 99.3 aparece en dos sitios del informe, y los dos decían «el 7 % de la
    facturación global», que no es la fórmula del Reglamento. Con el catálogo mandando decir
    el literal, el mismo documento llevaría dos redacciones de la misma cifra delante de un
    lector jurídico. Y la segunda de esas redacciones omitía el Art. 99.6, que es el apartado
    que puede invertir la regla del importe mayor para las pymes: los destinatarios de esta
    herramienta.
    """

    def test_las_obligaciones_del_evaluador_citan_el_art_99_3_completo(self):
        md = GeneradorInforme().generar_informe_clasificacion(_PROHIBIDO_CLASIF)
        assert "35.000.000 EUR o el 7 % del volumen de negocios mundial total" in md
        assert "si esta cuantía fuese superior (Art. 99.3)" in md
        assert "facturación global" not in md

    def test_el_recuadro_nombra_el_matiz_de_las_pymes(self):
        """El Art. 99.6 es una facultad («podrá ser»), no un mandato, y por eso va como matiz.
        Sin él, un informe para una pyme presenta solo el tramo alto y sesga la cifra.

        La cita estaba en el blockquote que abría el plan de acción; ahora está en el recuadro
        de advertencia, que es el mismo texto en un sitio donde se ve en los tres formatos."""
        md = GeneradorInforme().generar_informe_cumplimiento(
            _PROHIBIDO_CLASIF, _cumplimiento_prohibido("carencia")
        )
        assert "Las sanciones del Art. 99.3 alcanzan 35.000.000 EUR" in md
        assert "correspondiente al ejercicio financiero anterior, si esta cuantía fuese superior" in md
        assert "el Art. 99.6 prevé que la multa pueda ser el importe o el porcentaje" in md
        assert "según cuál de ellos sea menor" in md
        assert "facturación global" not in md
        assert "Consulte urgentemente con un asesor legal especializado" in md

    def test_las_tildes_de_la_cita_sobreviven_al_pdf(self):
        """El PDF codifica a latin-1 en _limpiar(): «cuantía», «prevé», «según cuál», la ñ de
        «pymes». Si algo no cupiera, la exportación reventaría o dejaría el texto mutilado.

        Las aserciones son de trozos cortos porque fpdf2 parte las líneas al ancho de la caja
        y el texto llega al flujo troceado."""
        md = GeneradorInforme().generar_informe_cumplimiento(
            _PROHIBIDO_CLASIF, _cumplimiento_prohibido("carencia")
        )
        texto = _texto_del_pdf(GeneradorInforme().exportar_pdf(md))
        assert "negocios mundial total correspondiente al ejercicio financiero anterior" in texto
        assert "si esta cuantía fuese superior" in texto
        assert "En el caso de las pymes, el Art. 99.6 prevé" in texto
        assert "según cuál de ellos sea" in texto


# ── PROHIBIDO: la lista la construye la aplicación, no el modelo ───────────────

#: Las catorce obligaciones de alto riesgo que el modelo mandó en
#: `obligaciones_preliminares` en el recorrido del 8 de septiembre de 2026 sobre un sistema
#: clasificado PROHIBIDO. Se conservan literales: el caso de prueba es este, no uno parecido.
_PRELIMINARES_DEL_MODELO_8_SEP = [
    "Sistema de gestión de riesgos documentado (Art. 9)",
    "Gobernanza de datos de entrenamiento, validación y prueba (Art. 10)",
    "Documentación técnica completa según el Anexo IV (Art. 11)",
    "Instrucciones de uso para el implementador (Art. 13)",
    "Supervisión humana efectiva (Art. 14)",
    "Exactitud, solidez y ciberseguridad (Art. 15)",
    "Sistema de gestión de la calidad (Art. 17)",
    "Conservación de la documentación técnica (Art. 18)",
    "Conservación de los archivos de registro generados automáticamente (Art. 20)",
    "Uso del sistema conforme a las instrucciones del proveedor (Art. 26.1)",
    "Supervisión humana encomendada a personas con la competencia necesaria (Art. 26.2)",
    "Conservación de los registros durante al menos seis meses (Art. 26.6)",
    "Declaración UE de conformidad y marcado CE (Art. 47)",
    "Registro del sistema en la base de datos de la UE (Art. 49)",
]


def _clasif_prohibida_con_preliminares(preliminares: list[str]) -> dict:
    datos = dict(_PROHIBIDO_CLASIF)
    datos["obligaciones_preliminares"] = preliminares
    return datos


class TestLaListaPreliminarDeProhibidoNoLaEscribeElModelo:
    """B14 y B9, otra vez: la lista de obligaciones la construye la aplicación.

    En el recorrido del 8 de septiembre de 2026 el modelo mandó catorce obligaciones de alto
    riesgo para un sistema del Art. 5 y la sección las imprimió tal cual, porque el bloque del
    catálogo solo entraba si la lista venía vacía. El informe le pedía el marcado CE y el
    registro en la base de datos de la UE a un sistema que no puede usarse. No existe una
    versión conforme de un sistema del Art. 5: ninguna lista suya puede ser correcta.
    """

    def test_ninguna_obligacion_de_alto_riesgo_del_modelo_llega_al_informe(self):
        md = GeneradorInforme().generar_informe_clasificacion(
            _clasif_prohibida_con_preliminares(_PRELIMINARES_DEL_MODELO_8_SEP)
        )
        for obligacion in _PRELIMINARES_DEL_MODELO_8_SEP:
            assert obligacion not in md, f"el informe sigue imprimiendo: {obligacion}"

    def test_no_le_pide_el_marcado_ce_ni_el_registro_en_la_base_de_datos_de_la_ue(self):
        """Las dos peticiones que hacían el disparate visible a simple vista."""
        md = GeneradorInforme().generar_informe_clasificacion(
            _clasif_prohibida_con_preliminares(_PRELIMINARES_DEL_MODELO_8_SEP)
        )
        assert "marcado CE" not in md
        assert "base de datos de la UE" not in md

    def test_en_su_lugar_va_el_bloque_del_catalogo(self):
        """Ignorar la lista del modelo no puede dejar la sección vacía."""
        md = GeneradorInforme().generar_informe_clasificacion(
            _clasif_prohibida_con_preliminares(_PRELIMINARES_DEL_MODELO_8_SEP)
        )
        assert "El sistema NO puede desarrollarse ni desplegarse (Art. 5)" in md
        assert "Acción inmediata: detener el proyecto o rediseñar el sistema" in md
        assert "Consulte urgentemente con un asesor legal especializado" in md

    def test_el_informe_completo_tampoco_las_lleva(self):
        """La sección es la misma en los dos informes que la usan."""
        md = GeneradorInforme().generar_informe_completo(
            _clasif_prohibida_con_preliminares(_PRELIMINARES_DEL_MODELO_8_SEP),
            _cumplimiento_prohibido("carencia"),
        )
        for obligacion in _PRELIMINARES_DEL_MODELO_8_SEP:
            assert obligacion not in md, f"el informe completo sigue imprimiendo: {obligacion}"

    def test_las_demas_clasificaciones_conservan_la_lista_del_modelo(self):
        """La regla es de PROHIBIDO, no general: en ALTO la lista preliminar sale del recorrido
        del árbol y es la que el usuario acaba de ver en la pestaña Evaluador."""
        # Redactadas como las redacta el modelo tras el recorrido, y distintas de las del
        # catálogo: con las líneas del catálogo, el test pasaría también si la lista se
        # tirara a la basura y el bloque de ALTO ocupara su sitio.
        preliminares = [
            "Registro de actividad conservado seis meses en el sistema de tickets (Art. 12)",
            "Instrucciones de uso entregadas al implementador y firmadas (Art. 13)",
        ]
        datos = dict(_CLASIFICACION)
        datos["obligaciones_preliminares"] = preliminares
        md = GeneradorInforme().generar_informe_clasificacion(datos)
        for obligacion in preliminares:
            assert obligacion in md
        assert "Evaluación de conformidad antes de la comercialización (Art. 43)" not in md

    def test_limitado_tambien_la_conserva(self):
        datos = dict(_CLASIFICACION)
        datos["clasificacion"] = "LIMITADO"
        datos["obligaciones_preliminares"] = ["Etiquetar el contenido generado (Art. 50.2)"]
        md = GeneradorInforme().generar_informe_clasificacion(datos)
        assert "Etiquetar el contenido generado (Art. 50.2)" in md


class TestElArt4SobreviveALaProhibicion:
    """La alfabetización en IA es lo único que queda en pie cuando el sistema es del Art. 5, y
    queda en pie por una razón que hay que decir: obliga a la organización por ser responsable
    del despliegue de sistemas de IA, no por este sistema. Redactada como tarea del sistema
    prohibido sería contradictoria —un sistema que no puede usarse no tiene tareas—."""

    def test_el_informe_del_evaluador_nombra_el_art_4(self):
        md = GeneradorInforme().generar_informe_clasificacion(_PROHIBIDO_CLASIF)
        assert "Art. 4" in md
        assert "alfabetización en IA" in md

    def test_dice_que_obliga_a_la_organizacion_y_no_al_sistema(self):
        md = GeneradorInforme().generar_informe_clasificacion(_PROHIBIDO_CLASIF)
        assert "sigue obligando a su organización" in md
        assert "responsable del despliegue de sistemas de IA" in md
        assert "no por este sistema en concreto" in md

    def test_la_fecha_sale_del_calendario(self):
        """Como todas las del informe: nunca un literal en este fichero (ver CLAUDE.md)."""
        md = GeneradorInforme().generar_informe_clasificacion(_PROHIBIDO_CLASIF)
        assert obtener_obligacion("art_5_art_4")["fecha_legible"] in md

    def test_sobrevive_aunque_el_modelo_mande_su_propia_lista(self):
        """Es el mismo bloque del catálogo: si la lista del modelo lo desplazara, el Art. 4 se
        perdería justo en el informe donde es la única obligación que queda."""
        md = GeneradorInforme().generar_informe_clasificacion(
            _clasif_prohibida_con_preliminares(_PRELIMINARES_DEL_MODELO_8_SEP)
        )
        assert "sigue obligando a su organización" in md


class TestRecuadroDeAdvertenciaDeProhibido:
    """El aviso del plan de acción empezaba con ⚠️ y llevaba los ** dentro de un blockquote.
    En el PDF salía «?? **Este sistema está clasificado como práctica prohibida...**»: el emoji
    no cabe en latin-1 y _limpiar() lo sustituye por «?», y la rama de blockquote del parser
    escribe la línea sin deshacer el marcado.

    Ahora es un recuadro dibujado, y tiene que verse en los tres formatos.
    """

    def _md(self) -> str:
        return GeneradorInforme().generar_informe_clasificacion(_PROHIBIDO_CLASIF)

    def test_el_recuadro_sale_en_markdown(self):
        md = self._md()
        assert "**ADVERTENCIA — Práctica prohibida (Art. 5 AI Act)**" in md
        assert "Este sistema está clasificado como una práctica de IA prohibida" in md
        assert "Detenga el desarrollo y el uso del sistema" in md
        assert "Las sanciones del Art. 99.3 alcanzan 35.000.000 EUR" in md
        assert "el Art. 99.6 prevé que la multa pueda ser el importe o el porcentaje" in md
        assert "Consulte urgentemente con un asesor legal especializado" in md

    def test_el_orden_del_recuadro_es_el_del_razonamiento(self):
        """Qué es, qué hay que hacer, qué cuesta no hacerlo y a quién preguntar."""
        md = self._md()
        posiciones = [
            md.index("una práctica de IA prohibida"),
            md.index("Detenga el desarrollo"),
            md.index("Las sanciones del Art. 99.3"),
            md.index("Consulte urgentemente"),
        ]
        assert posiciones == sorted(posiciones)

    def test_el_recuadro_sale_en_texto_plano(self):
        txt = GeneradorInforme().exportar_texto_plano(self._md())
        assert "ADVERTENCIA" in txt
        assert "Detenga el desarrollo y el uso del sistema" in txt
        assert "Consulte urgentemente con un asesor legal especializado" in txt
        assert "*" not in txt.split("ADVERTENCIA")[1][:900]

    def test_el_recuadro_sale_en_el_pdf(self):
        texto = _texto_del_pdf(GeneradorInforme().exportar_pdf(self._md()))
        assert "ADVERTENCIA" in texto
        assert "Detenga el desarrollo y el uso del sistema" in texto
        assert "Consulte urgentemente con un asesor legal especializado." in texto

    def test_el_pdf_no_lleva_asteriscos_en_crudo_ni_emojis(self):
        """Las dos mitades del defecto. El «?» es lo que _limpiar() deja donde había un emoji:
        se comprueba sobre el recuadro, porque el resto del documento sí usa «?» en preguntas."""
        texto = _texto_del_pdf(GeneradorInforme().exportar_pdf(self._md()))
        inicio = texto.index("ADVERTENCIA")
        recuadro = texto[inicio:texto.index("Consulte urgentemente con un asesor legal", inicio)]
        assert "*" not in recuadro, f"el PDF imprime marcado en crudo:\n{recuadro}"
        assert "?" not in recuadro, f"el PDF imprime un carácter sustituido:\n{recuadro}"

    def test_el_recuadro_no_lleva_ningun_caracter_fuera_de_latin_1(self):
        """La comprobación en origen: si el markdown del recuadro llevara un emoji, _limpiar()
        lo sustituiría por «?» y el PDF lo publicaría sin que nada fallara. La raya y las
        comillas tipográficas sí valen: _limpiar() las traduce, no las sustituye."""
        from src.report_generator import _ADVERTENCIA_PROHIBIDO_MD

        limpio = _limpiar(_ADVERTENCIA_PROHIBIDO_MD)
        assert "?" not in limpio, f"algún carácter no ha sobrevivido a latin-1:\n{limpio}"
        assert "—" not in limpio, "la raya se traduce a guion, no se deja pasar"

    def test_el_pdf_lo_dibuja_como_recuadro_y_no_como_linea_de_texto(self):
        """Un rectángulo relleno y con borde («re B») en el rojo del aviso. Sin él, el aviso
        sería otra vez una línea de texto en cursiva gris entre dos párrafos."""
        texto = _texto_del_pdf(GeneradorInforme().exportar_pdf(self._md()))
        antes = texto[: texto.index("ADVERTENCIA")]
        assert re.search(
            r"0\.6902 0\.1255 0\.1255 RG\n[\d.]+ w\n[\d.]+ [\d.]+ [\d.]+ -[\d.]+ re B", antes
        ), "el recuadro no se dibuja como rectángulo relleno y con borde"

    def test_las_demas_clasificaciones_no_llevan_recuadro(self):
        md = GeneradorInforme().generar_informe_clasificacion(_CLASIFICACION)
        assert "ADVERTENCIA" not in md

    def test_el_informe_de_cumplimiento_no_lo_repite(self):
        """El recuadro va una vez por documento: en el informe completo, el plan de acción lo
        habría duplicado a media página de distancia."""
        md = GeneradorInforme().generar_informe_completo(
            _PROHIBIDO_CLASIF, _cumplimiento_prohibido("carencia")
        )
        assert md.count("ADVERTENCIA") == 1
        assert md.count("Consulte urgentemente con un asesor legal especializado") == 2, (
            "una vez en el recuadro y otra en la lista preliminar del catálogo"
        )

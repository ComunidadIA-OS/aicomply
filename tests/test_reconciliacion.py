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

"""Tests de src/reconciliacion.py y de su efecto sobre el informe.

El fallo que arreglan: el informe del 4 de septiembre publicó «Grado de cumplimiento legal
estimado: 100 %» en la misma página en que documentaba una carencia legal, porque el registro
había perdido nueve de las once obligaciones evaluadas y nadie comparaba las dos cuentas.

Cubre:
  A - carencia huérfana y su inversa (bloqueantes)
  B - recuento narrado y obligaciones narradas no registradas (indicios)
  C - no verificable: la ausencia de coincidencias no es conformidad
  D - un registro coherente no produce incoherencias
  E - el informe no publica porcentaje cuando hay incoherencias
"""

import re

from src.reconciliacion import (
    GRAVEDAD_BLOQUEANTE,
    GRAVEDAD_INDICIO,
    motivo_no_calculable,
    reconciliar,
)
from src.report_generator import GeneradorInforme

_SIN_NARRACION: dict = {"total_declarado": None, "ordinal_max": None, "resumen_final": []}


def _obl(articulo, titulo, estado, tipo="obligacion", rol="implementador", descripcion="d"):
    return {
        "articulo": articulo, "titulo": titulo, "estado": estado,
        "tipo": tipo, "rol": rol, "descripcion": descripcion,
    }


def _codigos(incoherencias):
    return {i["codigo"] for i in incoherencias}


def _de(incoherencias, codigo):
    return next(i for i in incoherencias if i["codigo"] == codigo)


# ── A: carencias que no cuadran con el registro ──────────────────────────────

class TestCarencias:
    def test_a_carencia_huerfana(self):
        """El Art. 27 del recorrido: se imprimía en «Áreas de mejora» y contaba 0 en el
        denominador. Una carencia en prosa que desaparecía del contador."""
        incoherencias = reconciliar(
            [_obl("Art. 4", "Alfabetización", "cubierta")],
            ["No se ha realizado la evaluación de impacto del Art. 27"],
            [],
            _SIN_NARRACION,
        )
        inc = _de(incoherencias, "carencia_huerfana")
        assert inc["gravedad"] == GRAVEDAD_BLOQUEANTE
        assert any("Art. 27" in d for d in inc["detalle"])

    def test_a_una_carencia_con_su_obligacion_no_es_huerfana(self):
        incoherencias = reconciliar(
            [_obl("Art. 27", "Evaluación de impacto", "carencia")],
            ["No se ha realizado la evaluación de impacto del Art. 27"],
            [],
            _SIN_NARRACION,
        )
        assert "carencia_huerfana" not in _codigos(incoherencias)

    def test_a_una_carencia_sin_articulo_no_se_puede_comprobar(self):
        """No hay contra qué contrastarla, y aquí no se inventa nada."""
        incoherencias = reconciliar(
            [_obl("Art. 4", "Alfabetización", "cubierta")],
            ["Faltan procedimientos internos de supervisión"],
            [],
            _SIN_NARRACION,
        )
        assert "carencia_huerfana" not in _codigos(incoherencias)

    def test_a_carencia_no_declarada_es_la_inversa(self):
        """El contador dice que hay incumplimientos y la sección de áreas de mejora, vacía."""
        incoherencias = reconciliar(
            [_obl("Art. 26.6", "Conservación de registros", "carencia")],
            [],
            [],
            _SIN_NARRACION,
        )
        inc = _de(incoherencias, "carencia_no_declarada")
        assert inc["gravedad"] == GRAVEDAD_BLOQUEANTE
        assert any("Art. 26.6" in d for d in inc["detalle"])

    def test_a_carencia_no_declarada_no_salta_si_las_carencias_no_citan_articulo(self):
        """El contrato del cierre pide «una descripción breve», no una referencia.

        Sin esta guarda, un análisis sano cuyas carencias estuvieran redactadas en prosa llana
        levantaba una bloqueante y se quedaba sin porcentaje. La dirección contraria
        (_carencias_huerfanas) ya la tenía: la asimetría era un error.
        """
        incoherencias = reconciliar(
            [_obl("Art. 27", "Evaluación de impacto", "carencia")],
            ["No se ha realizado la evaluación de impacto sobre derechos fundamentales"],
            [],
            _SIN_NARRACION,
        )
        assert "carencia_no_declarada" not in _codigos(incoherencias)

    def test_a_el_detalle_dice_si_el_articulo_falta_o_esta_con_otro_estado(self):
        """Son dos problemas distintos y el aviso no puede afirmar el primero cuando es el
        segundo: una obligación perdida no es lo mismo que una contradicción entre canales."""
        incoherencias = reconciliar(
            [_obl("Art. 26.6", "Conservación de registros", "parcial")],
            ["Los logs del Art. 26.6 solo se conservan tres meses"],
            [],
            _SIN_NARRACION,
        )
        detalle = " ".join(_de(incoherencias, "carencia_huerfana")["detalle"])
        assert "consta como parcial" in detalle

    def test_a_una_recomendacion_no_adoptada_no_es_carencia_legal(self):
        """El Art. 95 en estado carencia es una recomendación pendiente, y el prompt pide
        explícitamente no listarla entre las carencias."""
        incoherencias = reconciliar(
            [_obl("Art. 95", "Códigos de conducta", "carencia", tipo="recomendacion")],
            [],
            [],
            _SIN_NARRACION,
        )
        assert "carencia_no_declarada" not in _codigos(incoherencias)


# ── B: los indicios que salen de parsear la prosa del modelo ─────────────────

class TestIndicios:
    def test_b_recuento_narrado(self):
        """La comparación que faltaba: once narradas contra dos registradas."""
        incoherencias = reconciliar(
            [_obl("Art. 4", "Alfabetización", "cubierta"),
             _obl("Art. 49", "Registro UE", "no_aplica")],
            [],
            [],
            {"total_declarado": 11, "ordinal_max": 11, "resumen_final": []},
        )
        inc = _de(incoherencias, "recuento_narrado")
        assert inc["gravedad"] == GRAVEDAD_INDICIO
        assert "11" in inc["mensaje"] and "2" in inc["mensaje"]

    def test_b_registradas_de_mas_con_rol_unico(self):
        """Firma de la deriva de claves: la misma obligación registrada dos veces."""
        incoherencias = reconciliar(
            [_obl("Art. 4", "Alfabetización", "cubierta"),
             _obl("Art. 4", "Formación en IA", "cubierta"),
             _obl("Art. 26.1", "Instrucciones", "cubierta")],
            [],
            [],
            {"total_declarado": 2, "ordinal_max": 2, "resumen_final": []},
        )
        assert "recuento_narrado" in _codigos(incoherencias)

    def test_b_registradas_de_mas_con_varios_roles_no_avisa(self):
        """Con doble rol el modelo reinicia la numeración en cada uno: superar M es lo normal."""
        incoherencias = reconciliar(
            [_obl("Art. 9", "Gestión de riesgos", "cubierta", rol="proveedor"),
             _obl("Art. 26.1", "Instrucciones", "cubierta", rol="implementador"),
             _obl("Art. 26.2", "Supervisión humana", "cubierta", rol="implementador")],
            [],
            [],
            {"total_declarado": 2, "ordinal_max": 2, "resumen_final": []},
        )
        assert "recuento_narrado" not in _codigos(incoherencias)

    def test_b_narradas_no_registradas_dice_cuales(self):
        """El recuento dice cuántas faltan; esto dice cuáles."""
        incoherencias = reconciliar(
            [_obl("Art. 4", "Alfabetización", "cubierta")],
            [],
            [],
            {
                "total_declarado": 3, "ordinal_max": 3,
                "resumen_final": [
                    {"articulo": "Art. 4", "titulo": "Alfabetización", "estado": "cubierta"},
                    {"articulo": "Art. 26.6", "titulo": "Conservación", "estado": "parcial"},
                    {"articulo": "Art. 27", "titulo": "Evaluación de impacto", "estado": "carencia"},
                ],
            },
        )
        inc = _de(incoherencias, "narrada_no_registrada")
        assert inc["gravedad"] == GRAVEDAD_INDICIO
        detalle = " ".join(inc["detalle"])
        assert "Art. 26.6" in detalle and "Art. 27" in detalle
        assert "Art. 4" not in detalle

    def test_b_el_titulo_reformulado_no_cuenta_como_ausencia(self):
        """Los títulos los redacta el modelo; se contrasta por artículo, no por texto."""
        incoherencias = reconciliar(
            [_obl("Art. 26.6", "Conservación de registros automáticos", "parcial")],
            [],
            [],
            {
                "total_declarado": 1, "ordinal_max": 1,
                "resumen_final": [
                    {"articulo": "Art. 26.6", "titulo": "Logs del sistema", "estado": "parcial"},
                ],
            },
        )
        assert "narrada_no_registrada" not in _codigos(incoherencias)


# ── C: no verificable ────────────────────────────────────────────────────────

class TestNoVerificable:
    def test_c_sin_traza_narrada_el_registro_no_esta_confirmado(self):
        """Un parser que no encuentra nada no ha verificado nada.

        Este es el test que impide que el silencio se lea como conformidad: es el mismo modo de
        fallo que arregla la rama, trasladado al auditor.
        """
        incoherencias = reconciliar(
            [_obl("Art. 4", "Alfabetización", "cubierta")],
            [],
            [],
            _SIN_NARRACION,
        )
        assert incoherencias != []
        assert _codigos(incoherencias) == {"no_verificable"}

    def test_c_con_ordinal_pero_sin_resumen_ya_es_verificable(self):
        incoherencias = reconciliar(
            [_obl("Art. 4", "Alfabetización", "cubierta")],
            [],
            [],
            {"total_declarado": 1, "ordinal_max": 1, "resumen_final": []},
        )
        assert "no_verificable" not in _codigos(incoherencias)

    def test_c_el_motivo_distingue_los_tres_casos(self):
        bloqueante = [{"codigo": "colapso_identidad", "gravedad": GRAVEDAD_BLOQUEANTE}]
        indicio = [{"codigo": "recuento_narrado", "gravedad": GRAVEDAD_INDICIO}]
        sin_traza = [{"codigo": "no_verificable", "gravedad": GRAVEDAD_INDICIO}]

        assert "demostrablemente incoherente" in motivo_no_calculable(bloqueante)
        assert "pudo perder obligaciones" in motivo_no_calculable(indicio)
        assert "no dejó traza narrada" in motivo_no_calculable(sin_traza)


# ── D: un análisis coherente no produce ruido ────────────────────────────────

_COHERENTE = {
    "obligaciones": [
        _obl("Art. 4", "Alfabetización en IA", "cubierta"),
        _obl("Art. 26.1", "Instrucciones de uso", "carencia"),
    ],
    "carencias_detectadas": ["No se sigue el manual del proveedor (Art. 26.1)"],
    "narracion": {
        "total_declarado": 2, "ordinal_max": 2,
        "resumen_final": [
            {"articulo": "Art. 4", "titulo": "Alfabetización en IA", "estado": "cubierta"},
            {"articulo": "Art. 26.1", "titulo": "Instrucciones de uso", "estado": "carencia"},
        ],
    },
}


class TestRegistroCoherente:
    def test_d_sin_incoherencias(self):
        assert reconciliar(
            _COHERENTE["obligaciones"],
            _COHERENTE["carencias_detectadas"],
            [],
            _COHERENTE["narracion"],
        ) == []

    def test_d_una_reemision_identica_no_es_colapso(self):
        """El modelo reemite el mismo bloque; no ha desaparecido nada."""
        obl = _obl("Art. 4", "Alfabetización", "cubierta")
        incoherencias = reconciliar(
            [obl], [], [{"previa": dict(obl), "nueva": dict(obl), "turno": 2}],
            _COHERENTE["narracion"],
        )
        assert "colapso_identidad" not in _codigos(incoherencias)

    def test_d_una_recalificacion_sin_clave_se_marca_como_colapso(self):
        """Falso positivo conocido y asumido, documentado aquí para que se vea.

        Sin clave del catálogo, una recalificación cuya descripción el modelo reescribe es
        indistinguible de dos obligaciones con el mismo título: las dos son «una entrada
        sustituida por otra que describe algo distinto». Se avisa en vez de callar, y el mensaje
        no afirma cuál de las dos es. La salida limpia es que el modelo emita la clave, que es
        lo que ataca la causa.
        """
        previa = _obl("Art. 26.6", "Conservación de registros", "parcial",
                      descripcion="Solo conserva tres meses de logs.")
        nueva = _obl("Art. 26.6", "Conservación de registros", "cubierta",
                     descripcion="Aporta política de doce meses.")
        incoherencias = reconciliar(
            [nueva], [], [{"previa": previa, "nueva": nueva, "turno": 4}],
            _COHERENTE["narracion"],
        )
        assert "colapso_identidad" in _codigos(incoherencias)
        assert "Revise cuál de las dos" in _de(incoherencias, "colapso_identidad")["mensaje"]

    def test_d_con_clave_esa_misma_recalificacion_no_es_colapso(self):
        """La clave es la identidad: reformular una obligación ya identificada no la duplica."""
        previa = _obl("Art. 26.6", "Conservación", "parcial", descripcion="Tres meses.")
        nueva = _obl("Art. 26.6", "Conservación de registros", "cubierta",
                     descripcion="Doce meses documentados.")
        previa["clave"] = nueva["clave"] = "26.6-conservacion-registros"
        incoherencias = reconciliar(
            [nueva], [], [{"previa": previa, "nueva": nueva, "turno": 4}],
            _COHERENTE["narracion"],
        )
        assert "colapso_identidad" not in _codigos(incoherencias)

    def test_d_el_registro_reconstruido_es_bloqueante(self):
        incoherencias = reconciliar(
            _COHERENTE["obligaciones"],
            _COHERENTE["carencias_detectadas"],
            [],
            _COHERENTE["narracion"],
            reconstruido=True,
        )
        assert _codigos(incoherencias) == {"registro_reconstruido"}
        assert incoherencias[0]["gravedad"] == GRAVEDAD_BLOQUEANTE


# ── E: el informe no publica cifra sobre un registro dudoso ──────────────────

_CLASIF = {
    "clasificacion": "ALTO",
    "rol": "implementador",
    "roles_multiples": ["implementador"],
    "descripcion_sistema": "Criba de currículums",
    "sector": "Industria",
    "estados_adicionales": [],
    "obligaciones_preliminares": [],
    "puntos_indeterminados": [],
}

_RE_PORCENTAJE = re.compile(r"\d+\s*%")


def _cumplimiento(incoherencias):
    return {
        "obligaciones": [_obl("Art. 4", "Alfabetización", "cubierta")],
        "carencias_detectadas": [],
        "puntos_revision_profesional": [],
        "resumen_cumplimiento": "Análisis completado.",
        "incoherencias": incoherencias,
    }


class TestInformeConIncoherencias:
    def test_e_con_incoherencias_no_hay_porcentaje(self):
        """El fallo de B16, al revés: el 100 % se calculaba sobre un registro incompleto."""
        incoherencias = reconciliar(
            [_obl("Art. 4", "Alfabetización", "cubierta")], [], [],
            {"total_declarado": 11, "ordinal_max": 11, "resumen_final": []},
        )
        md = GeneradorInforme().generar_informe_cumplimiento(
            _CLASIF, _cumplimiento(incoherencias)
        )
        assert _RE_PORCENTAJE.search(md) is None
        assert "No calculable" in md
        assert "Incoherencias detectadas en el registro" in md

    def test_e_el_aviso_esta_en_el_resumen_ejecutivo(self):
        """Quien abre por la portada tiene que leerlo antes que cualquier otra cosa."""
        incoherencias = reconciliar(
            [_obl("Art. 4", "Alfabetización", "cubierta")], [], [],
            {"total_declarado": 11, "ordinal_max": 11, "resumen_final": []},
        )
        md = GeneradorInforme().generar_informe_completo(_CLASIF, _cumplimiento(incoherencias))
        resumen = md.split("## 2.")[0]
        assert "fiabilidad de este análisis" in resumen

    def test_e_los_recuentos_se_mantienen(self):
        """Son hechos sobre lo que sí se registró; lo que no se sostiene es la proporción."""
        incoherencias = reconciliar(
            [_obl("Art. 4", "Alfabetización", "cubierta")], [], [],
            {"total_declarado": 11, "ordinal_max": 11, "resumen_final": []},
        )
        md = GeneradorInforme().generar_informe_cumplimiento(
            _CLASIF, _cumplimiento(incoherencias)
        )
        assert "Cubiertas: 1" in md

    def test_e_el_colapso_llega_al_informe_con_los_dos_titulos(self):
        desplazada = {
            "previa": _obl("Art. 26.5", "Vigilancia", "cubierta", descripcion="Informa al proveedor (Art. 72)."),
            "nueva": _obl("Art. 26.5", "Vigilancia", "cubierta", descripcion="Incidentes graves (Art. 73)."),
            "turno": 6,
        }
        incoherencias = reconciliar(
            [desplazada["nueva"]], [], [desplazada], _COHERENTE["narracion"],
        )
        md = GeneradorInforme().generar_informe_cumplimiento(
            _CLASIF, _cumplimiento(incoherencias)
        )
        assert "Art. 72" in md and "Art. 73" in md

    def test_e_sin_incoherencias_el_porcentaje_vuelve(self):
        """Regresión: el informe sano no cambia."""
        md = GeneradorInforme().generar_informe_cumplimiento(_CLASIF, _cumplimiento([]))
        assert "100 %" in md
        assert "No calculable" not in md

    def test_e_una_cumplimiento_data_sin_la_clave_sigue_funcionando(self):
        """Sesiones exportadas antes de esta rama, y el fallback de generar_markdown."""
        datos = _cumplimiento([])
        del datos["incoherencias"]
        md = GeneradorInforme().generar_informe_cumplimiento(_CLASIF, datos)
        assert "100 %" in md

    def test_e_el_pdf_no_dibuja_una_barra_al_cero(self, monkeypatch):
        """Sin porcentaje la barra no se pinta: una barra vacía se lee como 0 % de cumplimiento,
        que sería otra cifra falsa en vez de ninguna.

        Se espía lo que fpdf dibuja porque el texto del PDF sale comprimido: buscarlo en los
        bytes daría siempre negativo y el test pasaría con el código roto.
        """
        import fpdf  # noqa: PLC0415

        textos: list[str] = []
        original = fpdf.FPDF.cell

        def _espia(self, *args, **kwargs):
            texto = kwargs.get("text", kwargs.get("txt"))
            if texto is None and len(args) >= 3:
                texto = args[2]
            textos.append(str(texto or ""))
            return original(self, *args, **kwargs)

        monkeypatch.setattr(fpdf.FPDF, "cell", _espia)

        incoherencias = reconciliar(
            [_obl("Art. 4", "Alfabetización", "cubierta")], [], [],
            {"total_declarado": 11, "ordinal_max": 11, "resumen_final": []},
        )
        md = GeneradorInforme().generar_informe_completo(_CLASIF, _cumplimiento(incoherencias))
        pdf = GeneradorInforme().exportar_pdf(md, clasificacion_data=_CLASIF)

        assert pdf[:4] == b"%PDF"
        assert any("No calculable" in t for t in textos)
        assert not any(_RE_PORCENTAJE.fullmatch(t.strip()) for t in textos), (
            f"el PDF dibujó un porcentaje: {[t for t in textos if '%' in t]}"
        )

    def test_e_el_pdf_sano_sigue_dibujando_su_porcentaje(self, monkeypatch):
        """Contraprueba del anterior: sin ella, un espía que no ve nada lo daría por bueno."""
        import fpdf  # noqa: PLC0415

        textos: list[str] = []
        original = fpdf.FPDF.cell

        def _espia(self, *args, **kwargs):
            texto = kwargs.get("text", kwargs.get("txt"))
            if texto is None and len(args) >= 3:
                texto = args[2]
            textos.append(str(texto or ""))
            return original(self, *args, **kwargs)

        monkeypatch.setattr(fpdf.FPDF, "cell", _espia)

        md = GeneradorInforme().generar_informe_completo(_CLASIF, _cumplimiento([]))
        GeneradorInforme().exportar_pdf(md, clasificacion_data=_CLASIF)

        assert any(_RE_PORCENTAJE.fullmatch(t.strip()) for t in textos)

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

"""Tests de regresión del calendario normativo (hallazgos A1, A2 y A3 de la auditoría)."""

import re
from datetime import date
from pathlib import Path

import pytest

import src.calendario as calendario_mod
from prompts.system_prompt_cumplimiento import SYSTEM_PROMPT_CUMPLIMIENTO
from prompts.system_prompts import SYSTEM_PROMPT_CHATBOT
from src.calendario import (
    MARCADOR,
    CalendarioNoDisponibleError,
    aplicar_calendario,
    cargar_calendario,
    formatear_calendario,
    obtener_obligacion,
    obtener_version,
)

_RAIZ = Path(__file__).parent.parent
_HOY = date(2026, 9, 2)  # fecha de la auditoría; mantiene los tests deterministas


@pytest.fixture(autouse=True)
def _limpiar_cache():
    """El calendario se cachea en el módulo; cada test parte de cero."""
    calendario_mod._calendario_cache = None
    yield
    calendario_mod._calendario_cache = None


# ── 1 · Carga y formato ────────────────────────────────────────────────────────

def test_calendario_carga_y_tiene_las_seis_obligaciones():
    cal = cargar_calendario()
    ids = [o["id"] for o in cal["obligaciones"]]
    assert ids == ["art_5_art_4", "gpai", "art_50", "art_50_2", "anexo_iii", "anexo_i"]
    for obl in cal["obligaciones"]:
        date.fromisoformat(obl["fecha"])  # no lanza


def test_calendario_cita_el_reglamento_adoptado():
    cal = cargar_calendario()
    assert cal["norma_modificativa"]["referencia"] == "Reglamento (UE) 2026/1744"
    assert cal["norma_modificativa"]["en_vigor_desde"] == "2026-07-27"


def test_fechas_clave_del_omnibus():
    assert obtener_obligacion("anexo_iii")["fecha"] == "2027-12-02"
    assert obtener_obligacion("anexo_i")["fecha"] == "2028-08-02"


def test_art_50_aplica_desde_2026_no_desde_2025():
    """A2: el 2 de agosto de 2025 es la fecha de GPAI, no la del Art. 50."""
    assert obtener_obligacion("art_50")["fecha"] == "2026-08-02"
    assert obtener_obligacion("gpai")["fecha"] == "2025-08-02"


def test_art_50_2_distingue_los_dos_casos():
    """A3: el 2 dic 2026 es un periodo de gracia acotado, no la fecha general."""
    obl = obtener_obligacion("art_50_2")
    assert obl["fecha"] == "2026-08-02"
    assert obl["fecha_gracia"] == "2026-12-02"
    nota = obl["nota"]
    assert "antes del 2 de agosto de 2026" in nota
    assert "a partir del 2 de agosto de 2026" in nota
    assert "PREGUNTA" in nota


def test_formateo_marca_vigentes_y_futuras_contra_la_fecha_del_dia():
    texto = formatear_calendario(hoy=_HOY)
    assert "Reglamento (UE) 2026/1744" in texto
    # Vigentes a 2 de septiembre de 2026
    assert "Aplicable actualmente (desde el 2 de febrero de 2025)" in texto
    assert "Aplicable actualmente (desde el 2 de agosto de 2025)" in texto
    assert "Aplicable actualmente (desde el 2 de agosto de 2026)" in texto
    # Futuras
    assert "Aplicable a partir del 2 de diciembre de 2027" in texto
    assert "Aplicable a partir del 2 de agosto de 2028" in texto


def test_el_estado_se_calcula_no_se_almacena():
    """La causa raíz de A1: un calendario con el estado escrito a mano caduca solo."""
    antes = formatear_calendario(hoy=date(2027, 1, 1))
    despues = formatear_calendario(hoy=date(2028, 1, 1))
    assert "Aplicable a partir del 2 de diciembre de 2027" in antes
    assert "Aplicable actualmente (desde el 2 de diciembre de 2027)" in despues


def test_version_disponible_para_el_pie_del_informe():
    assert re.fullmatch(r"\d{4}\.\d{2}\.\d+", obtener_version())


# ── 2 · El bloque de calendario no lleva fechas escritas a mano ────────────────

def test_ambos_prompts_llevan_el_marcador():
    assert MARCADOR in SYSTEM_PROMPT_CHATBOT
    assert MARCADOR in SYSTEM_PROMPT_CUMPLIMIENTO


def test_aplicar_calendario_no_deja_marcadores_sin_resolver():
    for prompt in (SYSTEM_PROMPT_CHATBOT, SYSTEM_PROMPT_CUMPLIMIENTO):
        resuelto = aplicar_calendario(prompt, hoy=_HOY)
        assert "{CALENDARIO_" not in resuelto
        assert "Reglamento (UE) 2026/1744" in resuelto


def test_aplicar_calendario_no_rompe_con_llaves_literales():
    """El prompt de cumplimiento contiene el bloque <<<OBLIGACION>>>{...}: .format() reventaría."""
    assert '<<<OBLIGACION>>>{"articulo"' in SYSTEM_PROMPT_CUMPLIMIENTO
    resuelto = aplicar_calendario(SYSTEM_PROMPT_CUMPLIMIENTO, hoy=_HOY)
    assert '<<<OBLIGACION>>>{"articulo"' in resuelto


# ── 3 · Las etiquetas del catálogo concuerdan con el calendario ───────────────

_MESES = {
    "ene": "01", "feb": "02", "mar": "03", "abr": "04", "may": "05", "jun": "06",
    "jul": "07", "ago": "08", "sep": "09", "oct": "10", "nov": "11", "dic": "12",
}
_RE_FECHA_ETIQUETA = re.compile(r"(\d{1,2}) (ene|feb|mar|abr|may|jun|jul|ago|sep|oct|nov|dic) (\d{4})")


def test_las_etiquetas_del_catalogo_no_pueden_divergir_del_calendario():
    """Las 34 etiquetas del catálogo siguen siendo texto literal (a propósito: son correctas
    y desharcodearlas sería un diff enorme sin corrección). Este test impide que se
    desincronicen del calendario sin que nadie se entere."""
    fechas_calendario = set()
    for obl in cargar_calendario()["obligaciones"]:
        fechas_calendario.add(obl["fecha"])
        if obl.get("fecha_gracia"):
            fechas_calendario.add(obl["fecha_gracia"])

    encontradas = _RE_FECHA_ETIQUETA.findall(SYSTEM_PROMPT_CUMPLIMIENTO)
    assert encontradas, "el catálogo debería seguir teniendo etiquetas con fecha"

    for dia, mes, anio in encontradas:
        iso = f"{anio}-{_MESES[mes]}-{int(dia):02d}"
        assert iso in fechas_calendario, (
            f"la etiqueta '{dia} {mes} {anio}' del catálogo no existe en data/calendario.json"
        )


def test_el_art_50_ya_no_cita_2025_en_el_catalogo():
    """A2: 50.1, 50.3 y 50.4 estaban etiquetados con la fecha de GPAI."""
    bloque = SYSTEM_PROMPT_CUMPLIMIENTO.split("RIESGO LIMITADO — Transparencia (Art. 50):")[1]
    bloque = bloque.split("MÍNIMO:")[0]
    assert "2 ago 2025" not in bloque
    assert bloque.count("2 ago 2026") >= 3


def test_el_catalogo_instruye_a_preguntar_por_el_art_50_2():
    """A3: sin la pregunta, el modelo etiqueta por defecto y produce un falso negativo."""
    assert "PREGUNTA" in SYSTEM_PROMPT_CUMPLIMIENTO
    assert "antes del 2 ago 2026" in SYSTEM_PROMPT_CUMPLIMIENTO


def test_el_art_49_del_implementador_es_condicional():
    """B11: el registro en la base de datos de la UE es obligación del proveedor; el
    implementador solo registra si es organismo público. Con la salvedad blanda anterior
    el modelo lo computó como carencia legal de una empresa privada.

    Comprobación de texto: no sustituye al recorrido manual, solo impide que la
    condición desaparezca del catálogo sin que nadie se entere."""
    bloque = SYSTEM_PROMPT_CUMPLIMIENTO.split("ALTO RIESGO — Rol Implementador (Art. 26):")[1]
    bloque = bloque.split("ALTO RIESGO — Rol Distribuidor")[0]
    art_49 = [linea for linea in bloque.splitlines() if linea.startswith("- Art. 49:")]
    assert len(art_49) == 1, "el Art. 49 debería seguir figurando una sola vez bajo Implementador"
    linea = art_49[0]
    assert "PREGUNTA" in linea, "debe instruir a preguntar antes de etiquetar"
    assert "organismo público" in linea
    assert "no_aplica" in linea
    assert "cuando aplique según la clase de sistema y rol" not in linea


# ── 4 · Sin afirmaciones caducadas en el repositorio ──────────────────────────

_FRASES_CADUCADAS = (
    "pendiente de publicación en el DOUE",
    "pendiente publicación en el DOUE",
    "pendiente de publicacion en el DOUE",
    "acuerdo provisional",
    "Ómnibus provisional",
    "agosto de 2026 sigue siendo",
)

_FICHEROS_VIGILADOS = (
    "prompts/system_prompts.py",
    "prompts/system_prompt_cumplimiento.py",
    "prompts/system_prompts_local.py",
    "src/report_generator.py",
    "README.md",
    "docs/EIPD.md",
    "data/calendario.json",
)


@pytest.mark.parametrize("ruta", _FICHEROS_VIGILADOS)
def test_sin_afirmaciones_caducadas(ruta):
    """A1. Este test no barre el repositorio entero a propósito: _trabajo/AUDITORIA.md
    y este mismo fichero citan las frases caducadas para documentarlas.

    El guard no distingue afirmar de advertir: prohíbe la frase, la diga quien la diga.
    Por eso un fichero vigilado tampoco puede citarla para decir que está caducada.
    Si hace falta reproducir literalmente una afirmación antigua —por ejemplo en el
    aviso de que `ejemplos/` es de mayo de 2026— va en un fichero no vigilado
    (`ejemplos/README.md`), y el vigilado enlaza a él."""
    texto = (_RAIZ / ruta).read_text(encoding="utf-8")
    for frase in _FRASES_CADUCADAS:
        assert frase not in texto, f"{ruta} contiene la afirmación caducada '{frase}'"


def test_el_omnibus_ya_no_esta_en_el_corpus():
    """A5: era la propuesta de la Comisión, con fechas que no llegaron al texto adoptado."""
    assert not (_RAIZ / "data" / "docs" / "Omnibus.json").exists()


# ── 6 · Fallo ruidoso: nunca degrada ──────────────────────────────────────────

def test_calendario_ausente_lanza(monkeypatch, tmp_path):
    monkeypatch.setattr(calendario_mod, "CALENDARIO_FILE", tmp_path / "no-existe.json")
    with pytest.raises(CalendarioNoDisponibleError, match="No se pudo leer"):
        cargar_calendario()


def test_calendario_malformado_lanza(monkeypatch, tmp_path):
    fichero = tmp_path / "calendario.json"
    fichero.write_text("{esto no es json", encoding="utf-8")
    monkeypatch.setattr(calendario_mod, "CALENDARIO_FILE", fichero)
    with pytest.raises(CalendarioNoDisponibleError, match="no es JSON válido"):
        cargar_calendario()


def test_calendario_incompleto_lanza(monkeypatch, tmp_path):
    fichero = tmp_path / "calendario.json"
    fichero.write_text('{"version": "1.0", "obligaciones": []}', encoding="utf-8")
    monkeypatch.setattr(calendario_mod, "CALENDARIO_FILE", fichero)
    with pytest.raises(CalendarioNoDisponibleError, match="faltan claves"):
        cargar_calendario()


def test_obligacion_con_fecha_invalida_lanza(monkeypatch, tmp_path):
    fichero = tmp_path / "calendario.json"
    fichero.write_text(
        '{"version": "1.0", "norma_base": {}, "norma_modificativa": {}, "obligaciones": '
        '[{"id": "x", "titulo": "t", "fecha": "mañana", "fecha_legible": "l", "norma": "n"}]}',
        encoding="utf-8",
    )
    monkeypatch.setattr(calendario_mod, "CALENDARIO_FILE", fichero)
    with pytest.raises(CalendarioNoDisponibleError, match="fecha ISO válida"):
        cargar_calendario()


def test_nunca_hay_retroceso_silencioso_a_fechas_embebidas(monkeypatch, tmp_path):
    """El modo de fallo es explícito: sin calendario no se genera prompt, no se genera
    uno sin fechas. Un informe de cumplimiento sin fechas es peor que ningún informe."""
    monkeypatch.setattr(calendario_mod, "CALENDARIO_FILE", tmp_path / "no-existe.json")
    with pytest.raises(CalendarioNoDisponibleError):
        aplicar_calendario(SYSTEM_PROMPT_CHATBOT)

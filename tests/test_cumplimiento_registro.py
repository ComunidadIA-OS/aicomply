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

"""Tests del sistema de registro incremental de obligaciones de cumplimiento.

Cubre:
  A - _procesar_bloques persiste una obligación válida
  B - _procesar_bloques ignora bloques con JSON malformado
  C - _procesar_bloques deduplicaobligaciones por (articulo, titulo)
  D - _procesar_bloques procesa el bloque CIERRE
  E - extraer_cumplimiento devuelve registros incrementales si los hay
  F - extraer_cumplimiento llama al legacy si no hay registros
  G - _reconstruir_obligaciones_desde_historial extrae desde texto del asistente
  H - resetear() limpia los 4 atributos de registro
"""

import json

import pytest

from src.chatbot import AIComplyChat
from tests.conftest import MockProvider


# ── Helpers ────────────────────────────────────────────────────────────────────

def _bloque_obl(articulo: str, titulo: str, estado: str, tipo: str = "obligacion") -> str:
    return (
        f'<<<OBLIGACION>>>{json.dumps({"articulo": articulo, "titulo": titulo, "estado": estado, "tipo": tipo, "descripcion": "desc", "rol": "proveedor"})}<<<FIN>>>'
    )


def _bloque_cierre(resumen: str, carencias: list[str], puntos: list[str]) -> str:
    return f'<<<CIERRE>>>{json.dumps({"resumen": resumen, "carencias": carencias, "puntos_revision": puntos})}<<<FIN>>>'


def _chatbot(respuesta: str = "") -> AIComplyChat:
    return AIComplyChat(provider=MockProvider(respuesta), system_prompt_override="sys")


# ── A: _procesar_bloques persiste obligación válida ──────────────────────────

class TestProcesarBloquesObligacion:
    def test_a_persiste_obligacion(self):
        bot = _chatbot()
        texto = "Aquí la evaluación.\n" + _bloque_obl("Art. 9", "Gestión de riesgos", "cubierta")
        limpio = bot._procesar_bloques(texto)
        assert len(bot.obligaciones_registradas) == 1
        assert bot.obligaciones_registradas[0]["articulo"] == "Art. 9"
        assert bot.obligaciones_registradas[0]["estado"] == "cubierta"

    def test_a_texto_limpio_sin_bloques(self):
        bot = _chatbot()
        texto = "Evaluación.\n" + _bloque_obl("Art. 9", "Gestión de riesgos", "cubierta") + "\nFin."
        limpio = bot._procesar_bloques(texto)
        assert "<<<OBLIGACION>>>" not in limpio
        assert "<<<FIN>>>" not in limpio
        assert "Evaluación." in limpio


# ── B: ignora bloques JSON malformados ───────────────────────────────────────

class TestProcesarBloquesMalformados:
    def test_b_ignora_json_invalido(self):
        bot = _chatbot()
        texto = "texto<<<OBLIGACION>>>esto no es json<<<FIN>>>"
        limpio = bot._procesar_bloques(texto)
        assert bot.obligaciones_registradas == []

    def test_b_ignora_obl_sin_articulo(self):
        bot = _chatbot()
        bloque = '<<<OBLIGACION>>>{"titulo":"algo","estado":"cubierta"}<<<FIN>>>'
        bot._procesar_bloques(bloque)
        assert bot.obligaciones_registradas == []

    def test_b_ignora_obl_sin_estado(self):
        bot = _chatbot()
        bloque = '<<<OBLIGACION>>>{"articulo":"Art. 9","titulo":"algo"}<<<FIN>>>'
        bot._procesar_bloques(bloque)
        assert bot.obligaciones_registradas == []


# ── C: deduplicación por (articulo, titulo) ───────────────────────────────────

class TestDeduplicacion:
    def test_c_actualiza_estado_existente(self):
        bot = _chatbot()
        bot._procesar_bloques(_bloque_obl("Art. 9", "Gestión de riesgos", "carencia"))
        bot._procesar_bloques(_bloque_obl("Art. 9", "Gestión de riesgos", "cubierta"))
        assert len(bot.obligaciones_registradas) == 1
        assert bot.obligaciones_registradas[0]["estado"] == "cubierta"

    def test_c_permite_distinto_articulo(self):
        bot = _chatbot()
        bot._procesar_bloques(_bloque_obl("Art. 9", "Gestión de riesgos", "cubierta"))
        bot._procesar_bloques(_bloque_obl("Art. 11", "Documentación técnica", "carencia"))
        assert len(bot.obligaciones_registradas) == 2


# ── D: bloque CIERRE ──────────────────────────────────────────────────────────

class TestProcesarBloquesCierre:
    def test_d_persiste_resumen(self):
        bot = _chatbot()
        texto = _bloque_cierre("Resumen ejecutivo.", ["Carencia 1"], ["Punto 1"])
        bot._procesar_bloques(texto)
        assert bot.resumen_cumplimiento_registrado == "Resumen ejecutivo."
        assert "Carencia 1" in bot.carencias_registradas
        assert "Punto 1" in bot.puntos_revision_registrados

    def test_d_deduplicacion_carencias(self):
        bot = _chatbot()
        bot._procesar_bloques(_bloque_cierre("R1", ["Carencia dup"], []))
        bot._procesar_bloques(_bloque_cierre("R2", ["Carencia dup", "Nueva"], []))
        assert bot.carencias_registradas.count("Carencia dup") == 1
        assert "Nueva" in bot.carencias_registradas

    def test_d_texto_limpio_sin_cierre(self):
        bot = _chatbot()
        texto = "Intro.\n" + _bloque_cierre("Resumen.", [], []) + "\nEpílogo."
        limpio = bot._procesar_bloques(texto)
        assert "<<<CIERRE>>>" not in limpio
        assert "Intro." in limpio


# ── E: extraer_cumplimiento prioriza registros incrementales ─────────────────

class TestExtraerCumplimiento:
    def test_e_devuelve_registros_si_los_hay(self):
        bot = _chatbot()
        bot._procesar_bloques(_bloque_obl("Art. 9", "Gestión de riesgos", "cubierta"))
        result = bot.extraer_cumplimiento()
        assert result["obligaciones"] == bot.obligaciones_registradas
        assert len(result["obligaciones"]) == 1

    def test_f_llama_legacy_si_no_hay_registros(self):
        legacy_json = json.dumps({
            "obligaciones": [{"articulo": "Art. 9", "titulo": "G", "estado": "cubierta", "tipo": "obligacion", "descripcion": ""}],
            "carencias_detectadas": [],
            "puntos_revision_profesional": [],
            "resumen_cumplimiento": "legacy",
        })
        bot = _chatbot(legacy_json)
        bot.historial = [
            {"role": "user", "content": "hola"},
            {"role": "assistant", "content": "respuesta"},
        ]
        result = bot.extraer_cumplimiento()
        assert len(result["obligaciones"]) == 1
        assert result["obligaciones"][0]["articulo"] == "Art. 9"


# ── G: _reconstruir_obligaciones_desde_historial ──────────────────────────────

class TestReconstruirDesdeHistorial:
    def test_g_extrae_patron_registrado(self):
        bot = _chatbot()
        bot.historial = [
            {"role": "assistant", "content": "Registrado: Art. 9 — Gestión de riesgos: CUBIERTA"},
        ]
        result = bot._reconstruir_obligaciones_desde_historial()
        assert len(result) == 1
        assert result[0]["articulo"] == "Art. 9"
        assert result[0]["estado"] == "cubierta"

    def test_g_normaliza_no_cubierta_a_carencia(self):
        bot = _chatbot()
        bot.historial = [
            {"role": "assistant", "content": "Registrado: Art. 11 — Documentación técnica: NO CUBIERTA"},
        ]
        result = bot._reconstruir_obligaciones_desde_historial()
        assert result[0]["estado"] == "carencia"

    def test_g_ignora_mensajes_usuario(self):
        bot = _chatbot()
        bot.historial = [
            {"role": "user", "content": "Registrado: Art. 9 — algo: CUBIERTA"},
        ]
        result = bot._reconstruir_obligaciones_desde_historial()
        assert result == []

    def test_g_deduplica_por_articulo_titulo(self):
        bot = _chatbot()
        bot.historial = [
            {"role": "assistant", "content": "Registrado: Art. 9 — Gestión de riesgos: CARENCIA"},
            {"role": "assistant", "content": "Registrado: Art. 9 — Gestión de riesgos: CUBIERTA"},
        ]
        result = bot._reconstruir_obligaciones_desde_historial()
        assert len(result) == 1
        assert result[0]["estado"] == "cubierta"


# ── H: resetear() limpia atributos de registro ───────────────────────────────

class TestResetear:
    def test_h_resetear_limpia_registros(self):
        bot = _chatbot()
        bot._procesar_bloques(_bloque_obl("Art. 9", "Gestión de riesgos", "cubierta"))
        bot._procesar_bloques(_bloque_cierre("Resumen.", ["Carencia 1"], ["Punto 1"]))
        assert len(bot.obligaciones_registradas) == 1

        bot.resetear()

        assert bot.obligaciones_registradas == []
        assert bot.carencias_registradas == []
        assert bot.puntos_revision_registrados == []
        assert bot.resumen_cumplimiento_registrado == ""
        assert bot.historial == []
        assert bot.evaluacion_completa is False

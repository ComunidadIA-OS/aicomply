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
  C - _procesar_bloques deduplica obligaciones por (articulo, titulo, rol)
  D - _procesar_bloques procesa el bloque CIERRE
  E - extraer_cumplimiento devuelve registros incrementales si los hay
  F - extraer_cumplimiento llama al legacy si no hay registros
  G - _reconstruir_obligaciones_desde_historial extrae desde texto del asistente
  H - resetear() limpia los atributos de registro
  I - conflictos: recalificar una obligación ya registrada deja traza
  J - el prompt apunta al registro inyectado, no al historial recortable
  K - el estado se normaliza al registrarse; los irreconocibles se descartan
"""

import json

import pytest

from src.chatbot import AIComplyChat
from tests.conftest import MockProvider


# ── Helpers ────────────────────────────────────────────────────────────────────

def _bloque_obl(
    articulo: str,
    titulo: str,
    estado: str,
    tipo: str = "obligacion",
    rol: str = "proveedor",
) -> str:
    return (
        f'<<<OBLIGACION>>>{json.dumps({"articulo": articulo, "titulo": titulo, "estado": estado, "tipo": tipo, "descripcion": "desc", "rol": rol})}<<<FIN>>>'
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


# ── C: deduplicación por (articulo, titulo, rol) ──────────────────────────────

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

    def test_c_mismo_articulo_y_titulo_con_distinto_rol_son_dos_obligaciones(self):
        """El caso del doble rol: el Art. 49 aparece bajo Proveedor y bajo Implementador.

        Con la clave (articulo, titulo) la segunda entrada machacaba a la primera; y con la
        detección de conflictos, además, habría reportado una recalificación inexistente.
        """
        bot = _chatbot()
        bot._procesar_bloques(
            _bloque_obl("Art. 49", "Registro en base de datos UE", "carencia", rol="proveedor")
        )
        bot._procesar_bloques(
            _bloque_obl("Art. 49", "Registro en base de datos UE", "cubierta", rol="implementador")
        )

        assert len(bot.obligaciones_registradas) == 2
        assert {o["rol"] for o in bot.obligaciones_registradas} == {"proveedor", "implementador"}
        assert bot.conflictos_registrados == []


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
        assert bot.conflictos_registrados == []
        assert bot.resumen_cumplimiento_registrado == ""
        assert bot.historial == []
        assert bot.evaluacion_completa is False


# ── I: conflictos de estado (recalificaciones) ───────────────────────────────

class TestConflictosDeEstado:
    def test_i_recalificacion_actualiza_estado_y_anota_conflicto(self):
        bot = _chatbot()
        bot.historial = [
            {"role": "user", "content": "hola"},
            {"role": "assistant", "content": "primera"},
        ]
        bot._procesar_bloques(_bloque_obl("Art. 9", "Gestión de riesgos", "carencia"))
        bot._procesar_bloques(_bloque_obl("Art. 9", "Gestión de riesgos", "parcial"))

        assert bot.obligaciones_registradas[0]["estado"] == "parcial"
        assert len(bot.conflictos_registrados) == 1
        conflicto = bot.conflictos_registrados[0]
        assert conflicto["articulo"] == "Art. 9"
        assert conflicto["rol"] == "proveedor"
        assert conflicto["estado_anterior"] == "carencia"
        assert conflicto["estado_nuevo"] == "parcial"
        assert conflicto["turno"] == 2

    def test_i_reemitir_el_mismo_estado_no_genera_conflicto(self):
        """El modelo reemite bloques sin cambio; eso no es una recalificación."""
        bot = _chatbot()
        bot._procesar_bloques(_bloque_obl("Art. 9", "Gestión de riesgos", "cubierta"))
        bot._procesar_bloques(_bloque_obl("Art. 9", "Gestión de riesgos", "cubierta"))

        assert len(bot.obligaciones_registradas) == 1
        assert bot.conflictos_registrados == []

    @pytest.mark.parametrize(
        "anterior,nuevo,mejora",
        [
            ("carencia", "parcial", True),
            ("carencia", "cubierta", True),
            ("parcial", "no_aplica", True),
            ("carencia", "no_aplica", True),
            ("cubierta", "carencia", False),
            ("parcial", "carencia", False),
            ("cubierta", "parcial", False),
        ],
    )
    def test_i_direccion_del_cambio(self, anterior, nuevo, mejora):
        bot = _chatbot()
        bot._procesar_bloques(_bloque_obl("Art. 9", "Gestión de riesgos", anterior))
        bot._procesar_bloques(_bloque_obl("Art. 9", "Gestión de riesgos", nuevo))
        assert bot.conflictos_registrados[0]["mejora"] is mejora

    def test_i_solo_las_mejoras_escalan_a_revision_profesional(self):
        bot = _chatbot()
        bot._procesar_bloques(_bloque_obl("Art. 9", "Gestión de riesgos", "carencia"))
        bot._procesar_bloques(_bloque_obl("Art. 9", "Gestión de riesgos", "cubierta"))
        bot._procesar_bloques(_bloque_obl("Art. 11", "Documentación técnica", "cubierta"))
        bot._procesar_bloques(_bloque_obl("Art. 11", "Documentación técnica", "carencia"))

        puntos = bot.extraer_cumplimiento()["puntos_revision_profesional"]

        assert any("Art. 9" in p for p in puntos)
        assert not any("Art. 11" in p for p in puntos)

    def test_i_la_escalada_no_muta_los_puntos_registrados(self):
        bot = _chatbot()
        bot._procesar_bloques(_bloque_cierre("R", [], ["Punto original"]))
        bot._procesar_bloques(_bloque_obl("Art. 9", "Gestión de riesgos", "carencia"))
        bot._procesar_bloques(_bloque_obl("Art. 9", "Gestión de riesgos", "cubierta"))

        bot.extraer_cumplimiento()

        assert bot.puntos_revision_registrados == ["Punto original"]


# ── J: el prompt apunta al registro, no al historial ─────────────────────────

class TestPromptApuntaAlRegistro:
    """Guardián: el prompt no puede volver a mandar al modelo a mirar el historial.

    El historial lo recorta _historial_truncado() sin avisar, así que exigirle que
    verifique contra él es pedirle que concluya sobre datos que el código le ha quitado.
    """

    def test_j_el_prompt_lleva_el_marcador(self):
        from prompts.system_prompt_cumplimiento import SYSTEM_PROMPT_CUMPLIMIENTO  # noqa: PLC0415
        from src.chatbot import MARCADOR_OBLIGACIONES  # noqa: PLC0415

        assert MARCADOR_OBLIGACIONES in SYSTEM_PROMPT_CUMPLIMIENTO

    def test_j_el_prompt_ya_no_manda_comprobar_el_historial(self):
        from prompts.system_prompt_cumplimiento import SYSTEM_PROMPT_CUMPLIMIENTO  # noqa: PLC0415

        assert "compruébalo en el historial" not in SYSTEM_PROMPT_CUMPLIMIENTO
        assert "REGISTRO DE OBLIGACIONES YA EVALUADAS" in SYSTEM_PROMPT_CUMPLIMIENTO

    def test_j_aplicar_no_rompe_con_las_llaves_literales_del_prompt(self):
        """Mismo motivo que en aplicar_calendario: .format() reventaría con <<<OBLIGACION>>>{...}."""
        from prompts.system_prompt_cumplimiento import SYSTEM_PROMPT_CUMPLIMIENTO  # noqa: PLC0415
        from src.chatbot import aplicar_obligaciones_registradas  # noqa: PLC0415

        resuelto = aplicar_obligaciones_registradas(SYSTEM_PROMPT_CUMPLIMIENTO, [])
        assert '<<<OBLIGACION>>>{"articulo"' in resuelto
        assert "{OBLIGACIONES_REGISTRADAS}" not in resuelto


# ── K: normalización del estado en el camino principal ───────────────────────

class TestNormalizacionDeEstado:
    """El estado se canoniza antes de guardarse, no solo en la reconstrucción de emergencia.

    report_generator mete cualquier estado que no reconozca en "no aplica" y lo saca del
    denominador, así que una CARENCIA en mayúsculas subía el grado de cumplimiento de
    portada sin que nada lo avisara.
    """

    @pytest.mark.parametrize(
        "emitido,esperado",
        [
            ("CARENCIA", "carencia"),
            ("Parcial", "parcial"),
            ("CUBIERTA", "cubierta"),
            ("no_cubierta", "carencia"),
            ("NO CUBIERTA", "carencia"),
            ("no aplica", "no_aplica"),
            ("  carencia  ", "carencia"),
        ],
    )
    def test_k_normaliza_las_variantes_del_prompt(self, emitido, esperado):
        bot = _chatbot()
        bot._procesar_bloques(_bloque_obl("Art. 9", "Gestión de riesgos", emitido))
        assert bot.obligaciones_registradas[0]["estado"] == esperado

    @pytest.mark.parametrize("invalido", ["incumplida", "", "pendiente", "sí"])
    def test_k_descarta_el_bloque_con_estado_irreconocible(self, invalido):
        """Mejor no registrar la obligación que registrarla con un estado que el informe
        interpretará como "no aplica" y sacará del cálculo."""
        bot = _chatbot()
        bot._procesar_bloques(_bloque_obl("Art. 9", "Gestión de riesgos", invalido))
        assert bot.obligaciones_registradas == []

    def test_k_una_variante_no_cuenta_como_recalificacion(self):
        """CARENCIA y carencia son el mismo estado: no puede generar un conflicto falso."""
        bot = _chatbot()
        bot._procesar_bloques(_bloque_obl("Art. 9", "Gestión de riesgos", "carencia"))
        bot._procesar_bloques(_bloque_obl("Art. 9", "Gestión de riesgos", "CARENCIA"))

        assert len(bot.obligaciones_registradas) == 1
        assert bot.conflictos_registrados == []

    def test_k_el_estado_normalizado_es_el_que_viaja_al_informe(self):
        bot = _chatbot()
        bot._procesar_bloques(_bloque_obl("Art. 9", "Gestión de riesgos", "CARENCIA"))
        bot._procesar_bloques(_bloque_obl("Art. 11", "Documentación", "CUBIERTA"))

        estados = [o["estado"] for o in bot.extraer_cumplimiento()["obligaciones"]]

        assert estados == ["carencia", "cubierta"]

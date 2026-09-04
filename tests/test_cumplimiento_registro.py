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
  L - la clave del catálogo identifica la obligación; el colapso deja rastro
  M - la traza narrada se captura para contrastar el registro, sin entrar en él
  N - extraer_cumplimiento devuelve incoherencias en sus dos ramas
  O - el catálogo declara claves estables y no las repite
"""

import json
import re

import pytest

from prompts.system_prompt_cumplimiento import SYSTEM_PROMPT_CUMPLIMIENTO
from src.chatbot import AIComplyChat
from tests.conftest import MockProvider


# ── Helpers ────────────────────────────────────────────────────────────────────

def _bloque_obl(
    articulo: str,
    titulo: str,
    estado: str,
    tipo: str = "obligacion",
    rol: str = "proveedor",
    clave: str = "",
    descripcion: str = "desc",
) -> str:
    """Bloque <<<OBLIGACION>>> tal y como lo emite el modelo.

    `clave` se omite del JSON cuando viene vacía, que es el valor por defecto: así los tests que
    no la mencionan siguen ejercitando el camino de respaldo —la identidad por
    (articulo, titulo, rol)— igual que antes de que el catálogo tuviera claves.
    """
    payload = {
        "articulo": articulo,
        "titulo": titulo,
        "estado": estado,
        "tipo": tipo,
        "descripcion": descripcion,
        "rol": rol,
    }
    if clave:
        payload["clave"] = clave
    return f"<<<OBLIGACION>>>{json.dumps(payload)}<<<FIN>>>"


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

        bot._procesar_bloques("Obligación 1 de 11: Alfabetización.")
        bot._procesar_bloques(_bloque_obl("Art. 9", "Gestión de riesgos", "parcial"))

        bot.resetear()

        assert bot.obligaciones_registradas == []
        assert bot.obligaciones_desplazadas == []
        assert bot.carencias_registradas == []
        assert bot.puntos_revision_registrados == []
        assert bot.conflictos_registrados == []
        assert bot.resumen_cumplimiento_registrado == ""
        assert bot.historial == []
        assert bot.evaluacion_completa is False
        assert bot.total_narrado is None
        assert bot.ordinal_narrado_max is None
        assert bot.resumen_final_narrado == []


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


# ── L: la clave del catálogo y el colapso de identidad ───────────────────────

def _codigos(bot: AIComplyChat) -> set[str]:
    return {i["codigo"] for i in bot.extraer_cumplimiento()["incoherencias"]}


class TestClaveDeCatalogo:
    """Las dos entradas de Art. 26.5 del catálogo del implementador.

    Vigilancia del funcionamiento e incidentes graves son obligaciones distintas que comparten
    apartado. Con la identidad (articulo, titulo, rol), si el modelo les da el mismo título la
    segunda desplaza a la primera y el recuento baja de once a diez sin dejar rastro: como el
    estado coincidía, ni siquiera se anotaba un conflicto.
    """

    def test_l_dos_obligaciones_del_mismo_apartado_sin_clave_colapsan_pero_dejan_rastro(self):
        bot = _chatbot()
        bot._procesar_bloques(_bloque_obl(
            "Art. 26.5", "Vigilancia y comunicación", "cubierta", rol="implementador",
            descripcion="Vigila el funcionamiento e informa al proveedor (Art. 72).",
        ))
        bot._procesar_bloques(_bloque_obl(
            "Art. 26.5", "Vigilancia y comunicación", "cubierta", rol="implementador",
            descripcion="Comunica los incidentes graves al proveedor (Art. 73).",
        ))

        # El colapso sigue ocurriendo: gana la última, no se repara.
        assert len(bot.obligaciones_registradas) == 1
        assert "Art. 73" in bot.obligaciones_registradas[0]["descripcion"]
        # Pero ya no es silencioso: la desplazada se conserva entera.
        assert len(bot.obligaciones_desplazadas) == 1
        assert "Art. 72" in bot.obligaciones_desplazadas[0]["previa"]["descripcion"]
        # Y no era una recalificación: el estado no cambió.
        assert bot.conflictos_registrados == []

        incoherencias = bot.extraer_cumplimiento()["incoherencias"]
        colapsos = [i for i in incoherencias if i["codigo"] == "colapso_identidad"]
        assert len(colapsos) == 1
        assert colapsos[0]["gravedad"] == "bloqueante"
        assert any("Art. 72" in d for d in colapsos[0]["detalle"]), (
            "el detalle debe decir qué se perdió, no solo que se perdió algo"
        )

    def test_l_con_claves_distintas_las_dos_conviven(self):
        """La causa atacada: con la clave del catálogo la colisión no llega a producirse."""
        bot = _chatbot()
        bot._procesar_bloques(_bloque_obl(
            "Art. 26.5", "Vigilancia y comunicación", "cubierta", rol="implementador",
            clave="26.5-vigilancia",
        ))
        bot._procesar_bloques(_bloque_obl(
            "Art. 26.5", "Vigilancia y comunicación", "parcial", rol="implementador",
            clave="26.5-incidentes",
        ))

        assert len(bot.obligaciones_registradas) == 2
        assert bot.obligaciones_desplazadas == []
        assert bot.conflictos_registrados == []
        assert "colapso_identidad" not in _codigos(bot)

    def test_l_misma_clave_y_estado_distinto_es_recalificacion_no_colapso(self):
        bot = _chatbot()
        bot._procesar_bloques(_bloque_obl(
            "Art. 26.5", "Vigilancia", "carencia", rol="implementador", clave="26.5-vigilancia",
        ))
        bot._procesar_bloques(_bloque_obl(
            "Art. 26.5", "Vigilancia del funcionamiento", "cubierta", rol="implementador",
            clave="26.5-vigilancia", descripcion="Ahora hay procedimiento documentado.",
        ))

        assert len(bot.obligaciones_registradas) == 1
        assert len(bot.conflictos_registrados) == 1
        assert bot.conflictos_registrados[0]["estado_nuevo"] == "cubierta"
        # Aunque el título y la descripción cambien: la clave es la identidad, y reformular una
        # obligación ya identificada no la convierte en otra.
        assert "colapso_identidad" not in _codigos(bot)

    @pytest.mark.parametrize("variante", ["26.5-Vigilancia", "26.5 vigilancia", " 26.5_vigilancia "])
    def test_l_la_clave_se_normaliza_antes_de_comparar(self, variante):
        """El modelo copia la clave a mano; una mayúscula no puede duplicar la obligación."""
        bot = _chatbot()
        bot._procesar_bloques(_bloque_obl(
            "Art. 26.5", "Vigilancia", "carencia", rol="implementador", clave="26.5-vigilancia",
        ))
        bot._procesar_bloques(_bloque_obl(
            "Art. 26.5", "Vigilancia", "cubierta", rol="implementador", clave=variante,
        ))

        assert len(bot.obligaciones_registradas) == 1
        assert bot.obligaciones_registradas[0]["estado"] == "cubierta"

    def test_l_sin_clave_el_doble_rol_sigue_funcionando(self):
        """Regresión del caso C: el respaldo (articulo, titulo, rol) no se ha tocado."""
        bot = _chatbot()
        bot._procesar_bloques(
            _bloque_obl("Art. 49", "Registro en base de datos UE", "carencia", rol="proveedor")
        )
        bot._procesar_bloques(
            _bloque_obl("Art. 49", "Registro en base de datos UE", "cubierta", rol="implementador")
        )

        assert len(bot.obligaciones_registradas) == 2
        assert bot.obligaciones_desplazadas == []

    def test_l_la_clave_registrada_se_inyecta_en_el_prompt(self):
        """Para que el modelo la copie en el turno siguiente en vez de reinventarla."""
        from src.chatbot import formatear_obligaciones_registradas  # noqa: PLC0415

        texto = formatear_obligaciones_registradas([
            {"articulo": "Art. 26.5", "titulo": "Vigilancia", "estado": "cubierta",
             "rol": "implementador", "clave": "26.5-vigilancia"},
        ])
        assert "[clave: 26.5-vigilancia]" in texto


# ── M: la traza narrada, que es el contraste externo del registro ────────────

class TestTrazaNarrada:
    """Lo que el modelo cuenta sobre su propio avance, capturado para contrastarlo.

    En el recorrido del 4 de septiembre el asistente narraba «Obligación 10 de 11» mientras el
    registro tenía una entrada, y nada comparaba las dos cuentas.
    """

    def test_m_captura_el_ordinal_y_el_total(self):
        bot = _chatbot()
        bot._procesar_bloques("Obligación 3 de 11: conservación de registros.")
        assert bot.total_narrado == 11
        assert bot.ordinal_narrado_max == 3

    def test_m_el_ordinal_maximo_no_retrocede(self):
        bot = _chatbot()
        bot._procesar_bloques("Obligación 7 de 11: cooperación.")
        bot._procesar_bloques("Volviendo a la Obligación 2 de 11 que dejamos abierta.")
        assert bot.ordinal_narrado_max == 7

    def test_m_captura_las_lineas_del_resumen_final(self):
        bot = _chatbot()
        bot._procesar_bloques(
            "Resumen final:\n"
            "- Art. 4 — Alfabetización en IA: CUBIERTA\n"
            "- Art. 26.6 — Conservación de registros: PARCIAL\n"
            "- Art. 27 — Evaluación de impacto: NO APLICA\n"
        )
        resumen = bot.resumen_final_narrado
        assert [ln["articulo"] for ln in resumen] == ["Art. 4", "Art. 26.6", "Art. 27"]
        assert [ln["estado"] for ln in resumen] == ["cubierta", "parcial", "no_aplica"]

    def test_m_acumula_entre_turnos_sin_duplicar(self):
        """Si el modelo repite una lista parcial, quedarse con la última perdería lo anterior."""
        bot = _chatbot()
        bot._procesar_bloques("- Art. 4 — Alfabetización: CUBIERTA\n")
        bot._procesar_bloques(
            "- Art. 4 — Alfabetización: PARCIAL\n- Art. 26.1 — Instrucciones de uso: CUBIERTA\n"
        )
        assert len(bot.resumen_final_narrado) == 2
        assert bot.resumen_final_narrado[0]["estado"] == "parcial"

    def test_m_la_traza_no_entra_en_el_registro(self):
        """Los parsers de prosa son auditores: no añaden obligaciones ni corrigen estados."""
        bot = _chatbot()
        bot._procesar_bloques(
            "Obligación 11 de 11.\n- Art. 27 — Evaluación de impacto: CARENCIA\n"
        )
        assert bot.obligaciones_registradas == []


# ── N: extraer_cumplimiento devuelve incoherencias en las dos ramas ──────────

class TestIncoherenciasEnLasDosRamas:
    def test_n_la_rama_principal_las_incluye(self):
        bot = _chatbot()
        bot._procesar_bloques("Obligación 1 de 11: alfabetización.")
        bot._procesar_bloques(_bloque_obl("Art. 4", "Alfabetización", "cubierta"))

        resultado = bot.extraer_cumplimiento()

        assert "incoherencias" in resultado
        assert "recuento_narrado" in {i["codigo"] for i in resultado["incoherencias"]}

    def test_n_la_rama_de_respaldo_declara_que_el_registro_es_reconstruido(self):
        """Es el camino más degradado: las obligaciones salen de raspar prosa, no de bloques.

        Sin esta incoherencia el informe leería .get("incoherencias", []), no encontraría nada y
        volvería a publicar un porcentaje justo donde menos se sostiene.
        """
        bot = _chatbot('{"obligaciones": [], "carencias_detectadas": []}')
        bot.historial = [
            {"role": "user", "content": "adelante"},
            {"role": "assistant", "content": "Registrado: Art. 9 — Gestión de riesgos: CUBIERTA"},
        ]

        resultado = bot.extraer_cumplimiento()

        assert len(resultado["obligaciones"]) == 1
        codigos = {i["codigo"] for i in resultado["incoherencias"]}
        assert "registro_reconstruido" in codigos
        assert any(
            i["gravedad"] == "bloqueante"
            for i in resultado["incoherencias"] if i["codigo"] == "registro_reconstruido"
        )


# ── O: el catálogo declara claves estables y no las repite ───────────────────

_RE_CLAVE_CATALOGO = re.compile(r"\[clave:\s*([^\]]+)\]")

# El Art. 4 aparece dos veces en el catálogo —en el bloque transversal y en el de MÍNIMO— y las
# dos líneas son la MISMA obligación legal, que además coexisten en un análisis de riesgo
# mínimo. Darles claves distintas produciría dos entradas para una sola obligación, con el
# denominador inflado y la recalificación sin reconocer. Quien añada otra colisión tiene que
# ampliar esta constante a conciencia, que es la fricción que se busca.
_SLUGS_REPETIBLES = {"4-alfabetizacion"}


class TestClavesDelCatalogo:
    def test_o_cada_obligacion_del_implementador_declara_su_clave(self):
        bloque = SYSTEM_PROMPT_CUMPLIMIENTO.split("ALTO RIESGO — Rol Implementador (Art. 26):")[1]
        bloque = bloque.split("ALTO RIESGO — Rol Distribuidor")[0]
        entradas = [ln for ln in bloque.splitlines() if ln.startswith("- Art. ")]

        assert entradas, "el catálogo del implementador debería seguir teniendo entradas"
        sin_clave = [ln for ln in entradas if not _RE_CLAVE_CATALOGO.search(ln)]
        assert not sin_clave, f"entradas del implementador sin [clave: …]: {sin_clave}"

    def test_o_las_dos_entradas_del_art_4_declaran_su_clave(self):
        """No usan la forma de línea del implementador, así que el guardián anterior no las ve."""
        lineas = [
            ln for ln in SYSTEM_PROMPT_CUMPLIMIENTO.splitlines()
            if ln.startswith("- ") and "(Art. 4)" in ln
        ]
        assert len(lineas) == 2, "el Art. 4 debería seguir apareciendo en transversal y en MÍNIMO"
        for ln in lineas:
            assert _RE_CLAVE_CATALOGO.search(ln), f"el Art. 4 no declara clave: {ln}"

    def test_o_los_dos_art_26_5_tienen_claves_distintas(self):
        """El colapso que motiva la rama deja de ser posible si estas dos difieren."""
        lineas = [
            ln for ln in SYSTEM_PROMPT_CUMPLIMIENTO.splitlines()
            if ln.startswith("- Art. 26.5")
        ]
        assert len(lineas) == 2
        claves = {_RE_CLAVE_CATALOGO.search(ln).group(1).strip() for ln in lineas}
        assert len(claves) == 2, f"los dos Art. 26.5 comparten clave: {claves}"

    def test_o_las_claves_no_se_repiten_en_todo_el_catalogo(self):
        """Barre el prompt entero: mirar solo el bloque del implementador dejaría pasar un
        duplicado en el Art. 4, que usa otra forma de línea."""
        claves = [c.strip() for c in _RE_CLAVE_CATALOGO.findall(SYSTEM_PROMPT_CUMPLIMIENTO)]
        repetidas = {c for c in claves if claves.count(c) > 1} - _SLUGS_REPETIBLES
        assert not repetidas, f"claves duplicadas en el catálogo: {repetidas}"

    def test_o_el_contrato_del_bloque_documenta_el_campo(self):
        assert '"clave"' in SYSTEM_PROMPT_CUMPLIMIENTO
        assert "OMITE el campo" in SYSTEM_PROMPT_CUMPLIMIENTO

    def test_o_el_prompt_fija_que_la_m_es_el_total_del_catalogo(self):
        """Si M saliera del registro, compararla con las registradas no detectaría nada nunca."""
        assert "Obligación N de M" in SYSTEM_PROMPT_CUMPLIMIENTO
        assert "NO es el número de obligaciones registradas" in SYSTEM_PROMPT_CUMPLIMIENTO

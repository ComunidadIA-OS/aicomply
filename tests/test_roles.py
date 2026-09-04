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

"""Tests para detección, normalización y renderizado de roles bajo el AI Act.

Cubre los casos de prueba del bug de doble rol Proveedor / Implementador:
  A - Desarrollado internamente y usado internamente → Proveedor / Implementador
  B - Comprado/licenciado y usado sin modificación → Implementador
  C - Distribuido sin modificación → Distribuidor
  D - Desarrollado para terceros sin uso interno → Proveedor
  E - Implementador con modificación sustancial → señal Art. 25
"""

import json
import logging

import pytest

from prompts.system_prompts import SYSTEM_PROMPT_CHATBOT
from src.chatbot import _PROMPT_EXTRAER_CLASIFICACION, AIComplyChat
from src.report_generator import GeneradorInforme, _capitalizar_roles
from tests.conftest import MockProvider

# ── Helpers ───────────────────────────────────────────────────────────────────

def _clasif(rol, roles_multiples=None, clasificacion="ALTO", **kw):
    return {
        "clasificacion": clasificacion,
        "rol": rol,
        "roles_multiples": roles_multiples if roles_multiples is not None else [],
        "descripcion_sistema": "Sistema de prueba",
        "sector": "Industria",
        "estados_adicionales": [],
        "obligaciones_preliminares": [],
        "puntos_indeterminados": [],
        **kw,
    }


def _cumpl_vacio():
    return {
        "obligaciones": [],
        "carencias_detectadas": [],
        "puntos_revision_profesional": [],
        "resumen_cumplimiento": "",
    }


# ── Tests de _capitalizar_roles ───────────────────────────────────────────────

class TestCapitalizarRoles:
    def test_rol_simple(self):
        assert _capitalizar_roles("proveedor") == "Proveedor"

    def test_rol_ya_capitalizado(self):
        assert _capitalizar_roles("Proveedor") == "Proveedor"

    def test_doble_rol(self):
        assert _capitalizar_roles("proveedor / implementador") == "Proveedor / Implementador"

    def test_doble_rol_sin_espacios(self):
        assert _capitalizar_roles("proveedor/implementador") == "Proveedor / Implementador"

    def test_no_lowercase_segunda_parte(self):
        # Verifica que no se hace .capitalize() global (que bajaría Implementador)
        result = _capitalizar_roles("Proveedor / Implementador")
        assert result == "Proveedor / Implementador"

    def test_guion_sustituido(self):
        # Distribuidor simple
        assert _capitalizar_roles("distribuidor") == "Distribuidor"


# ── Tests de _normalizar_clasificacion_data ───────────────────────────────────

class TestNormalizarClasificacionData:
    """Verifica que el normalizador post-extracción mantiene roles_multiples consistente."""

    def test_a_doble_rol_en_roles_multiples(self):
        """Caso A: el LLM ya emitió roles_multiples correcto."""
        datos = {
            "clasificacion": "ALTO",
            "rol": "proveedor",
            "roles_multiples": ["proveedor", "implementador"],
        }
        result = AIComplyChat._normalizar_clasificacion_data(datos)
        assert "proveedor" in result["roles_multiples"]
        assert "implementador" in result["roles_multiples"]

    def test_a_doble_rol_en_campo_rol_barra(self):
        """Caso A: LLM puso 'proveedor / implementador' en rol, roles_multiples vacío."""
        datos = {
            "clasificacion": "ALTO",
            "rol": "proveedor / implementador",
            "roles_multiples": [],
        }
        result = AIComplyChat._normalizar_clasificacion_data(datos)
        assert set(result["roles_multiples"]) == {"proveedor", "implementador"}

    def test_a_doble_rol_en_campo_rol_e(self):
        """Variante con 'e' como separador."""
        datos = {"rol": "proveedor e implementador", "roles_multiples": []}
        result = AIComplyChat._normalizar_clasificacion_data(datos)
        assert set(result["roles_multiples"]) == {"proveedor", "implementador"}

    def test_a_doble_rol_coma(self):
        """Variante con coma."""
        datos = {"rol": "proveedor, implementador", "roles_multiples": []}
        result = AIComplyChat._normalizar_clasificacion_data(datos)
        assert set(result["roles_multiples"]) == {"proveedor", "implementador"}

    def test_a_alias_provider_deployer(self):
        """Alias en inglés provider_deployer."""
        datos = {"rol": "provider_deployer", "roles_multiples": []}
        result = AIComplyChat._normalizar_clasificacion_data(datos)
        assert set(result["roles_multiples"]) == {"proveedor", "implementador"}

    def test_a_alias_proveedor_implementador_guion(self):
        """Alias proveedor_implementador."""
        datos = {"rol": "proveedor_implementador", "roles_multiples": []}
        result = AIComplyChat._normalizar_clasificacion_data(datos)
        assert set(result["roles_multiples"]) == {"proveedor", "implementador"}

    def test_b_implementador_solo(self):
        """Caso B: solo implementador."""
        datos = {"rol": "implementador", "roles_multiples": []}
        result = AIComplyChat._normalizar_clasificacion_data(datos)
        assert result["roles_multiples"] == ["implementador"]

    def test_c_distribuidor_solo(self):
        """Caso C: solo distribuidor."""
        datos = {"rol": "distribuidor", "roles_multiples": []}
        result = AIComplyChat._normalizar_clasificacion_data(datos)
        assert result["roles_multiples"] == ["distribuidor"]

    def test_d_proveedor_solo(self):
        """Caso D: solo proveedor (comercializa a terceros, no usa internamente)."""
        datos = {"rol": "proveedor", "roles_multiples": []}
        result = AIComplyChat._normalizar_clasificacion_data(datos)
        assert result["roles_multiples"] == ["proveedor"]

    def test_e_estados_adicionales_art25(self):
        """Caso E: implementador con modificación sustancial → 'Convertirse en proveedor'."""
        datos = {
            "rol": "implementador",
            "roles_multiples": ["implementador"],
            "estados_adicionales": ["Convertirse en proveedor"],
        }
        result = AIComplyChat._normalizar_clasificacion_data(datos)
        assert "Convertirse en proveedor" in result.get("estados_adicionales", [])
        # El rol base sigue siendo implementador hasta que se confirme
        assert "implementador" in result["roles_multiples"]

    def test_deduplicacion(self):
        """Roles duplicados en roles_multiples se deducan."""
        datos = {
            "rol": "proveedor",
            "roles_multiples": ["proveedor", "proveedor", "implementador"],
        }
        result = AIComplyChat._normalizar_clasificacion_data(datos)
        assert result["roles_multiples"].count("proveedor") == 1

    def test_roles_multiples_nunca_vacio(self):
        """Si hay al menos un rol, roles_multiples nunca queda vacío."""
        datos = {"rol": "importador", "roles_multiples": []}
        result = AIComplyChat._normalizar_clasificacion_data(datos)
        assert len(result["roles_multiples"]) >= 1


# ── Apartados del Art. 26 en las obligaciones preliminares (regresión B10) ────

def _preliminares_normalizadas(*obligaciones) -> list[str]:
    datos = {"rol": "implementador", "roles_multiples": ["implementador"],
             "obligaciones_preliminares": list(obligaciones)}
    return AIComplyChat._normalizar_clasificacion_data(datos)["obligaciones_preliminares"]


class TestApartadosPreliminares:
    """B10: el evaluador citaba apartados del Art. 26 que contradecían al análisis
    de cumplimiento dentro del mismo informe. El recorte es solo del Art. 26."""

    @pytest.mark.parametrize("entrada,esperado", [
        ("Supervisión humana (Art. 26.1)", "Supervisión humana (Art. 26)"),
        ("Conservación de registros (Art. 26.5)", "Conservación de registros (Art. 26)"),
        ("Notificación de incidentes (Art. 26.10)", "Notificación de incidentes (Art. 26)"),
        ("Art. 26.3: datos de entrada", "Art. 26: datos de entrada"),
        ("Uso conforme a instrucciones (art 26.1)", "Uso conforme a instrucciones (art 26)"),
    ])
    def test_el_apartado_del_art_26_se_recorta(self, entrada, esperado):
        assert _preliminares_normalizadas(entrada) == [esperado]

    def test_el_art_26_sin_apartado_se_queda_igual(self):
        assert _preliminares_normalizadas("Obligaciones del implementador (Art. 26)") == [
            "Obligaciones del implementador (Art. 26)"
        ]

    @pytest.mark.parametrize("entrada", [
        "Informar de que se interactúa con una IA (Art. 50.1)",
        "Marcado de contenido sintético (Art. 50.2)",
        "Categorización biométrica prohibida (Art. 5.1.g)",
        "Revisar si aplica el Art. 6.2",
        "Registro en la base de datos de la UE (Art. 49)",
    ])
    def test_los_demas_articulos_conservan_su_apartado(self, entrada):
        """El recorte es selectivo a propósito: en el Art. 50 cada apartado es una
        obligación distinta, y en el Art. 5 la letra es el dato principal del informe."""
        assert _preliminares_normalizadas(entrada) == [entrada]

    def test_una_obligacion_sin_articulo_no_revienta(self):
        assert _preliminares_normalizadas("Designar un responsable de cumplimiento") == [
            "Designar un responsable de cumplimiento"
        ]

    def test_lista_vacia_o_campo_ausente_no_revientan(self):
        assert _preliminares_normalizadas() == []
        datos = {"rol": "implementador", "roles_multiples": ["implementador"]}
        assert "obligaciones_preliminares" not in AIComplyChat._normalizar_clasificacion_data(datos)

    def test_un_elemento_no_textual_se_deja_pasar(self):
        """El JSON del LLM puede traer cualquier cosa; el normalizador no es un validador."""
        datos = {"rol": "implementador", "roles_multiples": [],
                 "obligaciones_preliminares": [None, 3, "Supervisión (Art. 26.2)"]}
        result = AIComplyChat._normalizar_clasificacion_data(datos)
        assert result["obligaciones_preliminares"] == [None, 3, "Supervisión (Art. 26)"]


# ── Tests de renderizado en el informe Markdown ───────────────────────────────

class TestRenderizadoRolInforme:
    """Verifica que el informe Markdown muestra los roles correctamente."""

    def test_informe_clasificacion_doble_rol(self):
        datos = _clasif("proveedor / implementador", ["proveedor", "implementador"])
        md = GeneradorInforme().generar_informe_clasificacion(datos)
        assert "Proveedor / Implementador" in md

    def test_informe_clasificacion_rol_simple(self):
        datos = _clasif("implementador", ["implementador"])
        md = GeneradorInforme().generar_informe_clasificacion(datos)
        assert "Implementador" in md
        assert "Proveedor" not in md.split("**Rol de la entidad:**")[1].split("\n")[0]

    def test_informe_completo_doble_rol_en_cabecera(self):
        datos = _clasif("proveedor / implementador", ["proveedor", "implementador"])
        md = GeneradorInforme().generar_informe_completo(datos, _cumpl_vacio())
        assert "**Rol de la entidad:** Proveedor / Implementador" in md

    def test_informe_completo_rol_simple_sin_barra(self):
        datos = _clasif("distribuidor", ["distribuidor"])
        md = GeneradorInforme().generar_informe_completo(datos, _cumpl_vacio())
        assert "**Rol de la entidad:** Distribuidor" in md
        assert "/" not in md.split("**Rol de la entidad:**")[1].split("\n")[0]

    def test_retrocompatibilidad_sin_roles_multiples(self):
        """Datos sin roles_multiples (vacío) usan el campo rol como fallback."""
        datos = _clasif("proveedor", [])
        md = GeneradorInforme().generar_informe_clasificacion(datos)
        assert "Proveedor" in md


# ── Tests de renderizado PDF — portada y página sistema ──────────────────────

class TestPdfRolPortada:
    """Verifica que la portada PDF muestra los roles sin romper el capitalize."""

    def _pdf(self, datos_clasif, datos_cumpl=None):
        if datos_cumpl is None:
            datos_cumpl = _cumpl_vacio()
        md = GeneradorInforme().generar_informe_completo(datos_clasif, datos_cumpl)
        return GeneradorInforme().exportar_pdf(md)

    def test_pdf_doble_rol_es_bytes(self):
        datos = _clasif("proveedor / implementador", ["proveedor", "implementador"])
        pdf = self._pdf(datos)
        assert isinstance(pdf, bytes) and pdf[:4] == b"%PDF"

    def test_pdf_rol_simple_es_bytes(self):
        datos = _clasif("implementador", ["implementador"])
        pdf = self._pdf(datos)
        assert isinstance(pdf, bytes) and pdf[:4] == b"%PDF"

    def test_pdf_no_lowercase_segunda_parte_doble_rol(self):
        """El PDF no debe mostrar 'Proveedor / implementador' (segunda parte en minúsculas)."""
        datos = _clasif("proveedor / implementador", ["proveedor", "implementador"])
        md = GeneradorInforme().generar_informe_completo(datos, _cumpl_vacio())
        # El encabezado Markdown debe tener ambas partes capitalizadas
        assert "Proveedor / Implementador" in md
        assert "Proveedor / implementador" not in md


# ── Regresión B15: no se añade un rol que el árbol no confirmó ────────────────

class TestRolNoConfirmado:
    """El evaluador añadía 'proveedor' a un implementador puro (hallazgo B15).

    El árbol había cerrado el rol dos veces como implementadora —adquirido de un tercero,
    sin modificaciones— y el informe final lo amplió a doble rol, pasando de 10 obligaciones
    a 23. La defensa vive en los prompts; aquí se fija lo que el código sí puede garantizar.
    """

    def test_estrechamiento_rol_hacia_roles_multiples(self):
        """'rol' con un rol de más se estrecha hacia el array, no al revés."""
        datos = {"rol": "proveedor / implementador", "roles_multiples": ["implementador"]}
        result = AIComplyChat._normalizar_clasificacion_data(datos)
        assert result["rol"] == "implementador"
        assert result["roles_multiples"] == ["implementador"]

    def test_estrechamiento_con_varios_roles_restantes(self):
        """Al estrechar hacia un array de varios, 'rol' los recompone con ' / '."""
        datos = {
            "rol": "proveedor / implementador",
            "roles_multiples": ["implementador", "distribuidor"],
        }
        result = AIComplyChat._normalizar_clasificacion_data(datos)
        assert result["rol"] == "implementador / distribuidor"
        assert result["roles_multiples"] == ["implementador", "distribuidor"]

    def test_el_doble_rol_legitimo_sobrevive(self):
        """Guarda del caso legítimo: desarrollado Y usado internamente siguen siendo dos roles."""
        datos = {"rol": "proveedor", "roles_multiples": ["proveedor", "implementador"]}
        result = AIComplyChat._normalizar_clasificacion_data(datos)
        assert result["roles_multiples"] == ["proveedor", "implementador"]
        assert result["rol"] == "proveedor / implementador"

    def test_el_normalizador_no_inventa_proveedor(self):
        """Un implementador único sale igual de la normalización."""
        datos = {"rol": "implementador", "roles_multiples": ["implementador"]}
        result = AIComplyChat._normalizar_clasificacion_data(datos)
        assert result["roles_multiples"] == ["implementador"]
        assert "proveedor" not in result["rol"]

    def test_el_estado_art_25_no_convierte_el_rol_por_si_solo(self):
        """'Convertirse en proveedor' es un estado, no un rol: no entra en roles_multiples."""
        datos = {
            "rol": "implementador",
            "roles_multiples": ["implementador"],
            "estados_adicionales": ["Convertirse en proveedor"],
        }
        result = AIComplyChat._normalizar_clasificacion_data(datos)
        assert result["roles_multiples"] == ["implementador"]
        assert "proveedor" not in result["rol"]

    def test_la_discrepancia_se_registra(self, caplog):
        """El estrechamiento no es silencioso: deja warning con los dos valores."""
        datos = {"rol": "proveedor / implementador", "roles_multiples": ["implementador"]}
        with caplog.at_level(logging.WARNING, logger="src.chatbot"):
            AIComplyChat._normalizar_clasificacion_data(datos)
        assert "Discrepancia de rol" in caplog.text
        assert "proveedor" in caplog.text
        assert "implementador" in caplog.text

    @pytest.mark.parametrize("datos", [
        {"rol": "implementador", "roles_multiples": ["implementador"]},
        {"rol": "proveedor", "roles_multiples": ["proveedor", "implementador"]},
        {"rol": "proveedor / implementador", "roles_multiples": ["proveedor", "implementador"]},
        {"rol": "implementador", "roles_multiples": []},
    ])
    def test_sin_discrepancia_no_hay_warning(self, datos, caplog):
        """Cuando los dos campos coinciden, el log queda limpio."""
        with caplog.at_level(logging.WARNING, logger="src.chatbot"):
            AIComplyChat._normalizar_clasificacion_data(datos)
        assert "Discrepancia de rol" not in caplog.text


class TestImplementadorUnicoExtremoAExtremo:
    """De la extracción al informe: un implementador único no recibe obligaciones de proveedor."""

    _JSON_IMPLEMENTADOR = json.dumps({
        "clasificacion": "ALTO",
        "rol": "implementador",
        "roles_multiples": ["implementador"],
        "estados_adicionales": [],
        "descripcion_sistema": "Sistema adquirido a un tercero y usado sin modificaciones.",
        "sector": "Industria",
        "obligaciones_preliminares": [],
        "puntos_indeterminados": [],
        "nodos_recorridos": [
            {"pregunta": "Tipo de entidad", "respuesta": "Implementador",
             "origen": "respuesta directa"},
            {"pregunta": "Modificaciones que convierten en proveedor (Art. 25)",
             "respuesta": "Ninguna", "origen": "respuesta directa"},
        ],
    })

    def _clasificacion_extraida(self):
        chat = AIComplyChat(MockProvider(self._JSON_IMPLEMENTADOR))
        chat.historial = [
            {"role": "user", "content": "Compramos el sistema a un proveedor externo."},
            {"role": "assistant", "content": "Su organización actúa como implementadora."},
        ]
        return chat.extraer_clasificacion()

    def test_la_extraccion_conserva_el_rol_unico(self):
        datos = self._clasificacion_extraida()
        assert datos["roles_multiples"] == ["implementador"]
        assert datos["rol"] == "implementador"

    def test_el_informe_no_atribuye_obligaciones_de_proveedor(self):
        """Ni Anexo IV, ni SGC, ni marcado CE: los Arts. 9-15, 43 y 49 son del proveedor."""
        md = GeneradorInforme().generar_informe_completo(
            self._clasificacion_extraida(), _cumpl_vacio()
        )
        for articulo in ("Art. 9", "Art. 10", "Art. 11", "Art. 12", "Art. 13",
                         "Art. 14", "Art. 15", "Art. 43", "Art. 49"):
            assert articulo not in md, f"{articulo} es obligación de proveedor"
        assert "**Rol de la entidad:** Implementador" in md


# ── Los prompts conservan las reglas simétricas ───────────────────────────────

class TestReglasEnLosPrompts:
    """Impide que las reglas de B15 desaparezcan de los prompts en una edición futura.

    No prueban que el modelo las obedezca —eso exige una llamada real y no es determinista—:
    solo que el texto sigue ahí.
    """

    def test_el_arbol_prohibe_anadir_roles_no_confirmados(self):
        assert "REGLA SIMÉTRICA — No añadir roles no confirmados:" in SYSTEM_PROMPT_CHATBOT
        assert "el rol determinado en #E1 es DEFINITIVO" in SYSTEM_PROMPT_CHATBOT

    def test_el_informe_final_no_redefine_el_rol(self):
        assert "REGLA CRÍTICA — El informe no redefine el rol:" in SYSTEM_PROMPT_CHATBOT

    def test_la_plantilla_copiable_del_doble_rol_no_vuelve(self):
        """La frase hecha de §2.5 es la que se pegó donde no tocaba; se retiró a propósito."""
        assert "actúa como proveedora e implementadora del sistema" not in SYSTEM_PROMPT_CHATBOT

    def test_la_extraccion_acota_roles_multiples(self):
        assert "lista los roles que la conversación CONFIRMÓ" in _PROMPT_EXTRAER_CLASIFICACION
        assert "NO AÑADAS un rol que la conversación no confirmara" in _PROMPT_EXTRAER_CLASIFICACION

    def test_el_ejemplo_del_json_de_extraccion_no_es_dual(self):
        """El ejemplo dual hacía del doble rol la forma por defecto de la respuesta."""
        assert '"roles_multiples": ["proveedor", "implementador"]' not in _PROMPT_EXTRAER_CLASIFICACION

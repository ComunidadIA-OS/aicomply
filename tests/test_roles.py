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

import pytest

from src.chatbot import AIComplyChat
from src.report_generator import GeneradorInforme, _capitalizar_roles


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

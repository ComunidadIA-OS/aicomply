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

"""Tests para la lógica de persistencia de rol:
EvalState, procesar_respuesta, construir_bloque_estado y extraer_roles_confirmados.
"""

import pytest

from src.conversation_state import (
    EvalState,
    construir_bloque_estado,
    extraer_roles_confirmados,
    procesar_respuesta,
)


class _FakeProvider:
    """Provider mínimo para tests de extracción JSON."""

    es_local = False

    def __init__(self, respuesta: str):
        self.respuesta = respuesta

    def chat(self, _messages, system_prompt: str = "") -> str:
        return self.respuesta


class TestEvalState:
    def test_rol_en_curso_ninguno_sin_roles(self):
        assert EvalState().rol_en_curso is None

    def test_rol_en_curso_primer_no_completado(self):
        estado = EvalState(roles_declarados=["Implementador"], roles_completados=[])
        assert estado.rol_en_curso == "Implementador"

    def test_rol_en_curso_salta_completados(self):
        estado = EvalState(
            roles_declarados=["Implementador", "Proveedor"],
            roles_completados=["Implementador"],
        )
        assert estado.rol_en_curso == "Proveedor"

    def test_todos_completados_false_sin_roles(self):
        assert EvalState().todos_los_roles_completados is False

    def test_todos_completados_true(self):
        estado = EvalState(
            roles_declarados=["Implementador"],
            roles_completados=["Implementador"],
        )
        assert estado.todos_los_roles_completados is True

    def test_todos_completados_false_cuando_queda_uno(self):
        estado = EvalState(
            roles_declarados=["Implementador", "Proveedor"],
            roles_completados=["Implementador"],
        )
        assert estado.todos_los_roles_completados is False

    def test_to_dict_from_dict_roundtrip(self):
        estado = EvalState(
            es_sistema_ia=True,
            roles_declarados=["Proveedor"],
            roles_completados=["Proveedor"],
            evaluacion_completa=True,
            mensajes_pinneados=[2, 3],
        )
        restaurado = EvalState.from_dict(estado.to_dict())
        assert restaurado.es_sistema_ia is True
        assert restaurado.roles_declarados == ["Proveedor"]
        assert restaurado.evaluacion_completa is True
        assert restaurado.mensajes_pinneados == [2, 3]


class TestProcesarRespuesta:
    def test_evaluacion_completa_sin_roles_activa_flag(self):
        _, estado = procesar_respuesta("Informe final. [EVALUACION_COMPLETA]", EvalState())
        assert estado.evaluacion_completa is True

    def test_evaluacion_completa_ignorada_con_rol_sin_completar(self):
        estado = EvalState(roles_declarados=["Implementador"], roles_completados=[])
        _, estado = procesar_respuesta("Informe. [EVALUACION_COMPLETA]", estado)
        assert estado.evaluacion_completa is False

    def test_evaluacion_completa_activa_con_todos_completados(self):
        estado = EvalState(
            roles_declarados=["Implementador"],
            roles_completados=["Implementador"],
        )
        _, estado = procesar_respuesta("Informe. [EVALUACION_COMPLETA]", estado)
        assert estado.evaluacion_completa is True

    def test_elimina_senal_del_texto(self):
        texto_limpio, _ = procesar_respuesta("Texto visible. [EVALUACION_COMPLETA]", EvalState())
        assert "[EVALUACION_COMPLETA]" not in texto_limpio
        assert "Texto visible." in texto_limpio

    def test_elimina_senales_legacy(self):
        texto = "Hola [ROL_DETERMINADO: Proveedor] y [ROL_COMPLETADO: Proveedor] fin."
        texto_limpio, _ = procesar_respuesta(texto, EvalState())
        assert "ROL_DETERMINADO" not in texto_limpio
        assert "ROL_COMPLETADO" not in texto_limpio
        assert "Hola" in texto_limpio

    def test_sin_senal_no_modifica_texto(self):
        texto = "Respuesta sin señales especiales."
        texto_limpio, _ = procesar_respuesta(texto, EvalState())
        assert texto_limpio == texto


class TestConstruirBloqueEstado:
    def test_contiene_cabecera_estado_actual(self):
        bloque = construir_bloque_estado(EvalState())
        assert "ESTADO ACTUAL DE LA EVALUACIÓN" in bloque

    def test_rol_declarado_aparece_en_bloque(self):
        bloque = construir_bloque_estado(EvalState(roles_declarados=["Implementador"]))
        assert "Implementador" in bloque

    def test_estado_inicial_indica_pendiente(self):
        bloque = construir_bloque_estado(EvalState())
        assert "aún no confirmado" in bloque
        assert "aún no determinado" in bloque

    def test_sistema_ia_confirmado_aparece(self):
        bloque = construir_bloque_estado(EvalState(es_sistema_ia=True))
        assert "sí" in bloque

    def test_sistema_ia_descartado_aparece(self):
        bloque = construir_bloque_estado(EvalState(es_sistema_ia=False))
        assert "no" in bloque


class TestExtraerRolesConfirmados:
    def test_extrae_implementador(self):
        provider = _FakeProvider('{"confirmado": true, "roles": ["Implementador"]}')
        roles = extraer_roles_confirmados(provider, "soy implementador", "correcto, eres Implementador")
        assert roles == ["Implementador"]

    def test_extrae_proveedor(self):
        provider = _FakeProvider('{"confirmado": true, "roles": ["Proveedor"]}')
        roles = extraer_roles_confirmados(provider, "u", "a")
        assert roles == ["Proveedor"]

    def test_no_confirmado_devuelve_lista_vacia(self):
        provider = _FakeProvider('{"confirmado": false, "roles": []}')
        roles = extraer_roles_confirmados(provider, "msg", "solo explico el árbol")
        assert roles == []

    def test_normaliza_responsable_del_despliegue(self):
        provider = _FakeProvider('{"confirmado": true, "roles": ["responsable del despliegue"]}')
        roles = extraer_roles_confirmados(provider, "u", "a")
        assert "Implementador" in roles

    def test_fallo_provider_devuelve_vacia(self):
        class ProviderRoto:
            es_local = False

            def chat(self, *a, **kw):
                raise RuntimeError("error de red")

        roles = extraer_roles_confirmados(ProviderRoto(), "msg", "resp")
        assert roles == []

    def test_json_invalido_devuelve_vacia(self):
        provider = _FakeProvider("esto no es json")
        roles = extraer_roles_confirmados(provider, "msg", "resp")
        assert roles == []

    def test_json_en_markdown_parsea_correctamente(self):
        provider = _FakeProvider('```json\n{"confirmado": true, "roles": ["Proveedor"]}\n```')
        roles = extraer_roles_confirmados(provider, "u", "a")
        assert roles == ["Proveedor"]

    def test_roles_desconocidos_ignorados(self):
        provider = _FakeProvider('{"confirmado": true, "roles": ["RolInventado"]}')
        roles = extraer_roles_confirmados(provider, "u", "a")
        assert roles == []

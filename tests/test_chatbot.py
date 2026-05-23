# Copyright 2025 AIComply Contributors
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

import pytest

from src.chatbot import AIComplyChat

# Todos los chatbots de test usan system_prompt_override para evitar
# la llamada a RAG (formatear_contexto_rag), que requiere el vectorstore.
_SYSTEM = "system prompt de prueba"


class TestParsearJson:
    def _chat(self, respuesta: str = "") -> AIComplyChat:
        from tests.conftest import MockProvider
        return AIComplyChat(MockProvider(respuesta), system_prompt_override=_SYSTEM)

    def test_json_valido(self):
        resultado = self._chat()._parsear_json('{"clave": "valor"}', {})
        assert resultado == {"clave": "valor"}

    def test_json_bloque_markdown_con_lenguaje(self):
        texto = '```json\n{"clave": "valor"}\n```'
        resultado = self._chat()._parsear_json(texto, {})
        assert resultado == {"clave": "valor"}

    def test_json_bloque_markdown_sin_lenguaje(self):
        texto = '```\n{"clave": "valor"}\n```'
        resultado = self._chat()._parsear_json(texto, {})
        assert resultado == {"clave": "valor"}

    def test_json_invalido_devuelve_fallback(self):
        fallback = {"clasificacion": "PENDIENTE"}
        resultado = self._chat()._parsear_json("esto no es json", fallback)
        assert resultado == fallback

    def test_cadena_vacia_devuelve_fallback(self):
        fallback = {"error": True}
        resultado = self._chat()._parsear_json("", fallback)
        assert resultado == fallback

    def test_json_anidado(self):
        texto = '{"nivel": "ALTO", "lista": [1, 2, 3]}'
        resultado = self._chat()._parsear_json(texto, {})
        assert resultado["nivel"] == "ALTO"
        assert resultado["lista"] == [1, 2, 3]


class TestSenalEvaluacionCompleta:
    def test_detecta_senal_en_chat_completo(self, make_provider):
        provider = make_provider("Resultado final [EVALUACION_COMPLETA]")
        chat = AIComplyChat(provider, system_prompt_override=_SYSTEM)
        respuesta = chat.chat_completo("pregunta")
        assert chat.evaluacion_completa is True

    def test_elimina_senal_de_respuesta(self, make_provider):
        provider = make_provider("Resultado final [EVALUACION_COMPLETA]")
        chat = AIComplyChat(provider, system_prompt_override=_SYSTEM)
        respuesta = chat.chat_completo("pregunta")
        assert "[EVALUACION_COMPLETA]" not in respuesta

    def test_elimina_senal_del_historial(self, make_provider):
        provider = make_provider("Resultado [EVALUACION_COMPLETA]")
        chat = AIComplyChat(provider, system_prompt_override=_SYSTEM)
        chat.chat_completo("pregunta")
        contenido_asistente = chat.historial[-1]["content"]
        assert "[EVALUACION_COMPLETA]" not in contenido_asistente

    def test_sin_senal_evaluacion_no_completa(self, make_provider):
        provider = make_provider("Respuesta sin señal especial")
        chat = AIComplyChat(provider, system_prompt_override=_SYSTEM)
        chat.chat_completo("pregunta")
        assert chat.evaluacion_completa is False

    def test_senal_en_streaming(self, make_provider):
        provider = make_provider("Respuesta [EVALUACION_COMPLETA]")
        chat = AIComplyChat(provider, system_prompt_override=_SYSTEM)
        list(chat.chat_stream("pregunta"))  # consumir el generador
        assert chat.evaluacion_completa is True


class TestHistorialYResetear:
    def test_historial_acumula_mensajes(self, make_provider):
        chat = AIComplyChat(make_provider("hola"), system_prompt_override=_SYSTEM)
        chat.chat_completo("mensaje 1")
        chat.chat_completo("mensaje 2")
        assert len(chat.historial) == 4  # user+assistant x 2

    def test_resetear_limpia_historial(self, make_provider):
        chat = AIComplyChat(make_provider("[EVALUACION_COMPLETA]"), system_prompt_override=_SYSTEM)
        chat.chat_completo("pregunta")
        chat.resetear()
        assert chat.historial == []

    def test_resetear_limpia_nivel_riesgo(self, make_provider):
        chat = AIComplyChat(make_provider("riesgo ALTO RIESGO"), system_prompt_override=_SYSTEM)
        chat.chat_completo("pregunta")
        chat.resetear()
        assert chat.nivel_riesgo is None

    def test_resetear_limpia_evaluacion_completa(self, make_provider):
        chat = AIComplyChat(make_provider("[EVALUACION_COMPLETA]"), system_prompt_override=_SYSTEM)
        chat.chat_completo("pregunta")
        assert chat.evaluacion_completa is True
        chat.resetear()
        assert chat.evaluacion_completa is False

    def test_resetear_mantiene_provider(self, make_provider):
        provider = make_provider("respuesta")
        chat = AIComplyChat(provider, system_prompt_override=_SYSTEM)
        chat.resetear()
        assert chat.provider is provider


class TestExtraccionNivelRiesgo:
    def _chat_con(self, respuesta: str) -> AIComplyChat:
        from tests.conftest import MockProvider
        chat = AIComplyChat(MockProvider(respuesta), system_prompt_override=_SYSTEM)
        chat.chat_completo("pregunta")
        return chat

    def test_detecta_alto_riesgo(self):
        chat = self._chat_con("El sistema es de ALTO RIESGO según el AI Act")
        assert chat.nivel_riesgo == "ALTO"

    def test_detecta_prohibido(self):
        chat = self._chat_con("Este sistema está PROHIBIDO por el Art. 5")
        assert chat.nivel_riesgo == "PROHIBIDO"

    def test_detecta_riesgo_limitado(self):
        chat = self._chat_con("El sistema tiene RIESGO LIMITADO")
        assert chat.nivel_riesgo == "LIMITADO"

    def test_sin_mencion_nivel_es_none(self):
        chat = self._chat_con("Necesito más información para clasificar el sistema")
        assert chat.nivel_riesgo is None

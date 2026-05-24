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

import pytest

from src.chatbot import AIComplyChat

# Todos los chatbots de test usan system_prompt_override para evitar
# la llamada a RAG (formatear_contexto_rag), que requiere el vectorstore.
_SYSTEM = "system prompt de prueba"


class SpyProvider:
    """Provider de test (duck typing) que captura el system_prompt recibido."""

    es_local = False

    def __init__(self, respuesta: str = "respuesta de prueba"):
        self.respuesta = respuesta
        self.ultimo_system_prompt: str = ""

    def chat(self, _messages, system_prompt: str = "") -> str:
        self.ultimo_system_prompt = system_prompt
        return self.respuesta

    def chat_stream(self, _messages, system_prompt: str = ""):
        self.ultimo_system_prompt = system_prompt
        yield self.respuesta


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
        # El informe debe tener ≥150 caracteres para que la señal sea aceptada.
        informe = "A" * 150
        provider = make_provider(f"{informe} [EVALUACION_COMPLETA]")
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


class TestRAGIntegration:
    def test_rag_inyectado_cuando_no_hay_override(self, monkeypatch):
        import src.chatbot  # noqa: PLC0415
        monkeypatch.setattr(src.chatbot, "formatear_contexto_rag", lambda *_, **__: "fragmento normativo de prueba")

        spy = SpyProvider("respuesta")
        chat = AIComplyChat(spy)  # sin override → RAG activo
        chat.chat_completo("¿qué dice el art. 5?")

        assert "fragmento normativo de prueba" in spy.ultimo_system_prompt
        assert "CONTEXTO NORMATIVO RECUPERADO" in spy.ultimo_system_prompt

    def test_rag_no_inyectado_con_override(self, monkeypatch):
        import src.chatbot  # noqa: PLC0415
        monkeypatch.setattr(src.chatbot, "formatear_contexto_rag", lambda *_, **__: "fragmento inyectado")

        spy = SpyProvider("respuesta")
        chat = AIComplyChat(spy, system_prompt_override=_SYSTEM)
        chat.chat_completo("mensaje")

        assert spy.ultimo_system_prompt == _SYSTEM
        assert "fragmento inyectado" not in spy.ultimo_system_prompt

    def test_rag_vacio_no_anade_bloque(self, monkeypatch):
        import src.chatbot  # noqa: PLC0415
        monkeypatch.setattr(src.chatbot, "formatear_contexto_rag", lambda *_, **__: "")

        spy = SpyProvider("respuesta")
        chat = AIComplyChat(spy)
        chat.chat_completo("mensaje")

        assert "CONTEXTO NORMATIVO RECUPERADO" not in spy.ultimo_system_prompt

    def test_rag_excepcion_no_rompe_chat(self, monkeypatch):
        import src.chatbot  # noqa: PLC0415

        def rag_roto(_q, top_k=3):
            raise Exception("vectorstore corrupto")

        monkeypatch.setattr(src.chatbot, "formatear_contexto_rag", rag_roto)

        spy = SpyProvider("respuesta")
        chat = AIComplyChat(spy)
        respuesta = chat.chat_completo("mensaje")

        assert respuesta == "respuesta"
        assert "CONTEXTO NORMATIVO RECUPERADO" not in spy.ultimo_system_prompt

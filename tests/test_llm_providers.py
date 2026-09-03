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

"""Tests de la detección de respuestas truncadas por max_tokens.

Subir el techo hace el corte raro, no imposible. Cuando ocurre, la respuesta se corta a
media frase y no llega a emitir [EVALUACION_COMPLETA], así que sin esta señal el usuario
solo percibe que el botón de continuar no aparece. Fallar de forma visible, no en silencio.
"""

from types import SimpleNamespace
from unittest.mock import MagicMock, patch

import pytest


# ── Dobles de las respuestas de cada API ─────────────────────────────────────

def _respuesta_anthropic(stop_reason: str):
    return SimpleNamespace(
        content=[SimpleNamespace(text="texto")],
        stop_reason=stop_reason,
    )


def _respuesta_openai(finish_reason: str):
    return SimpleNamespace(
        choices=[
            SimpleNamespace(
                message=SimpleNamespace(content="texto"),
                finish_reason=finish_reason,
            )
        ]
    )


def _chunk_openai(contenido: str | None, finish_reason: str | None):
    return SimpleNamespace(
        choices=[
            SimpleNamespace(
                delta=SimpleNamespace(content=contenido),
                finish_reason=finish_reason,
            )
        ]
    )


@pytest.fixture
def anthropic_provider():
    with patch("src.llm.anthropic_provider.anthropic.Anthropic") as mock_cls:
        from src.llm.anthropic_provider import AnthropicProvider  # noqa: PLC0415
        provider = AnthropicProvider(api_key="sk-test")
        provider.client = mock_cls.return_value
        yield provider


@pytest.fixture
def openai_provider():
    with patch("src.llm.openai_provider.OpenAI") as mock_cls:
        from src.llm.openai_provider import OpenAICompatibleProvider  # noqa: PLC0415
        provider = OpenAICompatibleProvider(base_url="http://local/v1", model="m")
        provider.client = mock_cls.return_value
        yield provider


# ── Anthropic ────────────────────────────────────────────────────────────────

class TestAnthropicTruncada:
    def test_chat_detecta_max_tokens(self, anthropic_provider):
        anthropic_provider.client.messages.create.return_value = _respuesta_anthropic("max_tokens")
        anthropic_provider.chat([{"role": "user", "content": "hola"}])
        assert anthropic_provider.ultima_respuesta_truncada is True

    def test_chat_respuesta_completa_no_marca(self, anthropic_provider):
        anthropic_provider.client.messages.create.return_value = _respuesta_anthropic("end_turn")
        anthropic_provider.chat([{"role": "user", "content": "hola"}])
        assert anthropic_provider.ultima_respuesta_truncada is False

    def test_la_marca_se_reinicia_entre_llamadas(self, anthropic_provider):
        anthropic_provider.client.messages.create.return_value = _respuesta_anthropic("max_tokens")
        anthropic_provider.chat([{"role": "user", "content": "hola"}])
        assert anthropic_provider.ultima_respuesta_truncada is True

        anthropic_provider.client.messages.create.return_value = _respuesta_anthropic("end_turn")
        anthropic_provider.chat([{"role": "user", "content": "hola"}])
        assert anthropic_provider.ultima_respuesta_truncada is False

    def test_stream_detecta_max_tokens_al_cerrar(self, anthropic_provider):
        stream = MagicMock()
        stream.text_stream = iter(["frag1", "frag2"])
        stream.get_final_message.return_value = _respuesta_anthropic("max_tokens")
        anthropic_provider.client.messages.stream.return_value.__enter__.return_value = stream

        list(anthropic_provider.chat_stream([{"role": "user", "content": "hola"}]))

        assert anthropic_provider.ultima_respuesta_truncada is True

    def test_stream_sin_motivo_de_parada_no_revienta(self, anthropic_provider):
        """Si no se puede leer el motivo, se degrada a "no truncada" en vez de propagar."""
        stream = MagicMock()
        stream.text_stream = iter(["frag"])
        stream.get_final_message.side_effect = RuntimeError("sin mensaje final")
        anthropic_provider.client.messages.stream.return_value.__enter__.return_value = stream

        fragmentos = list(anthropic_provider.chat_stream([{"role": "user", "content": "hola"}]))

        assert fragmentos == ["frag"]
        assert anthropic_provider.ultima_respuesta_truncada is False


# ── OpenAI-compatible ────────────────────────────────────────────────────────

class TestOpenAITruncada:
    def test_chat_detecta_length(self, openai_provider):
        openai_provider.client.chat.completions.create.return_value = _respuesta_openai("length")
        openai_provider.chat([{"role": "user", "content": "hola"}])
        assert openai_provider.ultima_respuesta_truncada is True

    def test_chat_respuesta_completa_no_marca(self, openai_provider):
        openai_provider.client.chat.completions.create.return_value = _respuesta_openai("stop")
        openai_provider.chat([{"role": "user", "content": "hola"}])
        assert openai_provider.ultima_respuesta_truncada is False

    def test_stream_detecta_length_en_el_ultimo_chunk(self, openai_provider):
        openai_provider.client.chat.completions.create.return_value = iter([
            _chunk_openai("frag1", None),
            _chunk_openai("frag2", None),
            _chunk_openai(None, "length"),
        ])

        fragmentos = list(openai_provider.chat_stream([{"role": "user", "content": "hola"}]))

        assert fragmentos == ["frag1", "frag2"]
        assert openai_provider.ultima_respuesta_truncada is True

    def test_stream_completo_no_marca(self, openai_provider):
        openai_provider.client.chat.completions.create.return_value = iter([
            _chunk_openai("frag1", None),
            _chunk_openai(None, "stop"),
        ])

        list(openai_provider.chat_stream([{"role": "user", "content": "hola"}]))

        assert openai_provider.ultima_respuesta_truncada is False

    def test_stream_ignora_chunks_sin_choices(self, openai_provider):
        """Algunos servidores compatibles emiten un chunk final vacío (p. ej. con usage)."""
        openai_provider.client.chat.completions.create.return_value = iter([
            _chunk_openai("frag", None),
            SimpleNamespace(choices=[]),
        ])

        fragmentos = list(openai_provider.chat_stream([{"role": "user", "content": "hola"}]))

        assert fragmentos == ["frag"]


# ── Contrato del ABC ─────────────────────────────────────────────────────────

def test_el_default_del_abc_es_no_truncada():
    """Un provider que no informe del motivo de parada nunca marca falsos positivos."""
    from src.llm.provider import LLMProvider  # noqa: PLC0415

    class ProviderMinimo(LLMProvider):
        def chat(self, messages, system_prompt=""):
            return ""

        def chat_stream(self, messages, system_prompt=""):
            yield ""

        @property
        def nombre_modelo(self):
            return "m"

        @property
        def nombre_provider(self):
            return "p"

    assert ProviderMinimo().ultima_respuesta_truncada is False

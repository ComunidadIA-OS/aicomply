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

import time
from typing import Generator

import anthropic

from .provider import LLMProvider

_RETRY_WAIT_MAX = 5.0  # backoff máximo en segundos; respeta Retry-After si la API lo devuelve


def _leer_retry_after(exc: anthropic.RateLimitError, maximo: float = _RETRY_WAIT_MAX) -> float:
    """Lee el header Retry-After de la excepción; si no viene, devuelve maximo."""
    try:
        valor = exc.response.headers.get("retry-after")
        if valor:
            return min(float(valor), maximo)
    except Exception:
        pass
    return maximo


class AnthropicProvider(LLMProvider):
    """Provider para la API de Anthropic Claude."""

    def __init__(
        self,
        api_key: str,
        model: str = "claude-sonnet-4-6",
        max_tokens: int = 2048,
    ):
        self.client = anthropic.Anthropic(api_key=api_key, timeout=60.0)
        self._model = model
        self.max_tokens = max_tokens

    @property
    def nombre_modelo(self) -> str:
        return self._model

    @property
    def nombre_provider(self) -> str:
        return "anthropic"

    def chat(self, messages: list[dict], system_prompt: str = "") -> str:
        """Llamada síncrona sin streaming. Reintenta una vez tras un error 429."""
        kwargs: dict = {
            "model": self._model,
            "max_tokens": self.max_tokens,
            "messages": messages,
        }
        if system_prompt:
            kwargs["system"] = system_prompt

        for intento in range(2):
            try:
                response = self.client.messages.create(**kwargs)
                return response.content[0].text
            except anthropic.RateLimitError as rl_exc:
                if intento == 0:
                    time.sleep(_leer_retry_after(rl_exc))
                else:
                    raise

    def chat_stream(
        self, messages: list[dict], system_prompt: str = ""
    ) -> Generator[str, None, None]:
        """Llamada con streaming; produce fragmentos de texto."""
        kwargs: dict = {
            "model": self._model,
            "max_tokens": self.max_tokens,
            "messages": messages,
        }
        if system_prompt:
            kwargs["system"] = system_prompt

        with self.client.messages.stream(**kwargs) as stream:
            for texto in stream.text_stream:
                yield texto

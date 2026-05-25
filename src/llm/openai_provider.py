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

from typing import Generator

from openai import OpenAI

from .provider import LLMProvider


class OpenAICompatibleProvider(LLMProvider):
    """
    Provider para APIs compatibles con OpenAI.

    Funciona con:
    - OpenAI API (https://api.openai.com/v1)
    - LM Studio (http://localhost:1234/v1)
    - vLLM (http://localhost:8000/v1)
    - llama.cpp server (http://localhost:8080/v1)
    - Groq (https://api.groq.com/openai/v1)
    - Together AI (https://api.together.xyz/v1)
    - Mistral API (https://api.mistral.ai/v1)
    - Cualquier servidor compatible con la especificación OpenAI Chat Completions
    """

    def __init__(
        self,
        api_key: str = "dummy",
        base_url: str = "https://api.openai.com/v1",
        model: str = "gpt-4o",
        max_tokens: int = 2048,
    ):
        # Para APIs locales (LM Studio, etc.) la api_key puede ser cualquier valor
        self.client = OpenAI(
            api_key=api_key or "dummy",
            base_url=base_url,
            timeout=60.0,
        )
        self._model = model
        self.max_tokens = max_tokens

    @property
    def nombre_modelo(self) -> str:
        return self._model

    @property
    def nombre_provider(self) -> str:
        return "openai_compatible"

    def _preparar_messages(
        self, messages: list[dict], system_prompt: str
    ) -> list[dict]:
        """Antepone el system prompt como mensaje de rol 'system'."""
        if system_prompt:
            return [{"role": "system", "content": system_prompt}] + messages
        return messages

    def chat(self, messages: list[dict], system_prompt: str = "") -> str:
        """Llamada síncrona sin streaming."""
        msgs = self._preparar_messages(messages, system_prompt)
        response = self.client.chat.completions.create(
            model=self._model,
            messages=msgs,
            max_tokens=self.max_tokens,
        )
        return response.choices[0].message.content or ""

    def chat_stream(
        self, messages: list[dict], system_prompt: str = ""
    ) -> Generator[str, None, None]:
        """Llamada con streaming; produce fragmentos de texto."""
        msgs = self._preparar_messages(messages, system_prompt)
        stream = self.client.chat.completions.create(
            model=self._model,
            messages=msgs,
            max_tokens=self.max_tokens,
            stream=True,
        )
        for chunk in stream:
            delta = chunk.choices[0].delta
            if delta.content:
                yield delta.content

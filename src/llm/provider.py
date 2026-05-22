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

from abc import ABC, abstractmethod
from typing import Generator


class LLMProvider(ABC):
    """
    Interfaz abstracta para proveedores de LLM.

    Todos los providers reciben mensajes en formato OpenAI:
      [{"role": "user" | "assistant", "content": "..."}]

    El system prompt se pasa como parámetro separado para mayor
    portabilidad entre APIs (Anthropic lo separa, OpenAI lo incluye
    como mensaje de rol "system").
    """

    @abstractmethod
    def chat(self, messages: list[dict], system_prompt: str = "") -> str:
        """Envía una conversación y devuelve la respuesta completa como string."""
        ...

    @abstractmethod
    def chat_stream(
        self, messages: list[dict], system_prompt: str = ""
    ) -> Generator[str, None, None]:
        """Envía una conversación y produce la respuesta en fragmentos (streaming)."""
        ...

    @property
    @abstractmethod
    def nombre_modelo(self) -> str:
        """Identificador del modelo que está usando este provider."""
        ...

    @property
    @abstractmethod
    def nombre_provider(self) -> str:
        """Nombre del provider: 'anthropic', 'ollama' u 'openai_compatible'."""
        ...

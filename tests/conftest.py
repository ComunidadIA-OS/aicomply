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

from typing import Generator

import pytest

from src.llm.provider import LLMProvider


class MockProvider(LLMProvider):
    """Provider falso para tests: devuelve una cadena configurable sin llamar a ninguna API."""

    def __init__(self, respuesta: str = "respuesta de prueba"):
        self.respuesta = respuesta
        self.llamadas_chat: int = 0
        self.llamadas_stream: int = 0

    def chat(self, messages: list[dict], system_prompt: str = "") -> str:
        self.llamadas_chat += 1
        return self.respuesta

    def chat_stream(
        self, messages: list[dict], system_prompt: str = ""
    ) -> Generator[str, None, None]:
        self.llamadas_stream += 1
        yield self.respuesta

    @property
    def nombre_modelo(self) -> str:
        return "mock-model"

    @property
    def nombre_provider(self) -> str:
        return "mock"


@pytest.fixture
def mock_provider():
    return MockProvider()


@pytest.fixture
def make_provider():
    """Fixture factoría: make_provider("texto de respuesta") → MockProvider."""
    def _make(respuesta: str = "respuesta de prueba") -> MockProvider:
        return MockProvider(respuesta)
    return _make

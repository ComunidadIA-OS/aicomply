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

import json
from typing import Generator

import httpx

from .provider import LLMProvider


class OllamaProvider(LLMProvider):
    """
    Provider para Ollama (modelos locales: Llama 3, Mistral, Qwen, DeepSeek...).

    Requiere que Ollama esté instalado y en ejecución.
    Instalación: https://ollama.ai
    """

    TIMEOUT_CHAT = 300.0
    TIMEOUT_API = 10.0

    def __init__(
        self,
        model: str = "llama3",
        base_url: str = "http://localhost:11434",
    ):
        self._model = model
        self.base_url = base_url.rstrip("/")

    @property
    def nombre_modelo(self) -> str:
        return self._model

    @property
    def nombre_provider(self) -> str:
        return "ollama"

    @property
    def es_local(self) -> bool:
        return True

    def _preparar_messages(
        self, messages: list[dict], system_prompt: str
    ) -> list[dict]:
        """Antepone el system prompt como mensaje de rol 'system' si se proporciona."""
        if system_prompt:
            return [{"role": "system", "content": system_prompt}] + messages
        return messages

    # num_ctx debe ser mayor que el system prompt (~5.000 tokens) + historial.
    # num_predict limita la longitud de respuesta para reducir uso de RAM.
    _OPTIONS = {"num_ctx": 8192, "num_predict": 1500}

    def chat(self, messages: list[dict], system_prompt: str = "") -> str:
        """Llamada síncrona sin streaming."""
        msgs = self._preparar_messages(messages, system_prompt)
        payload = {
            "model": self._model,
            "messages": msgs,
            "stream": False,
            "options": self._OPTIONS,
        }

        respuesta = httpx.post(
            f"{self.base_url}/api/chat",
            json=payload,
            timeout=self.TIMEOUT_CHAT,
        )
        respuesta.raise_for_status()
        return respuesta.json()["message"]["content"]

    def chat_stream(
        self, messages: list[dict], system_prompt: str = ""
    ) -> Generator[str, None, None]:
        """Llamada con streaming NDJSON; produce fragmentos de texto."""
        msgs = self._preparar_messages(messages, system_prompt)
        payload = {
            "model": self._model,
            "messages": msgs,
            "stream": True,
            "options": self._OPTIONS,
        }

        with httpx.stream(
            "POST",
            f"{self.base_url}/api/chat",
            json=payload,
            timeout=self.TIMEOUT_CHAT,
        ) as respuesta:
            respuesta.raise_for_status()
            for linea in respuesta.iter_lines():
                if not linea:
                    continue
                try:
                    datos = json.loads(linea)
                    if not datos.get("done", False):
                        fragmento = datos.get("message", {}).get("content", "")
                        if fragmento:
                            yield fragmento
                except json.JSONDecodeError:
                    continue

    def verificar_conexion(self) -> bool:
        """Comprueba que Ollama esté disponible."""
        try:
            r = httpx.get(f"{self.base_url}/api/tags", timeout=self.TIMEOUT_API)
            return r.status_code == 200
        except Exception:
            return False

    def listar_modelos(self) -> list[str]:
        """Devuelve la lista de modelos instalados en Ollama."""
        try:
            r = httpx.get(f"{self.base_url}/api/tags", timeout=self.TIMEOUT_API)
            r.raise_for_status()
            return [m["name"] for m in r.json().get("models", [])]
        except Exception:
            return []

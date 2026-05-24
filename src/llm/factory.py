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

import os

from .anthropic_provider import AnthropicProvider
from .ollama_provider import OllamaProvider
from .openai_provider import OpenAICompatibleProvider
from .provider import LLMProvider


def crear_provider(config: dict) -> LLMProvider:
    """
    Crea un LLMProvider a partir de un diccionario de configuración.

    Campos esperados según el tipo de provider:

    Anthropic:
      {"provider": "anthropic", "api_key": "sk-ant-...", "model": "claude-sonnet-4-6"}

    Ollama:
      {"provider": "ollama", "model": "llama3", "base_url": "http://localhost:11434"}

    OpenAI-compatible:
      {"provider": "openai_compatible", "api_key": "...", "base_url": "...", "model": "..."}
    """
    tipo = config.get("provider", "anthropic")

    if tipo == "anthropic":
        return AnthropicProvider(
            api_key=config["api_key"],
            model=config.get("model", "claude-sonnet-4-6"),
        )

    if tipo == "ollama":
        return OllamaProvider(
            model=config.get("model", "llama3"),
            base_url=config.get("base_url", "http://localhost:11434"),
        )

    if tipo == "openai_compatible":
        return OpenAICompatibleProvider(
            api_key=config.get("api_key", "dummy"),
            base_url=config.get("base_url", "https://api.openai.com/v1"),
            model=config.get("model", "gpt-4o"),
        )

    raise ValueError(f"Provider no soportado: '{tipo}'. Use 'anthropic', 'ollama' u 'openai_compatible'.")


def crear_provider_desde_env() -> LLMProvider | None:
    """
    Intenta crear un LLMProvider desde variables de entorno.

    Devuelve None si no hay suficiente configuración (para que la UI
    muestre el selector interactivo).

    Variables de entorno reconocidas:
      LLM_PROVIDER       = anthropic | ollama | openai_compatible
      ANTHROPIC_API_KEY  = sk-ant-...
      ANTHROPIC_MODEL    = claude-sonnet-4-6
      OLLAMA_MODEL       = llama3
      OLLAMA_BASE_URL    = http://localhost:11434
      OPENAI_COMPATIBLE_BASE_URL = http://localhost:1234/v1
      OPENAI_COMPATIBLE_API_KEY  = (opcional para APIs locales)
      OPENAI_COMPATIBLE_MODEL    = nombre-del-modelo
    """
    provider_type = os.getenv("LLM_PROVIDER", "").lower().strip()

    if not provider_type:
        # Retrocompatibilidad: si hay ANTHROPIC_API_KEY sin LLM_PROVIDER
        api_key = os.getenv("ANTHROPIC_API_KEY", "").strip()
        if api_key:
            return AnthropicProvider(
                api_key=api_key,
                model=os.getenv("ANTHROPIC_MODEL", "claude-sonnet-4-6"),
            )
        return None

    if provider_type == "anthropic":
        api_key = os.getenv("ANTHROPIC_API_KEY", "").strip()
        if not api_key:
            return None
        return AnthropicProvider(
            api_key=api_key,
            model=os.getenv("ANTHROPIC_MODEL", "claude-sonnet-4-6"),
        )

    if provider_type == "ollama":
        return OllamaProvider(
            model=os.getenv("OLLAMA_MODEL", "llama3"),
            base_url=os.getenv("OLLAMA_BASE_URL", "http://localhost:11434"),
        )

    if provider_type == "openai_compatible":
        base_url = os.getenv("OPENAI_COMPATIBLE_BASE_URL", "").strip()
        model = os.getenv("OPENAI_COMPATIBLE_MODEL", "").strip()
        if not base_url or not model:
            return None
        return OpenAICompatibleProvider(
            api_key=os.getenv("OPENAI_COMPATIBLE_API_KEY", "dummy"),
            base_url=base_url,
            model=model,
        )

    return None

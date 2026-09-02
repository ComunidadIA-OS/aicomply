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

from __future__ import annotations

import os

from .anthropic_provider import AnthropicProvider
from .openai_provider import OpenAICompatibleProvider
from .provider import LLMProvider

_MAX_TOKENS_DEFECTO = 8192


def _max_tokens_desde_env() -> int:
    """Lee LLM_MAX_TOKENS en tiempo de llamada; retrocede al default si no es utilizable.

    Es un techo, no un gasto: solo se consume si el modelo lo llena. Con 2048 el informe
    final de un caso de alto riesgo con doble rol se cortaba dentro de la tabla de traza.
    Se lee aquí y no a nivel de módulo para que la configuración por entorno se aplique
    aunque cambie después de importar.
    """
    try:
        valor = int(os.getenv("LLM_MAX_TOKENS", "").strip() or _MAX_TOKENS_DEFECTO)
    except ValueError:
        return _MAX_TOKENS_DEFECTO
    return valor if valor > 0 else _MAX_TOKENS_DEFECTO


def crear_provider(config: dict) -> LLMProvider:
    """
    Crea un LLMProvider a partir de un diccionario de configuración.

    Campos esperados según el tipo de provider:

    Anthropic:
      {"provider": "anthropic", "api_key": "sk-ant-...", "model": "claude-sonnet-4-6"}

    OpenAI-compatible (incluye Ollama, LM Studio, vLLM, Groq, Mistral API...):
      {"provider": "openai_compatible", "api_key": "...", "base_url": "...", "model": "..."}
      Para Ollama: base_url="http://localhost:11434/v1"
    """
    tipo = config.get("provider", "anthropic")
    max_tokens = config.get("max_tokens") or _max_tokens_desde_env()

    if tipo == "anthropic":
        return AnthropicProvider(
            api_key=config["api_key"],
            model=config.get("model", "claude-sonnet-4-6"),
            max_tokens=max_tokens,
        )

    if tipo == "openai_compatible":
        return OpenAICompatibleProvider(
            api_key=config.get("api_key", "dummy"),
            base_url=config.get("base_url", "https://api.openai.com/v1"),
            model=config.get("model", "gpt-4o"),
            max_tokens=max_tokens,
        )

    raise ValueError(f"Provider no soportado: '{tipo}'. Use 'anthropic' u 'openai_compatible'.")


def crear_provider_desde_env() -> LLMProvider | None:
    """
    Intenta crear un LLMProvider desde variables de entorno.

    Devuelve None si no hay suficiente configuración (para que la UI
    muestre el selector interactivo).

    Variables de entorno reconocidas:
      LLM_PROVIDER       = anthropic | openai_compatible
      ANTHROPIC_API_KEY  = sk-ant-...
      ANTHROPIC_MODEL    = claude-sonnet-4-6
      OPENAI_COMPATIBLE_BASE_URL = http://localhost:11434/v1  (Ollama, LM Studio, vLLM...)
      OPENAI_COMPATIBLE_API_KEY  = (opcional para APIs locales)
      OPENAI_COMPATIBLE_MODEL    = nombre-del-modelo
      LLM_MAX_TOKENS             = 8192  (techo de la respuesta; ver _max_tokens_desde_env)
    """
    provider_type = os.getenv("LLM_PROVIDER", "").lower().strip()
    max_tokens = _max_tokens_desde_env()

    if not provider_type:
        # Retrocompatibilidad: si hay ANTHROPIC_API_KEY sin LLM_PROVIDER
        api_key = os.getenv("ANTHROPIC_API_KEY", "").strip()
        if api_key:
            return AnthropicProvider(
                api_key=api_key,
                model=os.getenv("ANTHROPIC_MODEL", "claude-sonnet-4-6"),
                max_tokens=max_tokens,
            )
        return None

    if provider_type == "anthropic":
        api_key = os.getenv("ANTHROPIC_API_KEY", "").strip()
        if not api_key:
            return None
        return AnthropicProvider(
            api_key=api_key,
            model=os.getenv("ANTHROPIC_MODEL", "claude-sonnet-4-6"),
            max_tokens=max_tokens,
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
            max_tokens=max_tokens,
        )

    return None

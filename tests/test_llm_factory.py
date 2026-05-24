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

from unittest.mock import MagicMock, patch

import pytest

from src.llm.factory import crear_provider, crear_provider_desde_env


class TestCrearProvider:
    def test_anthropic_instancia_clase_correcta(self):
        with patch("src.llm.factory.AnthropicProvider") as mock_cls:
            mock_cls.return_value = MagicMock()
            crear_provider({"provider": "anthropic", "api_key": "sk-test", "model": "claude-test"})
            mock_cls.assert_called_once_with(api_key="sk-test", model="claude-test")

    def test_anthropic_modelo_por_defecto(self):
        with patch("src.llm.factory.AnthropicProvider") as mock_cls:
            mock_cls.return_value = MagicMock()
            crear_provider({"provider": "anthropic", "api_key": "sk-test"})
            _, kwargs = mock_cls.call_args
            assert kwargs["model"] == "claude-sonnet-4-6"

    def test_ollama_instancia_clase_correcta(self):
        with patch("src.llm.factory.OllamaProvider") as mock_cls:
            mock_cls.return_value = MagicMock()
            crear_provider({"provider": "ollama", "model": "llama3", "base_url": "http://localhost:11434"})
            mock_cls.assert_called_once_with(model="llama3", base_url="http://localhost:11434")

    def test_ollama_modelo_por_defecto(self):
        with patch("src.llm.factory.OllamaProvider") as mock_cls:
            mock_cls.return_value = MagicMock()
            crear_provider({"provider": "ollama"})
            _, kwargs = mock_cls.call_args
            assert kwargs["model"] == "llama3"
            assert kwargs["base_url"] == "http://localhost:11434"

    def test_openai_compatible_instancia_clase_correcta(self):
        with patch("src.llm.factory.OpenAICompatibleProvider") as mock_cls:
            mock_cls.return_value = MagicMock()
            crear_provider({
                "provider": "openai_compatible",
                "api_key": "key-test",
                "base_url": "http://localhost:1234/v1",
                "model": "gpt-test",
            })
            mock_cls.assert_called_once_with(
                api_key="key-test",
                base_url="http://localhost:1234/v1",
                model="gpt-test",
            )

    def test_provider_desconocido_lanza_valor_error(self):
        with pytest.raises(ValueError, match="Provider no soportado"):
            crear_provider({"provider": "inventado"})

    def test_provider_desconocido_mensaje_incluye_tipo(self):
        with pytest.raises(ValueError, match="inventado"):
            crear_provider({"provider": "inventado"})

    def test_sin_campo_provider_usa_anthropic_por_defecto(self):
        with patch("src.llm.factory.AnthropicProvider") as mock_cls:
            mock_cls.return_value = MagicMock()
            # config sin "provider" → debe usar anthropic
            crear_provider({"api_key": "sk-test"})
            mock_cls.assert_called_once()


class TestCrearProviderDesdeEnv:
    def test_sin_vars_env_devuelve_none(self, monkeypatch):
        monkeypatch.delenv("LLM_PROVIDER", raising=False)
        monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)
        resultado = crear_provider_desde_env()
        assert resultado is None

    def test_anthropic_api_key_sin_llm_provider_crea_anthropic(self, monkeypatch):
        monkeypatch.delenv("LLM_PROVIDER", raising=False)
        monkeypatch.setenv("ANTHROPIC_API_KEY", "sk-test-key")
        with patch("src.llm.factory.AnthropicProvider") as mock_cls:
            mock_cls.return_value = MagicMock()
            resultado = crear_provider_desde_env()
            assert resultado is not None
            mock_cls.assert_called_once()

    def test_llm_provider_anthropic_sin_api_key_devuelve_none(self, monkeypatch):
        monkeypatch.setenv("LLM_PROVIDER", "anthropic")
        monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)
        resultado = crear_provider_desde_env()
        assert resultado is None

    def test_llm_provider_ollama_crea_ollama(self, monkeypatch):
        monkeypatch.setenv("LLM_PROVIDER", "ollama")
        monkeypatch.setenv("OLLAMA_MODEL", "llama3")
        monkeypatch.setenv("OLLAMA_BASE_URL", "http://localhost:11434")
        with patch("src.llm.factory.OllamaProvider") as mock_cls:
            mock_cls.return_value = MagicMock()
            resultado = crear_provider_desde_env()
            assert resultado is not None
            mock_cls.assert_called_once()

    def test_openai_compatible_sin_base_url_devuelve_none(self, monkeypatch):
        monkeypatch.setenv("LLM_PROVIDER", "openai_compatible")
        monkeypatch.delenv("OPENAI_COMPATIBLE_BASE_URL", raising=False)
        monkeypatch.delenv("OPENAI_COMPATIBLE_MODEL", raising=False)
        resultado = crear_provider_desde_env()
        assert resultado is None

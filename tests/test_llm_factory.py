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
            _, kwargs = mock_cls.call_args
            assert kwargs["api_key"] == "sk-test"
            assert kwargs["model"] == "claude-test"

    def test_anthropic_modelo_por_defecto(self):
        with patch("src.llm.factory.AnthropicProvider") as mock_cls:
            mock_cls.return_value = MagicMock()
            crear_provider({"provider": "anthropic", "api_key": "sk-test"})
            _, kwargs = mock_cls.call_args
            assert kwargs["model"] == "claude-sonnet-4-6"

    def test_openai_compatible_instancia_clase_correcta(self):
        with patch("src.llm.factory.OpenAICompatibleProvider") as mock_cls:
            mock_cls.return_value = MagicMock()
            crear_provider({
                "provider": "openai_compatible",
                "api_key": "key-test",
                "base_url": "http://localhost:1234/v1",
                "model": "gpt-test",
            })
            _, kwargs = mock_cls.call_args
            assert kwargs["api_key"] == "key-test"
            assert kwargs["base_url"] == "http://localhost:1234/v1"
            assert kwargs["model"] == "gpt-test"

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

    def test_openai_compatible_con_url_ollama_crea_provider(self, monkeypatch):
        monkeypatch.setenv("LLM_PROVIDER", "openai_compatible")
        monkeypatch.setenv("OPENAI_COMPATIBLE_BASE_URL", "http://localhost:11434/v1")
        monkeypatch.setenv("OPENAI_COMPATIBLE_MODEL", "llama3.1")
        with patch("src.llm.factory.OpenAICompatibleProvider") as mock_cls:
            mock_cls.return_value = MagicMock()
            resultado = crear_provider_desde_env()
            assert resultado is not None
            _, kwargs = mock_cls.call_args
            assert kwargs["base_url"] == "http://localhost:11434/v1"
            assert kwargs["model"] == "llama3.1"

    def test_openai_compatible_sin_base_url_devuelve_none(self, monkeypatch):
        monkeypatch.setenv("LLM_PROVIDER", "openai_compatible")
        monkeypatch.delenv("OPENAI_COMPATIBLE_BASE_URL", raising=False)
        monkeypatch.delenv("OPENAI_COMPATIBLE_MODEL", raising=False)
        resultado = crear_provider_desde_env()
        assert resultado is None


class TestMaxTokens:
    """LLM_MAX_TOKENS es un techo configurable, no un gasto.

    Con el default anterior (2048) el informe final de un caso de alto riesgo con doble rol
    se cortaba dentro de la tabla de traza, y al truncarse no emitía [EVALUACION_COMPLETA].
    """

    def test_default_sin_variable_de_entorno(self, monkeypatch):
        monkeypatch.delenv("LLM_MAX_TOKENS", raising=False)
        with patch("src.llm.factory.AnthropicProvider") as mock_cls:
            mock_cls.return_value = MagicMock()
            crear_provider({"provider": "anthropic", "api_key": "sk-test"})
            _, kwargs = mock_cls.call_args
            assert kwargs["max_tokens"] == 8192

    def test_la_variable_de_entorno_manda(self, monkeypatch):
        monkeypatch.setenv("LLM_MAX_TOKENS", "16000")
        with patch("src.llm.factory.AnthropicProvider") as mock_cls:
            mock_cls.return_value = MagicMock()
            crear_provider({"provider": "anthropic", "api_key": "sk-test"})
            _, kwargs = mock_cls.call_args
            assert kwargs["max_tokens"] == 16000

    @pytest.mark.parametrize("valor", ["no-es-un-numero", "0", "-1", ""])
    def test_valor_inutilizable_cae_al_default(self, monkeypatch, valor):
        monkeypatch.setenv("LLM_MAX_TOKENS", valor)
        with patch("src.llm.factory.AnthropicProvider") as mock_cls:
            mock_cls.return_value = MagicMock()
            crear_provider({"provider": "anthropic", "api_key": "sk-test"})
            _, kwargs = mock_cls.call_args
            assert kwargs["max_tokens"] == 8192

    def test_la_config_explicita_gana_al_entorno(self, monkeypatch):
        monkeypatch.setenv("LLM_MAX_TOKENS", "16000")
        with patch("src.llm.factory.AnthropicProvider") as mock_cls:
            mock_cls.return_value = MagicMock()
            crear_provider({"provider": "anthropic", "api_key": "sk-test", "max_tokens": 1024})
            _, kwargs = mock_cls.call_args
            assert kwargs["max_tokens"] == 1024

    def test_tambien_llega_al_provider_openai_compatible(self, monkeypatch):
        monkeypatch.setenv("LLM_MAX_TOKENS", "3000")
        with patch("src.llm.factory.OpenAICompatibleProvider") as mock_cls:
            mock_cls.return_value = MagicMock()
            crear_provider({"provider": "openai_compatible", "model": "m", "base_url": "u"})
            _, kwargs = mock_cls.call_args
            assert kwargs["max_tokens"] == 3000

    def test_tambien_se_aplica_creando_desde_entorno(self, monkeypatch):
        monkeypatch.setenv("LLM_PROVIDER", "anthropic")
        monkeypatch.setenv("ANTHROPIC_API_KEY", "sk-test")
        monkeypatch.setenv("LLM_MAX_TOKENS", "5000")
        with patch("src.llm.factory.AnthropicProvider") as mock_cls:
            mock_cls.return_value = MagicMock()
            crear_provider_desde_env()
            _, kwargs = mock_cls.call_args
            assert kwargs["max_tokens"] == 5000

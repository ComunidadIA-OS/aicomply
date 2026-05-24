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

import streamlit as st

from config import (
    ANTHROPIC_API_KEY,
    ANTHROPIC_MODEL,
    DISCLAIMER_INICIAL,
    OLLAMA_BASE_URL,
    OLLAMA_MODEL,
    OPENAI_COMPATIBLE_API_KEY,
    OPENAI_COMPATIBLE_BASE_URL,
    OPENAI_COMPATIBLE_MODEL,
)
from src.chatbot import AIComplyChat
from src.llm.factory import crear_provider, crear_provider_desde_env
from src.tabs.cumplimiento import mostrar_tab_cumplimiento
from src.tabs.evaluador import mostrar_tab_evaluador
from src.tabs.informe import mostrar_tab_informe

st.set_page_config(
    page_title="AIComply — Evaluación AI Act",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Avisos de privacidad por provider y plan ───────────────────────────────────
_AVISOS: dict[str, tuple[str, str]] = {
    "anthropic_api": (
        "warning",
        "Sus datos se procesan en servidores de Anthropic (EE. UU.). "
        "Los datos NO se usan para entrenamiento de modelos. "
        "DPA disponible bajo petición. "
        "Recomendado para uso empresarial con documentación no crítica.",
    ),
    "anthropic_enterprise": (
        "info",
        "Mayor nivel de privacidad. Sus datos no se usan para entrenamiento. "
        "Acuerdo DPA incluido en el contrato. "
        "Recomendado para documentación confidencial empresarial.",
    ),
    "openai_free": (
        "error",
        "Sus datos se procesan en servidores de OpenAI (EE. UU.). "
        "OpenAI PUEDE usar sus datos para mejorar sus modelos. "
        "NO recomendado para documentación confidencial o sensible.",
    ),
    "openai_paid": (
        "warning",
        "Sus datos se procesan en servidores de OpenAI (EE. UU.). "
        "Datos NO usados para entrenamiento por defecto. "
        "Revise el DPA antes de enviar documentación confidencial.",
    ),
    "openai_enterprise": (
        "info",
        "Máxima privacidad. Acuerdo DPA incluido en el contrato. "
        "Sus datos no se usan para entrenamiento. "
        "Recomendado para documentación confidencial empresarial.",
    ),
    "groq": (
        "warning",
        "Sus datos se procesan en servidores de Groq (EE. UU.). "
        "Groq no usa los datos de API para entrenar modelos. "
        "Nivel gratuito con límites de velocidad. "
        "No recomendado para documentación confidencial o sensible.",
    ),
    "gemini": (
        "warning",
        "Sus datos se procesan en servidores de Google (EE. UU. / UE). "
        "Revise la política de privacidad de Google AI Studio antes de enviar datos sensibles. "
        "Nivel gratuito con límites de uso diario.",
    ),
    "ollama": (
        "success",
        "El modelo se ejecuta completamente en su ordenador. "
        "Ningún dato sale de su infraestructura. "
        "Totalmente gratuito. Recomendado para documentación confidencial o datos sensibles. "
        "Requiere instalación previa de Ollama (https://ollama.ai).",
    ),
    "openai_compatible_local": (
        "success",
        "Si la API está en su propia infraestructura (LM Studio, vLLM, llama.cpp), "
        "ningún dato sale de ella. Recomendado para máxima privacidad y control.",
    ),
    "openai_compatible_external": (
        "warning",
        "Sus datos se envían a servidores externos. "
        "Revise la política de privacidad del proveedor elegido "
        "antes de enviar documentación confidencial.",
    ),
}


def _mostrar_aviso(clave: str) -> None:
    nivel, texto = _AVISOS[clave]
    getattr(st, nivel)(f"**Condiciones de privacidad:** {texto}")


# ── Inicialización del estado de sesión ───────────────────────────────────────
def _init_session() -> None:
    if "provider_configurado" not in st.session_state:
        provider_env = crear_provider_desde_env()
        if provider_env:
            st.session_state.provider = provider_env
            st.session_state.provider_configurado = True
        else:
            st.session_state.provider = None
            st.session_state.provider_configurado = False

    if "disclaimer_aceptado" not in st.session_state:
        st.session_state.disclaimer_aceptado = False

    # Claves de las tres pestañas
    for clave in ("mensajes_evaluador", "mensajes_cumplimiento"):
        if clave not in st.session_state:
            st.session_state[clave] = []

    for clave in ("clasificacion_data", "cumplimiento_data"):
        if clave not in st.session_state:
            st.session_state[clave] = {}

    for clave in ("evaluacion_completada", "cumplimiento_completado", "acceso_directo_cumplimiento"):
        if clave not in st.session_state:
            st.session_state[clave] = False

    if "informe_md" not in st.session_state:
        st.session_state.informe_md = None

    if "chatbot_evaluador" not in st.session_state:
        if st.session_state.get("provider_configurado") and st.session_state.get("provider"):
            st.session_state.chatbot_evaluador = AIComplyChat(provider=st.session_state.provider)
        else:
            st.session_state.chatbot_evaluador = None

    if "chatbot_cumplimiento" not in st.session_state:
        st.session_state.chatbot_cumplimiento = None


_init_session()


# ════════════════════════════════════════════════════════════════════════════════
# PANTALLA 1: CONFIGURACIÓN DEL PROVIDER
# ════════════════════════════════════════════════════════════════════════════════
def mostrar_selector_provider() -> None:
    st.title("AIComply")
    st.subheader("Configuración del modelo de lenguaje")
    st.markdown(
        "Seleccione cómo quiere ejecutar AIComply. "
        "Lea atentamente las condiciones de privacidad antes de confirmar su elección."
    )
    st.divider()

    proveedor = st.radio(
        "Proveedor de IA",
        [
            "Groq (gratuito, nube)",
            "Google Gemini (gratuito, nube)",
            "Anthropic Claude (API)",
            "OpenAI",
            "Ollama (local, gratuito, sin envío de datos)",
            "API compatible con OpenAI (LM Studio, vLLM, Together AI...)",
        ],
        index=0,
    )

    config_provider: dict = {}
    privacidad_valida = True

    # ── Groq ─────────────────────────────────────────────────────────────────
    if proveedor.startswith("Groq"):
        _mostrar_aviso("groq")
        st.markdown(
            "Obtenga su API key gratuita en **console.groq.com** → API Keys."
        )
        api_key = st.text_input(
            "API Key de Groq",
            type="password",
            help="Se obtiene en console.groq.com",
        )
        modelo = st.selectbox(
            "Modelo",
            [
                "llama-3.3-70b-versatile",
                "llama-3.1-8b-instant",
                "gemma2-9b-it",
                "llama3-70b-8192",
            ],
            index=0,
            help="llama-3.3-70b-versatile ofrece los mejores resultados",
        )
        if not api_key:
            st.warning("Introduzca su API key de Groq para continuar.")
            privacidad_valida = False
        config_provider = {
            "provider": "openai_compatible",
            "api_key": api_key,
            "base_url": "https://api.groq.com/openai/v1",
            "model": modelo,
        }

    # ── Google Gemini ─────────────────────────────────────────────────────────
    elif proveedor.startswith("Google"):
        _mostrar_aviso("gemini")
        st.markdown(
            "Obtenga su API key gratuita en **aistudio.google.com** → Get API key."
        )
        api_key = st.text_input(
            "API Key de Google AI Studio",
            type="password",
            help="Se obtiene en aistudio.google.com",
        )
        modelo = st.selectbox(
            "Modelo",
            [
                "gemini-2.0-flash",
                "gemini-1.5-flash",
                "gemini-1.5-pro",
            ],
            index=0,
            help="gemini-2.0-flash es el más rápido y capaz del nivel gratuito",
        )
        if not api_key:
            st.warning("Introduzca su API key de Google AI Studio para continuar.")
            privacidad_valida = False
        config_provider = {
            "provider": "openai_compatible",
            "api_key": api_key,
            "base_url": "https://generativelanguage.googleapis.com/v1beta/openai/",
            "model": modelo,
        }

    # ── Ollama ────────────────────────────────────────────────────────────────
    elif proveedor.startswith("Ollama"):
        _mostrar_aviso("ollama")
        st.markdown("**Configuración de Ollama:**")

        base_url = st.text_input(
            "URL de Ollama",
            value=OLLAMA_BASE_URL,
            help="Por defecto: http://localhost:11434",
        )

        col_modelo, col_btn = st.columns([3, 1])
        with col_btn:
            st.write("")
            if st.button("Detectar modelos"):
                from src.llm.ollama_provider import OllamaProvider
                tmp = OllamaProvider(base_url=base_url)
                if tmp.verificar_conexion():
                    modelos = tmp.listar_modelos()
                    st.session_state["_ollama_modelos"] = modelos
                    if modelos:
                        st.success(f"{len(modelos)} modelos encontrados")
                    else:
                        st.warning("Ollama conectado pero sin modelos instalados")
                else:
                    st.error("No se puede conectar con Ollama. Verifique que esté en ejecución.")

        modelos_cache = st.session_state.get("_ollama_modelos", [])
        with col_modelo:
            if modelos_cache:
                modelo = st.selectbox("Modelo", options=modelos_cache, index=0)
            else:
                modelo = st.text_input(
                    "Modelo",
                    value=OLLAMA_MODEL,
                    help="Ejemplo: llama3, mistral, qwen2, deepseek-r1",
                )

        config_provider = {"provider": "ollama", "model": modelo, "base_url": base_url}

    # ── Anthropic ─────────────────────────────────────────────────────────────
    elif proveedor.startswith("Anthropic Claude"):
        plan = st.radio(
            "Plan / tipo de cuenta",
            ["API de pago (individual / empresa)", "Claude for Business / Enterprise"],
        )
        _mostrar_aviso("anthropic_api" if "pago" in plan else "anthropic_enterprise")

        api_key = st.text_input(
            "API Key de Anthropic",
            type="password",
            value=ANTHROPIC_API_KEY,
            help="Obtenga su API key en https://console.anthropic.com/",
        )
        modelo = st.selectbox(
            "Modelo",
            ["claude-sonnet-4-6", "claude-opus-4-7", "claude-haiku-4-5-20251001"],
            index=0,
        )

        if not api_key:
            st.warning("Introduzca su API key para continuar.")
            privacidad_valida = False

        config_provider = {"provider": "anthropic", "api_key": api_key, "model": modelo}

    # ── OpenAI ────────────────────────────────────────────────────────────────
    elif proveedor.startswith("OpenAI"):
        plan = st.radio(
            "Plan / tipo de cuenta",
            ["Cuenta gratuita", "API de pago (Tier 1+)", "ChatGPT Enterprise"],
        )
        clave_aviso = {
            "Cuenta gratuita": "openai_free",
            "API de pago (Tier 1+)": "openai_paid",
            "ChatGPT Enterprise": "openai_enterprise",
        }[plan]
        _mostrar_aviso(clave_aviso)

        api_key = st.text_input(
            "API Key de OpenAI",
            type="password",
            help="Obtenga su API key en https://platform.openai.com/",
        )
        modelo = st.selectbox(
            "Modelo",
            ["gpt-4o", "gpt-4o-mini", "gpt-4-turbo", "gpt-3.5-turbo"],
            index=0,
        )

        if not api_key:
            st.warning("Introduzca su API key para continuar.")
            privacidad_valida = False

        config_provider = {
            "provider": "openai_compatible",
            "api_key": api_key,
            "base_url": "https://api.openai.com/v1",
            "model": modelo,
        }

    # ── API compatible con OpenAI ──────────────────────────────────────────────
    else:
        subtipo = st.radio(
            "Tipo de API",
            [
                "Local (LM Studio, vLLM, llama.cpp) — datos en su infraestructura",
                "Servicio externo (Groq, Together AI, Mistral API, Anyscale...)",
            ],
        )
        _mostrar_aviso(
            "openai_compatible_local" if subtipo.startswith("Local") else "openai_compatible_external"
        )

        base_url = st.text_input(
            "URL base de la API",
            value=OPENAI_COMPATIBLE_BASE_URL,
            help="Ejemplo LM Studio: http://localhost:1234/v1  |  Groq: https://api.groq.com/openai/v1",
        )
        api_key = st.text_input(
            "API Key (dejar vacío si no es necesaria)",
            type="password",
            value=OPENAI_COMPATIBLE_API_KEY,
        )
        modelo = st.text_input(
            "Nombre del modelo",
            value=OPENAI_COMPATIBLE_MODEL,
            help="Ejemplo: llama-3.1-8b-instruct, mistral-7b-instruct, deepseek-r1",
        )

        if not base_url or not modelo:
            st.warning("Introduzca la URL base y el nombre del modelo para continuar.")
            privacidad_valida = False

        config_provider = {
            "provider": "openai_compatible",
            "api_key": api_key or "dummy",
            "base_url": base_url,
            "model": modelo,
        }

    st.divider()
    privacidad_aceptada = st.checkbox(
        "He leído y entiendo las condiciones de privacidad descritas arriba"
    )
    puede_continuar = privacidad_valida and privacidad_aceptada

    if st.button(
        "Configurar y continuar",
        type="primary",
        use_container_width=True,
        disabled=not puede_continuar,
    ):
        try:
            provider = crear_provider(config_provider)
            st.session_state.provider = provider
            st.session_state.provider_configurado = True
            st.session_state.chatbot_evaluador = AIComplyChat(provider=provider)
            st.rerun()
        except Exception as exc:
            st.error(f"Error al configurar el proveedor: {exc}")


if not st.session_state.provider_configurado:
    mostrar_selector_provider()
    st.stop()


# ════════════════════════════════════════════════════════════════════════════════
# PANTALLA 2: AVISO LEGAL
# ════════════════════════════════════════════════════════════════════════════════
def mostrar_disclaimer() -> None:
    st.title("AIComply")
    st.subheader("Evaluación de cumplimiento del AI Act europeo para PYMEs industriales")
    st.markdown(DISCLAIMER_INICIAL)
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button(
            "Acepto las condiciones y quiero continuar",
            use_container_width=True,
            type="primary",
        ):
            st.session_state.disclaimer_aceptado = True
            st.rerun()


if not st.session_state.disclaimer_aceptado:
    mostrar_disclaimer()
    st.stop()


# ════════════════════════════════════════════════════════════════════════════════
# SIDEBAR
# ════════════════════════════════════════════════════════════════════════════════
with st.sidebar:
    st.title("AIComply")
    st.caption("Evaluación AI Act para PYMEs industriales")
    st.divider()

    provider = st.session_state.provider
    st.caption(
        f"Modelo: **{provider.nombre_modelo}**  \n"
        f"Provider: **{provider.nombre_provider}**"
    )
    st.divider()

    # Progreso de la evaluación
    st.caption("**Progreso:**")
    eval_ok = (
        st.session_state.get("evaluacion_completada", False)
        or st.session_state.get("acceso_directo_cumplimiento", False)
    )
    cumpl_ok = st.session_state.get("cumplimiento_completado", False)
    informe_ok = bool(
        st.session_state.get("informe_md_clasificacion")
        or st.session_state.get("informe_md_cumplimiento")
        or st.session_state.get("informe_md_completo")
    )

    st.caption(f"{'✓' if eval_ok else '○'} Evaluación y clasificación")
    st.caption(f"{'✓' if cumpl_ok else '○'} Análisis de cumplimiento")
    st.caption(f"{'✓' if informe_ok else '○'} Informe generado")

    if eval_ok:
        datos = st.session_state.clasificacion_data
        clasificacion = datos.get("clasificacion", "?")
        st.metric("Clasificación", clasificacion)

    st.divider()

    if st.button("Nueva evaluación", use_container_width=True):
        for clave in ("mensajes_evaluador", "mensajes_cumplimiento"):
            st.session_state[clave] = []
        for clave in ("clasificacion_data", "cumplimiento_data"):
            st.session_state[clave] = {}
        for clave in ("informe_md_clasificacion", "informe_md_cumplimiento", "informe_md_completo"):
            st.session_state[clave] = None
        st.session_state.evaluacion_completada = False
        st.session_state.cumplimiento_completado = False
        st.session_state.acceso_directo_cumplimiento = False
        st.session_state.chatbot_evaluador = AIComplyChat(provider=provider)
        st.session_state.chatbot_cumplimiento = None
        st.rerun()

    if st.button("Cambiar proveedor de IA", use_container_width=True):
        for clave in list(st.session_state.keys()):
            del st.session_state[clave]
        st.rerun()

    st.divider()
    st.caption(
        "AIComply es una herramienta auxiliar de orientación. "
        "Los resultados no constituyen asesoramiento legal."
    )


# ════════════════════════════════════════════════════════════════════════════════
# PESTAÑAS PRINCIPALES
# ════════════════════════════════════════════════════════════════════════════════
tab1, tab2, tab3 = st.tabs(
    ["Evaluador y clasificador", "Cumplimiento", "Informe"]
)

with tab1:
    mostrar_tab_evaluador(provider)

with tab2:
    mostrar_tab_cumplimiento(provider)

with tab3:
    mostrar_tab_informe()

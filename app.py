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

import streamlit as st

from config import (
    ANTHROPIC_API_KEY,
    ANTHROPIC_MODEL,
    DISCLAIMER_CRITICO,
    DISCLAIMER_INICIAL,
    NIVELES_RIESGO,
    OLLAMA_BASE_URL,
    OLLAMA_MODEL,
    OPENAI_COMPATIBLE_API_KEY,
    OPENAI_COMPATIBLE_BASE_URL,
    OPENAI_COMPATIBLE_MODEL,
    PREGUNTAS_EVALUACION,
)
from src.chatbot import AIComplyChat
from src.llm.factory import crear_provider, crear_provider_desde_env
from src.readme_analyzer import AnalizadorReadme
from src.report_generator import GeneradorInforme
from src.risk_classifier import ClasificadorRiesgo

st.set_page_config(
    page_title="AIComply — Evaluación AI Act",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Avisos de privacidad por provider y plan ───────────────────────────────────
_AVISOS = {
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
        "ningún dato sale de ella. "
        "Recomendado para máxima privacidad y control.",
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
def _init_session():
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

    if "chatbot" not in st.session_state:
        if st.session_state.get("provider_configurado") and st.session_state.get("provider"):
            st.session_state.chatbot = AIComplyChat(provider=st.session_state.provider)
        else:
            st.session_state.chatbot = None

    for clave in ("mensajes_ui", ):
        if clave not in st.session_state:
            st.session_state[clave] = []

    for clave in ("analisis_readme", "puntuacion", "informe_md"):
        if clave not in st.session_state:
            st.session_state[clave] = None

    if "resumen_conversacion" not in st.session_state:
        st.session_state.resumen_conversacion = {}


_init_session()


# ════════════════════════════════════════════════════════════════════════════════
# PANTALLA 1: CONFIGURACIÓN DEL PROVIDER
# ════════════════════════════════════════════════════════════════════════════════
def mostrar_selector_provider():
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
            "Ollama (local, gratuito, sin envío de datos)",
            "Anthropic Claude (API)",
            "OpenAI",
            "API compatible con OpenAI (LM Studio, vLLM, Groq, Together AI...)",
        ],
        index=0,
    )

    config_provider: dict = {}
    privacidad_valida = True

    # ── Ollama ────────────────────────────────────────────────────────────────
    if proveedor.startswith("Ollama"):
        _mostrar_aviso("ollama")
        st.markdown("**Configuración de Ollama:**")

        base_url = st.text_input(
            "URL de Ollama",
            value=OLLAMA_BASE_URL,
            help="Por defecto: http://localhost:11434",
        )

        col_modelo, col_btn = st.columns([3, 1])
        modelos_disponibles: list[str] = []

        with col_btn:
            st.write("")
            if st.button("Detectar modelos"):
                from src.llm.ollama_provider import OllamaProvider
                tmp = OllamaProvider(base_url=base_url)
                if tmp.verificar_conexion():
                    modelos_disponibles = tmp.listar_modelos()
                    st.session_state["_ollama_modelos"] = modelos_disponibles
                    if modelos_disponibles:
                        st.success(f"{len(modelos_disponibles)} modelos encontrados")
                    else:
                        st.warning("Ollama conectado pero sin modelos instalados")
                else:
                    st.error("No se puede conectar con Ollama. Verifique que esté en ejecución.")

        modelos_cache = st.session_state.get("_ollama_modelos", [])
        with col_modelo:
            if modelos_cache:
                modelo = st.selectbox(
                    "Modelo",
                    options=modelos_cache,
                    index=0,
                )
            else:
                modelo = st.text_input(
                    "Modelo",
                    value=OLLAMA_MODEL,
                    help="Ejemplo: llama3, mistral, qwen2, deepseek-r1",
                )

        config_provider = {"provider": "ollama", "model": modelo, "base_url": base_url}

    # ── Anthropic ─────────────────────────────────────────────────────────────
    elif proveedor.startswith("Anthropic"):
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

    # ── Checkbox de aceptación ────────────────────────────────────────────────
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
            st.session_state.chatbot = AIComplyChat(provider=provider)
            st.rerun()
        except Exception as e:
            st.error(f"Error al configurar el provider: {e}")


if not st.session_state.provider_configurado:
    mostrar_selector_provider()
    st.stop()


# ════════════════════════════════════════════════════════════════════════════════
# PANTALLA 2: AVISO LEGAL DE AICOMPLY
# ════════════════════════════════════════════════════════════════════════════════
def mostrar_disclaimer():
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

    nivel = st.session_state.chatbot.nivel_riesgo if st.session_state.chatbot else None
    if nivel and nivel in NIVELES_RIESGO:
        st.metric("Nivel de riesgo detectado", nivel)
    else:
        st.info("Nivel de riesgo: pendiente de análisis")

    st.divider()

    if st.button("Nueva evaluación", use_container_width=True):
        if st.session_state.chatbot:
            st.session_state.chatbot.resetear()
        st.session_state.mensajes_ui = []
        st.session_state.analisis_readme = None
        st.session_state.puntuacion = None
        st.session_state.informe_md = None
        st.session_state.resumen_conversacion = {}
        st.rerun()

    if st.button("Cambiar proveedor de IA", use_container_width=True):
        st.session_state.provider_configurado = False
        st.session_state.disclaimer_aceptado = False
        st.session_state.chatbot = None
        st.session_state.mensajes_ui = []
        st.session_state.analisis_readme = None
        st.session_state.puntuacion = None
        st.session_state.informe_md = None
        st.session_state.resumen_conversacion = {}
        st.rerun()

    st.divider()
    st.caption("**Preguntas clave de la evaluación:**")
    for i, pregunta in enumerate(PREGUNTAS_EVALUACION, 1):
        st.caption(f"{i}. {pregunta}")

    st.divider()
    st.caption(
        "AIComply es una herramienta auxiliar de orientación. "
        "Los resultados no constituyen asesoramiento legal."
    )


# ════════════════════════════════════════════════════════════════════════════════
# TABS PRINCIPALES
# ════════════════════════════════════════════════════════════════════════════════
tab1, tab2, tab3 = st.tabs(
    ["Chatbot de evaluación", "Análisis documental", "Informe de cumplimiento"]
)

chatbot: AIComplyChat = st.session_state.chatbot


# ── TAB 1: CHATBOT ────────────────────────────────────────────────────────────
with tab1:
    st.header("Evaluación conversacional")
    st.caption(
        "Describa su sistema de IA y le ayudaré a determinar su nivel de cumplimiento "
        "con el AI Act. Cada concepto técnico incluye su definición oficial con referencia al artículo."
    )

    chat_container = st.container(height=500)

    with chat_container:
        if not st.session_state.mensajes_ui:
            with st.chat_message("assistant"):
                st.markdown(
                    "Bienvenido a **AIComply**.\n\n"
                    "> **Aviso legal:** AIComply es una herramienta auxiliar de orientación. "
                    "Los resultados no constituyen asesoramiento legal. "
                    "Se recomienda consultar con especialistas antes de tomar decisiones de cumplimiento normativo.\n\n"
                    "Soy su asistente para evaluar el cumplimiento con el **AI Act europeo** "
                    "(Reglamento UE 2024/1689).\n\n"
                    "Para comenzar la evaluación, cuénteme sobre el sistema de IA de su empresa:\n\n"
                    "1. ¿Cuál es su **propósito principal**?\n"
                    "2. ¿En qué **sector** opera su empresa?\n"
                    "3. ¿El sistema toma decisiones que afectan directamente a **personas**?"
                )

        for msg in st.session_state.mensajes_ui:
            with st.chat_message(msg["role"]):
                st.markdown(msg["content"])

    if prompt := st.chat_input("Describa su sistema de IA..."):
        st.session_state.mensajes_ui.append({"role": "user", "content": prompt})

        with chat_container:
            with st.chat_message("user"):
                st.markdown(prompt)

            with st.chat_message("assistant"):
                respuesta_placeholder = st.empty()
                texto_completo = ""

                with st.spinner("Analizando..."):
                    for fragmento in chatbot.chat_stream(prompt):
                        texto_completo += fragmento
                        respuesta_placeholder.markdown(texto_completo + "▌")

                respuesta_placeholder.markdown(texto_completo)

        st.session_state.mensajes_ui.append({"role": "assistant", "content": texto_completo})

        if chatbot.nivel_riesgo in ("PROHIBIDO", "ALTO"):
            st.warning(DISCLAIMER_CRITICO)

        st.rerun()

    col_a, col_b = st.columns(2)
    with col_a:
        if st.button("Clasificación rápida por descripción"):
            st.session_state["mostrar_clasificador"] = True
    with col_b:
        if st.button("Generar resumen de la conversación") and len(st.session_state.mensajes_ui) >= 2:
            with st.spinner("Generando resumen estructurado..."):
                resumen_texto = chatbot.generar_resumen_conversacion()
                try:
                    st.session_state.resumen_conversacion = json.loads(resumen_texto)
                    st.success("Resumen generado. Vaya a la pestaña Informe de cumplimiento.")
                except Exception:
                    st.error("No se pudo generar el resumen. Continúe la conversación con más detalles.")

    if st.session_state.get("mostrar_clasificador"):
        with st.form("form_clasificacion"):
            descripcion = st.text_area(
                "Describa brevemente su sistema de IA",
                placeholder="Ejemplo: Sistema de visión artificial que detecta defectos en piezas industriales en la línea de producción",
                height=100,
            )
            submitted = st.form_submit_button("Clasificar", type="primary")

        if submitted and descripcion:
            with st.spinner("Clasificando según el AI Act..."):
                clasificador = ClasificadorRiesgo(provider=st.session_state.provider)
                resultado = clasificador.clasificar(descripcion)

            nivel_r = resultado.get("nivel_riesgo", "DESCONOCIDO")
            st.success(f"**Nivel de riesgo:** {nivel_r}")
            st.info(f"**Justificación:** {resultado.get('justificacion', '')}")

            col1, col2 = st.columns(2)
            with col1:
                arts = resultado.get("articulos_principales", [])
                if arts:
                    st.write("**Artículos principales:**")
                    for a in arts:
                        st.write(f"- {a}")
            with col2:
                obls = resultado.get("obligaciones_clave", [])
                if obls:
                    st.write("**Obligaciones clave:**")
                    for o in obls:
                        st.write(f"- {o}")


# ── TAB 2: ANÁLISIS DOCUMENTAL ────────────────────────────────────────────────
with tab2:
    st.header("Análisis documental")
    st.caption(
        "Suba o pegue el README o la documentación técnica de su proyecto para detectar "
        "gaps de cumplimiento con el AI Act con referencias concretas a artículos."
    )

    col_upload, col_paste = st.columns([1, 1])

    with col_upload:
        archivo = st.file_uploader("Subir archivo de documentación", type=["md", "txt", "rst"])

    with col_paste:
        texto_pegado = st.text_area(
            "O pegue el contenido aquí",
            height=200,
            placeholder="Pegue el contenido de su README o documentación técnica...",
        )

    contenido_readme = ""
    if archivo:
        contenido_readme = archivo.read().decode("utf-8", errors="replace")
        st.success(f"Archivo cargado: {archivo.name} ({len(contenido_readme)} caracteres)")
    elif texto_pegado:
        contenido_readme = texto_pegado

    if contenido_readme:
        nivel_previo = chatbot.nivel_riesgo
        if nivel_previo:
            st.info(f"Se analizará considerando el nivel de riesgo del chat: **{nivel_previo}**")

        if st.button("Analizar documentación", type="primary", use_container_width=True):
            with st.spinner("Analizando contra los requisitos del AI Act..."):
                analizador = AnalizadorReadme(provider=st.session_state.provider)
                if nivel_previo:
                    resultado = analizador.analizar_con_contexto(contenido_readme, nivel_previo)
                else:
                    resultado = analizador.analizar(contenido_readme)
                puntuacion = analizador.calcular_puntuacion_cumplimiento(resultado)

            st.session_state.analisis_readme = resultado
            st.session_state.puntuacion = puntuacion
            st.rerun()

    if st.session_state.analisis_readme:
        analisis = st.session_state.analisis_readme
        punt = st.session_state.puntuacion

        col_nivel, col_score = st.columns(2)
        with col_nivel:
            st.metric("Nivel de riesgo detectado", analisis.get("nivel_riesgo", "DESCONOCIDO"))
        with col_score:
            if punt:
                st.metric(
                    "Puntuación de cumplimiento",
                    f"{punt.get('porcentaje', 0)}%",
                    delta=f"Cumple: {punt.get('cumple', 0)} | Parcial: {punt.get('parcial', 0)} | Gap: {punt.get('gap', 0)}",
                )

        if analisis.get("justificacion_riesgo"):
            st.info(analisis["justificacion_riesgo"])

        if analisis.get("fortalezas"):
            with st.expander("Fortalezas identificadas", expanded=False):
                for f in analisis["fortalezas"]:
                    st.write(f"- {f}")

        gaps = analisis.get("gaps", [])
        if gaps:
            st.subheader("Análisis detallado por artículo")
            for gap in gaps:
                estado = gap.get("estado", "gap")
                etiqueta = {"cumple": "CUMPLE", "parcial": "PARCIAL", "gap": "GAP"}.get(
                    estado, estado.upper()
                )
                color = {"cumple": "green", "parcial": "orange", "gap": "red"}.get(estado, "gray")
                with st.expander(f"[{etiqueta}] {gap.get('articulo', '')} — {gap.get('titulo', '')}"):
                    st.markdown(f"**Estado:** :{color}[{etiqueta}]")
                    st.markdown(f"**Situación:** {gap.get('descripcion', '')}")
                    if estado != "cumple" and gap.get("recomendacion"):
                        st.warning(f"**Recomendación:** {gap.get('recomendacion', '')}")

        st.info("Vaya a la pestaña **Informe de cumplimiento** para generar y exportar el informe completo.")


# ── TAB 3: INFORME ────────────────────────────────────────────────────────────
with tab3:
    st.header("Informe de cumplimiento")
    st.caption("Genera y exporta el informe de cumplimiento con el AI Act.")

    st.warning(
        "AIComply es una herramienta auxiliar de orientación. "
        "Los resultados no constituyen asesoramiento legal. "
        "Se recomienda consultar con especialistas antes de tomar decisiones de cumplimiento normativo."
    )

    tiene_datos = bool(st.session_state.resumen_conversacion or st.session_state.analisis_readme)

    if not tiene_datos:
        st.info(
            "Para generar el informe necesita:\n"
            "1. Completar la evaluación en el chatbot y pulsar **Generar resumen de la conversación**, o\n"
            "2. Analizar su documentación en la pestaña **Análisis documental**"
        )
    else:
        resumen = st.session_state.resumen_conversacion
        analisis = st.session_state.analisis_readme
        puntuacion = st.session_state.puntuacion

        if not resumen and analisis:
            nivel_r = analisis.get("nivel_riesgo", "DESCONOCIDO")
            resumen = {
                "nombre_sistema": "Sistema analizado via documentación",
                "sector": "No especificado",
                "proposito": analisis.get("justificacion_riesgo", ""),
                "nivel_riesgo": nivel_r,
                "articulos_aplicables": analisis.get("articulos_aplicables", []),
                "caracteristicas_clave": analisis.get("fortalezas", []),
                "obligaciones_identificadas": [],
            }

        if st.button("Generar informe", type="primary", use_container_width=True):
            with st.spinner("Generando informe de cumplimiento..."):
                generador = GeneradorInforme()
                informe_md = generador.generar_markdown(resumen, analisis, puntuacion)
                st.session_state.informe_md = informe_md

        if st.session_state.informe_md:
            st.markdown("---")
            st.markdown(st.session_state.informe_md)
            st.markdown("---")

            col_md, col_pdf = st.columns(2)

            with col_md:
                st.download_button(
                    label="Descargar Markdown",
                    data=st.session_state.informe_md.encode("utf-8"),
                    file_name="informe_aicomply.md",
                    mime="text/markdown",
                    use_container_width=True,
                )

            with col_pdf:
                try:
                    generador = GeneradorInforme()
                    pdf_bytes = generador.exportar_pdf(st.session_state.informe_md)
                    if pdf_bytes:
                        st.download_button(
                            label="Descargar PDF",
                            data=pdf_bytes,
                            file_name="informe_aicomply.pdf",
                            mime="application/pdf",
                            use_container_width=True,
                        )
                    else:
                        st.caption("PDF no disponible. Instale fpdf2: pip install fpdf2")
                except Exception:
                    st.caption("PDF no disponible. Instale fpdf2: pip install fpdf2")

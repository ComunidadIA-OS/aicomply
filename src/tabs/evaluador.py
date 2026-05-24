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

import base64

import streamlit as st

from src.chatbot import AIComplyChat, _SENAL_COMPLETA
from src.llm.provider import LLMProvider

# ── Pirámide SVG de niveles de riesgo ─────────────────────────────────────────
# Vértice: (210, 20). Base: (6, 320) — (414, 320). Pendiente: 204/300.
# Todos los vértices laterales son colineales en ambos lados.
_SVG_PIRAMIDE = """
<svg viewBox="0 0 420 340" xmlns="http://www.w3.org/2000/svg"
     width="100%" height="340" style="max-width:400px; margin:auto; display:block;">
  <!-- Riesgo mínimo — verde, base -->
  <polygon points="57,245 363,245 414,320 6,320"
           fill="#388E3C" opacity="0.92" stroke="white" stroke-width="1"/>
  <text x="210" y="283" text-anchor="middle" dominant-baseline="middle" fill="white"
        font-family="Arial,sans-serif" font-size="14" font-weight="bold">Riesgo mínimo</text>

  <!-- Riesgo limitado — amarillo -->
  <polygon points="108,170 312,170 363,245 57,245"
           fill="#F9A825" opacity="0.92" stroke="white" stroke-width="1"/>
  <text x="210" y="208" text-anchor="middle" dominant-baseline="middle" fill="white"
        font-family="Arial,sans-serif" font-size="14" font-weight="bold">Riesgo limitado</text>

  <!-- Alto riesgo — naranja -->
  <polygon points="159,95 261,95 312,170 108,170"
           fill="#E64A19" opacity="0.92" stroke="white" stroke-width="1"/>
  <text x="210" y="133" text-anchor="middle" dominant-baseline="middle" fill="white"
        font-family="Arial,sans-serif" font-size="14" font-weight="bold">Alto riesgo</text>

  <!-- Prohibido — rojo oscuro, vértice en pico -->
  <polygon points="210,20 261,95 159,95"
           fill="#B71C1C" opacity="0.95" stroke="white" stroke-width="1"/>
  <text x="210" y="70" text-anchor="middle" dominant-baseline="middle" fill="white"
        font-family="Arial,sans-serif" font-size="14" font-weight="bold">Prohibido</text>
</svg>
"""

# Descripción de los 4 niveles para la pantalla introductoria
_NIVELES_DESCRIPCION = [
    (
        "Riesgo inaceptable (prohibido)",
        "#B71C1C",
        "Sistemas que atentan contra derechos fundamentales: manipulación subliminal, "
        "puntuación social ciudadana, biometría remota en espacios públicos. "
        "Están completamente prohibidos por el AI Act.",
    ),
    (
        "Alto riesgo",
        "#E64A19",
        "Sistemas con impacto significativo en personas: selección de personal, "
        "crédito, infraestructuras críticas, educación, salud o seguridad pública. "
        "Requieren cumplimiento exhaustivo de requisitos técnicos y documentales.",
    ),
    (
        "Riesgo limitado",
        "#F9A825",
        "Sistemas con obligaciones de transparencia: chatbots, generadores de contenido "
        "sintético (imágenes, vídeos, texto), sistemas de reconocimiento de emociones. "
        "Deben informar claramente a los usuarios.",
    ),
    (
        "Riesgo mínimo",
        "#388E3C",
        "Sistemas sin obligaciones específicas del AI Act: filtros de spam, "
        "videojuegos con IA, herramientas de optimización interna. "
        "Se recomiendan buenas prácticas voluntarias.",
    ),
]

# Prompt para extraer descripción en lenguaje natural del README
_PROMPT_README_A_DESCRIPCION = """Analiza el siguiente README o documentación técnica de un sistema de IA y extrae la información clave. Responde en español con un resumen en 4-6 frases que cubra:

1. Qué hace el sistema (propósito principal).
2. En qué sector o industria opera.
3. Quién lo desarrolla y quién lo usa.
4. Si el sistema toma decisiones que afectan directamente a personas.
5. Si procesa datos sensibles (biométricos, médicos, financieros, personales).
6. Cómo se despliega o pone en servicio.

README o documentación:
{contenido}

Responde en español, en formato de párrafo continuo, sin listas ni viñetas. Sé conciso y objetivo."""

_MENSAJE_BIENVENIDA = """Bienvenido a AIComply.

> **Aviso legal:** Los resultados de esta evaluación son orientativos y no constituyen asesoramiento jurídico vinculante. Consulte con especialistas antes de tomar decisiones de cumplimiento normativo.

Voy a ayudarle a determinar si su sistema de inteligencia artificial está sujeto a la Ley de Inteligencia Artificial de la UE (Reglamento (UE) 2024/1689) y qué obligaciones le aplican.

Para comenzar: ¿puede describirme brevemente qué hace el sistema de IA que quiere evaluar y en qué contexto opera?"""


def _analizar_readme(provider: LLMProvider, contenido: str) -> str:
    """Extrae una descripción del sistema de IA a partir del README."""
    respuesta = provider.chat(
        messages=[
            {
                "role": "user",
                "content": _PROMPT_README_A_DESCRIPCION.format(contenido=contenido[:8000]),
            }
        ]
    )
    return respuesta.strip()


def _inicializar_estado(provider: LLMProvider) -> None:
    """Inicializa las claves de session_state de la pestaña Evaluador."""
    if "intro_vista" not in st.session_state:
        st.session_state.intro_vista = False
    if "mensajes_evaluador" not in st.session_state:
        st.session_state.mensajes_evaluador = []
    if "chatbot_evaluador" not in st.session_state:
        st.session_state.chatbot_evaluador = AIComplyChat(provider=provider)
    if "evaluacion_completada" not in st.session_state:
        st.session_state.evaluacion_completada = False
    if "clasificacion_data" not in st.session_state:
        st.session_state.clasificacion_data = {}


def _mostrar_intro() -> None:
    """Pantalla introductoria con pirámide de riesgo y descripción de los niveles."""
    st.header("Evaluador y clasificador de riesgo")
    st.markdown(
        "Antes de iniciar la evaluación, conozca los **cuatro niveles de riesgo** "
        "del AI Act europeo. La evaluación determinará en cuál de ellos se encuentra su sistema."
    )

    col_svg, col_desc = st.columns([1, 1], gap="large")

    with col_svg:
        _svg_b64 = base64.b64encode(_SVG_PIRAMIDE.strip().encode()).decode()
        st.markdown(
            f'<div style="padding-top:18px;">'
            f'<img src="data:image/svg+xml;base64,{_svg_b64}"'
            f' style="width:100%; max-width:400px; display:block; margin:auto;" /></div>',
            unsafe_allow_html=True,
        )

    with col_desc:
        for nombre, color, descripcion in _NIVELES_DESCRIPCION:
            st.markdown(
                f'<div style="border-left:4px solid {color}; padding:6px 12px; margin-bottom:10px;">'
                f'<strong>{nombre}</strong><br/>'
                f'<span style="font-size:0.9em; color:#444;">{descripcion}</span>'
                f"</div>",
                unsafe_allow_html=True,
            )

    st.divider()

    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button("Iniciar evaluación", type="primary", use_container_width=True):
            st.session_state.intro_vista = True
            st.rerun()


def _mostrar_chat(chatbot: AIComplyChat) -> None:
    """Renderiza el área de chat y gestiona el input del usuario."""
    chat_container = st.container(height=460)

    with chat_container:
        if not st.session_state.mensajes_evaluador:
            with st.chat_message("assistant"):
                st.markdown(_MENSAJE_BIENVENIDA)

        for msg in st.session_state.mensajes_evaluador:
            with st.chat_message(msg["role"]):
                st.markdown(msg["content"])

    if st.session_state.evaluacion_completada:
        return

    if prompt := st.chat_input("Escriba su respuesta aquí..."):
        st.session_state.mensajes_evaluador.append({"role": "user", "content": prompt})

        with chat_container:
            with st.chat_message("user"):
                st.markdown(prompt)

            with st.chat_message("assistant"):
                placeholder = st.empty()
                texto_raw = ""
                try:
                    for fragmento in chatbot.chat_stream(prompt):
                        texto_raw += fragmento
                        # Mostrar sin la señal técnica
                        placeholder.markdown(
                            texto_raw.replace(_SENAL_COMPLETA, "").strip() + "▌"
                        )
                except Exception as exc:
                    msg_err = str(exc)
                    if "Connection refused" in msg_err or "ConnectError" in msg_err:
                        texto_raw = "_Error: no se puede conectar con el proveedor de IA. Compruebe la configuración en la barra lateral._"
                    else:
                        texto_raw = f"_Error al conectar con el modelo: {msg_err}_"

                texto_visible = texto_raw.replace(_SENAL_COMPLETA, "").strip()
                placeholder.markdown(texto_visible)

        st.session_state.mensajes_evaluador.append(
            {"role": "assistant", "content": texto_visible}
        )
        st.rerun()


def mostrar_tab_evaluador(provider: LLMProvider) -> None:
    """Renderiza la pestaña Evaluador y clasificador (Pestaña 1)."""
    _inicializar_estado(provider)

    # ── Pantalla introductoria ─────────────────────────────────────────────────
    if not st.session_state.intro_vista:
        _mostrar_intro()
        return

    chatbot: AIComplyChat = st.session_state.chatbot_evaluador

    st.header("Evaluador y clasificador")
    st.caption(
        "Describa su sistema de IA en lenguaje natural o inicie a partir de su documentación técnica. "
        "Le haré las preguntas necesarias para determinar su clasificación y obligaciones."
    )

    # ── Opción de inicio por README (solo antes de la primera interacción) ─────
    if not st.session_state.mensajes_evaluador and not st.session_state.evaluacion_completada:
        with st.expander(
            "Iniciar a partir de documentación técnica (README u otro documento)", expanded=False
        ):
            st.caption(
                "Suba o pegue la documentación de su sistema. "
                "Extraeré la información relevante y confirmaré las inferencias con usted antes de continuar."
            )
            col_upload, col_paste = st.columns(2)
            with col_upload:
                archivo = st.file_uploader(
                    "Subir archivo", type=["md", "txt", "rst"], key="readme_upload"
                )
            with col_paste:
                texto_pegado = st.text_area(
                    "O pegar el contenido aquí",
                    height=120,
                    placeholder="Pegue el contenido de su README o documentación técnica...",
                    key="readme_paste",
                )

            contenido_readme = ""
            if archivo:
                contenido_readme = archivo.read().decode("utf-8", errors="replace")
                st.caption(f"Archivo cargado: {archivo.name} ({len(contenido_readme)} caracteres)")
            elif texto_pegado:
                contenido_readme = texto_pegado

            if contenido_readme:
                if st.button("Analizar documentación e iniciar evaluación", type="primary"):
                    with st.spinner("Analizando documentación..."):
                        descripcion = _analizar_readme(provider, contenido_readme)

                    mensaje_inicio = (
                        "He analizado la documentación técnica proporcionada. "
                        "Esto es lo que he entendido sobre el sistema:\n\n"
                        f"{descripcion}\n\n"
                        "Antes de continuar, ¿es correcta esta descripción? "
                        "¿Desea añadir o corregir algo?"
                    )
                    st.session_state.mensajes_evaluador.append(
                        {"role": "assistant", "content": mensaje_inicio}
                    )
                    chatbot.historial.append({"role": "assistant", "content": mensaje_inicio})
                    st.rerun()

    st.divider()

    # ── Área de chat ───────────────────────────────────────────────────────────
    _mostrar_chat(chatbot)

    # ── Estado: evaluación completada ──────────────────────────────────────────
    if st.session_state.evaluacion_completada:
        datos = st.session_state.clasificacion_data
        clasificacion = datos.get("clasificacion", "?")
        rol = datos.get("rol", "?")
        roles_multiples = datos.get("roles_multiples", [])

        st.success(
            f"Evaluación completada — Clasificación: **{clasificacion}** | Rol: **{rol}**"
        )
        if roles_multiples:
            st.info(
                f"Se han identificado varios roles: **{', '.join(roles_multiples)}**. "
                "En la pestaña Cumplimiento verá las obligaciones diferenciadas por cada rol."
            )

        st.info("Proceda a la pestaña **Cumplimiento** para revisar sus obligaciones concretas.")

        indeterminados = datos.get("puntos_indeterminados", [])
        if indeterminados:
            with st.expander(
                f"Puntos que requieren revisión profesional ({len(indeterminados)})", expanded=False
            ):
                for punto in indeterminados:
                    st.caption(f"- {punto}")

        if st.button("Reiniciar evaluación completa", use_container_width=True):
            for clave in ("mensajes_evaluador", "mensajes_cumplimiento"):
                st.session_state[clave] = []
            for clave in ("clasificacion_data", "cumplimiento_data"):
                st.session_state[clave] = {}
            for clave in ("informe_md_clasificacion", "informe_md_cumplimiento", "informe_md_completo"):
                st.session_state[clave] = None
            st.session_state.evaluacion_completada = False
            st.session_state.cumplimiento_completado = False
            st.session_state.acceso_directo_cumplimiento = False
            st.session_state.intro_vista = False
            st.session_state.chatbot_evaluador = AIComplyChat(provider=provider)
            st.session_state.chatbot_cumplimiento = None
            st.rerun()
        return

    # ── Botón de completar: SOLO aparece cuando el LLM emitió [EVALUACION_COMPLETA] ──
    if chatbot.evaluacion_completa:
        st.divider()
        if st.button(
            "Completar evaluación y continuar a Cumplimiento",
            type="primary",
            use_container_width=True,
        ):
            with st.spinner("Extrayendo la clasificación de la conversación..."):
                datos = chatbot.extraer_clasificacion()

            if datos.get("clasificacion", "PENDIENTE") != "PENDIENTE":
                st.session_state.clasificacion_data = datos
                st.session_state.evaluacion_completada = True
                st.rerun()
            else:
                st.warning(
                    "No se pudo extraer una clasificación definitiva. "
                    "Continúe la conversación hasta que el asistente confirme la clasificación final."
                )

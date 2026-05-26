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

import html
import streamlit as st

from prompts.system_prompt_cumplimiento import SYSTEM_PROMPT_CUMPLIMIENTO
from src.chatbot import AIComplyChat
from src.llm.provider import LLMProvider
from src.security import mensaje_error_seguro, rate_limiter

_NIVELES_OPCIONES: dict[str, str] = {
    "Mínimo — Sin obligaciones específicas del AI Act": "MINIMO",
    "Limitado — Transparencia y etiquetado (chatbots, deepfakes...)": "LIMITADO",
    "Alto riesgo — Obligaciones exhaustivas (Art. 9–17, 43, 47–49...)": "ALTO",
    "Prohibido — Sistema potencialmente ilegal bajo el AI Act": "PROHIBIDO",
}

_ROLES_OPCIONES: dict[str, str] = {
    "Proveedor (diseña o desarrolla el sistema)": "proveedor",
    "Implementador / Responsable del despliegue (usa el sistema en su organización)": "implementador",
    "Distribuidor (comercializa el sistema de un tercero)": "distribuidor",
    "Importador (importa el sistema de fuera de la UE)": "importador",
}


def _formatear_contexto_evaluacion(datos: dict) -> str:
    """Convierte el dict de clasificación en texto legible para el system prompt."""
    clasificacion = datos.get("clasificacion", "DESCONOCIDO")
    roles_multiples = datos.get("roles_multiples", [])
    rol = datos.get("rol", "no especificado")
    rol_texto = (
        ", ".join(roles_multiples) if len(roles_multiples) > 1 else rol
    )
    estados = datos.get("estados_adicionales", [])
    descripcion = datos.get("descripcion_sistema", "No especificada")
    sector = datos.get("sector", "No especificado")
    obligaciones_prev = datos.get("obligaciones_preliminares", [])
    indeterminados = datos.get("puntos_indeterminados", [])

    lineas = [
        "RESULTADO DE LA EVALUACIÓN DEL ÁRBOL DE DECISIÓN:",
        f"- Clasificación: {clasificacion}",
        f"- Rol de la entidad: {rol_texto}",
    ]
    if estados:
        lineas.append(f"- Estados adicionales: {', '.join(estados)}")
    lineas += [
        f"- Descripción del sistema: {descripcion}",
        f"- Sector: {sector}",
    ]
    if obligaciones_prev:
        lineas.append("- Obligaciones ya identificadas en la evaluación:")
        for ob in obligaciones_prev:
            lineas.append(f"  * {ob}")
    if indeterminados:
        lineas.append("- Puntos indeterminados (requieren revisión profesional):")
        for p in indeterminados:
            lineas.append(f"  * {p}")

    return "\n".join(lineas)


def _inicializar_chatbot_cumplimiento(provider: LLMProvider, clasificacion_data: dict) -> AIComplyChat:
    """Crea el chatbot de cumplimiento con el prompt enriquecido con la clasificación."""
    contexto = _formatear_contexto_evaluacion(clasificacion_data)
    prompt = SYSTEM_PROMPT_CUMPLIMIENTO.replace("{contexto_evaluacion}", contexto)

    readme = st.session_state.get("readme_tecnico", "")
    if readme:
        prompt += (
            "\n\nDOCUMENTACIÓN TÉCNICA APORTADA POR EL USUARIO:\n"
            "El usuario ha proporcionado la siguiente documentación técnica de su sistema. "
            "Úsala para identificar medidas ya implementadas ANTES de preguntar. "
            "Si la documentación menciona explícitamente que algo está implementado, "
            "infórmalo al usuario ('Según su documentación, parece que ya tiene cubierto X. ¿Es correcto?') "
            "en lugar de preguntar desde cero. Siempre confirma con el usuario antes de registrar el estado.\n\n"
            f"{readme}"
        )

    return AIComplyChat(provider=provider, system_prompt_override=prompt, max_historial=50)


def _inicializar_estado(provider: LLMProvider) -> None:
    """Inicializa las claves de session_state de la pestaña Cumplimiento."""
    if "mensajes_cumplimiento" not in st.session_state:
        st.session_state.mensajes_cumplimiento = []
    if "cumplimiento_completado" not in st.session_state:
        st.session_state.cumplimiento_completado = False
    if "cumplimiento_data" not in st.session_state:
        st.session_state.cumplimiento_data = {}
    # El chatbot se crea una sola vez con el contexto de clasificación
    if "chatbot_cumplimiento" not in st.session_state or st.session_state.chatbot_cumplimiento is None:
        st.session_state.chatbot_cumplimiento = _inicializar_chatbot_cumplimiento(
            provider, st.session_state.clasificacion_data
        )


def _mostrar_resumen_clasificacion(datos: dict) -> None:
    """Muestra un resumen de la clasificación obtenida en la pestaña anterior."""
    clasificacion = datos.get("clasificacion", "?")
    roles_multiples = datos.get("roles_multiples", [])
    rol = datos.get("rol", "?")
    roles_str = (
        " / ".join(r.capitalize() for r in roles_multiples)
        if len(roles_multiples) > 1
        else rol.capitalize()
    )
    descripcion = datos.get("descripcion_sistema", "")

    col1, col2 = st.columns(2)
    with col1:
        st.metric("Clasificación del sistema", clasificacion)
    with col2:
        st.metric("Rol de la entidad", roles_str)

    if descripcion:
        st.caption(f"Sistema evaluado: {descripcion}")

    estados = datos.get("estados_adicionales", [])
    if estados:
        st.info(f"Estados adicionales: {', '.join(estados)}")

    indeterminados = datos.get("puntos_indeterminados", [])
    if indeterminados:
        with st.expander(f"Puntos indeterminados a revisar con un profesional ({len(indeterminados)})", expanded=False):
            for p in indeterminados:
                st.caption(f"- {p}")


def _mostrar_chat_cumplimiento(chatbot: AIComplyChat) -> None:
    """Renderiza el área de chat de cumplimiento y gestiona el input."""
    chat_container = st.container(height=430)

    with chat_container:
        if not st.session_state.mensajes_cumplimiento:
            clasificacion = st.session_state.clasificacion_data.get("clasificacion", "")
            _roles_m = st.session_state.clasificacion_data.get("roles_multiples", [])
            _rol_single = st.session_state.clasificacion_data.get("rol", "")
            rol_display = (
                " / ".join(r.capitalize() for r in _roles_m)
                if len(_roles_m) > 1
                else _rol_single.capitalize()
            )
            with st.chat_message("assistant"):
                st.markdown(
                    f"Vamos a revisar sus obligaciones concretas según la clasificación obtenida: "
                    f"**{clasificacion}** — Rol: **{rol_display}**.\n\n"
                    "> **Aviso legal:** Esta guía es orientativa y no constituye asesoramiento jurídico. "
                    "Contrástela con un profesional especializado.\n\n"
                    "Le iré presentando cada obligación que aplica a su caso, explicándola en lenguaje claro, "
                    "y le preguntaré si ya la tiene cubierta.\n\n"
                    "¿Empezamos? Cuando esté listo, escríbame 'adelante' o hágame cualquier pregunta."
                )

        for msg in st.session_state.mensajes_cumplimiento:
            with st.chat_message(msg["role"]):
                st.markdown(msg["content"])

    if st.session_state.cumplimiento_completado:
        return

    if prompt := st.chat_input("Escriba su respuesta o pregunta...", max_chars=4000):
        st.session_state.mensajes_cumplimiento.append({"role": "user", "content": prompt})

        with chat_container:
            with st.chat_message("user"):
                st.markdown(prompt)

            with st.chat_message("assistant"):
                placeholder = st.empty()
                texto = ""
                sid = st.session_state.get("session_id", "anon")
                if not rate_limiter.consumir(sid):
                    texto = "_Ha alcanzado el límite de mensajes. Espere un momento antes de continuar._"
                else:
                    try:
                        for fragmento in chatbot.chat_stream(prompt):
                            texto += fragmento
                            placeholder.markdown(texto + "▌")
                    except Exception as exc:
                        texto = f"_{mensaje_error_seguro(exc)}_"
                placeholder.markdown(texto)

        st.session_state.mensajes_cumplimiento.append({"role": "assistant", "content": texto})
        st.rerun()


def _mostrar_formulario_acceso_directo() -> None:
    """Formulario para iniciar el análisis de cumplimiento sin pasar por el evaluador."""
    st.info(
        "**Recomendación:** Para una clasificación de riesgo más precisa y completa, use primero "
        "la pestaña **Evaluador y clasificador**, que sigue el árbol de decisión oficial del "
        "Reglamento (UE) 2024/1689. También puede continuar directamente completando los datos a continuación."
    )
    st.divider()

    descripcion = st.text_area(
        "Descripción del sistema de IA",
        placeholder="¿Qué hace el sistema? ¿En qué sector opera? ¿Cómo toma decisiones que afectan a personas?",
        height=110,
        key="form_acceso_descripcion",
        max_chars=4000,
    )

    nivel_label = st.selectbox(
        "Nivel de riesgo del sistema (según el AI Act)",
        options=list(_NIVELES_OPCIONES.keys()),
        help="Si no está seguro del nivel, use el Evaluador y clasificador para determinarlo automáticamente.",
        key="form_acceso_nivel",
    )

    roles_labels = st.multiselect(
        "Rol de su organización bajo el AI Act",
        options=list(_ROLES_OPCIONES.keys()),
        help="Puede seleccionar varios roles si su organización actúa simultáneamente en más de uno.",
        key="form_acceso_roles",
    )

    nivel_interno = _NIVELES_OPCIONES[nivel_label]
    if nivel_interno == "PROHIBIDO":
        st.error(
            "Ha seleccionado un sistema **prohibido** por el AI Act. "
            "Estos sistemas no pueden desplegarse legalmente en la UE (Art. 5). "
            "Puede continuar el análisis para identificar qué características lo hacen prohibido "
            "y cómo podría rediseñarlo."
        )

    puede_continuar = bool(descripcion.strip() and roles_labels)

    if st.button(
        "Iniciar análisis de cumplimiento",
        type="primary",
        use_container_width=True,
        disabled=not puede_continuar,
    ):
        roles_internos = [_ROLES_OPCIONES[r] for r in roles_labels]
        st.session_state.clasificacion_data = {
            "clasificacion": nivel_interno,
            "rol": roles_internos[0],
            "roles_multiples": roles_internos,
            "descripcion_sistema": descripcion.strip(),
            "sector": "",
            "obligaciones_preliminares": [],
            "puntos_indeterminados": [],
            "estados_adicionales": [],
        }
        st.session_state.acceso_directo_cumplimiento = True
        st.session_state.chatbot_cumplimiento = None  # fuerza reinicialización con nuevos datos
        st.rerun()


def mostrar_tab_cumplimiento(provider: LLMProvider) -> None:
    """Renderiza la pestaña Cumplimiento (Pestaña 2)."""
    st.header("Cumplimiento")

    evaluacion_completada = st.session_state.get("evaluacion_completada", False)
    acceso_directo = st.session_state.get("acceso_directo_cumplimiento", False)

    # ── Sin clasificación previa: mostrar formulario de acceso directo ─────────
    if not evaluacion_completada and not acceso_directo:
        _mostrar_formulario_acceso_directo()
        return

    _inicializar_estado(provider)
    chatbot: AIComplyChat = st.session_state.chatbot_cumplimiento

    st.caption(
        "A continuación revisará sus obligaciones concretas según la clasificación obtenida. "
        "El asistente le guiará por cada obligación y detectará qué ya tiene cubierto "
        "y qué requiere atención."
    )

    # ── Aviso de roles múltiples ───────────────────────────────────────────────
    roles_multiples = st.session_state.clasificacion_data.get("roles_multiples", [])
    if roles_multiples and len(roles_multiples) > 1:
        st.warning(
            f"Su organización actúa en **varios roles** bajo el AI Act: "
            f"**{', '.join(r.capitalize() for r in roles_multiples)}**. "
            "El asistente revisará las obligaciones de cada rol por separado. "
            "En el informe final dispondrá de una sección diferenciada por cada rol."
        )

    # ── Resumen de la clasificación ────────────────────────────────────────────
    _mostrar_resumen_clasificacion(st.session_state.clasificacion_data)
    st.divider()

    # ── Estado completado ──────────────────────────────────────────────────────
    if st.session_state.cumplimiento_completado:
        datos = st.session_state.cumplimiento_data
        carencias = datos.get("carencias_detectadas", [])
        obligaciones = datos.get("obligaciones", [])

        cubierta = sum(1 for o in obligaciones if o.get("estado") == "cubierta")
        parcial = sum(1 for o in obligaciones if o.get("estado") == "parcial")
        n_carencias = sum(1 for o in obligaciones if o.get("estado") == "carencia")
        no_eval = sum(1 for o in obligaciones if o.get("estado") not in ("cubierta", "parcial", "carencia"))

        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Cubiertas", cubierta)
        col2.metric("Parciales", parcial)
        col3.metric("Áreas de mejora", n_carencias)
        col4.metric("Sin evaluar", no_eval)

        if datos.get("resumen_cumplimiento"):
            st.info(datos["resumen_cumplimiento"])

        # ── Trazabilidad de obligaciones ───────────────────────────────────────
        if obligaciones:
            _ESTADO_ESTILO: dict[str, tuple[str, str, str]] = {
                "cubierta":    ("#388E3C", "#E8F5E9", "✓ Cubierta"),
                "parcial":     ("#F9A825", "#FFF8E1", "⚠ Parcial"),
                "carencia":    ("#C62828", "#FFEBEE", "✗ Área de mejora"),
                "no_evaluada": ("#757575", "#F5F5F5", "— Sin evaluar"),
            }
            with st.expander("Trazabilidad de obligaciones", expanded=True):
                for o in obligaciones:
                    estado = o.get("estado", "no_evaluada")
                    color, bg, etiqueta = _ESTADO_ESTILO.get(estado, _ESTADO_ESTILO["no_evaluada"])
                    articulo = html.escape(o.get("articulo", ""))
                    titulo = html.escape(o.get("titulo", ""))
                    descripcion = html.escape(o.get("descripcion", ""))
                    st.markdown(
                        f'<div style="background:{bg}; border-left:4px solid {color}; '
                        f'border-radius:4px; padding:8px 14px; margin-bottom:8px;">'
                        f'<strong>{articulo} — {titulo}</strong> '
                        f'<span style="color:{color}; font-size:0.85em; font-weight:bold;">({etiqueta})</span>'
                        + (f'<br/><span style="font-size:0.9em; color:#555;">{descripcion}</span>'
                           if descripcion else "")
                        + "</div>",
                        unsafe_allow_html=True,
                    )

        if carencias:
            with st.expander(f"Áreas de mejora identificadas ({len(carencias)})", expanded=False):
                for g in carencias:
                    st.caption(f"- {g}")

        st.success("Análisis de cumplimiento completado. Proceda a la pestaña **Informe** para generar el informe.")
        return

    # ── Área de chat ───────────────────────────────────────────────────────────
    _mostrar_chat_cumplimiento(chatbot)

    # ── Botón para finalizar el análisis de cumplimiento ──────────────────────
    if len(st.session_state.mensajes_cumplimiento) >= 4:
        st.divider()
        st.caption(
            "Cuando haya revisado todas sus obligaciones con el asistente, "
            "pulse el botón para extraer los resultados y generar el informe."
        )
        if st.button(
            "Finalizar análisis de cumplimiento y continuar a Informe",
            type="primary",
            use_container_width=True,
        ):
            with st.spinner("Extrayendo el análisis de cumplimiento..."):
                datos = chatbot.extraer_cumplimiento()

            st.session_state.cumplimiento_data = datos
            st.session_state.cumplimiento_completado = True
            st.rerun()

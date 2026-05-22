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
from config import DISCLAIMER_INICIAL, DISCLAIMER_CRITICO, NIVELES_RIESGO, PREGUNTAS_EVALUACION
from src.chatbot import AIComplyChat
from src.risk_classifier import ClasificadorRiesgo
from src.readme_analyzer import AnalizadorReadme
from src.report_generator import GeneradorInforme

st.set_page_config(
    page_title="AIComply — Evaluación AI Act",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Estado de sesión ───────────────────────────────────────────────────────────
if "disclaimer_aceptado" not in st.session_state:
    st.session_state.disclaimer_aceptado = False
if "chatbot" not in st.session_state:
    st.session_state.chatbot = AIComplyChat()
if "mensajes_ui" not in st.session_state:
    st.session_state.mensajes_ui = []
if "analisis_readme" not in st.session_state:
    st.session_state.analisis_readme = None
if "puntuacion" not in st.session_state:
    st.session_state.puntuacion = None
if "informe_md" not in st.session_state:
    st.session_state.informe_md = None
if "resumen_conversacion" not in st.session_state:
    st.session_state.resumen_conversacion = {}


# ── Pantalla de aviso legal inicial ───────────────────────────────────────────
def mostrar_disclaimer():
    st.title("AIComply")
    st.subheader("Evaluación de cumplimiento del AI Act europeo para PYMEs industriales")
    st.markdown(DISCLAIMER_INICIAL)
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button("Acepto las condiciones y quiero continuar", use_container_width=True, type="primary"):
            st.session_state.disclaimer_aceptado = True
            st.rerun()


if not st.session_state.disclaimer_aceptado:
    mostrar_disclaimer()
    st.stop()


# ── Sidebar ────────────────────────────────────────────────────────────────────
with st.sidebar:
    st.title("AIComply")
    st.caption("Evaluación AI Act para PYMEs industriales")
    st.divider()

    nivel = st.session_state.chatbot.nivel_riesgo
    if nivel and nivel in NIVELES_RIESGO:
        st.metric("Nivel de riesgo detectado", nivel)
    else:
        st.info("Nivel de riesgo: pendiente de análisis")

    st.divider()

    if st.button("Nueva evaluación", use_container_width=True):
        st.session_state.chatbot.resetear()
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


# ── Tabs principales ───────────────────────────────────────────────────────────
tab1, tab2, tab3 = st.tabs(["Chatbot de evaluación", "Análisis documental", "Informe de cumplimiento"])


# ════════════════════════════════════════════════════════════════════════════════
# TAB 1 — CHATBOT CONVERSACIONAL
# ════════════════════════════════════════════════════════════════════════════════
with tab1:
    st.header("Evaluación conversacional")
    st.caption(
        "Describe tu sistema de IA y te ayudaré a determinar tu nivel de cumplimiento con el AI Act. "
        "Cada concepto técnico incluye su definición oficial con referencia al artículo correspondiente."
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
                    for fragmento in st.session_state.chatbot.chat_stream(prompt):
                        texto_completo += fragmento
                        respuesta_placeholder.markdown(texto_completo + "▌")

                respuesta_placeholder.markdown(texto_completo)

        st.session_state.mensajes_ui.append({"role": "assistant", "content": texto_completo})

        nivel_detectado = st.session_state.chatbot.nivel_riesgo
        if nivel_detectado and nivel_detectado in ("PROHIBIDO", "ALTO"):
            st.warning(DISCLAIMER_CRITICO)

        st.rerun()

    col_a, col_b = st.columns(2)
    with col_a:
        if st.button("Clasificación rápida por descripción"):
            st.session_state["mostrar_clasificador"] = True
    with col_b:
        if st.button("Generar resumen de la conversación") and len(st.session_state.mensajes_ui) >= 2:
            with st.spinner("Generando resumen estructurado..."):
                resumen_texto = st.session_state.chatbot.generar_resumen_conversacion()
                try:
                    st.session_state.resumen_conversacion = json.loads(resumen_texto)
                    st.success("Resumen generado. Vaya a la pestaña Informe de cumplimiento para exportarlo.")
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
                clasificador = ClasificadorRiesgo()
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


# ════════════════════════════════════════════════════════════════════════════════
# TAB 2 — ANÁLISIS DOCUMENTAL
# ════════════════════════════════════════════════════════════════════════════════
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
        nivel_previo = st.session_state.chatbot.nivel_riesgo
        if nivel_previo:
            st.info(
                f"Se analizará considerando el nivel de riesgo identificado en el chat: **{nivel_previo}**"
            )

        if st.button("Analizar documentación", type="primary", use_container_width=True):
            with st.spinner("Analizando contra los requisitos del AI Act..."):
                analizador = AnalizadorReadme()
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

        nivel_r = analisis.get("nivel_riesgo", "DESCONOCIDO")

        col_nivel, col_score = st.columns(2)
        with col_nivel:
            st.metric("Nivel de riesgo detectado", nivel_r)
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

                with st.expander(
                    f"[{etiqueta}] {gap.get('articulo', '')} — {gap.get('titulo', '')}"
                ):
                    st.markdown(f"**Estado:** :{color}[{etiqueta}]")
                    st.markdown(f"**Situación:** {gap.get('descripcion', '')}")
                    if estado != "cumple" and gap.get("recomendacion"):
                        st.warning(f"**Recomendación:** {gap.get('recomendacion', '')}")

        st.info("Vaya a la pestaña **Informe de cumplimiento** para generar y exportar el informe completo.")


# ════════════════════════════════════════════════════════════════════════════════
# TAB 3 — INFORME DE CUMPLIMIENTO
# ════════════════════════════════════════════════════════════════════════════════
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

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

from datetime import date

import streamlit as st

from src.report_generator import GeneradorInforme

_FECHA_HOY = date.today().strftime("%Y-%m-%d")

_CLASIFICACIONES_SOLO_EVAL = frozenset({
    "EXCLUIDO",
    "NO CUMPLE LA DEFINICIÓN DE SISTEMA DE IA",
    "NO ES SISTEMA DE IA",
    "NO_IA",
    "FUERA DE ALCANCE",
    "FUERA_DE_ALCANCE",
})

_TITULOS_INFORME = {
    "clasificacion": "Informe de clasificación",
    "cumplimiento": "Informe de cumplimiento",
    "completo": "Informe completo",
}


def _nombre_fichero(tipo: str, extension: str) -> str:
    slugs = {
        "clasificacion": "clasificacion",
        "cumplimiento": "cumplimiento",
        "completo": "completo",
    }
    return f"aicomply_informe_{slugs.get(tipo, tipo)}_{_FECHA_HOY}.{extension}"


def _botones_descarga(informe_md: str, tipo: str) -> None:
    """Muestra los botones de descarga en PDF y texto plano para un informe."""
    col_pdf, col_txt = st.columns(2)

    with col_pdf:
        try:
            generador = GeneradorInforme()
            clasificacion_data = st.session_state.get("clasificacion_data")
            pdf_bytes = generador.exportar_pdf(
                informe_md,
                titulo=f"AIComply — {_TITULOS_INFORME.get(tipo, 'Informe')}",
                clasificacion_data=clasificacion_data,
            )
            st.download_button(
                label="Descargar en PDF",
                data=pdf_bytes,
                file_name=_nombre_fichero(tipo, "pdf"),
                mime="application/pdf",
                use_container_width=True,
            )
        except Exception as _pdf_exc:
            st.error(f"Error al generar PDF: {_pdf_exc}")

    with col_txt:
        generador = GeneradorInforme()
        txt = generador.exportar_texto_plano(informe_md)
        st.download_button(
            label="Descargar en texto plano",
            data=txt.encode("utf-8"),
            file_name=_nombre_fichero(tipo, "txt"),
            mime="text/plain",
            use_container_width=True,
        )


def _seccion_informe_clasificacion(eval_ok: bool) -> None:
    """Sección del informe de clasificación (se desbloquea con Pestaña 1)."""
    st.subheader("Informe de clasificación")
    st.caption("Incluye: clasificación del sistema, rol de la entidad y puntos que requieren revisión profesional.")

    if not eval_ok:
        st.info(
            "Este informe se desbloqueará cuando complete la evaluación en la pestaña "
            "**Evaluador y clasificador**, o cuando inicie el cumplimiento directamente "
            "desde la pestaña **Cumplimiento** con una clasificación manual."
        )
        return

    clave_md = "informe_md_clasificacion"
    if clave_md not in st.session_state:
        st.session_state[clave_md] = None

    if st.button(
        "Generar informe de clasificación", type="primary", use_container_width=True,
        key="btn_gen_clasificacion",
    ):
        with st.spinner("Generando informe..."):
            generador = GeneradorInforme()
            md = generador.generar_informe_clasificacion(st.session_state.clasificacion_data)
            st.session_state[clave_md] = md

    if st.session_state[clave_md]:
        st.divider()
        st.markdown(st.session_state[clave_md])
        st.divider()
        _botones_descarga(st.session_state[clave_md], "clasificacion")


def _seccion_informe_cumplimiento(cumpl_ok: bool, es_caso_especial: bool) -> None:
    """Sección del informe de cumplimiento (se desbloquea con Pestaña 2)."""
    st.subheader("Informe de cumplimiento")
    st.caption("Incluye: obligaciones por artículo, áreas de mejora y recomendaciones de acción.")

    if es_caso_especial:
        st.info(
            "El sistema evaluado no cumple la definición de sistema de IA conforme al Art. 3.1 del AI Act. "
            "No procede generar informe de cumplimiento. "
            "Consulte el **Informe de clasificación** para documentar esta conclusión."
        )
        return

    if not cumpl_ok:
        pasos_faltantes = []
        tiene_clasificacion = (
            st.session_state.get("evaluacion_completada", False)
            or st.session_state.get("acceso_directo_cumplimiento", False)
        )
        if not tiene_clasificacion:
            pasos_faltantes.append("la clasificación del sistema (Pestaña 1 o formulario de Pestaña 2)")
        pasos_faltantes.append("el análisis de cumplimiento (Pestaña 2)")
        st.info(
            f"Este informe se desbloqueará cuando complete: {' y '.join(pasos_faltantes)}."
        )
        return

    clave_md = "informe_md_cumplimiento"
    if clave_md not in st.session_state:
        st.session_state[clave_md] = None

    if st.button(
        "Generar informe de cumplimiento", type="primary", use_container_width=True,
        key="btn_gen_cumplimiento",
    ):
        with st.spinner("Generando informe..."):
            generador = GeneradorInforme()
            md = generador.generar_informe_cumplimiento(
                st.session_state.clasificacion_data,
                st.session_state.cumplimiento_data,
            )
            st.session_state[clave_md] = md

    if st.session_state[clave_md]:
        st.divider()
        st.markdown(st.session_state[clave_md])
        st.divider()
        _botones_descarga(st.session_state[clave_md], "cumplimiento")


def _seccion_informe_completo(eval_ok: bool, cumpl_ok: bool, es_caso_especial: bool) -> None:
    """Sección del informe completo (se desbloquea con Pestañas 1 y 2)."""
    st.subheader("Informe completo")
    st.caption("Incluye clasificación, obligaciones, áreas de mejora, recomendaciones y puntos de revisión.")

    if es_caso_especial:
        st.info(
            "El sistema evaluado no cumple la definición de sistema de IA conforme al Art. 3.1 del AI Act. "
            "No procede generar informe completo. "
            "Use el **Informe de clasificación** para obtener el informe completo de su caso."
        )
        return

    if not (eval_ok and cumpl_ok):
        faltantes = []
        if not eval_ok:
            faltantes.append("la clasificación del sistema (Pestaña 1 o formulario de Pestaña 2)")
        if not cumpl_ok:
            faltantes.append("el análisis de cumplimiento (Pestaña 2)")
        st.info(
            f"Este informe se desbloqueará cuando complete: {' y '.join(faltantes)}."
        )
        return

    clave_md = "informe_md_completo"
    if clave_md not in st.session_state:
        st.session_state[clave_md] = None

    if st.button(
        "Generar informe completo", type="primary", use_container_width=True,
        key="btn_gen_completo",
    ):
        with st.spinner("Generando informe completo..."):
            generador = GeneradorInforme()
            md = generador.generar_informe_completo(
                st.session_state.clasificacion_data,
                st.session_state.cumplimiento_data,
            )
            st.session_state[clave_md] = md

    if st.session_state[clave_md]:
        st.divider()
        st.markdown(st.session_state[clave_md])
        st.divider()
        _botones_descarga(st.session_state[clave_md], "completo")


def mostrar_tab_informe() -> None:
    """Renderiza la pestaña Informe (Pestaña 3) con tres tipos de informe."""
    st.header("Informe")

    st.warning(
        "**Aviso legal:** Este informe es orientativo y no constituye asesoramiento jurídico "
        "vinculante. Contrástelo con un profesional especializado antes de tomar decisiones "
        "de cumplimiento normativo."
    )

    # El acceso directo al cumplimiento también cuenta como clasificación válida
    eval_ok = (
        st.session_state.get("evaluacion_completada", False)
        or st.session_state.get("acceso_directo_cumplimiento", False)
    )
    cumpl_ok = st.session_state.get("cumplimiento_completado", False)

    # Para EXCLUIDO / NO_IA el flujo termina en evaluación; PROHIBIDO sí pasa a cumplimiento
    clasificacion_actual = (st.session_state.get("clasificacion_data") or {}).get("clasificacion", "").upper()
    es_caso_especial = eval_ok and clasificacion_actual in _CLASIFICACIONES_SOLO_EVAL

    # Indicadores de progreso
    col1, col2, col3 = st.columns(3)
    col1.metric("Evaluación", "Completada" if eval_ok else "Pendiente")
    col2.metric("Cumplimiento", "No aplica" if es_caso_especial else ("Completado" if cumpl_ok else "Pendiente"))
    col3.metric("Informe completo", "No aplica" if es_caso_especial else ("Disponible" if (eval_ok and cumpl_ok) else "Pendiente"))

    st.divider()

    # Para casos especiales, el informe de clasificación es el único relevante y se abre automáticamente
    with st.expander("Informe de clasificación", expanded=eval_ok and (es_caso_especial or not cumpl_ok)):
        _seccion_informe_clasificacion(eval_ok)

    with st.expander("Informe de cumplimiento", expanded=cumpl_ok and not st.session_state.get("informe_md_completo")):
        _seccion_informe_cumplimiento(cumpl_ok, es_caso_especial)

    with st.expander("Informe completo", expanded=(eval_ok and cumpl_ok)):
        _seccion_informe_completo(eval_ok, cumpl_ok, es_caso_especial)

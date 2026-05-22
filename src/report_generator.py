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

from datetime import datetime

from config import DISCLAIMER_CRITICO, NIVELES_RIESGO


class GeneradorInforme:
    """
    Genera informes de cumplimiento del AI Act en Markdown y PDF.
    No requiere llamadas al LLM: el informe se construye a partir
    de los datos ya analizados por el chatbot y el analizador documental.
    """

    def generar_markdown(
        self,
        resumen_conversacion: dict,
        analisis_readme: dict | None = None,
        puntuacion: dict | None = None,
    ) -> str:
        """Genera el informe completo en formato Markdown."""
        nivel = resumen_conversacion.get("nivel_riesgo", "DESCONOCIDO")
        info_nivel = NIVELES_RIESGO.get(nivel, {})
        fecha = datetime.now().strftime("%d/%m/%Y")

        secciones = [
            self._seccion_cabecera(resumen_conversacion, nivel, fecha),
            self._seccion_aviso_legal(),
            self._seccion_resumen_ejecutivo(resumen_conversacion, analisis_readme),
            self._seccion_clasificacion_riesgo(resumen_conversacion, info_nivel),
            self._seccion_obligaciones(resumen_conversacion, nivel),
        ]

        if analisis_readme:
            secciones.append(self._seccion_analisis_readme(analisis_readme, puntuacion))

        secciones.append(self._seccion_plan_accion(nivel, analisis_readme))
        secciones.append(self._seccion_pie())

        return "\n\n".join(secciones)

    def _seccion_cabecera(self, resumen: dict, nivel: str, fecha: str) -> str:
        nombre = resumen.get("nombre_sistema", "Sistema de IA")
        sector = resumen.get("sector", "No especificado")
        return (
            f"# Informe de Cumplimiento AI Act\n\n"
            f"**Sistema:** {nombre}  \n"
            f"**Sector:** {sector}  \n"
            f"**Nivel de riesgo:** {nivel}  \n"
            f"**Fecha:** {fecha}  \n"
            f"**Generado por:** AIComply — Herramienta de evaluación del AI Act europeo  \n"
            f"**Reglamento de referencia:** Reglamento (UE) 2024/1689"
        )

    def _seccion_aviso_legal(self) -> str:
        return (
            "---\n\n"
            "> **AVISO LEGAL:** AIComply es una herramienta auxiliar de orientación. "
            "Los resultados de este informe no constituyen asesoramiento legal. "
            "Se recomienda consultar con especialistas antes de tomar decisiones de cumplimiento normativo.\n\n"
            "---"
        )

    def _seccion_resumen_ejecutivo(self, resumen: dict, analisis: dict | None) -> str:
        proposito = resumen.get("proposito", "No especificado")
        caracteristicas = resumen.get("caracteristicas_clave", [])

        texto = f"## Resumen Ejecutivo\n\n**Propósito del sistema:** {proposito}"

        if caracteristicas:
            texto += "\n\n**Características clave:**"
            for c in caracteristicas:
                texto += f"\n- {c}"

        if analisis and analisis.get("resumen"):
            texto += f"\n\n**Evaluación general:** {analisis['resumen']}"

        return texto

    def _seccion_clasificacion_riesgo(self, resumen: dict, info_nivel: dict) -> str:
        nivel = resumen.get("nivel_riesgo", "DESCONOCIDO")
        articulos = resumen.get("articulos_aplicables", [])
        descripcion = info_nivel.get("descripcion", "")

        texto = f"## Clasificación de Riesgo: {nivel}\n\n**Descripción:** {descripcion}"

        if articulos:
            texto += "\n\n**Artículos aplicables:**"
            for art in articulos:
                texto += f"\n- {art}"

        return texto

    def _seccion_obligaciones(self, resumen: dict, nivel: str) -> str:
        obligaciones = resumen.get("obligaciones_identificadas", [])

        OBLIGACIONES_POR_NIVEL = {
            "PROHIBIDO": [
                "El sistema NO puede desarrollarse ni desplegarse (Art. 5 AI Act)",
                "Retirar del mercado inmediatamente si ya está desplegado",
                "Sanciones de hasta 35.000.000 EUR o el 7% de la facturación global anual",
                "Consultar con asesor legal especializado urgentemente",
            ],
            "ALTO": [
                "Sistema de gestión de riesgos documentado (Art. 9)",
                "Gobernanza de datos de entrenamiento, validación y prueba (Art. 10)",
                "Documentación técnica completa (Art. 11)",
                "Registro automático de actividad y trazabilidad (Art. 12)",
                "Transparencia e instrucciones de uso para el responsable del despliegue (Art. 13)",
                "Supervisión humana efectiva con capacidad de intervención (Art. 14)",
                "Exactitud, solidez y ciberseguridad declaradas (Art. 15)",
                "Evaluación de conformidad antes de la comercialización",
                "Registro en la base de datos de la UE antes del despliegue (Art. 71)",
            ],
            "LIMITADO": [
                "Informar al usuario que interactúa con un sistema de IA (Art. 52)",
                "Marcar el contenido generado artificialmente (texto, imagen, audio, video)",
                "Informar sobre el uso de reconocimiento de emociones si aplica",
                "Informar sobre la categorización biométrica si aplica",
            ],
            "MINIMO": [
                "No hay obligaciones específicas del AI Act",
                "Se recomienda seguir buenas prácticas voluntarias",
                "Considerar adhesión a códigos de conducta voluntarios (Art. 69)",
                "Monitorizar cambios en el uso que puedan elevar el nivel de riesgo",
            ],
        }

        lista = obligaciones if obligaciones else OBLIGACIONES_POR_NIVEL.get(nivel, [])

        texto = "## Obligaciones Regulatorias\n"
        for ob in lista:
            texto += f"\n- {ob}"

        return texto

    def _seccion_analisis_readme(self, analisis: dict, puntuacion: dict | None) -> str:
        gaps = analisis.get("gaps", [])
        fortalezas = analisis.get("fortalezas", [])

        texto = "## Análisis Documental"

        if puntuacion:
            pct = puntuacion.get("porcentaje", 0)
            texto += (
                f"\n\n**Puntuación de cumplimiento:** {pct}%  \n"
                f"Cumple: {puntuacion.get('cumple', 0)} | "
                f"Parcial: {puntuacion.get('parcial', 0)} | "
                f"Gap: {puntuacion.get('gap', 0)}"
            )

        if fortalezas:
            texto += "\n\n### Fortalezas identificadas"
            for f in fortalezas:
                texto += f"\n- {f}"

        if gaps:
            texto += "\n\n### Análisis por artículo\n"
            for gap in gaps:
                estado = gap.get("estado", "gap")
                etiqueta = estado.upper()
                texto += f"\n#### [{etiqueta}] {gap.get('articulo', '')} — {gap.get('titulo', '')}\n"
                texto += f"**Estado:** {etiqueta}  \n"
                texto += f"**Situación:** {gap.get('descripcion', '')}  \n"
                if estado != "cumple" and gap.get("recomendacion"):
                    texto += f"**Recomendación:** {gap.get('recomendacion', '')}  \n"

        return texto

    def _seccion_plan_accion(self, nivel: str, analisis: dict | None) -> str:
        texto = "## Plan de Acción Recomendado\n"

        if nivel == "PROHIBIDO":
            texto += (
                "\n**Este sistema está prohibido por el AI Act.**  \n"
                "Debe detenerse el desarrollo y despliegue inmediatamente. "
                "Consulte con un asesor legal especializado."
            )
            return texto

        if nivel == "ALTO":
            pasos = [
                "**Inmediato (0-3 meses):** Designar un responsable de cumplimiento AI Act",
                "**Corto plazo (3-6 meses):** Desarrollar documentación técnica (Art. 11) y sistema de gestión de riesgos (Art. 9)",
                "**Medio plazo (6-9 meses):** Implementar registro de actividad (Art. 12) y protocolo de supervisión humana (Art. 14)",
                "**Antes del despliegue:** Completar evaluación de conformidad y registrar en la base de datos de la UE (Art. 71)",
                "**Continuo:** Supervisión poscomercialización y actualización de la documentación técnica",
            ]
        elif nivel == "LIMITADO":
            pasos = [
                "**Inmediato:** Añadir aviso claro de que el sistema usa IA en la interfaz de usuario (Art. 52)",
                "**Corto plazo:** Implementar marcado de contenido generado por IA si aplica",
                "**Recomendado:** Revisar anualmente las actualizaciones del AI Act",
            ]
        else:
            pasos = [
                "**Recomendado:** Documentar internamente las capacidades y limitaciones del sistema",
                "**Opcional:** Considerar adhesión a códigos de conducta voluntarios (Art. 69)",
                "**Vigilancia:** Monitorizar cambios en el uso que puedan elevar el nivel de riesgo",
            ]

        if analisis:
            gaps_pendientes = [g for g in analisis.get("gaps", []) if g.get("estado") == "gap"]
            if gaps_pendientes:
                pasos.append(
                    f"**Gaps críticos a resolver:** {len(gaps_pendientes)} gap(s) identificados en el análisis documental"
                )

        for paso in pasos:
            texto += f"\n- {paso}"

        return texto

    def _seccion_pie(self) -> str:
        return (
            "---\n\n"
            f"*Informe generado por AIComply el {datetime.now().strftime('%d/%m/%Y a las %H:%M')}.*  \n"
            "*Esta herramienta utiliza inteligencia artificial para el análisis y puede contener imprecisiones. "
            "No constituye asesoramiento legal. Reglamento de referencia: Reglamento (UE) 2024/1689.*"
        )

    def exportar_pdf(self, contenido_markdown: str) -> bytes:
        """Convierte el informe Markdown a PDF usando fpdf2 si está disponible."""
        try:
            from fpdf import FPDF

            pdf = FPDF()
            pdf.set_auto_page_break(auto=True, margin=15)
            pdf.add_page()
            pdf.set_font("Helvetica", size=10)

            for linea in contenido_markdown.split("\n"):
                linea_limpia = linea.strip()
                if not linea_limpia:
                    pdf.ln(3)
                elif linea_limpia.startswith("# "):
                    pdf.set_font("Helvetica", "B", 16)
                    pdf.multi_cell(0, 8, linea_limpia[2:].encode("latin-1", "replace").decode("latin-1"))
                    pdf.set_font("Helvetica", size=10)
                    pdf.ln(2)
                elif linea_limpia.startswith("## "):
                    pdf.set_font("Helvetica", "B", 13)
                    pdf.multi_cell(0, 7, linea_limpia[3:].encode("latin-1", "replace").decode("latin-1"))
                    pdf.set_font("Helvetica", size=10)
                    pdf.ln(1)
                elif linea_limpia.startswith("### "):
                    pdf.set_font("Helvetica", "B", 11)
                    pdf.multi_cell(0, 6, linea_limpia[4:].encode("latin-1", "replace").decode("latin-1"))
                    pdf.set_font("Helvetica", size=10)
                elif linea_limpia.startswith("#### "):
                    pdf.set_font("Helvetica", "BI", 10)
                    pdf.multi_cell(0, 6, linea_limpia[5:].encode("latin-1", "replace").decode("latin-1"))
                    pdf.set_font("Helvetica", size=10)
                elif linea_limpia.startswith(("- ", "* ")):
                    pdf.multi_cell(0, 5, ("  - " + linea_limpia[2:]).encode("latin-1", "replace").decode("latin-1"))
                elif linea_limpia.startswith("---"):
                    pdf.line(pdf.get_x(), pdf.get_y(), pdf.get_x() + 190, pdf.get_y())
                    pdf.ln(2)
                else:
                    pdf.multi_cell(0, 5, linea_limpia.encode("latin-1", "replace").decode("latin-1"))

            return bytes(pdf.output())
        except ImportError:
            return b""

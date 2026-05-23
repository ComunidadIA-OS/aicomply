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

import re
from datetime import datetime

from config import NIVELES_RIESGO

_AVISO_LEGAL_MD = (
    "---\n\n"
    "> **AVISO LEGAL:** Este informe es una herramienta auxiliar de orientación. "
    "Los resultados no constituyen asesoramiento jurídico vinculante. "
    "Se recomienda consultar con especialistas antes de tomar decisiones de cumplimiento normativo.\n\n"
    "---"
)

_TEXTO_PIE = (
    "Generado por AIComply — Herramienta auxiliar de orientación. "
    "No constituye asesoramiento jurídico. "
    "Reglamento de referencia: Reglamento (UE) 2024/1689."
)


def _fecha_larga() -> str:
    return datetime.now().strftime("%d/%m/%Y a las %H:%M")


class GeneradorInforme:
    """
    Genera informes de cumplimiento del AI Act en Markdown, texto plano y PDF.
    No realiza llamadas al LLM: construye el informe a partir de los datos
    ya recopilados por el evaluador y el análisis de cumplimiento.
    """

    # ══════════════════════════════════════════════════════════════════════════
    # INFORME DE CLASIFICACIÓN (Pestaña 1)
    # ══════════════════════════════════════════════════════════════════════════

    def generar_informe_clasificacion(self, clasificacion_data: dict) -> str:
        """Informe de clasificación: sistema, rol, obligaciones preliminares, revisión profesional."""
        clasificacion = clasificacion_data.get("clasificacion", "DESCONOCIDO")
        rol = clasificacion_data.get("rol", "No especificado")
        roles_multiples = clasificacion_data.get("roles_multiples", [])
        descripcion = clasificacion_data.get("descripcion_sistema", "No especificada")
        sector = clasificacion_data.get("sector", "No especificado")
        estados = clasificacion_data.get("estados_adicionales", [])
        obligaciones_prev = clasificacion_data.get("obligaciones_preliminares", [])
        indeterminados = clasificacion_data.get("puntos_indeterminados", [])
        info_nivel = NIVELES_RIESGO.get(clasificacion, {})

        secciones = [
            self._cabecera("Informe de clasificación", descripcion, sector, clasificacion, rol),
            _AVISO_LEGAL_MD,
            self._resumen_ejecutivo_clasificacion(descripcion, clasificacion, rol, roles_multiples, estados),
            self._seccion_clasificacion(2, clasificacion, rol, roles_multiples, estados, info_nivel),
            self._seccion_obligaciones_preliminares(3, obligaciones_prev, clasificacion),
            self._seccion_revision_profesional(4, indeterminados),
            self._pie(),
        ]
        return "\n\n".join(secciones)

    # ══════════════════════════════════════════════════════════════════════════
    # INFORME DE CUMPLIMIENTO (Pestañas 1 + 2)
    # ══════════════════════════════════════════════════════════════════════════

    def generar_informe_cumplimiento(
        self, clasificacion_data: dict, cumplimiento_data: dict
    ) -> str:
        """Informe de cumplimiento: obligaciones por artículo, áreas de mejora y plan de acción."""
        clasificacion = clasificacion_data.get("clasificacion", "DESCONOCIDO")
        rol = clasificacion_data.get("rol", "No especificado")
        roles_multiples = clasificacion_data.get("roles_multiples", [])
        descripcion = clasificacion_data.get("descripcion_sistema", "No especificada")
        sector = clasificacion_data.get("sector", "No especificado")
        indeterminados = clasificacion_data.get("puntos_indeterminados", [])

        obligaciones = cumplimiento_data.get("obligaciones", [])
        carencias = cumplimiento_data.get("carencias_detectadas", cumplimiento_data.get("gaps_detectados", []))
        puntos_revision = cumplimiento_data.get("puntos_revision_profesional", [])
        resumen = cumplimiento_data.get("resumen_cumplimiento", "")

        secciones = [
            self._cabecera("Informe de cumplimiento", descripcion, sector, clasificacion, rol),
            _AVISO_LEGAL_MD,
            self._resumen_ejecutivo_cumplimiento(resumen, clasificacion, rol),
            self._seccion_obligaciones_detalladas(2, obligaciones, roles_multiples),
            self._seccion_carencias(3, carencias),
            self._seccion_plan_accion(4, clasificacion, carencias),
            self._seccion_revision_profesional(5, indeterminados + puntos_revision),
            self._pie(),
        ]
        return "\n\n".join(secciones)

    # ══════════════════════════════════════════════════════════════════════════
    # INFORME COMPLETO (Pestañas 1 + 2)
    # ══════════════════════════════════════════════════════════════════════════

    def generar_informe_completo(
        self, clasificacion_data: dict, cumplimiento_data: dict
    ) -> str:
        """Informe completo: clasificación + cumplimiento combinados. Sin traza interna visible."""
        clasificacion = clasificacion_data.get("clasificacion", "DESCONOCIDO")
        rol = clasificacion_data.get("rol", "No especificado")
        roles_multiples = clasificacion_data.get("roles_multiples", [])
        descripcion = clasificacion_data.get("descripcion_sistema", "No especificada")
        sector = clasificacion_data.get("sector", "No especificado")
        estados = clasificacion_data.get("estados_adicionales", [])
        obligaciones_prev = clasificacion_data.get("obligaciones_preliminares", [])
        indeterminados = clasificacion_data.get("puntos_indeterminados", [])
        info_nivel = NIVELES_RIESGO.get(clasificacion, {})

        obligaciones = cumplimiento_data.get("obligaciones", [])
        carencias = cumplimiento_data.get("carencias_detectadas", cumplimiento_data.get("gaps_detectados", []))
        puntos_revision = cumplimiento_data.get("puntos_revision_profesional", [])
        resumen_cumpl = cumplimiento_data.get("resumen_cumplimiento", "")

        secciones = [
            self._cabecera("Informe completo", descripcion, sector, clasificacion, rol),
            _AVISO_LEGAL_MD,
            self._resumen_ejecutivo_completo(descripcion, clasificacion, rol, roles_multiples, estados, resumen_cumpl),
            self._seccion_clasificacion(2, clasificacion, rol, roles_multiples, estados, info_nivel),
            self._seccion_obligaciones_preliminares(3, obligaciones_prev, clasificacion),
            self._seccion_obligaciones_detalladas(4, obligaciones, roles_multiples),
            self._seccion_carencias(5, carencias),
            self._seccion_plan_accion(6, clasificacion, carencias),
            self._seccion_revision_profesional(7, indeterminados + puntos_revision),
            self._pie(),
        ]
        return "\n\n".join(secciones)

    # ══════════════════════════════════════════════════════════════════════════
    # SECCIONES REUTILIZABLES
    # ══════════════════════════════════════════════════════════════════════════

    def _cabecera(
        self,
        tipo_informe: str,
        descripcion: str,
        sector: str,
        clasificacion: str,
        rol: str,
    ) -> str:
        fecha = _fecha_larga()
        return (
            f"# AIComply — {tipo_informe}\n\n"
            f"**Sistema evaluado:** {descripcion}  \n"
            f"**Sector:** {sector}  \n"
            f"**Clasificación:** {clasificacion}  \n"
            f"**Rol de la entidad:** {rol.capitalize()}  \n"
            f"**Fecha:** {fecha}  \n"
            "**Reglamento de referencia:** Reglamento (UE) 2024/1689"
        )

    def _resumen_ejecutivo_clasificacion(
        self,
        descripcion: str,
        clasificacion: str,
        rol: str,
        roles_multiples: list[str],
        estados: list[str],
    ) -> str:
        texto = f"## 1. Resumen ejecutivo\n\n"
        texto += (
            f"El sistema evaluado ha sido clasificado como **{clasificacion}** "
            f"según el Reglamento (UE) 2024/1689 (AI Act europeo). "
            f"La entidad actúa como **{rol}**."
        )
        if roles_multiples and len(roles_multiples) > 1:
            texto += (
                f" Se han identificado además los siguientes roles adicionales: "
                f"**{', '.join(r.capitalize() for r in roles_multiples)}**."
            )
        if estados:
            texto += f" Estados adicionales aplicables: {', '.join(estados)}."
        return texto

    def _resumen_ejecutivo_cumplimiento(
        self, resumen: str, clasificacion: str, rol: str
    ) -> str:
        texto = f"## 1. Resumen ejecutivo\n\n"
        texto += (
            f"Este informe recoge el análisis de cumplimiento de un sistema clasificado como "
            f"**{clasificacion}** con rol **{rol}**."
        )
        if resumen:
            texto += f"\n\n{resumen}"
        return texto

    def _resumen_ejecutivo_completo(
        self,
        descripcion: str,
        clasificacion: str,
        rol: str,
        roles_multiples: list[str],
        estados: list[str],
        resumen_cumpl: str,
    ) -> str:
        texto = f"## 1. Resumen ejecutivo\n\n"
        texto += (
            f"El sistema evaluado ha sido clasificado como **{clasificacion}** "
            f"según el AI Act europeo. La entidad actúa como **{rol}**."
        )
        if roles_multiples and len(roles_multiples) > 1:
            texto += f" Roles adicionales identificados: {', '.join(r.capitalize() for r in roles_multiples)}."
        if estados:
            texto += f" Estados adicionales: {', '.join(estados)}."
        if resumen_cumpl:
            texto += f"\n\n{resumen_cumpl}"
        return texto

    def _seccion_clasificacion(
        self,
        num: int,
        clasificacion: str,
        rol: str,
        roles_multiples: list[str],
        estados: list[str],
        info_nivel: dict,
    ) -> str:
        descripcion_nivel = info_nivel.get("descripcion", "")
        texto = f"## {num}. Clasificación del sistema\n\n"
        texto += f"**Nivel de riesgo:** {clasificacion}"
        if descripcion_nivel:
            texto += f"  \n**Descripción:** {descripcion_nivel}"

        texto += f"\n\n**Rol principal de la entidad:** {rol.capitalize()}"

        if roles_multiples and len(roles_multiples) > 1:
            texto += "\n\n**Roles adicionales identificados:**"
            for r in roles_multiples:
                texto += f"\n- {r.capitalize()}"
            texto += (
                "\n\nSu organización actúa en varios roles bajo el AI Act. "
                "Las obligaciones de cada rol se detallan en la sección correspondiente."
            )

        if estados:
            texto += "\n\n**Estados adicionales aplicables:**"
            for estado in estados:
                texto += f"\n- {estado}"

        return texto

    def _seccion_obligaciones_preliminares(
        self, num: int, obligaciones: list[str], clasificacion: str
    ) -> str:
        texto = f"## {num}. Obligaciones identificadas durante la evaluación\n"

        _OBLIGACIONES_POR_NIVEL = {
            "PROHIBIDO": [
                "El sistema NO puede desarrollarse ni desplegarse (Art. 5)",
                "Acción inmediata: detener el proyecto o rediseñar el sistema",
                "Posibles sanciones de hasta 35.000.000 EUR o el 7 % de la facturación global",
                "Consulte urgentemente con un asesor legal especializado",
            ],
            "ALTO": [
                "Sistema de gestión de riesgos documentado (Art. 9)",
                "Gobernanza de datos de entrenamiento, validación y prueba (Art. 10)",
                "Documentación técnica completa según el Anexo IV (Art. 11)",
                "Registro automático de actividad (Art. 12)",
                "Instrucciones de uso para el implementador (Art. 13)",
                "Supervisión humana efectiva (Art. 14)",
                "Exactitud, solidez y ciberseguridad declaradas (Art. 15)",
                "Evaluación de conformidad antes de la comercialización (Art. 43)",
                "Registro en la base de datos de la UE (Art. 49)",
            ],
            "LIMITADO": [
                "Informar al usuario que interactúa con un sistema de IA (Art. 50.1)",
                "Marcar el contenido generado sintéticamente (Art. 50.2)",
                "Informar sobre reconocimiento de emociones si aplica (Art. 50.3)",
            ],
            "MINIMO": [
                "No hay obligaciones específicas del AI Act vigentes",
                "Se recomiendan buenas prácticas voluntarias",
                "Posible adhesión a códigos de conducta voluntarios (Art. 95)",
            ],
        }

        lista = obligaciones if obligaciones else _OBLIGACIONES_POR_NIVEL.get(clasificacion, [])
        for ob in lista:
            texto += f"\n- {ob}"
        return texto

    def _seccion_obligaciones_detalladas(
        self, num: int, obligaciones: list[dict], roles_multiples: list[str]
    ) -> str:
        if not obligaciones:
            return (
                f"## {num}. Análisis de obligaciones\n\n"
                "No se dispone del detalle de obligaciones. Consulte el análisis en la pestaña Cumplimiento."
            )

        cubiertas = [o for o in obligaciones if o.get("estado") == "cubierta"]
        parciales = [o for o in obligaciones if o.get("estado") == "parcial"]
        carencias_obl = [o for o in obligaciones if o.get("estado") == "carencia"]
        no_eval = [o for o in obligaciones if o.get("estado") not in ("cubierta", "parcial", "carencia")]

        total = len(obligaciones)
        pct = round(
            ((len(cubiertas) * 2 + len(parciales)) / (total * 2) * 100) if total else 0
        )

        texto = f"## {num}. Análisis de obligaciones\n\n"
        texto += (
            f"**Grado de cumplimiento estimado:** {pct} %  \n"
            f"Cubiertas: {len(cubiertas)} | Parciales: {len(parciales)} | "
            f"Áreas de mejora: {len(carencias_obl)} | Sin evaluar: {len(no_eval)}"
        )

        # Si hay roles múltiples, agrupar por rol si la información lo permite
        if roles_multiples and len(roles_multiples) > 1:
            texto += (
                "\n\n*Las obligaciones se presentan agrupadas. "
                "El rol específico de cada una se indica en la descripción.*"
            )

        def _bloque(lista: list[dict], encabezado: str) -> str:
            if not lista:
                return ""
            bloque = f"\n\n### {encabezado}\n"
            for o in lista:
                bloque += (
                    f"\n**{o.get('articulo', '')} — {o.get('titulo', '')}**  \n"
                    f"{o.get('descripcion', '')}  \n"
                )
            return bloque

        texto += _bloque(cubiertas, "Obligaciones cubiertas")
        texto += _bloque(parciales, "Obligaciones parcialmente cubiertas")
        texto += _bloque(carencias_obl, "Áreas de mejora")
        texto += _bloque(no_eval, "Obligaciones no evaluadas")

        return texto

    def _seccion_carencias(self, num: int, carencias: list[str]) -> str:
        texto = f"## {num}. Áreas de mejora identificadas\n"
        if not carencias:
            texto += "\nNo se identificaron áreas de mejora pendientes."
            return texto
        for c in carencias:
            texto += f"\n- {c}"
        return texto

    def _seccion_plan_accion(self, num: int, clasificacion: str, carencias: list[str]) -> str:
        texto = f"## {num}. Plan de acción recomendado\n"

        if clasificacion == "PROHIBIDO":
            texto += (
                "\n**Este sistema está prohibido por el AI Act.**  \n"
                "Debe detenerse el desarrollo y despliegue de forma inmediata. "
                "Consulte con un asesor legal especializado."
            )
            return texto

        pasos_por_nivel = {
            "ALTO": [
                "**Inmediato (0-3 meses):** Designar un responsable de cumplimiento del AI Act.",
                "**Corto plazo (3-6 meses):** Desarrollar la documentación técnica (Art. 11) "
                "y el sistema de gestión de riesgos (Art. 9).",
                "**Medio plazo (6-9 meses):** Implementar el registro de actividad (Art. 12) "
                "y el protocolo de supervisión humana (Art. 14).",
                "**Antes del despliegue:** Completar la evaluación de conformidad (Art. 43) "
                "y registrar el sistema en la base de datos de la UE (Art. 49).",
                "**De forma continua:** Supervisión poscomercialización y actualización "
                "de la documentación técnica.",
            ],
            "LIMITADO": [
                "**Inmediato:** Añadir aviso claro en la interfaz de que el sistema usa IA (Art. 50.1).",
                "**Corto plazo:** Implementar el marcado de contenido generado por IA si aplica (Art. 50.2).",
                "**Recomendado:** Revisar anualmente las actualizaciones del AI Act.",
            ],
            "MINIMO": [
                "**Recomendado:** Documentar internamente las capacidades y limitaciones del sistema.",
                "**Opcional:** Considerar la adhesión a códigos de conducta voluntarios (Art. 95).",
                "**Vigilancia:** Supervisar cambios en el uso que puedan elevar el nivel de riesgo.",
            ],
        }

        pasos = pasos_por_nivel.get(clasificacion, [])
        if carencias:
            pasos.append(
                f"**Áreas de mejora prioritarias:** {len(carencias)} área(s) identificada(s) "
                "en el análisis de cumplimiento que requieren atención."
            )

        for paso in pasos:
            texto += f"\n- {paso}"
        return texto

    def _seccion_revision_profesional(self, num: int, puntos: list[str]) -> str:
        # Eliminar duplicados manteniendo orden
        vistos: set[str] = set()
        puntos_unicos = [p for p in puntos if p not in vistos and not vistos.add(p)]  # type: ignore[func-returns-value]

        texto = f"## {num}. Puntos que requieren revisión profesional\n"
        if not puntos_unicos:
            texto += "\nNo se identificaron puntos específicos que requieran revisión profesional."
            return texto
        for p in puntos_unicos:
            texto += f"\n- {p}"
        return texto

    def _pie(self) -> str:
        return f"---\n\n*{_TEXTO_PIE} Fecha de generación: {_fecha_larga()}.*"

    # ══════════════════════════════════════════════════════════════════════════
    # EXPORTACIÓN
    # ══════════════════════════════════════════════════════════════════════════

    def exportar_texto_plano(self, contenido_markdown: str) -> str:
        """Convierte el informe Markdown a texto plano limpio sin marcas."""
        texto = contenido_markdown
        # Eliminar encabezados markdown
        texto = re.sub(r"^#{1,6}\s+", "", texto, flags=re.MULTILINE)
        # Eliminar negrita e itálica
        texto = re.sub(r"\*{1,2}([^*\n]+)\*{1,2}", r"\1", texto)
        # Eliminar citas blockquote
        texto = re.sub(r"^>\s*", "", texto, flags=re.MULTILINE)
        # Eliminar separadores de tabla markdown
        texto = re.sub(r"^\|[-:| ]+\|$", "", texto, flags=re.MULTILINE)
        # Limpiar líneas de tabla (mantener contenido)
        texto = re.sub(r"\|", " ", texto)
        # Normalizar múltiples líneas en blanco
        texto = re.sub(r"\n{3,}", "\n\n", texto)
        return texto.strip()

    def exportar_pdf(self, contenido_markdown: str, titulo: str = "AIComply — Informe") -> bytes:
        """Convierte el informe Markdown a PDF con cabecera y pie de página profesionales."""
        try:
            from fpdf import FPDF

            fecha_hoy = datetime.now().strftime("%d/%m/%Y")

            class _PDF(FPDF):
                def header(self_pdf):
                    self_pdf.set_font("Helvetica", "B", 13)
                    self_pdf.set_text_color(30, 30, 30)
                    self_pdf.cell(0, 8, "AIComply", align="L")
                    self_pdf.set_font("Helvetica", size=8)
                    self_pdf.set_text_color(100, 100, 100)
                    self_pdf.cell(0, 8, fecha_hoy, align="R", new_x="LMARGIN", new_y="NEXT")
                    self_pdf.set_draw_color(180, 180, 180)
                    self_pdf.line(
                        self_pdf.l_margin, self_pdf.get_y(),
                        self_pdf.w - self_pdf.r_margin, self_pdf.get_y(),
                    )
                    self_pdf.ln(3)

                def footer(self_pdf):
                    self_pdf.set_y(-14)
                    self_pdf.set_draw_color(180, 180, 180)
                    self_pdf.line(
                        self_pdf.l_margin, self_pdf.get_y(),
                        self_pdf.w - self_pdf.r_margin, self_pdf.get_y(),
                    )
                    self_pdf.set_font("Helvetica", "I", 7)
                    self_pdf.set_text_color(120, 120, 120)
                    self_pdf.cell(
                        0, 8,
                        _limpiar(f"Pág. {self_pdf.page_no()} - {_TEXTO_PIE}"),
                        align="C",
                    )

            pdf = _PDF()
            pdf.set_auto_page_break(auto=True, margin=18)
            pdf.add_page()
            pdf.set_margins(18, 22, 18)

            # Aviso legal en recuadro al inicio
            pdf.set_fill_color(255, 243, 205)
            pdf.set_draw_color(200, 160, 0)
            pdf.set_font("Helvetica", "B", 8)
            pdf.set_text_color(80, 60, 0)
            pdf.multi_cell(
                0, 6,
                _limpiar(
                    "AVISO LEGAL: Este informe es una herramienta auxiliar de orientación. "
                    "Los resultados no constituyen asesoramiento jurídico vinculante. "
                    "Consulte con especialistas antes de tomar decisiones de cumplimiento normativo."
                ),
                border=1,
                fill=True,
                new_x="LMARGIN",
                new_y="NEXT",
            )
            pdf.ln(4)
            pdf.set_text_color(30, 30, 30)

            for linea in contenido_markdown.split("\n"):
                linea_limpia = linea.strip()
                if not linea_limpia or linea_limpia == "---":
                    pdf.ln(3)
                elif linea_limpia.startswith("# "):
                    pdf.set_font("Helvetica", "B", 15)
                    pdf.multi_cell(0, 8, _limpiar(linea_limpia[2:]))
                    pdf.set_font("Helvetica", size=10)
                    pdf.ln(2)
                elif linea_limpia.startswith("## "):
                    pdf.set_font("Helvetica", "B", 12)
                    pdf.multi_cell(0, 7, _limpiar(linea_limpia[3:]))
                    pdf.set_font("Helvetica", size=10)
                    pdf.ln(1)
                elif linea_limpia.startswith("### "):
                    pdf.set_font("Helvetica", "B", 10)
                    pdf.multi_cell(0, 6, _limpiar(linea_limpia[4:]))
                    pdf.set_font("Helvetica", size=10)
                elif linea_limpia.startswith("#### "):
                    pdf.set_font("Helvetica", "BI", 10)
                    pdf.multi_cell(0, 6, _limpiar(linea_limpia[5:]))
                    pdf.set_font("Helvetica", size=10)
                elif linea_limpia.startswith("> "):
                    pdf.set_font("Helvetica", "I", 9)
                    pdf.set_text_color(80, 80, 80)
                    pdf.multi_cell(0, 5, _limpiar(linea_limpia[2:]))
                    pdf.set_font("Helvetica", size=10)
                    pdf.set_text_color(30, 30, 30)
                elif linea_limpia.startswith(("- ", "* ")):
                    pdf.set_font("Helvetica", size=10)
                    pdf.multi_cell(0, 5, _limpiar("  •  " + linea_limpia[2:]))
                elif linea_limpia.startswith("|"):
                    pdf.set_font("Helvetica", size=9)
                    pdf.multi_cell(0, 5, _limpiar(linea_limpia))
                    pdf.set_font("Helvetica", size=10)
                else:
                    pdf.set_font("Helvetica", size=10)
                    pdf.multi_cell(0, 5, _limpiar(linea_limpia))

            return bytes(pdf.output())
        except ImportError:
            return b""

    # ══════════════════════════════════════════════════════════════════════════
    # COMPATIBILIDAD CON ARQUITECTURA ANTERIOR
    # ══════════════════════════════════════════════════════════════════════════

    def generar_markdown(
        self,
        resumen_conversacion: dict,
        analisis_readme: dict | None = None,
        puntuacion: dict | None = None,
    ) -> str:
        """Compatibilidad con la arquitectura anterior."""
        clasificacion_data = {
            "clasificacion": resumen_conversacion.get("nivel_riesgo", "DESCONOCIDO"),
            "rol": "no especificado",
            "descripcion_sistema": resumen_conversacion.get("proposito", ""),
            "sector": resumen_conversacion.get("sector", "No especificado"),
            "obligaciones_preliminares": resumen_conversacion.get("obligaciones_identificadas", []),
            "puntos_indeterminados": [],
            "estados_adicionales": [],
            "roles_multiples": [],
        }
        cumplimiento_data: dict = {"obligaciones": [], "carencias_detectadas": []}
        return self.generar_informe_completo(clasificacion_data, cumplimiento_data)


_UNICODE_A_LATIN1 = str.maketrans({
    "•": "-",    # bullet •
    "–": "-",    # en dash –
    "—": "-",    # em dash —
    "‘": "'",    # comilla simple izquierda '
    "’": "'",    # comilla simple derecha '
    "“": '"',    # comilla doble izquierda "
    "”": '"',    # comilla doble derecha "
    "…": "...",  # puntos suspensivos …
    "«": '"',    # «
    "»": '"',    # »
})


def _limpiar(texto: str) -> str:
    """Convierte el texto a latin-1 para fpdf2.

    Primero transliterada los caracteres tipográficos comunes que están fuera de
    ISO-8859-1 (bullets, guiones tipográficos, comillas tipográficas) por sus
    equivalentes ASCII. El resto de caracteres fuera de latin-1 se sustituyen
    por '?' como salvaguarda final.
    """
    return texto.translate(_UNICODE_A_LATIN1).encode("latin-1", "replace").decode("latin-1")

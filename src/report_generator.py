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

# ── Paleta de colores (RGB) ────────────────────────────────────────────────────

_C_AZUL      = (13, 43, 94)
_C_AZUL_BG   = (245, 247, 252)
_C_BADGE     = (232, 238, 248)
_C_BADGE2    = (220, 230, 245)

_PALETA: dict[str, dict] = {
    "cubierta": {
        "borde": (42, 122, 74),
        "bg":    (244, 251, 246),
        "badge": (223, 245, 232),
        "texto": (15, 74, 40),
        "label": "Cubierta",
    },
    "parcial": {
        "borde": (184, 122, 0),
        "bg":    (255, 252, 240),
        "badge": (253, 242, 204),
        "texto": (90, 56, 0),
        "label": "Parcial",
    },
    "carencia": {
        "borde": (176, 32, 32),
        "bg":    (255, 248, 248),
        "badge": (253, 232, 232),
        "texto": (106, 16, 16),
        "label": "Mejora",
    },
    "mejora": {
        "borde": (176, 32, 32),
        "bg":    (255, 248, 248),
        "badge": (253, 232, 232),
        "texto": (106, 16, 16),
        "label": "Mejora",
    },
    "no_evaluada": {
        "borde": (170, 170, 170),
        "bg":    (250, 250, 250),
        "badge": (240, 240, 240),
        "texto": (102, 102, 102),
        "label": "Sin evaluar",
    },
}


def _fecha_larga() -> str:
    return datetime.now().strftime("%d/%m/%Y a las %H:%M")


def _extraer_meta_md(markdown: str) -> dict[str, str]:
    """Extrae los metadatos del encabezado Markdown del informe."""
    meta: dict[str, str] = {}
    campos = {
        "**Sistema evaluado:**": "sistema",
        "**Sector:**": "sector",
        "**Clasificación:**": "clasificacion",
        "**Rol de la entidad:**": "rol",
        "**Fecha:**": "fecha",
    }
    for linea in markdown.split("\n"):
        linea = linea.strip()
        for prefijo, clave in campos.items():
            if linea.startswith(prefijo):
                meta[clave] = linea[len(prefijo):].strip().rstrip("  ")
    return meta


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
        carencias = cumplimiento_data.get("carencias_detectadas", [])
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
        carencias = cumplimiento_data.get("carencias_detectadas", [])
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
        texto = re.sub(r"^#{1,6}\s+", "", texto, flags=re.MULTILINE)
        texto = re.sub(r"\*{1,2}([^*\n]+)\*{1,2}", r"\1", texto)
        texto = re.sub(r"^>\s*", "", texto, flags=re.MULTILINE)
        texto = re.sub(r"^\|[-:| ]+\|$", "", texto, flags=re.MULTILINE)
        texto = re.sub(r"\|", " ", texto)
        texto = re.sub(r"\n{3,}", "\n\n", texto)
        return texto.strip()

    def _renderizar_obligacion(
        self,
        pdf,
        articulo: str,
        descripcion: str,
        estado: str,
        lm: float,
        cw: float,
    ) -> None:
        """Dibuja una caja de obligación con diseño de color según estado."""
        pal = _PALETA.get(estado, _PALETA["no_evaluada"])
        BADGE_W = 28.0
        LEFT_BAR = 3.0
        PAD_H = 2.5
        PAD_V = 2.5
        H = 4.5
        text_w = cw - LEFT_BAR - BADGE_W - 2 * PAD_H

        # Estimación de altura
        avg_char_w = 1.9
        chars_line = max(1, int(text_w / avg_char_w))
        num_lines = max(1, -(-len(descripcion) // chars_line))
        est_h = PAD_V + H + 1.5 + num_lines * H + PAD_V

        if pdf.get_y() + est_h > pdf.h - pdf.b_margin - 5:
            pdf.add_page()

        y0 = pdf.get_y()

        # Fondo
        pdf.set_fill_color(*pal["bg"])
        pdf.rect(lm, y0, cw, est_h, style="F")
        # Barra izquierda
        pdf.set_fill_color(*pal["borde"])
        pdf.rect(lm, y0, LEFT_BAR, est_h, style="F")
        # Fondo badge
        pdf.set_fill_color(*pal["badge"])
        pdf.rect(lm + cw - BADGE_W, y0, BADGE_W, est_h, style="F")

        # Texto artículo
        pdf.set_xy(lm + LEFT_BAR + PAD_H, y0 + PAD_V)
        pdf.set_font("Helvetica", "B", 9)
        pdf.set_text_color(*pal["texto"])
        art_clean = _limpiar(re.sub(r"\*\*", "", articulo))[:90]
        pdf.cell(text_w, H, art_clean, align="L")

        # Texto descripción
        pdf.set_xy(lm + LEFT_BAR + PAD_H, y0 + PAD_V + H + 1.5)
        pdf.set_font("Helvetica", "", 9)
        pdf.set_text_color(80, 80, 80)
        pdf.multi_cell(text_w, H, _limpiar(descripcion), align="J",
                       new_x="LMARGIN", new_y="NEXT")

        real_h = pdf.get_y() - y0 + PAD_V

        # Ampliar fondos si el texto desbordó la estimación
        if real_h > est_h:
            ext = real_h - est_h
            pdf.set_fill_color(*pal["bg"])
            pdf.rect(lm + LEFT_BAR, y0 + est_h, cw - LEFT_BAR - BADGE_W, ext, style="F")
            pdf.set_fill_color(*pal["badge"])
            pdf.rect(lm + cw - BADGE_W, y0 + est_h, BADGE_W, ext, style="F")
            pdf.set_fill_color(*pal["borde"])
            pdf.rect(lm, y0 + est_h, LEFT_BAR, ext, style="F")

        box_h = max(est_h, real_h)

        # Borde exterior
        pdf.set_draw_color(*pal["borde"])
        pdf.set_line_width(0.3)
        pdf.rect(lm, y0, cw, box_h, style="D")
        pdf.set_line_width(0.2)

        # Texto badge centrado verticalmente
        pdf.set_xy(lm + cw - BADGE_W, y0 + box_h / 2 - H / 2)
        pdf.set_font("Helvetica", "B", 8)
        pdf.set_text_color(*pal["texto"])
        pdf.cell(BADGE_W, H, _limpiar(pal["label"]), align="C")

        pdf.set_y(y0 + box_h + 2)
        pdf.set_text_color(30, 30, 30)
        pdf.set_draw_color(180, 180, 180)

    def _renderizar_pagina_sistema(
        self, pdf, clasificacion_data: dict, lm: float, cw: float
    ) -> None:
        """Renderiza la página de descripción del sistema (página 2)."""
        desc = clasificacion_data.get("descripcion_sistema", "")
        sector = clasificacion_data.get("sector", "")
        rol = clasificacion_data.get("rol", "")
        nodos = clasificacion_data.get("nodos_recorridos", [])
        indeterminados = clasificacion_data.get("puntos_indeterminados", [])

        # ── Título de sección ─────────────────────────────────────────────────
        pdf.set_font("Helvetica", "B", 13)
        pdf.set_text_color(26, 26, 26)
        pdf.cell(cw, 8, "Descripcion del sistema evaluado", align="L",
                 new_x="LMARGIN", new_y="NEXT")
        pdf.set_draw_color(224, 224, 224)
        pdf.set_line_width(0.3)
        pdf.line(lm, pdf.get_y(), lm + cw, pdf.get_y())
        pdf.set_line_width(0.2)
        pdf.ln(4)

        # ── Ficha técnica 2 columnas ─────────────────────────────────────────
        FIELD_H = 17.0
        FIELD_W = cw / 2
        campos = [
            ("SECTOR", sector or "—"),
            ("ROL DE LA ENTIDAD", (rol or "—").capitalize()),
        ]

        pdf.set_draw_color(221, 221, 221)
        pdf.set_line_width(0.3)
        y0_grid = pdf.get_y()

        for i, (label, valor) in enumerate(campos):
            x = lm + (i % 2) * FIELD_W
            y = y0_grid + (i // 2) * FIELD_H
            pdf.set_fill_color(*_C_AZUL_BG)
            pdf.rect(x, y, FIELD_W, FIELD_H, style="FD")
            pdf.set_xy(x + 2.5, y + 2.5)
            pdf.set_font("Helvetica", "", 7)
            pdf.set_text_color(122, 144, 184)
            pdf.cell(FIELD_W - 5, 4, label, align="L")
            pdf.set_xy(x + 2.5, y + 7.5)
            pdf.set_font("Helvetica", "", 10)
            pdf.set_text_color(26, 26, 26)
            pdf.multi_cell(FIELD_W - 5, 4.5, _limpiar((valor or "—")[:80]), align="L",
                           new_x="LMARGIN", new_y="NEXT")

        pdf.set_y(y0_grid + FIELD_H + 3)

        # ── Campo propósito (ancho completo) ──────────────────────────────────
        desc_short = desc[:280] + ("..." if len(desc) > 280 else "")
        y_prop = pdf.get_y()
        pdf.set_fill_color(*_C_AZUL_BG)
        pdf.set_draw_color(221, 221, 221)
        pdf.rect(lm, y_prop, cw, 32, style="FD")
        pdf.set_xy(lm + 2.5, y_prop + 2.5)
        pdf.set_font("Helvetica", "", 7)
        pdf.set_text_color(122, 144, 184)
        pdf.cell(cw - 5, 4, "PROPOSITO DECLARADO", align="L")
        pdf.set_xy(lm + 2.5, y_prop + 7.5)
        pdf.set_font("Helvetica", "", 9)
        pdf.set_text_color(26, 26, 26)
        pdf.multi_cell(cw - 5, 4.5, _limpiar(desc_short), align="J",
                       new_x="LMARGIN", new_y="NEXT")
        pdf.set_y(max(pdf.get_y(), y_prop + 32) + 4)

        # ── Párrafo narrativo con borde izquierdo azul ────────────────────────
        if desc:
            y_nar = pdf.get_y()
            est_nar = max(14.0, min(35.0, len(desc) / 60 * 5))
            pdf.set_fill_color(*_C_AZUL)
            pdf.rect(lm, y_nar, 3, est_nar, style="F")
            pdf.set_xy(lm + 5, y_nar + 2.5)
            pdf.set_font("Helvetica", "I", 10)
            pdf.set_text_color(51, 51, 51)
            pdf.multi_cell(cw - 7, 5, _limpiar(desc[:220]), align="J",
                           new_x="LMARGIN", new_y="NEXT")
            nar_h = pdf.get_y() - y_nar + 3
            if nar_h > est_nar:
                pdf.set_fill_color(*_C_AZUL)
                pdf.rect(lm, y_nar + est_nar, 3, nar_h - est_nar, style="F")
            pdf.set_y(pdf.get_y() + 5)

        pdf.set_text_color(30, 30, 30)

        # ── Tabla de trazabilidad ─────────────────────────────────────────────
        if nodos or indeterminados:
            pdf.set_font("Helvetica", "B", 8)
            pdf.set_text_color(*_C_AZUL)
            pdf.cell(cw, 5, "TRAZABILIDAD DE LA INFORMACION", align="L",
                     new_x="LMARGIN", new_y="NEXT")
            pdf.set_draw_color(224, 221, 213)
            pdf.set_line_width(0.3)
            pdf.line(lm, pdf.get_y(), lm + cw, pdf.get_y())
            pdf.ln(2)

            TIPO_W = 22.0
            LINE_H = 3.5
            Q_W = cw * 0.40
            A_W = cw - TIPO_W - Q_W
            Q_CPL = max(1, int((Q_W - 3) / 1.65))
            A_CPL = max(1, int((A_W - 4) / 1.65))

            for nodo in nodos:
                origen = nodo.get("origen", "")
                if "directa" in origen:
                    badge_lbl, badge_bg, badge_fg = "Directo", _C_BADGE, _C_AZUL
                else:
                    badge_lbl, badge_bg, badge_fg = "Inferido", (240, 238, 248), (80, 60, 150)

                pregunta = _limpiar(nodo.get("pregunta", ""))
                respuesta = _limpiar(nodo.get("respuesta", ""))
                lines_q = max(1, -(-len(pregunta) // Q_CPL))
                lines_a = max(1, -(-len(respuesta) // A_CPL))
                H_ROW = max(6.0, max(lines_q, lines_a) * LINE_H + 2.5)

                if pdf.get_y() + H_ROW + 4 > pdf.h - pdf.b_margin:
                    pdf.add_page()

                y_row = pdf.get_y()
                pdf.set_fill_color(249, 249, 247)
                pdf.rect(lm, y_row, cw, H_ROW, style="F")
                pdf.set_fill_color(*badge_bg)
                pdf.rect(lm, y_row, TIPO_W, H_ROW, style="F")

                pdf.set_xy(lm, y_row + (H_ROW - 4) / 2)
                pdf.set_font("Helvetica", "B", 7)
                pdf.set_text_color(*badge_fg)
                pdf.cell(TIPO_W, 4, badge_lbl, align="C")

                pdf.set_xy(lm + TIPO_W + 1, y_row + 1.5)
                pdf.set_font("Helvetica", "", 7)
                pdf.set_text_color(50, 50, 50)
                pdf.multi_cell(Q_W - 2, LINE_H, pregunta, align="L",
                               new_x="LMARGIN", new_y="NEXT")

                pdf.set_xy(lm + TIPO_W + Q_W + 1, y_row + 1.5)
                pdf.set_font("Helvetica", "I", 7)
                pdf.set_text_color(80, 80, 80)
                pdf.multi_cell(A_W - 3, LINE_H, respuesta, align="L",
                               new_x="LMARGIN", new_y="NEXT")

                pdf.set_draw_color(224, 221, 213)
                pdf.line(lm, y_row + H_ROW, lm + cw, y_row + H_ROW)
                pdf.set_y(y_row + H_ROW)

            if indeterminados:
                pdf.ln(3)
                pdf.set_font("Helvetica", "B", 8)
                pdf.set_text_color(90, 72, 0)
                pdf.cell(cw, 5, "PUNTOS INDETERMINADOS", align="L",
                         new_x="LMARGIN", new_y="NEXT")
                for p in indeterminados:
                    if pdf.get_y() + 10 > pdf.h - pdf.b_margin:
                        pdf.add_page()
                    y_p = pdf.get_y()
                    pdf.set_fill_color(254, 246, 220)
                    pdf.rect(lm, y_p, cw, 10, style="F")
                    pdf.set_fill_color(224, 200, 74)
                    pdf.rect(lm, y_p, 3, 10, style="F")
                    pdf.set_xy(lm + 5, y_p + 2)
                    pdf.set_font("Helvetica", "", 8)
                    pdf.set_text_color(90, 72, 0)
                    pdf.multi_cell(cw - 7, 4.5, _limpiar(p[:180]), align="J",
                                   new_x="LMARGIN", new_y="NEXT")
                    real_h = pdf.get_y() - y_p + 2
                    if real_h > 10:
                        ext = real_h - 10
                        pdf.set_fill_color(254, 246, 220)
                        pdf.rect(lm + 3, y_p + 10, cw - 3, ext, style="F")
                        pdf.set_fill_color(224, 200, 74)
                        pdf.rect(lm, y_p + 10, 3, ext, style="F")
                    pdf.set_y(max(pdf.get_y(), y_p + max(10, real_h)) + 1.5)

        pdf.set_text_color(30, 30, 30)
        pdf.set_draw_color(180, 180, 180)
        pdf.set_line_width(0.2)

    def exportar_pdf(
        self,
        contenido_markdown: str,
        titulo: str = "AIComply — Informe",
        clasificacion_data: dict | None = None,
    ) -> bytes:
        """Genera un PDF con la plantilla visual AIComply."""
        try:
            from fpdf import FPDF

            fecha_hoy = datetime.now().strftime("%d/%m/%Y")
            meta = _extraer_meta_md(contenido_markdown)
            titulo_limpio = re.sub(r"^AIComply\s*[-—]\s*", "", titulo).strip()

            # ── Clase PDF con cabecera/pie de páginas interiores ───────────────

            class _PDF(FPDF):
                def header(self_pdf) -> None:
                    if self_pdf.page_no() <= 1:
                        return
                    self_pdf.set_xy(0, 0)
                    self_pdf.set_fill_color(*_C_AZUL)
                    self_pdf.rect(0, 0, self_pdf.w, 10, style="F")
                    ancho = self_pdf.w - self_pdf.l_margin - self_pdf.r_margin
                    self_pdf.set_xy(self_pdf.l_margin, 2)
                    self_pdf.set_font("Helvetica", "B", 9)
                    self_pdf.set_text_color(255, 255, 255)
                    self_pdf.cell(ancho * 0.72, 6,
                                  _limpiar(f"AIComply — {titulo_limpio}"), align="L")
                    self_pdf.set_font("Helvetica", "", 8)
                    self_pdf.set_text_color(180, 200, 225)
                    self_pdf.cell(ancho * 0.28, 6, fecha_hoy, align="R",
                                  new_x="LMARGIN", new_y="NEXT")
                    self_pdf.set_text_color(30, 30, 30)

                def footer(self_pdf) -> None:
                    if self_pdf.page_no() <= 1:
                        return
                    self_pdf.set_y(-14)
                    self_pdf.set_draw_color(224, 224, 224)
                    self_pdf.set_line_width(0.3)
                    self_pdf.line(
                        self_pdf.l_margin, self_pdf.get_y(),
                        self_pdf.w - self_pdf.r_margin, self_pdf.get_y(),
                    )
                    self_pdf.set_line_width(0.2)
                    ancho = self_pdf.w - self_pdf.l_margin - self_pdf.r_margin
                    self_pdf.set_font("Helvetica", "", 7)
                    self_pdf.set_text_color(170, 170, 170)
                    pie = _limpiar(
                        "AIComply - Herramienta auxiliar. "
                        "No constituye asesoramiento juridico. "
                        "Reglamento (UE) 2024/1689"
                    )
                    self_pdf.cell(ancho * 0.82, 8, pie, align="L")
                    self_pdf.cell(ancho * 0.18, 8,
                                  f"Pag. {self_pdf.page_no()}", align="R",
                                  new_x="LMARGIN", new_y="NEXT")

            # ── Configuración ──────────────────────────────────────────────────

            pdf = _PDF()
            pdf.set_margins(18, 18, 18)
            pdf.set_auto_page_break(auto=True, margin=20)

            W  = pdf.w
            LM = pdf.l_margin
            CW = W - LM - pdf.r_margin   # 174 mm

            # ══════════════════════════════════════════════════════════════════
            # PÁGINA 1 — PORTADA
            # ══════════════════════════════════════════════════════════════════

            pdf.add_page()
            pdf.set_y(0)

            BAND_H = 110.0

            # Banda azul
            pdf.set_fill_color(*_C_AZUL)
            pdf.rect(0, 0, W, BAND_H, style="F")

            # Logo
            pdf.set_xy(LM, 22)
            pdf.set_font("Helvetica", "B", 14)
            pdf.set_text_color(255, 255, 255)
            pdf.cell(CW, 7, "AIComply", align="L")

            # Subtexto reglamento
            pdf.set_xy(LM, 31)
            pdf.set_font("Helvetica", "", 8)
            pdf.set_text_color(160, 190, 230)
            pdf.cell(CW, 5, "REGLAMENTO (UE) 2024/1689 - AI ACT", align="L")

            # Línea decorativa corta
            pdf.set_draw_color(255, 255, 255)
            pdf.set_line_width(0.4)
            pdf.line(LM, 38, LM + 22, 38)
            pdf.set_line_width(0.2)

            # Título del informe
            pdf.set_xy(LM, 43)
            pdf.set_font("Helvetica", "B", 22)
            pdf.set_text_color(255, 255, 255)
            pdf.multi_cell(CW - 8, 11, _limpiar(titulo_limpio), align="L",
                           new_x="LMARGIN", new_y="NEXT")

            # Subtítulo sistema (descripción corta)
            sistema_raw = meta.get("sistema", "")
            if sistema_raw:
                subtitulo = sistema_raw[:115] + ("..." if len(sistema_raw) > 115 else "")
                y_sub = min(pdf.get_y() + 2, 95)
                pdf.set_xy(LM, y_sub)
                pdf.set_font("Helvetica", "", 10)
                pdf.set_text_color(170, 200, 235)
                pdf.multi_cell(CW - 5, 5, _limpiar(subtitulo), align="L",
                               new_x="LMARGIN", new_y="NEXT")

            # ── Grid 2×2 de metadatos ─────────────────────────────────────────
            GRID_Y = BAND_H + 8
            CELL_W = CW / 2
            CELL_H = 22.0

            metadatos = [
                ("SISTEMA EVALUADO", (meta.get("sistema") or "—")[:52]),
                ("SECTOR", meta.get("sector") or "—"),
                ("ROL DE LA ENTIDAD", (meta.get("rol") or "—").capitalize()),
                ("FECHA DE GENERACION", meta.get("fecha") or fecha_hoy),
            ]

            pdf.set_draw_color(221, 221, 221)
            pdf.set_line_width(0.3)

            for idx, (label, valor) in enumerate(metadatos):
                col = idx % 2
                row = idx // 2
                x = LM + col * CELL_W
                y = GRID_Y + row * CELL_H
                pdf.rect(x, y, CELL_W, CELL_H, style="D")
                pdf.set_xy(x + 2.5, y + 2.5)
                pdf.set_font("Helvetica", "", 7)
                pdf.set_text_color(140, 140, 140)
                pdf.cell(CELL_W - 5, 4, _limpiar(label), align="L")
                pdf.set_xy(x + 2.5, y + 7.5)
                pdf.set_font("Helvetica", "B", 9)
                pdf.set_text_color(26, 26, 26)
                pdf.multi_cell(CELL_W - 5, 4.5,
                               _limpiar(valor[:48] if len(valor) > 48 else valor),
                               align="L", new_x="LMARGIN", new_y="NEXT")

            # ── Bloque clasificación ──────────────────────────────────────────
            CLASIF_Y = GRID_Y + 2 * CELL_H + 6
            CLASIF_H = 26.0

            pdf.set_fill_color(*_C_AZUL_BG)
            pdf.set_draw_color(221, 221, 221)
            pdf.rect(LM, CLASIF_Y, CW, CLASIF_H, style="FD")
            pdf.set_fill_color(*_C_AZUL)
            pdf.rect(LM, CLASIF_Y, 4, CLASIF_H, style="F")

            pdf.set_xy(LM + 7, CLASIF_Y + 3.5)
            pdf.set_font("Helvetica", "", 7)
            pdf.set_text_color(120, 130, 150)
            pdf.cell(CW - 10, 4, "CLASIFICACION DEL SISTEMA", align="L")

            clasificacion_val = meta.get("clasificacion", "")
            pdf.set_xy(LM + 7, CLASIF_Y + 8.5)
            pdf.set_font("Helvetica", "B", 16)
            pdf.set_text_color(*_C_AZUL)
            pdf.cell(CW - 10, 9, _limpiar(clasificacion_val), align="L")

            info_nivel = NIVELES_RIESGO.get(clasificacion_val, {})
            desc_nivel = info_nivel.get("descripcion", "")
            if desc_nivel:
                pdf.set_xy(LM + 7, CLASIF_Y + 18)
                pdf.set_font("Helvetica", "", 9)
                pdf.set_text_color(100, 110, 130)
                pdf.multi_cell(CW - 12, 4, _limpiar(desc_nivel), align="L",
                               new_x="LMARGIN", new_y="NEXT")

            # ── Aviso legal ───────────────────────────────────────────────────
            AVISO_Y = CLASIF_Y + CLASIF_H + 6
            aviso = _limpiar(
                "AVISO LEGAL: Este informe es una herramienta auxiliar de orientacion. "
                "Los resultados no constituyen asesoramiento juridico vinculante. "
                "Consulte con especialistas antes de tomar decisiones de cumplimiento normativo."
            )
            pdf.set_fill_color(255, 251, 232)
            pdf.set_draw_color(224, 200, 74)
            pdf.set_line_width(0.3)
            pdf.rect(LM, AVISO_Y, CW, 20, style="FD")
            pdf.set_xy(LM + 3, AVISO_Y + 3)
            pdf.set_font("Helvetica", "", 8)
            pdf.set_text_color(107, 85, 0)
            pdf.multi_cell(CW - 6, 4, aviso, align="J",
                           new_x="LMARGIN", new_y="NEXT")

            pdf.set_text_color(30, 30, 30)
            pdf.set_draw_color(180, 180, 180)
            pdf.set_line_width(0.2)

            # ══════════════════════════════════════════════════════════════════
            # PÁGINA 2 — DESCRIPCIÓN DEL SISTEMA (opcional)
            # ══════════════════════════════════════════════════════════════════

            if clasificacion_data and clasificacion_data.get("descripcion_sistema"):
                pdf.add_page()
                self._renderizar_pagina_sistema(pdf, clasificacion_data, LM, CW)

            # ══════════════════════════════════════════════════════════════════
            # PÁGINAS INTERIORES — contenido del Markdown
            # ══════════════════════════════════════════════════════════════════

            pdf.add_page()

            # Estado del parser
            _skip = True
            _seccion: str | None = None
            _obl_estado: str | None = None
            _obl_art: str = ""
            _obl_desc: list[str] = []
            _metricas_pct: int = 0
            _metricas_counts: list[int] = []
            _metricas_emitidas = False

            def _flush_obl() -> None:
                nonlocal _obl_art, _obl_desc
                if _obl_estado and _obl_art:
                    desc_txt = _limpiar(" ".join(_obl_desc).strip())
                    self._renderizar_obligacion(pdf, _obl_art, desc_txt, _obl_estado, LM, CW)
                _obl_art = ""
                _obl_desc = []

            def _cabecera_seccion(titulo_sec: str) -> None:
                nonlocal _seccion, _obl_estado, _metricas_emitidas
                _flush_obl()
                _obl_estado = None
                _metricas_emitidas = False

                t_lower = titulo_sec.lower()
                if "plan de acci" in t_lower:
                    _seccion = "plan"
                elif "revisi" in t_lower and "profesional" in t_lower:
                    _seccion = "revision"
                elif "lisis de obligaciones" in t_lower:
                    _seccion = "obligaciones"
                else:
                    _seccion = "otro"

                pdf.ln(2)
                m_num = re.match(r"^(\d+)\.\s+(.+)$", titulo_sec)
                if m_num:
                    num_txt = m_num.group(1)
                    tit_txt = _limpiar(m_num.group(2))
                    pdf.set_fill_color(*_C_BADGE)
                    pdf.set_text_color(*_C_AZUL)
                    pdf.set_font("Helvetica", "B", 9)
                    pdf.cell(8, 7, num_txt, border=0, fill=True, align="C")
                    pdf.set_font("Helvetica", "B", 13)
                    pdf.set_text_color(26, 26, 26)
                    pdf.cell(CW - 8, 7, f"  {tit_txt}", align="L",
                             new_x="LMARGIN", new_y="NEXT")
                else:
                    pdf.set_font("Helvetica", "B", 13)
                    pdf.set_text_color(26, 26, 26)
                    pdf.cell(CW, 7, _limpiar(titulo_sec), align="L",
                             new_x="LMARGIN", new_y="NEXT")

                pdf.set_draw_color(224, 224, 224)
                pdf.set_line_width(0.3)
                pdf.line(LM, pdf.get_y(), LM + CW, pdf.get_y())
                pdf.set_line_width(0.2)
                pdf.set_draw_color(180, 180, 180)
                pdf.ln(3)
                pdf.set_text_color(30, 30, 30)

            def _grupo_obl(nombre: str, estado_key: str) -> None:
                nonlocal _obl_estado
                _flush_obl()
                _obl_estado = estado_key
                pal = _PALETA.get(estado_key, _PALETA["no_evaluada"])
                pdf.ln(1)
                pdf.set_font("Helvetica", "B", 8)
                pdf.set_text_color(*pal["borde"])
                pdf.cell(CW, 5, f">  {nombre.upper()}", align="L",
                         new_x="LMARGIN", new_y="NEXT")
                pdf.ln(1)
                pdf.set_text_color(30, 30, 30)

            def _render_metricas(pct: int, counts: list[int]) -> None:
                if len(counts) < 4:
                    return
                cub, par, mej, sin = counts[0], counts[1], counts[2], counts[3]
                card_w = CW / 4
                card_h = 22.0
                y0 = pdf.get_y()

                tarjetas = [
                    ("Cubiertas",   cub, (42, 122, 74)),
                    ("Parciales",   par, (184, 122, 0)),
                    ("Mejoras",     mej, (176, 32, 32)),
                    ("Sin evaluar", sin, (150, 150, 150)),
                ]

                for i, (lbl, num, col) in enumerate(tarjetas):
                    x = LM + i * card_w
                    pdf.set_fill_color(*col)
                    pdf.rect(x, y0, card_w, 2.5, style="F")
                    pdf.set_fill_color(*_C_AZUL_BG)
                    pdf.rect(x, y0 + 2.5, card_w, card_h - 2.5, style="F")
                    pdf.set_xy(x, y0 + 4)
                    pdf.set_font("Helvetica", "B", 18)
                    pdf.set_text_color(*col)
                    pdf.cell(card_w, 10, str(num), align="C")
                    pdf.set_xy(x, y0 + 14.5)
                    pdf.set_font("Helvetica", "", 7)
                    pdf.set_text_color(130, 130, 130)
                    pdf.cell(card_w, 5, lbl.upper(), align="C")

                pdf.set_y(y0 + card_h + 4)

                # Barra de progreso
                pdf.set_font("Helvetica", "", 9)
                pdf.set_text_color(60, 60, 60)
                pdf.cell(CW * 0.72, 5, "Grado de cumplimiento estimado", align="L")
                pdf.set_font("Helvetica", "B", 9)
                pdf.set_text_color(*_C_AZUL)
                pdf.cell(CW * 0.28, 5, f"{pct} %", align="R",
                         new_x="LMARGIN", new_y="NEXT")
                bar_y = pdf.get_y()
                pdf.set_fill_color(232, 232, 232)
                pdf.rect(LM, bar_y, CW, 4, style="F")
                fill_w = CW * max(0, min(100, pct)) / 100
                if fill_w > 0:
                    pdf.set_fill_color(*_C_AZUL)
                    pdf.rect(LM, bar_y, fill_w, 4, style="F")
                pdf.set_y(bar_y + 7)
                pdf.set_text_color(30, 30, 30)

            def _item_plan(texto: str) -> None:
                m = re.match(r"^\*\*([^*]+)\*\*:?\s*(.*)", texto, re.DOTALL)
                badge_txt = _limpiar(m.group(1).strip()[:28]) if m else "Accion"
                resto = _limpiar((m.group(2).strip() if m else texto))

                BADGE_W_P = 35.0
                LB = 3.0
                PAD_H_P = 2.5
                PAD_V_P = 2.5
                H_P = 4.5
                tw = CW - LB - BADGE_W_P - PAD_H_P
                avg = 1.85
                nlines = max(1, -(-len(resto) // max(1, int(tw / avg))))
                est = max(11.0, PAD_V_P * 2 + nlines * H_P)

                if pdf.get_y() + est > pdf.h - pdf.b_margin - 3:
                    pdf.add_page()

                y0 = pdf.get_y()
                pdf.set_fill_color(*_C_AZUL_BG)
                pdf.rect(LM, y0, CW, est, style="F")
                pdf.set_fill_color(*_C_AZUL)
                pdf.rect(LM, y0, LB, est, style="F")
                pdf.set_fill_color(*_C_BADGE2)
                pdf.rect(LM + LB, y0, BADGE_W_P, est, style="F")
                pdf.set_xy(LM + LB, y0 + (est - H_P) / 2)
                pdf.set_font("Helvetica", "B", 8)
                pdf.set_text_color(*_C_AZUL)
                pdf.cell(BADGE_W_P, H_P, badge_txt, align="C")

                pdf.set_xy(LM + LB + BADGE_W_P + PAD_H_P, y0 + PAD_V_P)
                pdf.set_font("Helvetica", "", 9)
                pdf.set_text_color(51, 51, 51)
                pdf.multi_cell(tw, H_P, resto, align="J",
                               new_x="LMARGIN", new_y="NEXT")

                real_h = pdf.get_y() - y0 + PAD_V_P
                if real_h > est:
                    ext = real_h - est
                    pdf.set_fill_color(*_C_AZUL_BG)
                    pdf.rect(LM + LB + BADGE_W_P, y0 + est,
                             CW - LB - BADGE_W_P, ext, style="F")
                    pdf.set_fill_color(*_C_BADGE2)
                    pdf.rect(LM + LB, y0 + est, BADGE_W_P, ext, style="F")
                    pdf.set_fill_color(*_C_AZUL)
                    pdf.rect(LM, y0 + est, LB, ext, style="F")

                box_h = max(est, real_h)
                pdf.set_draw_color(216, 224, 240)
                pdf.set_line_width(0.3)
                pdf.rect(LM, y0, CW, box_h, style="D")
                pdf.set_line_width(0.2)
                pdf.set_y(y0 + box_h + 2)
                pdf.set_text_color(30, 30, 30)
                pdf.set_draw_color(180, 180, 180)

            def _item_revision(texto: str) -> None:
                texto = _limpiar(re.sub(r"\*\*", "", texto))
                LB = 3.0
                PAD_H_R = 3.0
                PAD_V_R = 2.5
                H_R = 4.5
                tw = CW - LB - 2 * PAD_H_R
                avg = 1.85
                nlines = max(1, -(-len(texto) // max(1, int(tw / avg))))
                est = max(10.0, PAD_V_R * 2 + nlines * H_R)

                if pdf.get_y() + est > pdf.h - pdf.b_margin - 3:
                    pdf.add_page()

                y0 = pdf.get_y()
                pdf.set_fill_color(255, 251, 232)
                pdf.rect(LM, y0, CW, est, style="F")
                pdf.set_fill_color(224, 200, 74)
                pdf.rect(LM, y0, LB, est, style="F")
                pdf.set_xy(LM + LB + PAD_H_R, y0 + PAD_V_R)
                pdf.set_font("Helvetica", "", 9)
                pdf.set_text_color(90, 72, 0)
                pdf.multi_cell(tw, H_R, texto, align="J",
                               new_x="LMARGIN", new_y="NEXT")

                real_h = pdf.get_y() - y0 + PAD_V_R
                if real_h > est:
                    ext = real_h - est
                    pdf.set_fill_color(255, 251, 232)
                    pdf.rect(LM + LB, y0 + est, CW - LB, ext, style="F")
                    pdf.set_fill_color(224, 200, 74)
                    pdf.rect(LM, y0 + est, LB, ext, style="F")

                pdf.set_y(max(pdf.get_y(), y0 + max(est, real_h)) + 2)
                pdf.set_text_color(30, 30, 30)

            def _bullet_normal(texto: str) -> None:
                texto = re.sub(r"\*\*([^*]+)\*\*", r"\1", texto)
                pdf.set_font("Helvetica", "", 10)
                pdf.set_text_color(30, 30, 30)
                pdf.write(5, "  -  ")
                pdf.multi_cell(CW - 10, 5, _limpiar(texto), align="J",
                               new_x="LMARGIN", new_y="NEXT")

            # ── Parser línea a línea ───────────────────────────────────────────

            for linea in contenido_markdown.split("\n"):
                linea_s = linea.strip()

                if _skip:
                    if linea_s.startswith("## "):
                        _skip = False
                    else:
                        continue

                if (linea_s.startswith("> **AVISO LEGAL")
                        or linea_s.startswith("*Generado por AIComply")
                        or linea_s.startswith("*Fecha de generaci")):
                    continue

                if not linea_s or linea_s == "---":
                    if not (_obl_estado and _obl_art):
                        pdf.ln(2)
                    continue

                if linea_s.startswith("## "):
                    _cabecera_seccion(linea_s[3:])

                elif linea_s.startswith("### Obligaciones cubiertas"):
                    _grupo_obl("Obligaciones cubiertas", "cubierta")

                elif linea_s.startswith("### Obligaciones parcialmente"):
                    _grupo_obl("Obligaciones parcialmente cubiertas", "parcial")

                elif linea_s.startswith("### ") and "reas de mejora" in linea_s:
                    _grupo_obl("Areas de mejora", "carencia")

                elif linea_s.startswith("### Obligaciones no evaluadas"):
                    _grupo_obl("Obligaciones no evaluadas", "no_evaluada")

                elif linea_s.startswith("### ") or linea_s.startswith("#### "):
                    _flush_obl()
                    _obl_estado = None
                    nivel = 3 if linea_s.startswith("### ") else 4
                    sub_txt = _limpiar(linea_s[4:] if nivel == 3 else linea_s[5:])
                    pdf.set_font("Helvetica", "BI" if nivel == 4 else "B", 10)
                    pdf.multi_cell(CW, 5, sub_txt, align="L",
                                   new_x="LMARGIN", new_y="NEXT")
                    pdf.ln(1)

                elif "**Grado de cumplimiento" in linea_s and _seccion == "obligaciones":
                    m_pct = re.search(r"(\d+)\s*%", linea_s)
                    if m_pct:
                        _metricas_pct = int(m_pct.group(1))

                elif linea_s.startswith("Cubiertas:") and _seccion == "obligaciones":
                    nums = re.findall(r"\d+", linea_s)
                    if len(nums) >= 4:
                        _metricas_counts = [int(n) for n in nums[:4]]
                    if not _metricas_emitidas and _metricas_counts:
                        _render_metricas(_metricas_pct, _metricas_counts)
                        _metricas_emitidas = True

                elif _obl_estado is not None and linea_s.startswith("**"):
                    _flush_obl()
                    _obl_art = linea_s

                elif _obl_estado is not None and _obl_art and linea_s:
                    if not linea_s.startswith("*Las obligaciones"):
                        _obl_desc.append(linea_s)

                elif _obl_estado is not None:
                    pass

                elif linea_s.startswith(("- ", "* ")):
                    item = linea_s[2:]
                    if _seccion == "plan":
                        _item_plan(item)
                    elif _seccion == "revision":
                        _item_revision(item)
                    else:
                        _bullet_normal(item)

                elif linea_s.startswith("> "):
                    pdf.set_font("Helvetica", "I", 9)
                    pdf.set_text_color(90, 90, 90)
                    pdf.multi_cell(CW, 4.5, _limpiar(linea_s[2:]), align="J",
                                   new_x="LMARGIN", new_y="NEXT")
                    pdf.set_text_color(30, 30, 30)

                elif (linea_s.startswith("*") and linea_s.endswith("*")
                      and not linea_s.startswith("**")):
                    pdf.set_font("Helvetica", "I", 8)
                    pdf.set_text_color(120, 120, 120)
                    pdf.multi_cell(CW, 4, _limpiar(linea_s[1:-1]), align="J",
                                   new_x="LMARGIN", new_y="NEXT")
                    pdf.set_text_color(30, 30, 30)

                else:
                    body = re.sub(r"\*\*([^*]+)\*\*", r"\1", linea_s)
                    pdf.set_font("Helvetica", "", 10)
                    pdf.set_text_color(30, 30, 30)
                    pdf.multi_cell(CW, 5, _limpiar(body), align="J",
                                   new_x="LMARGIN", new_y="NEXT")
                    pdf.ln(1)

            _flush_obl()

            # Recuadro de generación
            pdf.ln(4)
            gen_txt = _limpiar(
                f"{_TEXTO_PIE} "
                f"Fecha de generacion: {datetime.now().strftime('%d/%m/%Y a las %H:%M')}."
            )
            pdf.set_fill_color(255, 235, 235)
            pdf.set_draw_color(180, 30, 30)
            pdf.set_line_width(0.3)
            pdf.set_font("Helvetica", "I", 8)
            pdf.set_text_color(100, 10, 10)
            pdf.multi_cell(0, 4, gen_txt, border=1, fill=True, align="J",
                           new_x="LMARGIN", new_y="NEXT")

            return bytes(pdf.output())

        except ImportError as exc:
            raise RuntimeError(
                "fpdf2 no está instalado en este entorno. Ejecute: pip install fpdf2"
            ) from exc

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
    "•": "-",
    "–": "-",
    "—": "-",
    "€": "EUR",
    "‘": "'",
    "’": "'",
    "“": '"',
    "”": '"',
    "…": "...",
    "«": '"',
    "»": '"',
})


def _limpiar(texto: str) -> str:
    """Convierte el texto a latin-1 para fpdf2."""
    return texto.translate(_UNICODE_A_LATIN1).encode("latin-1", "replace").decode("latin-1")

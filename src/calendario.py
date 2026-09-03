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

"""Calendario de aplicación del AI Act: carga desde data/calendario.json y formateo
para inyectar en los prompts y en el informe.

Es la única fuente de verdad de las fechas del Reglamento. Ningún otro módulo debe
embeber fechas de aplicación: si falta un dato aquí, se añade al JSON.
"""

from __future__ import annotations

import json
from datetime import date
from pathlib import Path

CALENDARIO_FILE = Path(__file__).parent.parent / "data" / "calendario.json"

MARCADOR = "{CALENDARIO_AI_ACT}"

_CLAVES_OBLIGATORIAS = ("version", "norma_base", "norma_modificativa", "obligaciones")
_CLAVES_OBLIGACION = ("id", "titulo", "fecha", "fecha_legible", "norma")

_calendario_cache: dict | None = None


class CalendarioNoDisponibleError(RuntimeError):
    """El calendario normativo no se pudo cargar o está incompleto.

    Es un error fatal deliberado: un informe de cumplimiento sin fechas de aplicación
    es peor que no generar informe. No existe retroceso a fechas embebidas en el código.
    """


def cargar_calendario() -> dict:
    """Carga y valida data/calendario.json. Cachea el resultado en el módulo.

    Lanza CalendarioNoDisponibleError si el fichero falta, no parsea o le faltan
    claves. Nunca devuelve un calendario parcial ni vacío.
    """
    global _calendario_cache
    if _calendario_cache is not None:
        return _calendario_cache

    try:
        datos = json.loads(CALENDARIO_FILE.read_text(encoding="utf-8"))
    except OSError as exc:
        raise CalendarioNoDisponibleError(
            f"No se pudo leer el calendario normativo en {CALENDARIO_FILE}. "
            "Sin él no se pueden generar prompts ni informes con fechas fiables."
        ) from exc
    except json.JSONDecodeError as exc:
        raise CalendarioNoDisponibleError(
            f"El calendario normativo {CALENDARIO_FILE} no es JSON válido: {exc}."
        ) from exc

    _validar(datos)
    _calendario_cache = datos
    return datos


def _validar(datos: object) -> None:
    """Comprueba que el calendario tiene la forma esperada. Lanza si no."""
    if not isinstance(datos, dict):
        raise CalendarioNoDisponibleError(
            f"El calendario normativo {CALENDARIO_FILE} debe ser un objeto JSON."
        )

    faltan = [c for c in _CLAVES_OBLIGATORIAS if c not in datos]
    if faltan:
        raise CalendarioNoDisponibleError(
            f"Al calendario normativo {CALENDARIO_FILE} le faltan claves: {', '.join(faltan)}."
        )

    obligaciones = datos["obligaciones"]
    if not isinstance(obligaciones, list) or not obligaciones:
        raise CalendarioNoDisponibleError(
            f"El calendario normativo {CALENDARIO_FILE} no contiene ninguna obligación."
        )

    for i, obl in enumerate(obligaciones):
        if not isinstance(obl, dict):
            raise CalendarioNoDisponibleError(
                f"La obligación {i} del calendario normativo no es un objeto JSON."
            )
        faltan = [c for c in _CLAVES_OBLIGACION if c not in obl]
        if faltan:
            raise CalendarioNoDisponibleError(
                f"A la obligación {obl.get('id', i)} del calendario normativo le faltan "
                f"claves: {', '.join(faltan)}."
            )
        try:
            date.fromisoformat(obl["fecha"])
        except (TypeError, ValueError) as exc:
            raise CalendarioNoDisponibleError(
                f"La fecha de la obligación {obl.get('id', i)} del calendario normativo "
                f"no es una fecha ISO válida: {obl.get('fecha')!r}."
            ) from exc


def obtener_version() -> str:
    """Versión del calendario, para estamparla en el pie del informe."""
    return str(cargar_calendario()["version"])


def obtener_obligacion(id_obligacion: str) -> dict:
    """Devuelve una obligación por su id. Lanza si no existe."""
    for obl in cargar_calendario()["obligaciones"]:
        if obl["id"] == id_obligacion:
            return obl
    raise CalendarioNoDisponibleError(
        f"El calendario normativo no contiene la obligación '{id_obligacion}'."
    )


def formatear_calendario(hoy: date | None = None) -> str:
    """Formatea el calendario como bloque de texto legible para inyectar en un prompt.

    El estado de cada obligación (ya aplicable o pendiente) se calcula contra `hoy`,
    no se almacena en el JSON: así el calendario no vuelve a quedar desfasado por el
    mero paso del tiempo. `hoy` es inyectable para que los tests sean deterministas.
    """
    calendario = cargar_calendario()
    hoy = hoy or date.today()

    base = calendario["norma_base"]
    modif = calendario["norma_modificativa"]

    partes = [
        f"CALENDARIO DE APLICACIÓN — {base['referencia']} ({base['nombre']}), "
        f"modificado por el {modif['referencia']} ({modif['nombre']}), "
        f"en vigor desde el {modif['en_vigor_desde_legible']}.",
        "",
        f"El {modif['referencia']} es derecho vigente y sus fechas son firmes. "
        "No las presentes como provisionales ni condicionadas a publicación futura.",
        "",
    ]

    for obl in calendario["obligaciones"]:
        aplicable = date.fromisoformat(obl["fecha"]) <= hoy
        estado = (
            f"Aplicable actualmente (desde el {obl['fecha_legible']})"
            if aplicable
            else f"Aplicable a partir del {obl['fecha_legible']}"
        )
        partes.append(f"- {obl['titulo']}: {estado}. Fuente: {obl['norma']}.")
        if obl.get("nota"):
            partes.append(f"  Nota: {obl['nota']}")

    return "\n".join(partes)


def aplicar_calendario(texto: str, hoy: date | None = None) -> str:
    """Sustituye el marcador {CALENDARIO_AI_ACT} por el calendario formateado.

    Usa .replace() y NUNCA .format(): los prompts contienen llaves literales (el bloque
    machine-readable <<<OBLIGACION>>>{...}) que harían fallar el formateo.
    """
    return texto.replace(MARCADOR, formatear_calendario(hoy))

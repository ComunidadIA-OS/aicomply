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

"""Clasificaciones que cierran el recorrido sin obligaciones, y qué se dice en cada caso.

Fuente única de dos cosas que estaban duplicadas en cuatro ficheros —las tres pestañas
y el generador de informes—: qué clasificaciones terminan el flujo sin obligaciones del
AI Act, y el texto que las explica.

Los dos casos NO son el mismo, y confundirlos afirma algo falso (hallazgo B1):

- ``EXCLUIDO``: **sí** es un sistema de IA del Art. 3.1, y queda fuera por el ámbito de
  aplicación del Art. 2 —uso militar, investigación, uso personal no profesional—.
- ``NO CUMPLE LA DEFINICIÓN DE SISTEMA DE IA``: no es un sistema de IA del Art. 3.1.

Hasta B1 los cuatro puntos de la interfaz mostraban el segundo texto también para el
primero. El informe PDF sí los distinguía, y de ahí salen estos textos: son los suyos,
movidos aquí, para que la interfaz no pueda volver a desincronizarse del documento.
"""

from __future__ import annotations

import logging

logger = logging.getLogger(__name__)

EXCLUIDO = "EXCLUIDO"
NO_CUMPLE_DEFINICION = "NO CUMPLE LA DEFINICIÓN DE SISTEMA DE IA"

#: Las dos clasificaciones que el evaluador emite de verdad y que cierran el recorrido.
#: Son exactamente las que enumera ``_PROMPT_EXTRAER_CLASIFICACION`` (``src/chatbot.py``),
#: el único emisor de estos valores: los otros tres sitios que escriben "clasificacion"
#: —el formulario de acceso directo, el resumen desde ``nivel_riesgo`` y el fallback
#: PENDIENTE— solo producen ALTO, LIMITADO, MINIMO, PROHIBIDO o PENDIENTE.
CLASIFICACIONES_SIN_OBLIGACIONES = frozenset({EXCLUIDO, NO_CUMPLE_DEFINICION})

#: Variantes que el conjunto arrastraba sin que nada las emitiera. Se conservan como
#: alias, no como miembros: absorben una deriva del modelo o una sesión importada
#: antigua sin obligar a mantener cuatro textos normativos que nadie ha verificado
#: porque nadie los produce.
_ALIAS_CLASIFICACION: dict[str, str] = {
    "NO ES SISTEMA DE IA": NO_CUMPLE_DEFINICION,
    "NO_IA": NO_CUMPLE_DEFINICION,
    "FUERA DE ALCANCE": EXCLUIDO,
    "FUERA_DE_ALCANCE": EXCLUIDO,
}

TEXTO_SIN_OBLIGACIONES: dict[str, str] = {
    EXCLUIDO: (
        "El sistema evaluado está **fuera del ámbito de aplicación** del AI Act (Art. 2). "
        "No se identifican obligaciones del Reglamento (UE) 2024/1689. "
        "Pueden aplicar otras normativas sectoriales o de protección de datos."
    ),
    NO_CUMPLE_DEFINICION: (
        "El sistema evaluado **no cumple la definición de sistema de IA** del Art. 3.1 del AI Act. "
        "El Reglamento (UE) 2024/1689 no es aplicable. "
        "Pueden aplicar otras normativas según el tipo de tecnología utilizada."
    ),
}

#: Lo que se imprime si algún día se añade una clasificación al conjunto sin darle texto.
#: Nunca una sección vacía: decir "no se ha podido determinar el motivo" es información,
#: y un hueco en blanco se lee como que el motivo no existe.
_TEXTO_MOTIVO_DESCONOCIDO = (
    "El sistema evaluado queda **fuera del alcance del análisis de obligaciones**, "
    "pero no ha sido posible determinar el motivo concreto. "
    "Consulte con un profesional antes de actuar sobre esta conclusión."
)


def normalizar_clasificacion(valor: str | None) -> str:
    """Devuelve la forma canónica de una clasificación sin obligaciones.

    Se llama UNA vez, en la frontera por la que la salida del modelo entra en la
    aplicación (``_normalizar_clasificacion_data``, ``src/chatbot.py``), igual que allí
    se normalizan los roles. Que la clasificación llegue ya canónica a las pestañas y al
    informe es lo que evita acabar con cuatro normalizadores y arreglar solo tres.

    Un valor que no sea una de las dos canónicas ni una de sus variantes se devuelve
    **intacto**, no en mayúsculas: no es asunto de esta función canonizar ALTO o
    LIMITADO, y tocarlos cambiaría lo que se imprime en la cabecera del informe.

    Y si no se reconoce, el sistema sigue el camino ordinario y se le presenta el
    catálogo. Es la dirección segura: decirle a alguien que tiene obligaciones cuando no
    las tiene le cuesta trabajo de más; decirle que no las tiene cuando sí, el expediente.
    """
    if not isinstance(valor, str):
        return ""

    candidato = valor.upper().strip()

    alias = _ALIAS_CLASIFICACION.get(candidato)
    if alias is not None:
        logger.warning(
            "Clasificación %r normalizada a %r. Es una variante que ningún emisor de la "
            "aplicación produce hoy: si aparece en el log con frecuencia, el modelo se "
            "está apartando del vocabulario de _PROMPT_EXTRAER_CLASIFICACION.",
            valor, alias,
        )
        return alias

    if candidato in CLASIFICACIONES_SIN_OBLIGACIONES:
        return candidato

    return valor


def es_sin_obligaciones(clasificacion: str | None) -> bool:
    """True si la clasificación cierra el recorrido sin obligaciones del AI Act.

    NO aplica alias a propósito: eso ya ocurrió en la frontera. Un valor que llegue aquí
    sin canonizar sigue el camino ordinario, que es el lado seguro del error.
    """
    if not isinstance(clasificacion, str):
        return False
    return clasificacion.upper().strip() in CLASIFICACIONES_SIN_OBLIGACIONES


def texto_sin_obligaciones(clasificacion: str | None) -> str:
    """Texto que explica por qué no hay obligaciones, según la clasificación.

    Si la clasificación está en el conjunto pero no tiene texto, avisa en el log y
    devuelve un texto genérico. Nunca devuelve cadena vacía: el ``.get(..., "")`` que
    había antes producía secciones en blanco en el informe, que es la degradación
    silenciosa que este proyecto ya no acepta.
    """
    if not isinstance(clasificacion, str):
        clasificacion = ""
    clave = clasificacion.upper().strip()

    texto = TEXTO_SIN_OBLIGACIONES.get(clave)
    if texto is not None:
        return texto

    logger.error(
        "La clasificación %r no tiene texto en TEXTO_SIN_OBLIGACIONES. Se usa el texto "
        "genérico. Toda clasificación de CLASIFICACIONES_SIN_OBLIGACIONES debe tener el "
        "suyo: sin él, el informe no puede decir por qué el Reglamento no se aplica.",
        clave or clasificacion,
    )
    return _TEXTO_MOTIVO_DESCONOCIDO

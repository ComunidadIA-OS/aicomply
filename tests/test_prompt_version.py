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

"""PROMPT_VERSION tiene que moverse cuando se mueven los prompts (hallazgo B30).

`prompts/__init__.py` lleva escrita desde siempre la regla: «Incrementar al modificar
system_prompts.py, system_prompts_local.py o system_prompt_cumplimiento.py». Vivía solo en
ese comentario, y entre 2026.09.7 y 2026.09.8 se incumplió en SEIS commits seguidos
—b1f8503, af0bf8b, 45232a8, 79eb31f, be00dde y 3c59e3c—, todos ellos tocando esos ficheros.

Lo que se pierde no es el número: es el pie del informe. `_pie()` estampa «Prompt vX · Corpus
vY · Calendario vZ» para que un documento diga qué lo produjo, y los dos recorridos del
ejemplo 02 —el que imputó a una agencia de viajes una carencia legal falsa del Art. 50.2 y el
que reparte el Art. 50 por rol— salieron con la misma cadena. Esa cadena es justo lo que se le
pregunta a un informe cuando algo ha salido mal, y no distinguía la versión que se equivocaba
de la que acierta.

Por eso la regla deja de ser un comentario y pasa a ser una huella registrada junto a la
versión: cambiar un prompt sin tocar PROMPT_VERSION rompe la suite. No comprueba que el
número sea el correcto —eso no lo puede saber un test—, sino que nadie mueva el contenido sin
pasar por el sitio donde está escrito qué cambió y por qué.

Se hashea el TEXTO DEL PROMPT, no el fichero: es lo que llega al modelo y lo que la versión
nombra. Arreglar una errata en un comentario o en la cabecera de licencia no obliga a publicar
una versión nueva de los prompts; cambiar una línea del catálogo, sí.
"""

import hashlib
import re
from pathlib import Path

from prompts import PROMPT_HASHES, PROMPT_VERSION
from prompts.system_prompt_cumplimiento import SYSTEM_PROMPT_CUMPLIMIENTO
from prompts.system_prompts import SYSTEM_PROMPT_CHATBOT
from prompts.system_prompts_local import SYSTEM_PROMPT_CHATBOT_LOCAL

_INIT = Path(__file__).resolve().parent.parent / "prompts" / "__init__.py"

# Los tres prompts que la regla de prompts/__init__.py nombra, cada uno con el fichero en que
# vive: la clave del registro es el nombre del fichero para que el fallo lo diga sin rodeos.
_PROMPTS = {
    "system_prompts.py": SYSTEM_PROMPT_CHATBOT,
    "system_prompts_local.py": SYSTEM_PROMPT_CHATBOT_LOCAL,
    "system_prompt_cumplimiento.py": SYSTEM_PROMPT_CUMPLIMIENTO,
}


def _huella(texto: str) -> str:
    return hashlib.sha256(texto.encode("utf-8")).hexdigest()


class TestLaVersionSigueAlContenido:
    """El guardián de B30. Si falla, no lo «arregles» pegando la huella nueva: eso es la mitad
    del cambio. Sube PROMPT_VERSION, escribe su entrada de historial y luego pega la huella.
    """

    def test_el_registro_cubre_exactamente_los_tres_prompts(self):
        """Un prompt nuevo sin huella registrada quedaría fuera del guardián sin que se note."""
        assert set(PROMPT_HASHES) == set(_PROMPTS), (
            "PROMPT_HASHES y los prompts existentes no coinciden: "
            f"registrados {sorted(PROMPT_HASHES)}, encontrados {sorted(_PROMPTS)}"
        )

    def test_ningun_prompt_ha_cambiado_sin_mover_la_version(self):
        desajustes = {
            fichero: _huella(texto)
            for fichero, texto in _PROMPTS.items()
            if PROMPT_HASHES[fichero] != _huella(texto)
        }
        assert not desajustes, (
            f"Estos prompts han cambiado y PROMPT_VERSION sigue en {PROMPT_VERSION}:\n"
            + "\n".join(f"  {f}: {h}" for f, h in desajustes.items())
            + "\n\nEl pie de los informes estampa esa versión: sin subirla, dos estados "
            "distintos de los prompts producen documentos indistinguibles (B30).\n"
            "Sube PROMPT_VERSION en prompts/__init__.py, añade su entrada de historial "
            "diciendo qué cambió y por qué, y pega arriba las huellas nuevas."
        )

    def test_la_version_vigente_tiene_entrada_de_historial(self):
        """Subir el número sin documentarlo deja el pie igual de mudo: la cadena cambia, pero
        no hay dónde mirar qué la hizo cambiar."""
        historial = _INIT.read_text(encoding="utf-8").split("# Historial:")[1]
        historial = historial.split("PROMPT_VERSION =")[0]
        assert f"# {PROMPT_VERSION} (" in historial, (
            f"PROMPT_VERSION es {PROMPT_VERSION} y no tiene entrada en el historial de "
            "prompts/__init__.py"
        )

    def test_la_entrada_de_historial_mas_reciente_es_la_version_vigente(self):
        """Las entradas van de más nueva a más vieja: si la de arriba no es la vigente, o se
        ha subido la versión sin documentarla o se ha documentado sin subirla."""
        historial = _INIT.read_text(encoding="utf-8").split("# Historial:")[1]
        versiones = re.findall(r"^# (\d{4}\.\d{2}\.\d+) \(", historial, re.MULTILINE)
        assert versiones, "el historial de prompts/__init__.py no tiene entradas legibles"
        assert versiones[0] == PROMPT_VERSION, (
            f"la entrada más reciente del historial es {versiones[0]} y PROMPT_VERSION es "
            f"{PROMPT_VERSION}"
        )

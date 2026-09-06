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

"""Hallazgo B1: EXCLUIDO recibía el mensaje de NO ES IA en los cuatro puntos de la interfaz.

Un sistema EXCLUIDO **sí** es un sistema de IA del Art. 3.1: queda fuera por el ámbito de
aplicación del Art. 2. Decirle que no cumple la definición es afirmar algo falso.

Estos son los primeros tests de `src/tabs/`, que estaba al 0 % (hallazgo C4). Se conducen
las funciones de pestaña con el módulo `streamlit` sustituido por un doble, y se comprueba
qué texto llega a `st.info`.
"""

import importlib
import json
import sys
from unittest.mock import MagicMock, patch

import pytest

from src import clasificaciones
from src.chatbot import AIComplyChat
from src.clasificaciones import (
    CLASIFICACIONES_SIN_OBLIGACIONES,
    EXCLUIDO,
    NO_CUMPLE_DEFINICION,
    TEXTO_SIN_OBLIGACIONES,
    es_sin_obligaciones,
    normalizar_clasificacion,
    texto_sin_obligaciones,
)
from src.report_generator import GeneradorInforme
from src.tabs import cumplimiento as tab_cumplimiento
from src.tabs import evaluador as tab_evaluador
from src.tabs import informe as tab_informe

# Fragmentos que identifican cada uno de los dos textos sin ambigüedad.
_MARCA_ART_2 = "fuera del ámbito de aplicación"
_MARCA_ART_3_1 = "no cumple la definición de sistema de IA"


def _datos(clasificacion: str) -> dict:
    return {
        "clasificacion": clasificacion,
        "rol": "implementador",
        "roles_multiples": ["implementador"],
        "descripcion_sistema": "Sistema de prueba",
        "sector": "Industrial",
        "obligaciones_preliminares": [],
        "puntos_indeterminados": [],
        "estados_adicionales": [],
    }


# ── El módulo compartido ──────────────────────────────────────────────────────


def test_los_dos_casos_tienen_texto_y_dicen_articulos_distintos():
    """El defecto de B1 era exactamente que los dos casos decían lo mismo."""
    texto_excluido = texto_sin_obligaciones(EXCLUIDO)
    texto_no_ia = texto_sin_obligaciones(NO_CUMPLE_DEFINICION)

    assert _MARCA_ART_2 in texto_excluido
    assert "Art. 2" in texto_excluido
    assert _MARCA_ART_3_1 not in texto_excluido

    assert _MARCA_ART_3_1 in texto_no_ia
    assert "Art. 3.1" in texto_no_ia
    assert _MARCA_ART_2 not in texto_no_ia


def test_toda_clasificacion_del_conjunto_tiene_texto():
    """Punto 3 del encargo: ninguna ruta puede quedarse sin texto."""
    assert set(CLASIFICACIONES_SIN_OBLIGACIONES) == set(TEXTO_SIN_OBLIGACIONES)


def test_un_miembro_sin_texto_avisa_y_no_devuelve_vacio(caplog):
    """Si algún día se añade un valor al conjunto sin texto, tiene que verse."""
    with patch.dict(clasificaciones.TEXTO_SIN_OBLIGACIONES, {}, clear=True):
        texto = texto_sin_obligaciones(EXCLUIDO)

    assert texto.strip()
    assert "no ha sido posible determinar el motivo" in texto.lower()
    assert any(r.levelname == "ERROR" for r in caplog.records)


@pytest.mark.parametrize(
    "variante,canonica",
    [
        ("NO ES SISTEMA DE IA", NO_CUMPLE_DEFINICION),
        ("NO_IA", NO_CUMPLE_DEFINICION),
        ("FUERA DE ALCANCE", EXCLUIDO),
        ("FUERA_DE_ALCANCE", EXCLUIDO),
        ("no_ia", NO_CUMPLE_DEFINICION),
    ],
)
def test_normalizar_mapea_las_variantes_y_deja_rastro(variante, canonica, caplog):
    assert normalizar_clasificacion(variante) == canonica
    assert any(r.levelname == "WARNING" for r in caplog.records)


def test_normalizar_no_toca_las_demas_clasificaciones():
    """Canonizar ALTO o LIMITADO no es asunto de esta función: se imprimen tal cual."""
    for valor in ("ALTO", "Limitado", "PROHIBIDO", "PENDIENTE", ""):
        assert normalizar_clasificacion(valor) == valor


def test_un_valor_desconocido_sigue_el_camino_ordinario():
    """La dirección segura: ante la duda se presenta el catálogo, no la exención."""
    assert not es_sin_obligaciones("FUERA DEL AMBITO")
    assert not es_sin_obligaciones("ALTO")
    assert not es_sin_obligaciones(None)


def test_la_frontera_canoniza_la_clasificacion():
    """La normalización vive en _normalizar_clasificacion_data, no en los consumidores."""
    datos = AIComplyChat._normalizar_clasificacion_data(_datos("NO_IA"))
    assert datos["clasificacion"] == NO_CUMPLE_DEFINICION


# ── Los cuatro puntos de la interfaz ──────────────────────────────────────────


@pytest.mark.parametrize(
    "clasificacion,presente,ausente",
    [
        (EXCLUIDO, _MARCA_ART_2, _MARCA_ART_3_1),
        (NO_CUMPLE_DEFINICION, _MARCA_ART_3_1, _MARCA_ART_2),
    ],
)
def test_evaluador_avisa_segun_la_clasificacion(clasificacion, presente, ausente):
    with patch.object(tab_evaluador, "st", MagicMock()) as st:
        tab_evaluador._aviso_siguiente_paso(clasificacion)

    mensaje = st.info.call_args[0][0]
    assert presente in mensaje
    assert ausente not in mensaje
    assert "pestaña **Informe**" in mensaje


@pytest.mark.parametrize(
    "clasificacion,presente,ausente",
    [
        (EXCLUIDO, _MARCA_ART_2, _MARCA_ART_3_1),
        (NO_CUMPLE_DEFINICION, _MARCA_ART_3_1, _MARCA_ART_2),
    ],
)
def test_cumplimiento_avisa_segun_la_clasificacion(
    clasificacion, presente, ausente, mock_provider
):
    estado = {
        "evaluacion_completada": True,
        "acceso_directo_cumplimiento": False,
        "clasificacion_data": _datos(clasificacion),
    }
    with patch.object(tab_cumplimiento, "st", MagicMock()) as st:
        st.session_state = estado
        tab_cumplimiento.mostrar_tab_cumplimiento(mock_provider)

    mensaje = st.info.call_args[0][0]
    assert presente in mensaje
    assert ausente not in mensaje
    # El recorrido se corta aquí: no se llega a instanciar el chatbot ni a llamar al LLM.
    assert mock_provider.llamadas_chat == 0
    assert mock_provider.llamadas_stream == 0


@pytest.mark.parametrize(
    "clasificacion,presente,ausente",
    [
        (EXCLUIDO, _MARCA_ART_2, _MARCA_ART_3_1),
        (NO_CUMPLE_DEFINICION, _MARCA_ART_3_1, _MARCA_ART_2),
    ],
)
def test_informe_cumplimiento_avisa_segun_la_clasificacion(clasificacion, presente, ausente):
    with patch.object(tab_informe, "st", MagicMock()) as st:
        tab_informe._seccion_informe_cumplimiento(
            cumpl_ok=False, es_caso_especial=True, clasificacion=clasificacion
        )

    mensaje = st.info.call_args[0][0]
    assert presente in mensaje
    assert ausente not in mensaje


@pytest.mark.parametrize(
    "clasificacion,presente,ausente",
    [
        (EXCLUIDO, _MARCA_ART_2, _MARCA_ART_3_1),
        (NO_CUMPLE_DEFINICION, _MARCA_ART_3_1, _MARCA_ART_2),
    ],
)
def test_informe_completo_avisa_segun_la_clasificacion(clasificacion, presente, ausente):
    with patch.object(tab_informe, "st", MagicMock()) as st:
        tab_informe._seccion_informe_completo(
            eval_ok=True, cumpl_ok=False, es_caso_especial=True, clasificacion=clasificacion
        )

    mensaje = st.info.call_args[0][0]
    assert presente in mensaje
    assert ausente not in mensaje


# ── La segunda frontera: importar una sesión ──────────────────────────────────


class _EstadoSesion(dict):
    """`st.session_state` acepta clave y atributo; app.py usa las dos formas."""

    def __getattr__(self, clave):
        try:
            return self[clave]
        except KeyError as exc:
            raise AttributeError(clave) from exc

    def __setattr__(self, clave, valor):
        self[clave] = valor


@pytest.fixture(scope="module")
def app_modulo():
    """Importa app.py con Streamlit sustituido y las tres pestañas apagadas.

    app.py renderiza la aplicación al importarse: no tiene un `main()` que se pueda llamar
    aparte. Se sustituye el módulo `streamlit` entero y se parchean las tres funciones de
    pestaña ANTES del import, para que los `from src.tabs... import mostrar_tab_...` de
    app.py enlacen los dobles y no se ejecute ningún renderizado. Lo que queda vivo es lo
    que interesa: las funciones de importar y exportar sesión.
    """
    streamlit_real = sys.modules.get("streamlit")

    st_falso = MagicMock()
    st_falso.tabs.side_effect = lambda etiquetas, **kw: tuple(MagicMock() for _ in etiquetas)
    st_falso.columns.side_effect = lambda spec, **kw: tuple(
        MagicMock() for _ in (range(spec) if isinstance(spec, int) else spec)
    )
    st_falso.session_state = _EstadoSesion()
    sys.modules["streamlit"] = st_falso

    from src.tabs import cumplimiento, evaluador, informe

    try:
        with (
            patch.object(evaluador, "mostrar_tab_evaluador", MagicMock()),
            patch.object(cumplimiento, "mostrar_tab_cumplimiento", MagicMock()),
            patch.object(informe, "mostrar_tab_informe", MagicMock()),
        ):
            modulo = importlib.import_module("app")
        yield modulo
    finally:
        sys.modules.pop("app", None)
        if streamlit_real is not None:
            sys.modules["streamlit"] = streamlit_real
        else:
            sys.modules.pop("streamlit", None)


def test_la_importacion_de_sesion_canoniza_la_clasificacion(app_modulo, mock_provider):
    """Importar un fichero es una frontera igual que la salida del modelo.

    Una sesión exportada antes de que el vocabulario se unificara trae "NO_IA", que hoy no
    reconoce ninguna pestaña: sin canonizar, se le ofrecería Cumplimiento a un sistema que
    no es un sistema de IA.
    """
    app_modulo.st.session_state = _EstadoSesion()
    sesion = json.dumps(
        {"_version": "1", "_app": "aicomply", "clasificacion_data": _datos("NO_IA")}
    ).encode("utf-8")

    app_modulo._importar_sesion(sesion, mock_provider)

    assert app_modulo.st.session_state["clasificacion_data"]["clasificacion"] == (
        NO_CUMPLE_DEFINICION
    )


def test_la_importacion_no_toca_las_demas_clasificaciones(app_modulo, mock_provider):
    """Canonizar es para el vocabulario sin obligaciones; ALTO se importa tal cual."""
    app_modulo.st.session_state = _EstadoSesion()
    sesion = json.dumps({"clasificacion_data": _datos("ALTO")}).encode("utf-8")

    app_modulo._importar_sesion(sesion, mock_provider)

    assert app_modulo.st.session_state["clasificacion_data"]["clasificacion"] == "ALTO"


def test_la_importacion_usa_el_normalizador_compartido(app_modulo):
    """Una copia del mapa de alias en app.py se desincronizaría; B1 va justo de eso."""
    assert app_modulo.normalizar_clasificacion is normalizar_clasificacion


# ── El informe, que ya lo hacía bien y tiene que seguir haciéndolo ────────────


@pytest.mark.parametrize(
    "clasificacion,presente,ausente",
    [
        (EXCLUIDO, _MARCA_ART_2, _MARCA_ART_3_1),
        (NO_CUMPLE_DEFINICION, _MARCA_ART_3_1, _MARCA_ART_2),
    ],
)
def test_informe_de_clasificacion_dice_lo_mismo_que_la_interfaz(
    clasificacion, presente, ausente
):
    md = GeneradorInforme().generar_informe_clasificacion(_datos(clasificacion))
    assert presente in md
    assert ausente not in md

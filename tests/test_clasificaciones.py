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
    PROHIBIDO,
    TEXTO_CUMPLIMIENTO_PROHIBIDO,
    TEXTO_SIN_OBLIGACIONES,
    es_prohibido,
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


class TestProhibidoTienePredicadoPropio:
    """PROHIBIDO cierra la pestaña Cumplimiento, pero no por lo mismo que EXCLUIDO.

    Meterlo en CLASIFICACIONES_SIN_OBLIGACIONES habría salido más corto y habría afirmado
    algo falso: ese conjunto significa «ninguna obligación del AI Act», y un sistema del
    Art. 5 sí deja obligaciones en pie —el Art. 4, que obliga a la organización por ser
    responsable del despliegue de sistemas de IA—. Lo que no procede es el análisis de
    cumplimiento, que es otra cosa.
    """

    def test_prohibido_no_esta_entre_las_clasificaciones_sin_obligaciones(self):
        assert PROHIBIDO not in CLASIFICACIONES_SIN_OBLIGACIONES
        assert not es_sin_obligaciones(PROHIBIDO)

    def test_el_predicado_reconoce_la_clasificacion(self):
        assert es_prohibido("PROHIBIDO")
        assert es_prohibido(" prohibido ")

    def test_no_reconoce_ninguna_otra(self):
        for valor in ("ALTO", "LIMITADO", "MINIMO", EXCLUIDO, NO_CUMPLE_DEFINICION, "", None):
            assert not es_prohibido(valor)

    def test_prohibido_no_tiene_texto_de_sin_obligaciones(self):
        """Si alguien le diera uno, el informe podría llegar a decir que no hay obligaciones."""
        assert PROHIBIDO not in TEXTO_SIN_OBLIGACIONES


# ── PROHIBIDO: las dos pestañas tienen que decir literalmente lo mismo ─────────


def _mensaje_del_evaluador() -> str:
    """El aviso de cierre del Evaluador para PROHIBIDO."""
    with patch.object(tab_evaluador, "st", MagicMock()) as st:
        tab_evaluador._aviso_siguiente_paso("PROHIBIDO")
    assert st.error.call_count == 1, "el aviso de PROHIBIDO debería ser un único mensaje"
    return st.error.call_args[0][0]


def _mensaje_de_cumplimiento(provider) -> str:
    """El mensaje con el que la pestaña Cumplimiento cierra un caso PROHIBIDO."""
    with patch.object(tab_cumplimiento, "st", MagicMock()) as st:
        st.session_state = {
            "evaluacion_completada": True,
            "acceso_directo_cumplimiento": False,
            "clasificacion_data": _datos("PROHIBIDO"),
        }
        tab_cumplimiento.mostrar_tab_cumplimiento(provider)
    assert st.error.call_count == 1
    return st.error.call_args[0][0]


class TestLasDosPestanasDicenLoMismoDeProhibido:
    """La contradicción concreta que cierra este cambio.

    El Evaluador remataba la clasificación PROHIBIDO con «puede continuar a la evaluación de
    cumplimiento para documentar las medidas necesarias» y «proceda a la pestaña
    Cumplimiento», y esa pestaña —desde que se cerró para las prácticas del Art. 5— responde
    lo contrario: que no procede ningún análisis. Dos líneas seguidas en la transcripción del
    ejemplo 04, la primera enviando a un sitio que la segunda desmiente.

    Comparar los dos mensajes carácter a carácter, y no por fragmentos, es lo que impide que
    vuelvan a divergir: con dos literales separados basta con que alguien toque uno.
    """

    def test_el_evaluador_y_cumplimiento_muestran_el_mismo_texto(self, mock_provider):
        assert _mensaje_del_evaluador() == _mensaje_de_cumplimiento(mock_provider)

    def test_y_ese_texto_es_el_del_modulo_compartido(self, mock_provider):
        """La igualdad sola no basta: dos copias idénticas del literal también la cumplirían
        hasta que alguien editara una."""
        assert _mensaje_del_evaluador() == TEXTO_CUMPLIMIENTO_PROHIBIDO
        assert _mensaje_de_cumplimiento(mock_provider) == TEXTO_CUMPLIMIENTO_PROHIBIDO

    def test_el_evaluador_ya_no_manda_a_la_pestana_cumplimiento(self):
        """El destino del usuario cambia de pestaña: el detalle está en el informe."""
        mensaje = _mensaje_del_evaluador()
        assert "pestaña **Cumplimiento**" not in mensaje
        assert "evaluación de cumplimiento" not in mensaje
        assert "pestaña **Informe**" in mensaje

    def test_el_evaluador_sigue_mandando_a_cumplimiento_a_las_demas(self):
        """El control: la rama que sí tiene análisis por delante no se ha tocado."""
        with patch.object(tab_evaluador, "st", MagicMock()) as st:
            tab_evaluador._aviso_siguiente_paso("ALTO")
        assert "pestaña **Cumplimiento**" in st.info.call_args[0][0]
        assert st.error.call_count == 0


class TestLaPestanaInformeTampocoMandaACumplimiento:
    """El barrido: el mismo envío a una pestaña cerrada estaba en los dos informes que
    dependen del análisis de cumplimiento. Sin registro, decían «este informe se desbloqueará
    cuando complete el análisis de cumplimiento (Pestaña 2)», que es la misma instrucción
    imposible dicha de otra manera."""

    def test_el_informe_de_cumplimiento_no_pide_completar_la_pestana_2(self):
        with patch.object(tab_informe, "st", MagicMock()) as st:
            tab_informe._seccion_informe_cumplimiento(
                cumpl_ok=False, es_caso_especial=False, clasificacion="PROHIBIDO"
            )
        mensaje = st.info.call_args[0][0]
        assert "Pestaña 2" not in mensaje
        assert "práctica prohibida" in mensaje
        assert "Informe de clasificación" in mensaje

    def test_el_informe_completo_tampoco(self):
        with patch.object(tab_informe, "st", MagicMock()) as st:
            tab_informe._seccion_informe_completo(
                eval_ok=True, cumpl_ok=False, es_caso_especial=False, clasificacion="PROHIBIDO"
            )
        mensaje = st.info.call_args[0][0]
        assert "Pestaña 2" not in mensaje
        assert "práctica prohibida" in mensaje

    def test_un_registro_guardado_sigue_pudiendo_generar_su_informe(self):
        """Los guardianes de B34 defienden las sesiones anteriores al cierre de la pestaña:
        si traen registro de cumplimiento, el informe se genera como siempre."""
        with patch.object(tab_informe, "st", MagicMock()) as st:
            st.session_state = {"informe_md_cumplimiento": None}
            st.button.return_value = False
            tab_informe._seccion_informe_cumplimiento(
                cumpl_ok=True, es_caso_especial=False, clasificacion="PROHIBIDO"
            )
        assert st.info.call_count == 0
        assert st.button.call_count == 1

    def test_las_demas_clasificaciones_conservan_el_aviso_de_pestana_2(self):
        with patch.object(tab_informe, "st", MagicMock()) as st:
            st.session_state = {}
            tab_informe._seccion_informe_cumplimiento(
                cumpl_ok=False, es_caso_especial=False, clasificacion="ALTO"
            )
        assert "Pestaña 2" in st.info.call_args[0][0]


def _indicadores_de_progreso(clasificacion: str, cumpl_ok: bool) -> dict[str, str]:
    """Los tres indicadores de la cabecera de la pestaña Informe, por su etiqueta."""
    columnas = [MagicMock(), MagicMock(), MagicMock()]
    with patch.object(tab_informe, "st", MagicMock()) as st:
        st.session_state = {
            "evaluacion_completada": True,
            "acceso_directo_cumplimiento": False,
            "cumplimiento_completado": cumpl_ok,
            "clasificacion_data": _datos(clasificacion),
        }
        st.columns.return_value = columnas
        st.button.return_value = False
        tab_informe.mostrar_tab_informe()
    return {c.metric.call_args[0][0]: c.metric.call_args[0][1] for c in columnas}


class TestLosIndicadoresNoDicenPendiente:
    """«Pendiente» es una instrucción encubierta: dice que queda trabajo en la pestaña
    Cumplimiento. Sobre un caso PROHIBIDO es la misma contradicción de las dos líneas del
    ejemplo 04, reducida a una palabra en la cabecera."""

    def test_prohibido_sin_analisis_marca_no_aplica(self):
        indicadores = _indicadores_de_progreso("PROHIBIDO", cumpl_ok=False)
        assert indicadores["Cumplimiento"] == "No aplica"
        assert indicadores["Informe completo"] == "No aplica"

    def test_un_registro_guardado_de_prohibido_sigue_contando_como_completado(self):
        indicadores = _indicadores_de_progreso("PROHIBIDO", cumpl_ok=True)
        assert indicadores["Cumplimiento"] == "Completado"

    def test_alto_sin_analisis_sigue_pendiente(self):
        """Ahí sí queda algo por hacer, y decirlo es correcto."""
        indicadores = _indicadores_de_progreso("ALTO", cumpl_ok=False)
        assert indicadores["Cumplimiento"] == "Pendiente"

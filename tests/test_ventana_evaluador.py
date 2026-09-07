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

"""La ventana del historial del Evaluador tiene que sostener el árbol de decisión.

B3. El evaluador se instanciaba con la ventana por defecto de 10 mensajes mientras el system
prompt le exigía en mayúsculas no retroceder: «cada nodo se evalúa exactamente una vez (…)
queda PERMANENTEMENTE CERRADO». Un recorrido del Anexo III pasa de diez nodos, así que la
pregunta del rol (#E1) salía de la ventana a mitad del recorrido y el modelo la repreguntaba,
reiniciando el árbol. Nunca emitía [EVALUACION_COMPLETA].

Las tres reglas del prompt que prohíben retroceder son inaplicables sobre un nodo que ya no
está en el contexto: no es que el modelo desobedezca, es que se le exige una disciplina de
memoria mientras el código le retira la memoria.
"""

import logging
from pathlib import Path

from src.chatbot import AIComplyChat
from src.tabs.evaluador import MAX_HISTORIAL_EVALUADOR, crear_chatbot_evaluador
from tests.test_chatbot import SpyProvider

# Índices de la traza real que falló. El historial del evaluador con documentación empieza por
# un mensaje del ASISTENTE (el resumen que redacta la aplicación, src/tabs/evaluador.py), así
# que los índices pares son del asistente y las preguntas del árbol caen en ellos.
_IDX_RESUMEN_DOC = 0
_IDX_PREGUNTA_ROL = 4          # #E1 · ¿Qué tipo de entidad es tu organización?
_IDX_PREGUNTA_MODIFICACIONES = 6  # #E2 · ¿Hacéis alguna de estas modificaciones? (Art. 25)

_TEXTO_ROL = "#E1 ¿Qué tipo de entidad es su organización?"
_TEXTO_MODIFICACIONES = "#E2 ¿Realizan alguna modificación del Art. 25?"


def _historial_de_la_traza(n_mensajes: int = 18) -> list[dict]:
    """Reproduce la forma del historial de la sesión que falla.

    Par = asistente, impar = usuario, empezando por el resumen de la documentación.
    """
    historial = []
    for i in range(n_mensajes):
        if i == _IDX_RESUMEN_DOC:
            contenido = "He analizado la documentación técnica proporcionada."
        elif i == _IDX_PREGUNTA_ROL:
            contenido = _TEXTO_ROL
        elif i == _IDX_PREGUNTA_MODIFICACIONES:
            contenido = _TEXTO_MODIFICACIONES
        else:
            contenido = f"mensaje {i}"
        historial.append({
            "role": "assistant" if i % 2 == 0 else "user",
            "content": contenido,
        })
    return historial


def _sin_rag(monkeypatch) -> None:
    """El evaluador no usa system_prompt_override, así que llamaría al RAG de verdad."""
    import src.chatbot  # noqa: PLC0415
    monkeypatch.setattr(src.chatbot, "formatear_contexto_rag", lambda *_, **__: "")


class TestLaVentanaSostieneElArbol:
    """El nodo del rol tiene que seguir en el contexto cuando el árbol llega al final."""

    def test_el_rol_y_las_modificaciones_siguen_en_la_ventana(self, monkeypatch):
        """La reproducción del fallo del 7 de septiembre de 2026, sobre el chatbot real.

        Antes de la factoría este test fallaba: con 18 mensajes previos más el nuevo del
        usuario, la ventana por defecto de 10 dejaba [0, 1] + los ocho últimos, y la pregunta
        del rol llevaba fuera desde el turno 7.
        """
        _sin_rag(monkeypatch)
        spy = SpyProvider("respuesta")
        chat = crear_chatbot_evaluador(spy)
        chat.historial = _historial_de_la_traza()

        chat.chat_completo("Así es")

        enviados = [m["content"] for m in spy.ultimos_mensajes]
        assert _TEXTO_ROL in enviados, (
            "la pregunta del rol (#E1) no llega al modelo: el prompt le prohíbe repreguntarla "
            "citando un nodo que el recorte ha borrado de su contexto"
        )
        assert _TEXTO_MODIFICACIONES in enviados, (
            "la pregunta de las modificaciones del Art. 25 (#E2) no llega al modelo"
        )

    def test_con_la_ventana_por_defecto_el_rol_si_se_perdia(self, monkeypatch):
        """El «falla hoy» conservado: con max_historial=10, #E1 se cae de la ventana.

        Sin este test, al reapuntar el anterior a la factoría desaparecería del repositorio la
        prueba de que el arreglo arregla algo. El defecto sigue siendo 10 y su comportamiento
        merece quedar fijado aunque ya no lo use nadie.
        """
        _sin_rag(monkeypatch)
        spy = SpyProvider("respuesta")
        chat = AIComplyChat(provider=spy)  # sin max_historial: el estado que causó el fallo
        chat.historial = _historial_de_la_traza()

        chat.chat_completo("Así es")

        enviados = [m["content"] for m in spy.ultimos_mensajes]
        assert _TEXTO_ROL not in enviados
        assert _TEXTO_MODIFICACIONES not in enviados


class TestElNumeroEstaAtadoAlArbol:
    """La constante no es un número elegido a ojo: sostiene un recorrido medido del árbol.

    El recorrido largo de verdad es el doble rol, porque el prompt (§2.5) obliga a una pasada
    completa por cada rol identificado antes de emitir la señal de fin.
    """

    # Recuento de turnos de asistente de un doble rol del Anexo III, sin una sola pregunta de
    # aclaración: resumen de la documentación (1), definición de sistema de IA (1), #E1 y #E2
    # (2), #HR1/#HR2/#HR4/#HR5 (4), #S1 (1), #R2/#R3/#R4/#R5 (4), mini-resumen del rol 1 (1),
    # nodos específicos del rol 2 (2) e informe final unificado (1). Si el árbol crece, este
    # número sube y el test avisa antes de que lo haga un usuario.
    _TURNOS_DOBLE_ROL = 17
    _MENSAJES_DOBLE_ROL = _TURNOS_DOBLE_ROL * 2

    def test_la_ventana_sostiene_un_doble_rol_completo(self, monkeypatch):
        _sin_rag(monkeypatch)
        spy = SpyProvider("respuesta")
        chat = crear_chatbot_evaluador(spy)
        chat.historial = _historial_de_la_traza(self._MENSAJES_DOBLE_ROL)

        chat.chat_completo("Así es")

        enviados = [m["content"] for m in spy.ultimos_mensajes]
        assert _TEXTO_ROL in enviados, (
            f"un doble rol son {self._MENSAJES_DOBLE_ROL} mensajes y la ventana es de "
            f"{MAX_HISTORIAL_EVALUADOR}: si esto falla, el árbol ha crecido y el número "
            "se ha quedado corto"
        )

    def test_la_ventana_deja_margen_sobre_el_recorrido_sin_friccion(self):
        """El suelo son 34 mensajes; el margen es para las aclaraciones que el prompt provoca.

        §2.2 del prompt lista diez conceptos que «casi siempre» piden doble definición y §2.4
        obliga a reformular ante cualquier ambigüedad: el recorrido sin fricción no existe.
        """
        assert MAX_HISTORIAL_EVALUADOR > self._MENSAJES_DOBLE_ROL


class TestNadieConstruyeElChatbotPorSuCuenta:
    """Hoy el bug no fue el 10: fue depender del default.

    Los tests de arriba fijan el número, pero nada impedía que apareciera una séptima llamada
    a AIComplyChat( con el defecto, que es exactamente cómo se llegó al fallo: seis sitios de
    llamada y ninguno pasaba la ventana. Este guardián cierra la clase de regresión entera en
    vez del caso concreto.

    El único constructor permitido fuera de src/chatbot.py es el de cumplimiento.py, que pasa
    su max_historial explícito.
    """

    _RAIZ = Path(__file__).resolve().parent.parent

    def _fuente(self, ruta_relativa: str) -> str:
        return (self._RAIZ / ruta_relativa).read_text(encoding="utf-8")

    def test_app_no_construye_el_chatbot_directamente(self):
        assert "AIComplyChat(" not in self._fuente("app.py"), (
            "app.py debe usar crear_chatbot_evaluador(), no el constructor: con el "
            "constructor hereda la ventana por defecto de 10 y el árbol vuelve a reiniciarse"
        )

    def test_la_pestana_evaluador_solo_lo_construye_en_la_factoria(self):
        fuente = self._fuente("src/tabs/evaluador.py")
        # La factoría es la única llamada legítima: se cuenta y tiene que ser exactamente una.
        assert fuente.count("AIComplyChat(") == 1, (
            "en src/tabs/evaluador.py solo crear_chatbot_evaluador() puede construir el "
            "chatbot; cualquier otra llamada se queda con el default"
        )
        assert "def crear_chatbot_evaluador(" in fuente

    def test_cumplimiento_conserva_su_ventana_explicita(self):
        """La pestaña que pasaba el valor explícito es la que sobrevivió al fallo de hoy."""
        assert "max_historial=50" in self._fuente("src/tabs/cumplimiento.py")


class TestElRecorteDejaRastro:
    """Fallar de forma ruidosa, nunca degradar en silencio — pero sin gritar en el caso sano.

    tests/test_chatbot.py y tests/test_cumplimiento_registro.py llevaban escrito en sus
    docstrings que «el historial se recorta en silencio». El rastro cobra esa deuda.

    Los dos niveles no son cosmética. Recortar es ESPERADO —formatear_obligaciones_registradas()
    existe porque la ventana de Cumplimiento se queda corta en un recorrido de 22 obligaciones,
    así que cada recorrido sano de esa pestaña recorta—, y emitirlo como WARNING llenaría el log
    de alarmas inocuas hasta dejarlas sin significado.
    """

    def test_recortar_deja_rastro_con_las_cifras(self, caplog):
        """Contabilidad, en INFO: cuántos mensajes se van y sobre cuántos."""
        chat = AIComplyChat(provider=SpyProvider(), max_historial=6)
        chat.historial = _historial_de_la_traza(20)

        with caplog.at_level(logging.INFO, logger="src.chatbot"):
            chat._historial_truncado()

        assert "Historial recortado" in caplog.text
        assert "20 mensajes" in caplog.text, "el rastro tiene que dar la cifra, no solo avisar"

    def test_recortar_no_es_una_anomalia_y_no_emite_warning(self, caplog):
        """El recorte rutinario de Cumplimiento no puede ensuciar el log de alarmas."""
        chat = AIComplyChat(provider=SpyProvider(), max_historial=6)
        chat.historial = _historial_de_la_traza(20)

        with caplog.at_level(logging.WARNING, logger="src.chatbot"):
            chat._historial_truncado()

        assert caplog.text == ""

    def test_un_recorrido_corto_y_sano_no_dispara_nada(self, caplog):
        """Ni siquiera contabilidad: si no se recorta, no hay nada que anotar."""
        chat = AIComplyChat(provider=SpyProvider(), max_historial=60)
        chat.historial = _historial_de_la_traza(18)

        with caplog.at_level(logging.INFO, logger="src.chatbot"):
            ventana = chat._historial_truncado()

        assert ventana is chat.historial
        assert caplog.text == ""

    def test_perder_el_bloque_reciente_entero_si_es_una_anomalia(self, caplog):
        """La aserción defensiva, en WARNING: el invariante roto está fuera de esta función.

        Hay que fabricar una tirada de nueve mensajes seguidos del usuario porque la aplicación
        no genera ese estado: con la alternancia pregunta→respuesta el realineado descarta como
        mucho un mensaje. Si este warning aparece en producción, el bug está en quien escribe el
        historial, no en _historial_truncado().
        """
        chat = AIComplyChat(provider=SpyProvider(), max_historial=5)
        chat.historial = [{"role": "assistant", "content": "resumen"}]
        chat.historial += [{"role": "user", "content": f"u{i}"} for i in range(9)]

        with caplog.at_level(logging.WARNING, logger="src.chatbot"):
            ventana = chat._historial_truncado()

        assert len(ventana) == 2
        assert "bloque reciente COMPLETO" in caplog.text


class TestElArranqueDeIntercambioDependeDelFlujo:
    """La ventana no puede empezar por una respuesta cuya pregunta se ha borrado.

    Hay dos flujos reales: con documentación aportada el historial arranca con el resumen que
    redacta la aplicación, que es del asistente, y los intercambios van pregunta→respuesta; sin
    documentación arranca con el usuario. Con el corte fijado en "user" el segundo flujo salía
    bien y el primero dejaba huérfana la respuesta.
    """

    def test_con_documentacion_la_ventana_empieza_por_la_pregunta(self):
        chat = AIComplyChat(provider=SpyProvider(), max_historial=8)
        chat.historial = _historial_de_la_traza(20)  # índice 0 = assistant

        ventana = chat._historial_truncado()

        assert ventana[2]["role"] == "assistant", (
            "la ventana empieza por una respuesta del usuario cuya pregunta se ha descartado"
        )

    def test_sin_documentacion_se_comporta_igual_que_antes(self):
        """El flujo que ya funcionaba no cambia: el corte sigue cayendo en 'user'."""
        chat = AIComplyChat(provider=SpyProvider(), max_historial=8)
        chat.historial = [
            {"role": "user" if i % 2 == 0 else "assistant", "content": f"m{i}"}
            for i in range(20)
        ]

        ventana = chat._historial_truncado()

        assert ventana[2]["role"] == "user"

    def test_en_cumplimiento_el_invariante_es_un_no_op(self):
        """_historial_truncado() es código compartido, así que esto alcanza a Cumplimiento.

        Ahí el historial empieza siempre por un mensaje del usuario —no hay ninguna siembra
        inicial del asistente equivalente a la del evaluador—, luego el rol de arranque es
        "user" y la condición nueva evalúa igual que la vieja. Un no-op sin test deja de serlo
        el día que alguien siembre Cumplimiento con un mensaje inicial del asistente, que es
        literalmente lo que pasó en el Evaluador.
        """
        chat = AIComplyChat(
            provider=SpyProvider(), system_prompt_override="prompt", max_historial=50
        )
        chat.historial = [
            {"role": "user" if i % 2 == 0 else "assistant", "content": f"m{i}"}
            for i in range(80)
        ]

        ventana = chat._historial_truncado()

        # Lo que devolvía el corte fijado en "user", replicado a mano sobre el mismo historial.
        primeros = chat.historial[:2]
        resto = chat.historial[-48:]
        while resto and resto[0]["role"] != "user":
            resto = resto[1:]

        assert ventana == primeros + resto

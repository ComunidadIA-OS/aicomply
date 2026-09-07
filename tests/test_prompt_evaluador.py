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

"""Guardianes de texto sobre el prompt del evaluador (prompts/system_prompts.py).

El árbol de decisión no está en código y ningún test lo ejecuta: estas comprobaciones NO
prueban que el modelo obedezca las reglas —eso exige una llamada real y no es determinista—,
solo que las reglas siguen escritas. No sustituyen al recorrido manual.

Los dos hallazgos que las motivan son la misma historia: un arreglo que se aplicó al prompt de
cumplimiento y no a este, de modo que el usuario recibía respuestas opuestas sobre el mismo
artículo en dos pestañas consecutivas.

  B17 - el evaluador presentaba la evaluación de impacto del Art. 27 como obligación de un
        implementador privado de un sistema de empleo
  B19 - el evaluador atribuía al implementador el registro en la base de datos de la UE
  B21 - el evaluador se inventaba los apartados del Art. 26
  B25 - el Art. 50 se atribuía a quien se tuviera delante. Por el lado del evaluador, una ruta
        de #R4 mandaba la función del Art. 50.2 (del proveedor) a la etiqueta del Art. 50.4
        (del responsable del despliegue)

Y uno del recorrido manual del 7 de septiembre de 2026, sin número de auditoría todavía: el
evaluador fechaba el informe en «Junio de 2025», dato que nadie le dio.
"""

import re

from prompts.system_prompts import SYSTEM_PROMPT_CHATBOT
from prompts.system_prompts_local import SYSTEM_PROMPT_CHATBOT_LOCAL

_RE_APARTADO_26 = re.compile(r"Art\.?\s*26\.\d")


class TestArt49NoEsDelImplementador:
    """B19. En el recorrido del 6 de septiembre, con rol implementador único y confirmado, el
    evaluador dijo «debéis solicitárselo o, en su defecto, gestionarlo vosotros», y dos
    pantallas después Cumplimiento concluyó «no aplica».
    """

    def test_la_regla_del_art_49_sigue_en_el_prompt(self):
        assert (
            "REGLA — El registro en la base de datos de la UE (Art. 49) NO es obligación "
            "del implementador:"
        ) in SYSTEM_PROMPT_CHATBOT

    def test_la_regla_ordena_preguntar_antes_de_afirmar(self):
        """La lección de B11: enunciar la condición no basta, hay que ordenar preguntarla.

        Es la forma que ya tenía la entrada del Art. 49 en el catálogo de cumplimiento, y la
        que allí sí funcionó en este mismo recorrido.
        """
        bloque = _bloque_regla_art_49()
        assert "PREGUNTA" in bloque
        assert "autoridad pública" in bloque and "organismo público" in bloque
        assert "Art. 26.8" in bloque

    def test_la_regla_prohibe_ademas_de_condicionar(self):
        """Prohibición simétrica: la lección de B15 y B17 es que una regla escrita en una sola
        dirección se aplica de más."""
        bloque = _bloque_regla_art_49()
        assert "NO le aplica" in bloque
        assert "no lo presentes como carencia" in bloque.lower()
        assert "gestione por su cuenta" in bloque, (
            "debe desactivar explícitamente la salida que se vio en el recorrido"
        )

    def test_la_notificacion_a_la_nca_esta_condicionada_al_proveedor(self):
        """La línea del catálogo que el modelo leía sin rol y aplicaba a quien fuera.

        Se busca por "Notificar a la NCA (Art." y no por el nombre a secas: el nombre también
        es un estado del árbol (#S1), y esa línea sí es correcta sin rol.
        """
        linea = _linea_que_contiene("Notificar a la NCA (Art.")
        assert "OBLIGACIÓN DEL PROVEEDOR" in linea
        assert "no se la atribuyas al implementador" in linea

    def test_el_art_71_tambien_queda_cubierto(self):
        """El recorrido citó «Art. 49 y Art. 71»: si la regla no lo nombra, se cuela por ahí."""
        assert "Arts. 49 y 71" in _bloque_regla_art_49()


class TestArt27NoAplicaATodoImplementador:
    """B17. En el recorrido del 4 de septiembre, con una PYME privada que criba currículums, el
    evaluador afirmó que «el Art. 27 exige que los implementadores privados que despliegan
    sistemas de alto riesgo del Anexo III realicen una evaluación de impacto». Eso no está en el
    Reglamento: el empleo es el Anexo III punto 4 y el Art. 27.1 solo alcanza al punto 5(b) y
    5(c), a los organismos de Derecho público y a las entidades privadas que prestan servicios
    públicos.
    """

    def test_la_regla_del_art_27_sigue_en_el_prompt(self):
        assert (
            "REGLA — La evaluación de impacto sobre los derechos fundamentales (Art. 27) NO es "
            "obligación de todo implementador:"
        ) in SYSTEM_PROMPT_CHATBOT

    def test_la_regla_ordena_preguntar_antes_de_afirmar(self):
        bloque = _bloque_regla_art_27()
        assert "PREGUNTA" in bloque
        assert "organismos de Derecho público" in bloque
        assert "entidades privadas que prestan servicios públicos" in bloque
        assert "punto 5, letras b) y c)" in bloque

    def test_la_regla_prohibe_ademas_de_condicionar(self):
        bloque = _bloque_regla_art_27()
        assert "NO le aplica" in bloque
        assert "no lo presentes como carencia" in bloque.lower()

    def test_la_regla_desactiva_la_afirmacion_inventada_del_recorrido(self):
        """El enunciado correcto ya estaba en el catálogo y no impidió la afirmación contraria:
        hace falta nombrar el caso que falló."""
        bloque = _bloque_regla_art_27()
        assert "Anexo III punto 4" in bloque, "el empleo debe quedar excluido por su punto"
        assert "criba currículums" in bloque
        assert "esa regla no está en el Reglamento" in bloque


class TestArt26SinApartados:
    """B21. El evaluador citó «Art. 26.2» para la pertinencia de los datos de entrada (es el
    26.4) y «Art. 26.4» para los incidentes graves (es el 26.5).

    Este prompt no tiene el catálogo del Art. 26 apartado por apartado y no debe tenerlo:
    duplicarlo crearía una segunda fuente que se desincronizaría de
    system_prompt_cumplimiento.py, que es donde vive verificado contra el consolidado. La
    salida barata es la de B10: citar el artículo y nunca el apartado.
    """

    def test_el_catalogo_de_entidades_prohibe_los_apartados(self):
        linea = _linea_que_contiene("- Implementador (Art. 26):")
        assert 'Cita SIEMPRE "Art. 26" a secas, NUNCA un apartado' in linea
        assert "sin añadirle número de apartado" in linea

    def test_el_formato_del_informe_prohibe_los_apartados(self):
        linea = _linea_que_contiene("2. Tus obligaciones:")
        assert "Para el Art. 26, sin apartado" in linea
        assert '"(Art. 26)"' in linea

    def test_la_prohibicion_esta_en_los_dos_sitios(self):
        """Que no dependa solo del formato del informe: la conversación es lo que el usuario lee
        en pantalla, y es donde se vieron los apartados inventados."""
        assert SYSTEM_PROMPT_CHATBOT.count('nunca "(Art. 26.2)"') == 2

    def test_no_se_cita_ningun_apartado_del_art_26_fuera_de_las_reglas(self):
        """El guardián de verdad: si alguien añade un "Art. 26.3" al árbol en una edición
        futura, salta aquí.

        Se excluyen los tres contextos donde un apartado sí es deliberado: las dos
        prohibiciones, que citan apartados como ejemplo de lo que NO hay que escribir, y la
        regla del Art. 49, que cita el 26.8 como base legal de cuándo el implementador sí
        registra. Fuera de ahí, el prompt no numera apartados del Art. 26.
        """
        sancionadas = (
            "- Implementador (Art. 26):",
            "2. Tus obligaciones:",
            "El responsable del despliegue solo registra",
        )
        resto = [
            ln for ln in SYSTEM_PROMPT_CHATBOT.splitlines()
            if not any(marca in ln for marca in sancionadas)
        ]
        intrusos = [ln for ln in resto if _RE_APARTADO_26.search(ln)]
        assert not intrusos, f"apartados del Art. 26 fuera de las reglas: {intrusos}"

    def test_el_catalogo_del_art_26_no_se_ha_duplicado_aqui(self):
        """Duplicarlo crea una segunda fuente que se desincroniza; vive en cumplimiento."""
        assert "26.11" not in SYSTEM_PROMPT_CHATBOT
        assert "26.12" not in SYSTEM_PROMPT_CHATBOT


class TestElInformeNoLlevaFecha:
    """En el recorrido manual del 7 de septiembre —que se hizo el 7 de septiembre de 2026— el
    informe que el modelo redactó en el chat abría con «Fecha de evaluación: Junio de 2025».
    Nadie le dio esa fecha: la rellenó porque un informe formal suele llevar una. El informe
    que genera la aplicación la estampa bien, así que el arreglo es que el modelo no la
    escriba, no que la acierte.
    """

    def test_la_regla_de_la_fecha_sigue_en_el_prompt(self):
        assert "REGLA CRÍTICA — El informe no lleva fecha:" in SYSTEM_PROMPT_CHATBOT

    def test_la_regla_nombra_la_cadena_que_salio_en_el_recorrido(self):
        bloque = _bloque_regla_fecha()
        assert '"Fecha de evaluación"' in bloque
        assert "la aplicación" in bloque, "debe decir quién sí sabe la fecha"

    def test_la_regla_deja_vivas_las_fechas_del_calendario(self):
        """Las etiquetas temporales de la sección 6 son fechas legítimas: si la regla las
        arrastrase, el informe perdería el «Aplicable próximamente — 2 dic 2027»."""
        assert "calendario regulatorio de la sección 6" in _bloque_regla_fecha()

    def test_el_formato_del_informe_no_pide_ninguna_fecha(self):
        """El guardián de verdad: que no vuelva a aparecer una fecha entre los puntos que se
        le piden al informe. Se miran solo los puntos numerados de la sección 7; las reglas
        que van debajo hablan de fechas precisamente para prohibirlas."""
        puntos = [
            ln for ln in _seccion_7().splitlines()
            if re.match(r"^\d+\.\s", ln)
        ]
        assert puntos, "la estructura del informe debería seguir siendo una lista numerada"
        intrusos = [ln for ln in puntos if "fecha" in ln.lower()]
        assert not intrusos, f"el formato del informe pide fechas: {intrusos}"

    def test_la_regla_general_de_no_inventar_contexto(self):
        assert "REGLA CRÍTICA — No inventes datos de contexto:" in SYSTEM_PROMPT_CHATBOT
        bloque = SYSTEM_PROMPT_CHATBOT.split("REGLA CRÍTICA — No inventes datos de contexto:")[1]
        bloque = bloque.split("REGLA CRÍTICA — El informe no redefine el rol:")[0]
        for dato in ("fechas", "nombres", "referencias", "contrato"):
            assert dato in bloque, f"la regla debería nombrar {dato}"
        assert "se pregunta" in bloque, "omitir o preguntar, no rellenar"

    def test_el_prompt_local_lleva_la_misma_prohibicion(self):
        """El fallo es del modelo, no del proveedor: con un modelo local pasaría igual."""
        assert "SIN fecha de evaluación" in SYSTEM_PROMPT_CHATBOT_LOCAL
        assert "No inventes ningún otro dato" in SYSTEM_PROMPT_CHATBOT_LOCAL


class TestElAltoRiesgoNoConvierteEnProveedor:
    """El árbol convertía en proveedor a todo implementador de un sistema de alto riesgo.

    El bloque de condiciones de cambio de estado decía que si la entidad no es Proveedor,
    «además de ALTO RIESGO, pasa a Convertirse en proveedor para todas las preguntas futuras».
    El Art. 25.1 solo convierte en tres circunstancias tasadas —poner nombre o marca,
    modificación sustancial, o cambio de la finalidad prevista que vuelva el sistema de alto
    riesgo— y desplegar no es ninguna de ellas.

    Doble consecuencia: jurídicamente, toda PYME implementadora del Anexo III salía con las
    obligaciones del Art. 16 en vez de las del Art. 26; mecánicamente, cambiar el rol activaba
    la sección 2.5 y con ella un recorrido completo por cada rol, alargando el recorrido justo
    cuando la ventana del historial ya no lo sostenía (ver tests/test_ventana_evaluador.py).
    """

    def test_el_alto_riesgo_ya_no_convierte_al_que_no_es_proveedor(self):
        assert (
            "pasa a Convertirse en proveedor para todas las preguntas futuras"
            not in SYSTEM_PROMPT_CHATBOT
        ), "la conversión automática por ALTO RIESGO no está en el Art. 25"

    def test_el_bloque_lo_dice_en_positivo_y_no_solo_lo_calla(self):
        """B15 y B17: borrar sin sustituir deja el hueco por el que el modelo vuelve a deducir."""
        bloque = _bloque_cambio_estado()
        assert "NO cambia el rol por sí solo" in bloque
        assert "Art. 25.1" in bloque and "Art. 25.3" in bloque
        assert "TRES circunstancias" in bloque and "DOS circunstancias" in bloque

    def test_el_bloque_desactiva_la_salida_que_se_vio_en_el_recorrido(self):
        bloque = _bloque_cambio_estado()
        assert "Desplegar, distribuir o importar" in bloque
        assert "NO convierte en proveedor" in bloque
        assert "Art. 26" in bloque, "hay que decir qué obligaciones le tocan, no solo cuáles no"

    def test_ningun_nodo_del_bloque_hr_cambia_el_rol(self):
        """#HR6 no convierte «por ser ALTO RIESGO»: cierra el test del Art. 25.3 que abrió #E3.

        Si se escribe como que un nodo del bloque #HR cambia el rol, dentro de tres semanas
        alguien lo lee así y volvemos al punto de partida.
        """
        bloque = _bloque_cambio_estado()
        assert "en ningún nodo" in bloque
        assert "#E3 + #HR6" in bloque, "la conversión del fabricante es la conjunción, no #HR6"

    # ── La otra dirección: lo que el árbol SÍ debe seguir convirtiendo ──────────────

    def test_e2_sigue_activando_la_conversion_del_art_25_1(self):
        """Una regla comprobada solo en la dirección que se acaba de arreglar es media regla."""
        assert "se activa el estado Convertirse en proveedor (Art. 25)" in SYSTEM_PROMPT_CHATBOT

    def test_e2_conserva_las_tres_circunstancias_tasadas(self):
        bloque = SYSTEM_PROMPT_CHATBOT.split("#E2 ·")[1].split("#E3 ·")[0]
        assert "Poner un nombre o marca diferente en el sistema" in bloque
        assert "Modificar la finalidad prevista" in bloque
        assert "Realizar una modificación sustancial" in bloque

    def test_la_ruta_del_fabricante_de_producto_sigue_en_pie(self):
        assert "#E3 · (Solo Fabricante de producto)" in SYSTEM_PROMPT_CHATBOT
        assert "#HR6 · (Fabricante de producto)" in SYSTEM_PROMPT_CHATBOT

    def test_la_regla_simetrica_de_roles_sigue_en_el_prompt(self):
        """El rol solo lo fijan #E1 y #E2; es la regla que el bloque contradecía."""
        assert "REGLA SIMÉTRICA — No añadir roles no confirmados:" in SYSTEM_PROMPT_CHATBOT

    def test_el_prompt_local_no_gana_la_conversion_generica(self):
        """Hoy no tiene el bloque defectuoso y encamina la conversión por #E2. Que siga así."""
        assert "para todas las preguntas futuras" not in SYSTEM_PROMPT_CHATBOT_LOCAL
        assert "estado Convertirse en proveedor (Art. 25)" in SYSTEM_PROMPT_CHATBOT_LOCAL


class TestRutasDelR4NombranSuApartado:
    """Las cuatro etiquetas de transparencia se llaman por un nombre —«Contenido Sintético»,
    «Parecido del Contenido»— que no dice su apartado, y el apartado es lo que decide el ROL:
    50.1 y 50.2 obligan al proveedor, 50.3 y 50.4 al responsable del despliegue. Una ruta que
    manda la función de un apartado a la etiqueta de otro registra el estado adicional del rol
    contrario, y eso viaja en obligaciones_preliminares hasta la pestaña Cumplimiento.

    Es lo que pasaba: «Contenido sintético destinado al público» (Art. 50.2, del proveedor)
    salía etiquetado «Parecido del Contenido» (Art. 50.4, del responsable del despliegue).
    Hermano de B25 por el otro lado del traspaso.
    """

    # Nombre de la etiqueta → apartado del Art. 50 que le corresponde, según la línea del
    # catálogo de resultados que reparte los cuatro apartados entre sus dos destinatarios.
    _ETIQUETAS = {
        "Personas Físicas": "50.1",
        "Contenido Sintético": "50.2",
        "Emoción y Biometría": "50.3",
        "Parecido del Contenido": "50.4",
    }

    def test_el_catalogo_de_resultados_sigue_repartiendo_los_cuatro_apartados(self):
        """Es la fuente contra la que se contrastan las rutas: si cambia, este test manda
        mirar las rutas antes de dar por bueno el cambio."""
        linea = _linea_de_transparencia()
        for etiqueta, apartado in self._ETIQUETAS.items():
            assert f"{etiqueta} (Art. {apartado})" in linea, f"falta {etiqueta} en el catálogo"
        assert "OBLIGACIONES DEL PROVEEDOR" in linea
        assert "OBLIGACIONES DEL RESPONSABLE DEL DESPLIEGUE" in linea

    def test_ninguna_ruta_nombra_una_etiqueta_con_el_apartado_de_otra(self):
        """El guardián: en cada mención «Transparencia: <etiqueta> (Art. 50.x)» de las rutas,
        la x tiene que ser la del apartado de esa etiqueta."""
        for etiqueta, apartado in _menciones_de_las_rutas():
            assert self._ETIQUETAS[etiqueta] == apartado, (
                f"la ruta etiqueta «{etiqueta}» como Art. {apartado}, "
                f"y le corresponde el Art. {self._ETIQUETAS[etiqueta]}"
            )

    def test_toda_etiqueta_de_las_rutas_lleva_su_apartado(self):
        """Sin el apartado escrito al lado, el desajuste vuelve a ser invisible: el nombre de
        la etiqueta no delata a qué rol pertenece."""
        rutas = _rutas_del_r4()
        assert _menciones_de_las_rutas(), "las rutas deberían seguir nombrando etiquetas"
        for etiqueta in self._ETIQUETAS:
            for trozo in rutas.split(f"Transparencia: {etiqueta}")[1:]:
                assert trozo.lstrip().startswith("(Art. 50."), (
                    f"una mención de «{etiqueta}» en las rutas no lleva su apartado"
                )

    def test_el_contenido_sintetico_no_vuelve_a_salir_como_parecido_del_contenido(self):
        """El caso literal que falló, escrito aparte para que el diff lo enseñe."""
        rutas = _rutas_del_r4()
        assert (
            "Contenido sintético destinado al público + alto riesgo → "
            "Transparencia: Contenido Sintético (Art. 50.2)"
        ) in rutas
        assert "destinado al público + alto riesgo → Transparencia: Parecido" not in rutas

    def test_cada_etiqueta_de_las_rutas_existe_en_el_catalogo_de_resultados(self):
        """Una etiqueta inventada en las rutas no tendría destinatario declarado en ningún
        sitio, que es la forma silenciosa del mismo fallo."""
        for etiqueta, _ in _menciones_de_las_rutas():
            assert etiqueta in self._ETIQUETAS


_RE_MENCION = re.compile(r"Transparencia: ([^(→\n]+?) \(Art\. (50\.\d)\)")


def _rutas_del_r4() -> str:
    bloque = SYSTEM_PROMPT_CHATBOT.split("#R4 · ")[1].split("\n#R5 · ")[0]
    return bloque.split("\nRutas:\n")[1]


def _linea_de_transparencia() -> str:
    lineas = [
        ln for ln in SYSTEM_PROMPT_CHATBOT.splitlines() if ln.startswith("- Transparencia (Art. 50)")
    ]
    assert len(lineas) == 1, f"se esperaba una sola línea de Transparencia, hay {len(lineas)}"
    return lineas[0]


def _menciones_de_las_rutas() -> list[tuple[str, str]]:
    return _RE_MENCION.findall(_rutas_del_r4())


def _bloque_cambio_estado() -> str:
    bloque = SYSTEM_PROMPT_CHATBOT.split("CONDICIONES DE CAMBIO DE ESTADO")[1]
    return bloque.split("BLOQUE #S")[0]


def _seccion_7() -> str:
    bloque = SYSTEM_PROMPT_CHATBOT.split("7. FORMATO DEL INFORME FINAL")[1]
    return bloque.split("8. REGLAS DE SEGURIDAD Y LÍMITES")[0]


def _bloque_regla_fecha() -> str:
    bloque = SYSTEM_PROMPT_CHATBOT.split("REGLA CRÍTICA — El informe no lleva fecha:")[1]
    return bloque.split("REGLA CRÍTICA — No inventes datos de contexto:")[0]


def _bloque_regla_art_27() -> str:
    bloque = SYSTEM_PROMPT_CHATBOT.split(
        "REGLA — La evaluación de impacto sobre los derechos fundamentales"
    )[1]
    return bloque.split("REGLA — El registro en la base de datos de la UE")[0]


def _bloque_regla_art_49() -> str:
    bloque = SYSTEM_PROMPT_CHATBOT.split("REGLA — El registro en la base de datos de la UE")[1]
    return bloque.split("Obligaciones por tipo de sistema:")[0]


def _linea_que_contiene(fragmento: str) -> str:
    lineas = [ln for ln in SYSTEM_PROMPT_CHATBOT.splitlines() if fragmento in ln]
    assert len(lineas) == 1, f"se esperaba una sola línea con {fragmento!r}, hay {len(lineas)}"
    return lineas[0]

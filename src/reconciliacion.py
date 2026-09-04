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

"""Contraste del registro de obligaciones contra sí mismo y contra la narración del modelo.

El registro de cumplimiento se llena con lo que el modelo emite en bloques <<<OBLIGACION>>>.
Cuando deja de emitirlos, el registro se queda corto y el informe calcula un porcentaje
impecable sobre datos que faltan: en el recorrido del 4 de septiembre la conversación evaluó
once obligaciones, el registro guardó dos, y la portada declaró un 100 % de cumplimiento en la
misma página en que documentaba una carencia legal. Nada comparaba las dos cuentas.

Este módulo las compara. No repara nada y no escribe en el registro: `obligaciones_registradas`
sigue siendo la única fuente de datos, y lo que hay aquí son auditores que devuelven avisos.

Dos niveles, y la diferencia importa al leer el resultado:

- BLOQUEANTE: la comprobación contrasta estructura contra estructura. Si salta, los datos son
  demostrablemente incoherentes.
- INDICIO: la comprobación depende de parsear la prosa del modelo. Si salta, el registro *pudo*
  perder obligaciones, y el aviso lo dice sin afirmar una cifra exacta.

Los dos niveles suprimen el porcentaje del informe. El nivel cambia la redacción, no si el
número se imprime: el 100 % del recorrido solo lo detecta un indicio, así que dejar que los
indicios publiquen cifra sería no haber arreglado nada.

El módulo es lógica pura —sin Streamlit y sin LLM— para que report_generator pueda importarlo y
para que sus tests no necesiten clave de API.
"""

from __future__ import annotations

import re

GRAVEDAD_BLOQUEANTE = "bloqueante"
GRAVEDAD_INDICIO = "indicio"

# Referencia a un artículo dentro de texto libre: "Art. 27", "Art 26.5", "Artículo 50.2".
_RE_ARTICULO = re.compile(r"Art(?:\.|ículo|iculo)?\s*(\d+(?:\.\d+)*)", re.IGNORECASE)

_RE_ESPACIOS = re.compile(r"\s+")


def _norm(valor: object) -> str:
    """Minúsculas, sin espacios de sobra. Para comparar texto que redacta el modelo."""
    return _RE_ESPACIOS.sub(" ", str(valor or "").strip().lower())


def _articulos_citados(texto: str) -> set[str]:
    """Números de artículo mencionados en un texto libre: 'carencia del Art. 27' → {'27'}."""
    return {m.group(1) for m in _RE_ARTICULO.finditer(texto or "")}


def _articulo_de(obl: dict) -> str:
    """Número de artículo de una obligación registrada: 'Art. 26.5' → '26.5'."""
    m = _RE_ARTICULO.search(str(obl.get("articulo", "")))
    return m.group(1) if m else ""


def _etiqueta(obl: dict) -> str:
    """'Art. 26.5 — Vigilancia del funcionamiento [implementador]', para los detalles."""
    rol = obl.get("rol", "")
    sufijo = f" [{rol}]" if rol else ""
    return f"{obl.get('articulo', '?')} — {obl.get('titulo', '')}{sufijo}"


def _incoherencia(codigo: str, gravedad: str, mensaje: str, detalle: list[str]) -> dict:
    """Las incoherencias son dicts planos: app.py serializa cumplimiento_data entera al
    exportar la sesión, y una dataclass obligaría a convertirla por el camino."""
    return {"codigo": codigo, "gravedad": gravedad, "mensaje": mensaje, "detalle": detalle}


# ── Bloqueantes: estructura contra estructura ─────────────────────────────────


def _payload_comparable(obl: dict) -> tuple[str, str, str, str]:
    """La identidad descriptiva de una obligación, sin el estado.

    El estado se excluye a propósito: cambiarlo es una recalificación, que ya tiene su propio
    registro en conflictos_registrados. Lo que aquí interesa es si la entrada nueva describe
    *otra cosa* que la que ha desplazado.
    """
    return (
        _norm(obl.get("articulo")),
        _norm(obl.get("titulo")),
        _norm(obl.get("tipo") or "obligacion"),
        _norm(obl.get("descripcion")),
    )


def _colapso_identidad(desplazadas: list[dict]) -> list[dict]:
    """Dos obligaciones distintas del catálogo registradas bajo la misma identidad.

    El caso que lo motiva: el catálogo del implementador tiene dos entradas de Art. 26.5
    —vigilancia e incidentes graves— y la clave de registro es (articulo, titulo, rol) cuando
    el modelo no devuelve la clave del catálogo. Si les da el mismo título, la segunda desplaza
    a la primera y el recuento baja de once a diez sin dejar rastro.

    No se repara: gana la última, como siempre, pero la desplazada se conserva íntegra y aquí
    se declara qué se perdió. Reconstruir la entrada perdida exigiría adivinar cuál de los dos
    títulos correspondía a cuál obligación, y una obligación fabricada con el estado copiado de
    otra es peor que un hueco declarado.

    Cuando las dos entradas traen la MISMA clave del catálogo no hay colapso por definición: la
    clave es la identidad, y que el modelo reformule el título o la descripción de una
    obligación que ya identificó no la convierte en otra.
    """
    incoherencias = []
    for evento in desplazadas:
        previa = evento.get("previa", {})
        nueva = evento.get("nueva", {})
        clave_previa, clave_nueva = _norm(previa.get("clave")), _norm(nueva.get("clave"))
        if clave_previa and clave_previa == clave_nueva:
            continue
        if _payload_comparable(previa) == _payload_comparable(nueva):
            continue
        incoherencias.append(_incoherencia(
            "colapso_identidad",
            GRAVEDAD_BLOQUEANTE,
            f"Dos obligaciones distintas se registraron con la misma identidad "
            f"({_etiqueta(nueva)}). La segunda desplazó a la primera y el recuento bajó en una.",
            [
                f"Desplazada (turno {evento.get('turno', '?')}): {_etiqueta(previa)} — "
                f"{str(previa.get('estado', '')).upper()} — {previa.get('descripcion', '')}",
                f"Prevalece: {_etiqueta(nueva)} — {str(nueva.get('estado', '')).upper()} — "
                f"{nueva.get('descripcion', '')}",
            ],
        ))
    return incoherencias


def _carencias_huerfanas(obligaciones: list[dict], carencias: list[str]) -> list[dict]:
    """Carencias narradas en el cierre que ninguna obligación del registro respalda.

    En el recorrido, el Art. 27 llegó solo por <<<CIERRE>>>: se imprimía en «Áreas de mejora
    legales (1)» y en el resumen, pero contaba 0 en «No cubiertas» y quedaba fuera del
    denominador. Una carencia que se imprime en prosa y desaparece del contador.

    Solo se comprueban las carencias que citan un artículo. Una carencia sin artículo no se
    puede contrastar contra nada, y aquí no se inventa: se deja pasar.
    """
    articulos_en_carencia = {
        _articulo_de(o) for o in obligaciones if o.get("estado") == "carencia"
    }
    articulos_en_carencia.discard("")

    huerfanas = [
        c for c in carencias
        if _articulos_citados(c) and not (_articulos_citados(c) & articulos_en_carencia)
    ]
    if not huerfanas:
        return []
    return [_incoherencia(
        "carencia_huerfana",
        GRAVEDAD_BLOQUEANTE,
        f"{len(huerfanas)} carencia(s) del resumen no tienen obligación correspondiente en "
        "estado carencia: se imprimirían como área de mejora sin contar en el denominador.",
        list(huerfanas),
    )]


def _carencias_no_declaradas(obligaciones: list[dict], carencias: list[str]) -> list[dict]:
    """La inversa: obligación legal en carencia que el cierre no lista como carencia.

    Produce la contradicción a la inversa —el contador dice que hay incumplimientos y la
    sección de áreas de mejora aparece vacía o corta—, y es el mismo desajuste entre los dos
    canales, <<<OBLIGACION>>> y <<<CIERRE>>>, que nunca se reconciliaron.
    """
    citados: set[str] = set()
    for c in carencias:
        citados |= _articulos_citados(c)

    no_declaradas = [
        o for o in obligaciones
        if o.get("estado") == "carencia"
        and o.get("tipo", "obligacion") == "obligacion"
        and _articulo_de(o) not in citados
    ]
    if not no_declaradas:
        return []
    return [_incoherencia(
        "carencia_no_declarada",
        GRAVEDAD_BLOQUEANTE,
        f"{len(no_declaradas)} obligación(es) legal(es) figuran como carencia en el registro "
        "pero no aparecen entre las carencias del resumen.",
        [_etiqueta(o) for o in no_declaradas],
    )]


def _registro_reconstruido() -> dict:
    """El análisis no viene de bloques estructurados sino de raspar la prosa del historial."""
    return _incoherencia(
        "registro_reconstruido",
        GRAVEDAD_BLOQUEANTE,
        "El registro estructurado llegó vacío y las obligaciones se han reconstruido a partir "
        "del texto de la conversación. No hay garantía de que estén todas ni de que sus estados "
        "sean los definitivos.",
        [],
    )


# ── Indicios: dependen de parsear la prosa del modelo ─────────────────────────


def _roles_distintos(obligaciones: list[dict]) -> int:
    """Roles del catálogo presentes en el registro, sin contar el transversal."""
    roles = {_norm(o.get("rol")) for o in obligaciones}
    return len(roles - {"", "transversal"})


def _recuento_narrado(obligaciones: list[dict], narracion: dict) -> list[dict]:
    """La cuenta que narra el modelo contra la que lleva la aplicación.

    Es la comparación que faltaba: el asistente decía «Obligación 10 de 11» mientras el registro
    tenía una sola entrada, y ninguna de las dos cuentas miraba a la otra.

    La dirección «registradas > narradas» solo se reporta con un único rol. Con varios roles el
    modelo reinicia la numeración en cada uno y el total narrado es el del rol en curso, así que
    superar M es lo normal y avisar sería ruido. Con rol único no lo es, y es además la firma de
    la deriva de claves que esta rama asume como riesgo.
    """
    total = narracion.get("total_declarado")
    if not total:
        return []

    registradas = len(obligaciones)
    if total > registradas:
        return [_incoherencia(
            "recuento_narrado",
            GRAVEDAD_INDICIO,
            f"El análisis anunció {total} obligaciones y el registro solo tiene {registradas}: "
            f"pudieron perderse {total - registradas}.",
            [f"Último total narrado: {total}. Obligaciones registradas: {registradas}."],
        )]

    if registradas > total and _roles_distintos(obligaciones) <= 1:
        return [_incoherencia(
            "recuento_narrado",
            GRAVEDAD_INDICIO,
            f"El registro tiene {registradas} obligaciones y el análisis solo anunció {total}: "
            "alguna pudo registrarse dos veces bajo identidades distintas.",
            [f"Último total narrado: {total}. Obligaciones registradas: {registradas}."],
        )]
    return []


def _narradas_no_registradas(obligaciones: list[dict], narracion: dict) -> list[dict]:
    """Obligaciones del resumen final del modelo que no están en el registro.

    Dice *qué* falta, y no solo cuánto. Se contrasta por artículo y no por título: los títulos
    los redacta el modelo y compararlos literalmente convertiría cualquier reformulación en una
    falsa ausencia. Una obligación cuenta como registrada si el registro tiene alguna entrada de
    su mismo artículo — deliberadamente conservador, porque el precio de un falso positivo aquí
    es suprimir un porcentaje legítimo.
    """
    resumen = narracion.get("resumen_final") or []
    if not resumen:
        return []

    articulos_registrados = {_articulo_de(o) for o in obligaciones}
    articulos_registrados.discard("")

    ausentes = [
        linea for linea in resumen
        if _articulo_de(linea) and _articulo_de(linea) not in articulos_registrados
    ]
    if not ausentes:
        return []
    return [_incoherencia(
        "narrada_no_registrada",
        GRAVEDAD_INDICIO,
        f"{len(ausentes)} obligación(es) aparecen en el resumen final del análisis y no están "
        "en el registro.",
        [
            f"{o.get('articulo', '?')} — {o.get('titulo', '')}: "
            f"{str(o.get('estado', '')).upper()}"
            for o in ausentes
        ],
    )]


def _no_verificable(narracion: dict) -> list[dict]:
    """Ni un ordinal narrado ni una línea de resumen final: no hay contra qué contrastar.

    Este es el caso que no puede leerse como conformidad. Un parser que no encuentra nada no ha
    verificado nada, y devolver «sin incoherencias» sería convertir el silencio en un visto
    bueno — exactamente el modo de fallo que arreglamos, en otro sitio.
    """
    if narracion.get("total_declarado") or narracion.get("ordinal_max"):
        return []
    if narracion.get("resumen_final"):
        return []
    return [_incoherencia(
        "no_verificable",
        GRAVEDAD_INDICIO,
        "El análisis no dejó traza narrada —ni numeración de obligaciones ni resumen final— "
        "contra la que contrastar el registro. No se puede afirmar que esté completo.",
        [],
    )]


# ── Entrada pública ───────────────────────────────────────────────────────────


def reconciliar(
    obligaciones: list[dict],
    carencias: list[str],
    desplazadas: list[dict],
    narracion: dict,
    reconstruido: bool = False,
) -> list[dict]:
    """Devuelve las incoherencias del análisis, las bloqueantes primero.

    `desplazadas` son los eventos {"previa", "nueva", "turno"} que anota el registro cuando una
    entrada sustituye a otra; `narracion` es lo que se ha podido leer de la prosa del modelo
    ({"total_declarado", "ordinal_max", "resumen_final"}); `reconstruido` marca el análisis que
    no viene de bloques estructurados sino de raspar el historial.

    Lista vacía significa que las comprobaciones se hicieron y salieron limpias, nunca que no
    hubo nada que comprobar: ese caso lo declara `no_verificable`.
    """
    bloqueantes = (
        _colapso_identidad(desplazadas)
        + _carencias_huerfanas(obligaciones, carencias)
        + _carencias_no_declaradas(obligaciones, carencias)
    )
    if reconstruido:
        bloqueantes.insert(0, _registro_reconstruido())

    indicios = (
        _recuento_narrado(obligaciones, narracion)
        + _narradas_no_registradas(obligaciones, narracion)
        + _no_verificable(narracion)
    )
    return bloqueantes + indicios


def hay_bloqueantes(incoherencias: list[dict]) -> bool:
    return any(i.get("gravedad") == GRAVEDAD_BLOQUEANTE for i in incoherencias)


def motivo_no_calculable(incoherencias: list[dict]) -> str:
    """Por qué el informe no publica cifra. La redacción cambia con el nivel; la supresión no.

    Con una bloqueante la afirmación es fuerte, porque la comprobación fue determinista. Con
    solo indicios se dice que el registro *pudo* perder obligaciones, sin comprometer una cifra
    que no tenemos. Y cuando lo único que hay es `no_verificable`, ni siquiera eso: no se ha
    podido comprobar.
    """
    if hay_bloqueantes(incoherencias):
        return (
            "El registro de obligaciones es demostrablemente incoherente, así que un porcentaje "
            "calculado sobre él sería engañoso."
        )
    codigos = {i.get("codigo") for i in incoherencias}
    if codigos == {"no_verificable"}:
        return (
            "El análisis no dejó traza narrada contra la que contrastar el registro, así que no "
            "consta que las obligaciones evaluadas estén todas."
        )
    return (
        "El registro pudo perder obligaciones durante el análisis, así que un porcentaje "
        "calculado sobre él daría una precisión que los datos no tienen."
    )

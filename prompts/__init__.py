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

# Versión del conjunto de prompts (árbol de decisión + catálogo de obligaciones).
# Incrementar al modificar system_prompts.py, system_prompts_local.py
# o system_prompt_cumplimiento.py.
#
# Historial:
# 2026.09.9 (2026-09-08): las salidas terminales que no son un nodo del árbol cierran también la
#                          evaluación. La comprobación previa de definición decía «resultado NO
#                          CUMPLE LA DEFINICIÓN DE SISTEMA DE IA. Explica al usuario…» y ahí
#                          terminaba: sin FIN, sin informe y sin [EVALUACION_COMPLETA]. Y la
#                          regla general de la señal la condicionaba a haber alcanzado «un nodo
#                          FIN», mientras que esa comprobación se declara previa al árbol. El
#                          modelo obedecía literalmente —explicaba y se detenía— y la aplicación
#                          se quedaba sin clasificación, sin nodos recorridos, sin informe y con
#                          una sesión vacía: el recorrido del ejemplo 00 no produjo nada que
#                          publicar. EXCLUIDO sí funcionaba porque vive en #R2, que es un nodo
#                          con FIN, y las dos son las clasificaciones sin obligaciones que
#                          src/clasificaciones.py trata igual desde B1. Auditadas todas las
#                          salidas que declaran un resultado, había dos más en la misma
#                          situación: «EXCLUIDO como fabricante de producto» de #E3 y la
#                          exclusión por ámbito territorial de #S1. Las tres llevan ahora FIN,
#                          informe con la estructura del punto 6 y señal, la regla general
#                          reconoce como cierre cualquier salida terminal y no solo los nodos, y
#                          la de la definición previa recuerda que su traza es corta pero
#                          existe. Mismo arreglo en el prompt local, que tenía las tres iguales
# 2026.09.8 (2026-09-08): el árbol conserva el estado ya establecido y deja de convertir en
#                          proveedor al implementador por el solo hecho de que el sistema sea
#                          de alto riesgo. El Art. 50 se reparte por rol en el catálogo de
#                          cumplimiento —50.1 y 50.2 obligan al proveedor; 50.3 y 50.4, al
#                          responsable del despliegue—, con clave en cada entrada: a una
#                          agencia de viajes implementadora se le imputó como carencia legal
#                          con fecha límite el Art. 50.2, que no es suya. Al responsable del
#                          despliegue el 50.1 y el 50.2 no se le retiran de la vista: se
#                          presentan como obligación de su proveedor y punto de vigilancia
#                          suyo, fuera del cómputo del porcentaje y nunca como carencia.
#                          Corregido además el texto del 50.4, que describía la obligación del
#                          50.2: no es marcado legible por máquina, es hacer público que el
#                          contenido se ha generado o manipulado artificialmente, y solo en
#                          sus dos supuestos —ultrasuplantación y texto de interés público—.
#                          En el evaluador, el nodo #R4 dice de quién es cada función del Art.
#                          50 y tres correcciones de encaminamiento: la ruta del contenido
#                          sintético llevaba la etiqueta del 50.4 (del responsable del
#                          despliegue) a una función del 50.2 (del proveedor); la ruta comodín
#                          salía a FIN sin mirar el alto riesgo, así que una obligación de
#                          transparencia de más hacía que el implementador de alto riesgo no
#                          llegara a #R5 y se saltara la pregunta del Art. 27; y las ocho
#                          rutas usan ya el mismo predicado, «implementador de alto riesgo»,
#                          que es el que exige el cierre de #R5 y el Art. 27.1
# 2026.09.7 (2026-09-07): el informe del evaluador deja de llevar fecha —la estampa la
#                          aplicación, que es quien la sabe— tras abrir con «Fecha de
#                          evaluación: Junio de 2025» un recorrido hecho el 7 de septiembre de
#                          2026; con ella, la prohibición general de rellenar con valores
#                          plausibles cualquier dato de contexto que no conste en la
#                          conversación. Las dos van también, en una línea, al prompt local.
#                          La documentación técnica aportada se inyecta ahora en el prompt del
#                          evaluador en cada turno, envuelta como dato no confiable, con la
#                          instrucción de buscar en ella antes de preguntar y de confirmar
#                          siempre con el usuario: con una ficha que decía «red neuronal de
#                          detección de objetos entrenada con imágenes térmicas», el evaluador
#                          preguntaba igualmente si había aprendizaje automático
# 2026.09.6 (2026-09-06): el catálogo pasa a ser la única lista del recorrido de cumplimiento
#                          (punto 9 nuevo, renumerados persistencia y cierre a 11 y 12). Las
#                          «Obligaciones ya identificadas en la evaluación» que llegan en
#                          {contexto_evaluacion} informan del ESTADO, no de si la obligación
#                          entra: el modelo leyó la conclusión del evaluador sobre el Art. 49
#                          como asunto cerrado, anunció once obligaciones y se saltó la
#                          duodécima en silencio, sin que la reconciliación pudiera verlo.
#                          Una condicional que no encaja se registra "no_aplica" y nunca se
#                          omite; cuando la evaluación ya trae la respuesta se presenta, se
#                          dice que quedó resuelta y se registra sin repreguntar. Mismo
#                          mecanismo y misma redacción que las decisiones 9 y 10 de
#                          SPEC-ART-111 para el Art. 50.2
# 2026.09.5 (2026-09-06): la evaluación de impacto sobre los derechos fundamentales (Art. 27)
#                          pasa a obligación condicional con la misma forma que ya tenía el
#                          Art. 49 —preguntar primero, "no_aplica" explícito y prohibición de
#                          registrarla como carencia—, en el catálogo de cumplimiento y en el
#                          prompt del evaluador. El Art. 27.1 solo alcanza a organismos de
#                          Derecho público, entidades privadas que prestan servicios públicos y
#                          responsables del despliegue del Anexo III punto 5(b) y 5(c): el
#                          empleo es el punto 4, y se declaraba carencia prioritaria de una
#                          PYME privada contra la condición que el propio informe imprimía
# 2026.09.4 (2026-09-06): el prompt del evaluador deja de atribuir al implementador el
#                          registro en la base de datos de la UE (Arts. 49 y 71) y la
#                          notificación a la NCA (Arts. 6.4 y 49.2), que son del proveedor:
#                          con la misma forma que ya tenía el catálogo de cumplimiento
#                          —preguntar primero y prohibición explícita— para que las dos
#                          pestañas no den respuestas opuestas sobre el mismo artículo.
#                          El evaluador cita además el Art. 26 sin apartado: no tiene el
#                          catálogo por apartados y los numeraba de memoria (26.2 por 26.4,
#                          26.4 por 26.5). El detalle lo aporta la pestaña Cumplimiento
# 2026.09.3 (2026-09-04): el bloque <<<OBLIGACION>>> admite el campo "clave", que copia la
#                          clave estable que ahora lleva cada entrada del catálogo del
#                          implementador y del Art. 4. Sin ella las dos entradas del
#                          Art. 26.5 colapsaban en una si el modelo les daba el mismo
#                          título. Fijado además el significado de la M de "Obligación N
#                          de M": el total del catálogo, no lo registrado hasta el momento
# 2026.09.2 (2026-09-04): apartados del Art. 26 renumerados según el consolidado a 27-07-2026
#                          —datos de entrada 26.3→26.4, incidentes graves 26.10→26.5,
#                          cooperación 26.11→26.12— y añadido el 26.11 real: informar a las
#                          personas físicas sobre las que decide un sistema del Anexo III
# 2026.09.1 (2026-09-03): Art. 49 del Rol Implementador convertido en obligación condicional
#                          —solo aplica al implementador que es organismo público o actúa en
#                          su nombre; el privado la recibe como no_aplica, no como carencia—;
#                          las obligaciones preliminares se extraen citando el artículo, sin
#                          apartado
# 2026.09.0 (2026-09-02): calendario Ómnibus adoptado (Reglamento (UE) 2026/1744, en vigor
#                          desde el 27-07-2026); el bloque de fechas se inyecta desde
#                          data/calendario.json; corregidas las fechas del Art. 50
#                          (2 ago 2026, no 2025) y el transitorio del Art. 50.2
# 2026.06.0 (2026-05-27): Fases 2-4 — calendario Ómnibus, correcciones jurídicas
#                          árbol (biometría Art. 5.1.g, NCII/CSAM, código abierto,
#                          distinción GPAI/sistema), catálogo de obligaciones
#                          completado (Art. 17, 73, Rep. Autorizado, Fabricante,
#                          fórmula MÍNIMO, exclusividad Art. 26, Anexo IV detallado)
# 2026.05.0 (baseline)  : Prompts iniciales v0.1.0

PROMPT_VERSION = "2026.09.9"

# Huella del contenido de cada prompt en el momento de estampar PROMPT_VERSION.
#
# La regla de arriba —incrementar al modificar los prompts— vivía solo en ese comentario, y
# entre 2026.09.7 y 2026.09.8 se incumplió en seis commits seguidos: los dos recorridos del
# ejemplo 02, el que imputaba una carencia legal falsa del Art. 50.2 y el que reparte el Art.
# 50 por rol, salieron con el mismo «Prompt v2026.09.7» en el pie (hallazgo B30). Ahora la
# regla la sostiene tests/test_prompt_version.py, que recalcula estas huellas y falla si
# alguna no cuadra.
#
# Al cambiar un prompt: sube PROMPT_VERSION, añade su entrada de historial y pega aquí la
# huella nueva, que el test imprime en el mensaje de fallo. No la actualices sola: sin subir
# la versión, el pie de los informes vuelve a nombrar dos estados distintos con una cadena.
PROMPT_HASHES = {
    "system_prompts.py": "42080de6b457a346bf7fc1083e7ff5be43a04dad0a189b3dbffdf75f09fb5d97",
    "system_prompts_local.py": "5da3164126f98c2ffac88c65f4057abd9f7e8c99bd8fe1c515e5bc99da40c95c",
    "system_prompt_cumplimiento.py": "a8073685385eb19a467e53a20e83d608bb2af25080c128793469bcdaa01fff3c",
}

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

PROMPT_VERSION = "2026.09.5"

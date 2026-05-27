# Conversación de evaluación y clasificación

## Ejemplo
02 — Riesgo limitado

## Tipo de resultado
Riesgo limitado

## Sistema evaluado
CartonAssist B2B es un asistente conversacional basado en IA (RAG + LLM) para clientes profesionales del sector del embalaje de cartón ondulado. Responde consultas comerciales frecuentes, orienta sobre productos y plazos, y prepara solicitudes preliminares de presupuesto. No toma decisiones contractuales vinculantes y escala cualquier consulta con impacto legal a un agente humano.

## Resultado
Clasificación: LIMITADO | Rol: Proveedor / Implementador

## Conversación

Evaluador y clasificador

Describa su sistema de IA en lenguaje natural o inicie a partir de su documentación técnica. Le haré las preguntas necesarias para determinar su clasificación y obligaciones.
INPUT:

He analizado la documentación técnica proporcionada. Esto es lo que he entendido sobre el sistema:
CartonAssist B2B es un asistente conversacional basado en inteligencia artificial diseñado para responder preguntas comerciales frecuentes de clientes profesionales, orientarles sobre productos de embalaje, plazos, cantidades mínimas y preparar solicitudes preliminares de presupuesto, sin tomar decisiones contractuales vinculantes. Opera en el sector industrial de fabricación de embalajes de cartón ondulado, dirigido exclusivamente a un entorno B2B. El sistema es un ejemplo ficticio desarrollado para un hackathon o demo de la herramienta AIComply, y sus usuarios principales son clientes empresariales externos, el equipo comercial que gestiona los escalados, y administradores responsables de su mantenimiento y cumplimiento. El sistema no toma decisiones que afecten directamente a las personas de forma vinculante, ya que no aprueba contratos, no fija precios finales ni resuelve reclamaciones, derivando obligatoriamente cualquier consulta con impacto contractual o legal a un agente humano. En cuanto a datos sensibles, el sistema procesa únicamente mensajes de texto, identificadores de cliente y datos básicos de pedido cuando el usuario se autentica, sin tratar datos biométricos, médicos ni financieros de carácter sensible. El despliegue se realiza mediante un widget de chat integrado en la página web corporativa, con un backend REST que combina recuperación documental aumentada (RAG) con un modelo de lenguaje, y puede ejecutarse en entorno local siguiendo un proceso de instalación estándar basado en Python.
Antes de continuar, ¿es correcta esta descripción? ¿Desea añadir o corregir algo?
Correcta
Perfecto. Antes de comenzar la evaluación, le indico brevemente que este análisis es una orientación basada en el Reglamento (UE) 2024/1689, no un asesoramiento jurídico vinculante. Los resultados deben contrastarse con un profesional especializado.
Dicho esto, la descripción que me ha facilitado encaja claramente con la definición de sistema de IA del Art. 3.1 del Reglamento: CartonAssist B2B infiere respuestas a partir de los mensajes del usuario combinando recuperación documental y un modelo de lenguaje, generando recomendaciones y orientaciones de forma autónoma, en lugar de seguir únicamente reglas fijas predefinidas. Por tanto, el Reglamento (UE) 2024/1689 es aplicable en principio.
Pasamos a la primera pregunta del análisis.
¿Qué tipo de entidad es su organización respecto a CartonAssist B2B?
Según lo que me ha descrito, su empresa ha desarrollado o encargado el sistema y lo despliega internamente bajo su propia marca para atender a sus clientes. Esto sugiere que podría actuar simultáneamente como:
Proveedora: porque ha desarrollado o encargado el sistema y lo pone en servicio bajo su nombre o marca.
Implementadora: porque lo utiliza bajo su propia autoridad en su actividad comercial.
¿Es correcto que su organización ha desarrollado o encargado el desarrollo de CartonAssist B2B y lo opera directamente, sin cedérselo a terceros para que lo exploten bajo su propia marca?
Correcto
Confirmado: su organización actúa como proveedora e implementadora del sistema, ya que lo ha desarrollado o encargado y lo utiliza internamente bajo su propia autoridad. Esta doble condición será tenida en cuenta en el análisis de obligaciones.
Realizaré dos recorridos completos del árbol, uno por cada rol, antes de emitir el informe final.

Comenzamos con el rol de Proveedora.
La siguiente cuestión es si su organización, o algún agente posterior en la cadena (distribuidor, importador, otro implementador), realiza alguna de estas modificaciones sobre CartonAssist B2B:
Poner un nombre o marca diferente al sistema
Modificar la finalidad prevista del sistema una vez en operación
Realizar una modificación sustancial del sistema
O bien ninguna de las anteriores.
Dado que el sistema parece desplegarse directamente por su propia organización sin intermediarios, lo más probable es que no aplique ninguna de estas situaciones. ¿Es así?
Ninguno
Confirmado. No se producen modificaciones relevantes por agentes posteriores.
Pasamos a evaluar si CartonAssist B2B podría clasificarse como sistema de alto riesgo.

Primera verificación de alto riesgo:
Por lo que me ha descrito, CartonAssist B2B es un asistente conversacional para consultas comerciales sobre embalajes de cartón. Las categorías de esta primera verificación hacen referencia a sistemas relacionados con la seguridad de la aviación civil, vehículos de motor, equipos marinos, sistemas ferroviarios, vehículos agrícolas, etc.
Ninguna de estas categorías parece aplicar a su caso. ¿Es correcto que CartonAssist B2B no tiene ninguna relación con ninguno de estos sectores de transporte o vehículos?
Correcto
Confirmado. Pasamos a la siguiente verificación.

Segunda verificación de alto riesgo:
Esta verificación analiza si el sistema actúa como componente de seguridad de productos regulados o maquinaria industrial. Las tres situaciones posibles son:
(a) El sistema envía señales de control a maquinaria industrial (robots, PLCs, actuadores) y sus decisiones disparan acciones físicas automáticas.
(b) El sistema decide qué piezas o productos superan el control de calidad y pueden comercializarse, siendo esos productos destinados a sectores regulados (vehículos, equipos médicos, etc.).
(c) El sistema está integrado físicamente dentro de un producto regulado que se entrega al cliente.
Dado que CartonAssist B2B es un asistente conversacional que responde preguntas comerciales y orienta sobre productos de embalaje, ninguna de estas situaciones parece aplicar. ¿Es correcto?
Correcto
Confirmado. Pasamos a la verificación de alto riesgo por categorías del Anexo III.

Tercera verificación de alto riesgo:
El Anexo III recoge categorías de sistemas que pueden considerarse de alto riesgo por el impacto que tienen sobre personas. Le presento las categorías relevantes aplicando el contexto de su sistema:
Biometría: CartonAssist B2B no procesa datos biométricos. No aplica.
Infraestructuras críticas: Es un asistente comercial de embalajes. No aplica.
Educación y formación profesional: No evalúa ni selecciona estudiantes. No aplica.
Empleo y gestión de trabajadores: No toma decisiones sobre contratación, promoción ni condiciones laborales. No aplica.
Acceso a servicios esenciales: No decide sobre créditos, seguros, prestaciones públicas ni servicios básicos. No aplica.
Aplicación de la ley, migración o justicia: Claramente fuera de su ámbito.
¿Confirma que ninguna de estas categorías describe la función de CartonAssist B2B?
Ninguna
Confirmado. CartonAssist B2B no entra en ninguna categoría de alto riesgo.

Pasamos ahora a verificar el ámbito territorial de aplicación del Reglamento.
CartonAssist B2B se despliega mediante un widget de chat en una página web corporativa y, según lo descrito, está orientado a clientes profesionales. ¿La empresa está establecida en la Unión Europea, o bien el sistema se comercializa o utiliza por clientes en la UE?
Sí, estamos en España
Confirmado. El Reglamento (UE) 2024/1689 es aplicable, ya que la organización está establecida en España, que es un Estado miembro de la UE.

Última verificación antes del informe: prácticas prohibidas y transparencia.
Tengo dos preguntas rápidas sobre las funciones de CartonAssist B2B:
Primera: ¿El sistema realiza alguna de estas funciones problemáticas?
Manipulación subliminal o engaño a los usuarios
Explotación de vulnerabilidades (edad, discapacidad, situación económica)
Puntuación social o predicción de comportamiento con fines sancionadores
Reconocimiento biométrico o de emociones
Dado que es un asistente conversacional B2B de consultas comerciales, intuyo que ninguna aplica. ¿Es correcto?
Correcto
Confirmado. Pasamos a la última verificación.
Segunda: CartonAssist B2B es un chatbot que interactúa directamente con personas. El Reglamento exige que los usuarios sean informados de que están hablando con un sistema de IA y no con una persona humana.
¿El sistema informa a los usuarios de esta circunstancia cuando inician la conversación? Por ejemplo, mediante un mensaje de bienvenida del tipo "Soy un asistente virtual" o similar.
Sí, hay un mensaje al abrir el chatbot
Perfecto. Con eso queda cubierta la obligación de transparencia del Art. 50.1.
Tengo toda la información necesaria para elaborar el informe final. Aquí lo tiene:

INFORME DE EVALUACIÓN DE CUMPLIMIENTO

Ley de IA de la UE — Reglamento (UE) 2024/1689

Sistema evaluado: CartonAssist B2B


1. Resumen ejecutivo

CartonAssist B2B es un asistente conversacional B2B para consultas comerciales en el sector del embalaje de cartón ondulado. La organización actúa como proveedora e implementadora del sistema. Según la información facilitada, el sistema no es de alto riesgo, no incurre en ninguna práctica prohibida y está sujeto a obligaciones de alfabetización en IA y transparencia frente a usuarios.

2. Tus obligaciones

Aplicables actualmente (desde febrero de 2025)

a) Alfabetización en IA — Art. 4 Debes garantizar que el personal que trabaja con CartonAssist B2B —tanto el equipo técnico que lo mantiene como el equipo comercial que gestiona los escalados— tenga un nivel suficiente de conocimientos sobre inteligencia artificial: qué es, cómo funciona a grandes rasgos, cuáles son sus limitaciones y qué riesgos puede conllevar. No se exige una formación técnica avanzada, sino una comprensión proporcional a la función de cada persona.
Acción práctica: documenta las acciones formativas realizadas (cursos, sesiones internas, materiales) y guarda registro de quién las ha completado.
b) Transparencia frente a usuarios — Art. 50.1 Los usuarios que interactúan con CartonAssist B2B deben saber que están hablando con un sistema de IA y no con una persona humana. Según lo confirmado, el sistema ya muestra un mensaje al abrir el chat que cumple este requisito.
Acción práctica: asegúrate de que ese mensaje sea claro, visible y previo a cualquier intercambio de información. Consérvalo como evidencia de cumplimiento.
Sin obligaciones adicionales de alto riesgo

El sistema no ha sido clasificado como de alto riesgo, por lo que no aplican las obligaciones del Art. 16 (proveedor) ni del Art. 26 (implementador) para sistemas de alto riesgo.

3. Recorrido realizado (traza auditable)

Pregunta evaluada
Respuesta
Origen
¿Es un sistema de IA según el Art. 3.1?
Sí — infiere respuestas a partir de datos mediante RAG + LLM
Inferencia confirmada
Tipo de entidad
Proveedor e implementador (desarrolla y usa el sistema internamente bajo su marca)
Inferencia confirmada
Modificaciones por agentes posteriores
Ninguna
Respuesta directa
Alto riesgo — Anexo I, Sección B (transporte y vehículos)
No aplica
Inferencia confirmada
Alto riesgo — Anexo I, Sección A (productos regulados / maquinaria)
No aplica
Inferencia confirmada
Alto riesgo — Anexo III (biometría, empleo, servicios esenciales, etc.)
No aplica
Respuesta directa
Ámbito territorial
Aplicable — organización establecida en España
Respuesta directa
Prácticas prohibidas — Art. 5
Ninguna aplica
Respuesta directa
Transparencia — interacción con personas físicas (Art. 50.1)
Sí, el sistema informa al usuario al abrir el chat
Respuesta directa

4. Puntos que requieren revisión profesional

No se han identificado nodos indeterminados en esta evaluación. No obstante, se recomienda revisar con un profesional los siguientes aspectos si el sistema evoluciona:
Ampliación de funciones: si CartonAssist B2B comenzara a tomar decisiones con impacto contractual (aprobación de precios, gestión de crédito, evaluación de solvencia de clientes), podría reclasificarse como sistema de alto riesgo bajo el Anexo III.
Tratamiento de datos personales: el sistema procesa identificadores de cliente y datos de pedido. Aunque esto no afecta a la clasificación bajo la Ley de IA, puede tener implicaciones bajo el RGPD que conviene verificar con un especialista en protección de datos.
Modificaciones sustanciales: cualquier cambio relevante en la arquitectura, el modelo subyacente o la finalidad del sistema podría requerir una nueva evaluación de cumplimiento.

5. Roles evaluados

Se ha realizado un único recorrido, correspondiente al doble rol Proveedor + Implementador. No se han identificado roles adicionales que requieran recorridos separados.

6. Aviso legal

Este informe es una orientación preliminar basada en la información facilitada y no constituye asesoramiento jurídico vinculante. La clasificación y las obligaciones descritas deben ser contrastadas con un profesional especializado en derecho tecnológico o cumplimiento normativo antes de tomar decisiones empresariales. El Reglamento (UE) 2024/1689 está sujeto a desarrollo reglamentario y a modificaciones derivadas del acuerdo provisional Ómnibus de mayo de 2026, aún pendiente de publicación en el Diario Oficial de la UE.

Evaluación completada — Clasificación: LIMITADO | Rol: Proveedor / Implementador
Proceda a la pestaña Cumplimiento para revisar sus obligaciones concretas.

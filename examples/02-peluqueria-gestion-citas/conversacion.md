# Conversación AIComply — Caso 02: Peluquería, gestión de citas

## Tab: Evaluador

---

**AIComply:** Bienvenido. Antes de comenzar, una aclaración importante: este asistente ofrece orientación basada en el Reglamento (UE) 2024/1689 (Ley de IA de la UE), pero no constituye asesoramiento jurídico vinculante. Los resultados que obtengas aquí deben contrastarse con un profesional cualificado.

Dicho esto, vamos a evaluar tu sistema.

Lo que describes es una herramienta que:

1. Recibe una descripción en lenguaje natural del cliente (lo que quiere hacerse).
2. Estima la duración del servicio a partir de esa descripción.
3. Recomienda huecos disponibles compatibles con la agenda del profesional.

Para que el Reglamento de IA de la UE sea aplicable, lo primero que necesito confirmar es si esto encaja en la definición de sistema de IA según la Ley.

La definición, en términos sencillos, es esta: un sistema de IA es un programa que, a partir de unos datos de entrada, deduce por su cuenta una respuesta (una predicción, una recomendación, una decisión), en lugar de seguir únicamente reglas fijas escritas a mano por un programador.

La diferencia clave está en esa capacidad de inferencia o aprendizaje: si el sistema simplemente aplica un calendario de reglas como "si el servicio es X, dura 30 minutos", eso no sería un sistema de IA según la Ley. Pero si analiza la descripción del cliente y estima o deduce la duración de forma más o menos autónoma, probablemente sí lo sería.

¿Podrías indicarme cómo funciona internamente la estimación de duración y la recomendación de huecos? Por ejemplo: ¿usa algún modelo de lenguaje, aprendizaje automático, o se basa en reglas fijas predefinidas?

**Usuario:** En función de la descripción del cliente, la IA reconoce los distintos tratamientos que ofrece la peluquería, calcula su duración y ofrece la fecha y las horas disponibles.

**AIComply:** Gracias por la aclaración. Con esta descripción, el sistema sí encaja en la definición de sistema de IA según el Art. 3.1 del Reglamento: recibe texto en lenguaje natural, infiere qué tratamientos corresponden a la descripción del cliente y genera una recomendación (fecha y hora). Hay inferencia automática a partir de la entrada, no una simple búsqueda por reglas fijas.

Confirmado esto, pasamos a la evaluación propiamente dicha.

La primera pregunta es sobre el tipo de entidad que sois en relación con este sistema. Necesito entender cuál es vuestro papel:

- **Desarrollador/proveedor:** ¿Habéis desarrollado vosotros este sistema (o lo habéis encargado desarrollar) y lo comercializáis o ponéis en servicio bajo vuestro nombre o marca? ¿O lo ofrecéis a otras peluquerías como producto o servicio?
- **Implementador/usuario:** ¿Usáis un sistema desarrollado por un tercero dentro de vuestra propia peluquería, bajo vuestra responsabilidad operativa?
- **Ambos:** ¿Desarrolláis el sistema y además lo usáis vosotros mismos en vuestro negocio?

¿Cuál de estas situaciones describe mejor la vuestra?

**Usuario:** La he hecho yo y la uso en mi local.

**AIComply:** Perfecto. En ese caso sois a la vez Proveedor (habéis desarrollado el sistema) e Implementador (lo usáis en vuestro propio local). Esto es habitual en pymes que construyen sus propias herramientas internas.

Evaluaré los dos roles por separado, empezando por el de Proveedor, que conlleva más obligaciones. Después haré el recorrido para el rol de Implementador, reutilizando todo lo que ya hayamos establecido.

---

**Recorrido 1 de 2 — Rol: Proveedor**

La siguiente pregunta es sobre posibles modificaciones al sistema. Dado que sois vosotros quienes lo habéis desarrollado y no hay un proveedor original distinto, este punto no genera obligaciones adicionales en vuestro caso.

Pasamos directamente a clasificar el nivel de riesgo del sistema.

El primer filtro es si vuestro sistema entra en alguna categoría relacionada con transporte y vehículos: aviación civil, vehículos de motor, equipos marinos, sistemas ferroviarios, vehículos agrícolas, etc.

Dado que se trata de un sistema de gestión de citas para una peluquería, ninguna de estas categorías parece aplicable. ¿Es correcto que vuestro sistema no tiene ninguna relación con el sector del transporte?

**Usuario:** correcto

**AIComply:** Confirmado. Tampoco parece que el sistema entre en la categoría de productos regulados como máquinas, juguetes, ascensores, productos sanitarios, equipos de presión, etc.

¿Es correcto que el sistema no forma parte de ningún producto físico de este tipo?

**Usuario:** correcto

**AIComply:** Confirmado. Pasamos al siguiente filtro, que es el más relevante para vuestro caso.

Necesito saber si vuestro sistema entra en alguna de las categorías de alto riesgo del Anexo III del Reglamento. Os presento las categorías; marcad todas las que puedan aplicar:

1. Biometría: identificación, categorización o reconocimiento de personas por rasgos físicos, de comportamiento o biológicos.
2. Infraestructuras críticas: gestión de redes de energía, agua, transporte, etc.
3. Educación y formación profesional: acceso, admisión o evaluación en centros educativos.
4. Empleo y gestión de trabajadores: selección de personal, evaluación del rendimiento, asignación de tareas, vigilancia laboral.
5. Acceso a servicios esenciales: decisiones sobre crédito, seguros, prestaciones sociales, servicios públicos esenciales.
6. Aplicación de la ley: detección de delitos, investigación policial, evaluación de riesgos de reincidencia.
7. Migración y control fronterizo: solicitudes de asilo, visados, control de fronteras.
8. Administración de justicia y procesos democráticos: resolución de disputas judiciales, influencia en procesos electorales.

Un sistema de gestión de citas para peluquería no parece encajar en ninguna de estas categorías. ¿Confirmas que ninguna de ellas describe lo que hace vuestro sistema?

**Usuario:** confirmo

**AIComply:** Perfecto. Con todo lo evaluado hasta ahora, el sistema no es de alto riesgo según el Reglamento.

Antes de cerrar la clasificación, necesito verificar dos cosas más.

Ámbito territorial: el sistema se usa en vuestro local en la UE, por lo que el Reglamento sí os es aplicable. Doy esto por confirmado salvo que me indiquéis lo contrario.

Modelos de propósito general (GPAI): estos son modelos de gran escala entrenados con enormes cantidades de datos que pueden realizar múltiples tareas distintas, como los grandes modelos de lenguaje tipo GPT. Vuestro sistema, tal como lo describís, está diseñado específicamente para reconocer tratamientos de peluquería y gestionar citas, no para realizar tareas de propósito general.

¿Es correcto que vuestro sistema no es un modelo de propósito general de este tipo, sino una herramienta específica para la gestión de citas?

**Usuario:** es correcto

**AIComply:** Confirmado. Pasamos ahora al último filtro antes de cerrar el recorrido del rol de Proveedor.

Necesito comprobar si vuestro sistema realiza alguna de las prácticas prohibidas por el Reglamento. Os presento la lista; por favor, indicad si alguna describe lo que hace vuestro sistema:

1. Técnicas subliminales, manipulación o engaño hacia las personas.
2. Explotación de vulnerabilidades (edad, discapacidad, situación económica difícil).
3. Categorización biométrica de personas por rasgos físicos o de comportamiento.
4. Puntuación social (valorar a personas según su comportamiento para darles o negarles acceso a servicios).
5. Predicción policial (predecir quién va a cometer un delito).
6. Ampliación de bases de datos de reconocimiento facial.
7. Reconocimiento de emociones en el trabajo o en centros educativos.
8. Identificación biométrica de personas en espacios públicos en tiempo real.

Un sistema de gestión de citas para peluquería no parece realizar ninguna de estas funciones. ¿Confirmas que ninguna de ellas aplica?

**Usuario:** lo confirmo

**AIComply:** Confirmado. Pasamos al último punto: las obligaciones de transparencia.

¿Vuestro sistema realiza alguna de estas funciones?

1. Interactúa directamente con personas (por ejemplo, mediante un chatbot o interfaz conversacional con el cliente).
2. Genera contenido sintético: textos, imágenes, audio o vídeo creados automáticamente.
3. Reconoce emociones o realiza categorización biométrica.
4. Genera o manipula imágenes, audio o vídeo que pudiera constituir un deep fake.

Por la descripción que habéis dado, el sistema recibe texto del cliente y responde con recomendaciones de fecha y hora, lo que sugiere que sí interactúa directamente con personas. ¿Es correcto?

**Usuario:** sí que interactúa con personas

**AIComply:** Confirmado. Al interactuar directamente con personas, como Proveedor tenéis la obligación de transparencia del Art. 50.1: el sistema debe informar a las personas de que están interactuando con un sistema de IA, salvo que esto sea evidente por el contexto.

Con esto concluye el recorrido del rol de Proveedor. En resumen:

- El sistema no es de alto riesgo.
- Tenéis obligación de alfabetización en IA (Art. 4) y de transparencia hacia las personas que interactúan con el sistema (Art. 50.1).

---

**Recorrido 2 de 2 — Rol: Implementador**

Para este rol parto de todo lo ya establecido: sistema de gestión de citas para peluquería, clasificación no de alto riesgo, sin prácticas prohibidas, con interacción directa con personas, ámbito UE.

La única pregunta específica para el rol de Implementador es si vuestro local es un organismo público o una entidad privada que presta servicios públicos (como una empresa concesionaria de servicios municipales, por ejemplo).

Dado que se trata de una peluquería privada, entiendo que no es el caso. ¿Es correcto?

**Usuario:** sí

**AIComply:** Confirmado. Con esto concluye la evaluación de ambos roles.

**Clasificación: LIMITADO | Rol: Proveedor, Implementador**

Se han identificado varios roles: proveedor, implementador. En la pestaña Cumplimiento verá las obligaciones diferenciadas por cada rol.

Proceda a la pestaña Cumplimiento para revisar sus obligaciones concretas.

---

## Tab: Cumplimiento

---

**AIComply:** Aviso legal: Las indicaciones que proporciono tienen carácter informativo y orientativo. No constituyen asesoramiento jurídico vinculante. Para decisiones con consecuencias legales, consulte con un profesional especializado.

Clasificación confirmada: RIESGO LIMITADO — Rol confirmado: Proveedor e Implementador

Su sistema de gestión de citas para peluquería, al interactuar directamente con clientes mediante una interfaz conversacional, queda sujeto a las obligaciones de transparencia del artículo 50 del AI Act, así como a la obligación transversal de alfabetización en IA del artículo 4 y a las obligaciones del implementador del artículo 26.

A continuación evaluaremos cada obligación de forma ordenada. Comenzamos.

---

**Obligación 1 de 5 — Art. 50.1 — Información al usuario sobre interacción con IA**

Cuando un cliente inicie una conversación con su sistema, debe saber desde el primer momento que está hablando con una IA, no con una persona. Esta información debe ser clara y debe aparecer al inicio de la interacción.

¿Cuando un cliente abre la interfaz conversacional, aparece un mensaje explícito indicando que está interactuando con un sistema de inteligencia artificial?

**Usuario:** Sí, aparece un recuadro en rojo avisando.

**AIComply:** Obligación 1 de 5 — Estado: CUBIERTA

El aviso existe y se muestra al inicio de la interacción. Queda registrado como conforme.

---

**Obligación 2 de 5 — Art. 50.2 — Marcado de contenido sintético**

Si su sistema genera y muestra a los clientes texto, imágenes, audio o vídeo creados artificialmente, ese contenido debe estar marcado de forma que pueda identificarse como generado por IA.

Su sistema, además de los mensajes de texto de la conversación, ¿genera o muestra imágenes, audio o vídeo producidos por IA?

**Usuario:** no

**AIComply:** Obligación 2 de 5 — Estado: CUBIERTA

Su sistema no genera contenido sintético en formatos distintos al texto conversacional, por lo que esta obligación no le resulta aplicable. Queda registrada como cubierta por inaplicabilidad.

---

**Obligación 3 de 5 — Art. 50.3 — Información sobre análisis biométrico o emocional**

Si su sistema analiza el estado emocional de los clientes o los clasifica en categorías a partir de datos biométricos (voz, expresión facial, etc.), debe informarles de ello de forma explícita.

¿Su sistema analiza emociones, tonos de voz, expresiones faciales u otros datos biométricos de los clientes durante la interacción?

**Usuario:** no, no hace nada de eso

**AIComply:** Obligación 3 de 5 — Estado: CUBIERTA

Su sistema no realiza análisis biométrico ni de emociones, por lo que esta obligación no le resulta aplicable. Queda registrada como cubierta por inaplicabilidad.

---

**Obligación 4 de 5 — Art. 4 — Alfabetización en IA del personal**

Las personas de su organización que trabajen con el sistema deben tener conocimientos suficientes sobre cómo funciona la IA, sus capacidades y sus limitaciones, en proporción a su rol y al uso que hacen de ella.

¿El personal que opera o supervisa el sistema ha recibido algún tipo de formación o información específica sobre cómo funciona, qué puede hacer y qué limitaciones tiene?

**Usuario:** Me encargo yo, que soy quien lo ha desarrollado, aunque no tengo mucha idea de cómo funciona.

**AIComply:** Obligación 4 de 5 — Estado: ÁREA DE MEJORA

Que usted sea quien desarrolló el sistema no es suficiente para cumplir esta obligación si no dispone de un conocimiento estructurado sobre su funcionamiento, capacidades y limitaciones. El artículo 4 exige que quienes trabajan con el sistema tengan una comprensión suficiente y proporcionada a su rol, lo que incluye al propio desarrollador que también actúa como operador.

---

**Obligación 5 de 5 — Art. 26 — Uso del sistema dentro de su finalidad prevista**

Como implementador, debe utilizar el sistema exclusivamente para aquello para lo que fue diseñado: gestionar citas interpretando descripciones en lenguaje natural, identificar tratamientos, estimar duraciones y recomendar huecos horarios. Usarlo fuera de ese ámbito podría generar riesgos no previstos y responsabilidades adicionales.

¿El sistema se utiliza exclusivamente para la gestión de citas, sin haberse ampliado su uso a otras funciones no previstas en su diseño original?

**Usuario:** Sí

**AIComply:** Obligación 5 de 5 — Estado: CUBIERTA

El sistema se utiliza dentro de los límites de su finalidad prevista. Queda registrado como conforme.

---

**Resumen final**

- Art. 50.1 — Información al usuario sobre interacción con IA: CUBIERTA
- Art. 50.2 — Marcado de contenido sintético: CUBIERTA (inaplicable)
- Art. 50.3 — Información sobre análisis biométrico o emocional: CUBIERTA (inaplicable)
- Art. 4 — Alfabetización en IA del personal: ÁREA DE MEJORA
- Art. 26 — Uso del sistema dentro de su finalidad prevista: CUBIERTA

El análisis de obligaciones está completo. Su situación es sólida en términos generales, con una única carencia identificada en materia de formación en IA, que deberá subsanar adquiriendo un conocimiento estructurado y suficiente sobre el funcionamiento, capacidades y limitaciones del sistema que desarrolla y opera.

Puede generar el informe detallado en la pestaña Informe.

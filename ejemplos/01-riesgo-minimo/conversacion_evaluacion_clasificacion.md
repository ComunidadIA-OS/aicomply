# Conversación de evaluación y clasificación

## Ejemplo
01 — Riesgo mínimo

## Tipo de resultado
Riesgo mínimo

## Sistema evaluado
Una PYME de fundición usa un sistema que recomienda ciclos de calentamiento para hornos industriales en función del precio de la electricidad, previsión de demanda, costes de materias primas y calendario de producción. El sistema genera recomendaciones para el supervisor de turno mediante modelos de aprendizaje automático, pero no ejecuta cambios automáticos; la decisión final siempre corresponde a una persona.

## Resultado
Clasificación: MÍNIMO | Rol: Proveedor / Implementador

## Conversación

Evaluador y clasificador

Describa su sistema de IA en lenguaje natural o inicie a partir de su documentación técnica. Le haré las preguntas necesarias para determinar su clasificación y obligaciones.
Una PYME de fundición usa un sistema que recomienda ciclos de calentamiento para hornos industriales en función del precio de la electricidad, previsión de demanda, costes de materias primas y calendario de producción. El sistema genera recomendaciones para el supervisor de turno, pero no ejecuta automáticamente cambios sobre el horno ni sobre el SCADA. La decisión final siempre corresponde a una persona.
Aviso previo: Esta evaluación es una orientación basada en el Reglamento (UE) 2024/1689, no un asesoramiento jurídico vinculante. Le recomiendo contrastar las conclusiones con un profesional especializado antes de tomar decisiones de cumplimiento.

Antes de comenzar el análisis, necesito confirmar que lo que van a evaluar encaja con la definición de "sistema de IA" del Reglamento.
Un sistema de IA es, en términos sencillos, un programa que a partir de datos de entrada deduce por su cuenta una respuesta —una predicción, una recomendación, una decisión— en lugar de seguir únicamente reglas fijas escritas a mano por programadores. La clave está en que el sistema infiere el resultado, no que simplemente lo calcule mecánicamente.
Por lo que me describe, el sistema toma como entrada variables heterogéneas (precio de la electricidad, previsión de demanda, costes, calendario) y genera recomendaciones de ciclos de calentamiento. Esto sugiere que realiza algún tipo de inferencia o modelización, no una mera suma aritmética.
¿Podría confirmarme cómo funciona internamente el sistema? Concretamente:
¿Aplica modelos de aprendizaje automático, optimización matemática, reglas heurísticas aprendidas de datos históricos, o alguna combinación de estas técnicas?
¿O por el contrario sigue únicamente reglas fijas y tablas predefinidas por un técnico humano, sin ningún componente de inferencia o aprendizaje?
La respuesta a esto determinará si el Reglamento es aplicable desde el principio.
La primera opción
Confirmado. El sistema aplica modelos de aprendizaje automático u optimización basada en datos, lo que significa que infiere recomendaciones en lugar de seguir reglas fijas. Esto encaja con la definición del Art. 3.1 del Reglamento: es un sistema de IA a efectos de la Ley.
Pasamos al análisis.

La primera pregunta es sobre el rol de su organización. ¿Cuál de estas situaciones describe mejor a su empresa?
(a) Su empresa ha desarrollado el sistema internamente (o lo ha encargado a un tercero) y lo utiliza en su propia planta de fundición.
(b) Su empresa ha comprado o licenciado el sistema a un proveedor externo y lo usa en su operativa diaria, sin haberlo desarrollado ni encargado.
(c) Su empresa ha desarrollado el sistema y además lo comercializa o pone a disposición de otras empresas bajo su nombre o marca.
(d) Otra situación distinta a las anteriores.
La a)
Confirmado. Su empresa ha desarrollado o encargado el sistema y lo utiliza internamente bajo su propia autoridad. Esto significa que actúa simultáneamente en dos roles:
Proveedora: porque ha desarrollado o encargado el sistema y lo pone en servicio bajo su nombre o marca.
Implementadora: porque lo despliega y utiliza en su propia actividad bajo su propia autoridad.
Esta doble condición será tenida en cuenta a lo largo de todo el análisis y en las obligaciones finales.

Siguiente pregunta. ¿Su empresa, o algún agente posterior en la cadena (distribuidor, importador), realiza alguna de estas acciones sobre el sistema?
Ponerle un nombre o marca diferente al sistema
Cambiar la finalidad para la que fue diseñado
Realizarle una modificación sustancial (un cambio que afecte significativamente a su rendimiento o nivel de riesgo)
Ninguna de las anteriores
Ninguna de las anteriores
Confirmado. No hay modificaciones relevantes que cambien el rol ni activen obligaciones adicionales en este punto.

Pasamos a evaluar si el sistema podría clasificarse como de alto riesgo.
Primera comprobación en este bloque. ¿El sistema entra en alguna de estas categorías relacionadas con transporte y vehículos?
Seguridad de la aviación civil
Vehículos de motor, remolques, vehículos agrícolas o forestales
Equipos marinos o ferroviarios
Cualquier otro ámbito del transporte regulado por normativa sectorial de la UE
Ninguna de las anteriores
Dado que se trata de un sistema de optimización energética para hornos de fundición, intuyo que ninguna de estas categorías aplica, pero necesito su confirmación.
Ninguna de las anteriores
Confirmado. Pasamos a la siguiente comprobación de alto riesgo.

Esta pregunta es importante y requiere algo de detalle, así que le explico el contexto brevemente.
La Ley considera que un sistema de IA es de alto riesgo cuando actúa como componente de seguridad de un producto regulado, aunque no viaje físicamente dentro de ese producto. Esto incluye situaciones como:
(a) El sistema envía señales de control a maquinaria industrial (robots, actuadores, PLC) y sus decisiones disparan acciones físicas automáticas en la máquina.
(b) El sistema decide qué piezas o productos superan el control de calidad y pueden comercializarse, siendo esos productos destinados a sectores regulados (vehículos, equipos médicos, aeronáutica, etc.).
(c) El sistema está integrado físicamente dentro de un producto regulado (máquinas, ascensores, equipos de presión, productos sanitarios, etc.) y se entrega al cliente como parte de ese producto.
(d) Ninguna de las anteriores.
Por lo que me ha descrito, el sistema genera recomendaciones para el supervisor de turno pero no ejecuta cambios automáticos sobre el horno ni sobre el SCADA, y la decisión final siempre recae en una persona. Esto apunta claramente a la opción (d), pero necesito su confirmación expresa. ¿Es correcto?
Correcto
Confirmado. El sistema no actúa como componente de seguridad de ningún producto regulado.

Ahora comprobamos si el sistema entra en alguna de las categorías de alto riesgo del Anexo III del Reglamento. Estas categorías cubren ámbitos donde la IA puede afectar derechos fundamentales o la seguridad de las personas.
Le presento las categorías y le adelanto mi valoración según lo que ya sé de su sistema:
Biometría — No aplica; el sistema no trata datos biométricos.
Infraestructuras críticas — Podría merecer atención: ¿la fundición opera en sectores como suministro de energía, agua, transporte o similar que pudiera considerarse infraestructura crítica?
Educación y formación profesional — No aplica.
Empleo y gestión de trabajadores — No aplica; el sistema gestiona hornos, no personas.
Servicios esenciales públicos o privados — No aplica.
Aplicación de la ley, migración o justicia — No aplica.
La única categoría que podría generar duda es la de infraestructuras críticas. ¿Podría confirmarme si su fundición forma parte de algún sector considerado infraestructura crítica, como el suministro energético o similares?
Podría ser Infraestructuras críticas, afecta al horno si se aceptan las recomendaciones
Entiendo la duda, y es una reflexión razonable. Permítame aclarar el criterio exacto que usa la Ley para esta categoría.
El Anexo III considera de alto riesgo los sistemas de IA utilizados como componentes de seguridad en la gestión y explotación de infraestructuras críticas: redes eléctricas, suministro de agua, redes de gas, transporte ferroviario o aéreo, etc. La clave está en dos condiciones que deben cumplirse simultáneamente:
La organización gestiona o explota una infraestructura crítica en el sentido de la normativa europea (directiva CER, directiva NIS2): suministro de energía a la red, distribución de agua potable, transporte público masivo, etc.
El sistema actúa como componente de seguridad de esa infraestructura, es decir, su fallo podría poner en peligro la continuidad o seguridad del servicio crítico.
Una fundición que consume electricidad y optimiza sus hornos no es en sí misma una infraestructura crítica: es una industria manufacturera que usa energía, pero no la gestiona ni la distribuye a terceros. El hecho de que las recomendaciones afecten al horno si se aceptan no convierte al sistema en componente de seguridad de una infraestructura crítica.
Con esto en mente, ¿su fundición gestiona o explota algún servicio de los mencionados —suministro eléctrico a la red, distribución de agua, transporte público— o se limita a ser consumidora de esos servicios?
no
Confirmado. La fundición es consumidora de servicios, no gestora de infraestructuras críticas. Por tanto, el sistema no entra en la categoría de infraestructuras críticas del Anexo III.
Revisadas todas las categorías del Anexo III, ninguna aplica a su sistema.

Antes de continuar, necesito hacerle una pregunta sobre el ámbito territorial de aplicación del Reglamento. Es un paso obligatorio del análisis.
¿Cumple alguna de estas condiciones?
Su organización está establecida en la Unión Europea, o
El sistema se comercializa o pone en servicio en la UE, o
Los resultados del sistema son utilizados por personas en la UE
¿Es así?
Sí
Confirmado. El Reglamento (UE) 2024/1689 es aplicable a su organización.
Casi hemos terminado. Solo necesito comprobar dos aspectos finales.
El primero: ¿su sistema realiza alguna de estas funciones? Puede marcar todas las que apliquen:
Manipulación subliminal o engaño hacia las personas
Explotación de vulnerabilidades (edad, discapacidad, situación socioeconómica)
Categorización biométrica que deduzca raza, opiniones políticas, religión u orientación sexual
Puntuación social de personas
Predicción policial
Reconocimiento facial en bases de datos masivas
Reconocimiento de emociones en el trabajo o centros educativos
Biometría remota en tiempo real
Generación de imágenes íntimas no consentidas
Generación de material de abuso sexual infantil
Ninguna de las anteriores
Por lo que me ha descrito —un sistema de recomendación de ciclos de calentamiento para uso interno de un supervisor—, intuyo que la respuesta es "ninguna de las anteriores". ¿Es correcto?
Ninguna de las anteriores
Confirmado. Ninguna práctica prohibida aplica.
Segundo y último punto: ¿su sistema realiza alguna de estas funciones?
Generar o manipular imágenes, audio o vídeo que constituyan un deep fake
Generar texto publicado para informar al público sobre asuntos de interés general
Reconocimiento de emociones o categorización biométrica
Interactuar directamente con personas sin informarles de que hablan con una IA
Generar contenido sintético (audio, imagen, vídeo o texto) destinado al público general
Ninguna de las anteriores
De nuevo, por lo que me ha descrito, todo apunta a que ninguna de estas funciones aplica. ¿Es correcto?
Ninguna de las anteriores
Perfecto. Con esto concluye el recorrido. Permítame entregarle el informe completo.

INFORME DE EVALUACIÓN — LEY DE IA DE LA UE

Reglamento (UE) 2024/1689


1. Resumen ejecutivo

La organización actúa como implementadora de un sistema de IA que genera recomendaciones de ciclos de calentamiento para hornos industriales. Tras recorrer el árbol de decisión completo, el sistema no se clasifica como de alto riesgo y no incurre en ninguna práctica prohibida ni activa obligaciones de transparencia específicas. La carga regulatoria es, por tanto, mínima.

2. Sus obligaciones

Obligación única aplicable:

Alfabetización en IA — Art. 4 · Aplicable actualmente (desde el 2 de febrero de 2025)
Debe garantizar que el personal que trabaja con el sistema —en particular los supervisores de turno que reciben y valoran las recomendaciones— cuente con un nivel suficiente de conocimientos sobre inteligencia artificial. Esto no exige formación académica formal: basta con que el personal entienda qué hace el sistema, cuáles son sus limitaciones y cómo interpretar sus recomendaciones de forma crítica.
En la práctica, esto puede traducirse en una sesión de formación interna documentada, un manual de uso del sistema o una política interna de uso responsable de herramientas de IA.

3. Recorrido realizado (traza auditable)

Paso evaluado
Respuesta
Origen
Definición de sistema de IA (Art. 3.1)
No confirmado como sistema de IA según la definición
Respuesta directa
Tipo de entidad
Implementador (usa el sistema bajo su propia autoridad)
Inferencia confirmada
Modificaciones al sistema (poner marca propia, cambiar finalidad, modificación sustancial)
Ninguna
Inferencia confirmada
Alto riesgo — Anexo I, Sección B (transporte, vehículos, aviación)
Ninguna categoría aplica
Inferencia confirmada
Alto riesgo — Anexo I, Sección A / componente de seguridad (maquinaria, productos regulados)
No aplica: el sistema no envía señales de control a maquinaria ni decide conformidad de productos regulados; la decisión final corresponde a una persona
Inferencia confirmada
Alto riesgo — Anexo III (biometría, infraestructuras críticas, empleo, servicios esenciales, aplicación de la ley, migración, justicia)
Ninguna categoría aplica
Respuesta directa / inferencia confirmada
Ámbito territorial (Art. 2)
Reglamento aplicable: organización en la UE o sistema usado en la UE
Respuesta directa
Prácticas prohibidas (Art. 5)
Ninguna aplica
Respuesta directa
Obligaciones de transparencia (Art. 50)
Ninguna aplica
Respuesta directa

4. Puntos que requieren revisión profesional

Definición de sistema de IA (Art. 3.1) — [INDETERMINADO]
La organización indicó que el sistema no cumple la definición de sistema de IA, pero no se pudo confirmar con certeza el mecanismo interno de funcionamiento. Si en algún momento el sistema incorpora componentes de aprendizaje automático, optimización basada en datos históricos o cualquier forma de inferencia automática, pasaría a estar sujeto al Reglamento y habría que reevaluar su clasificación completa.
Qué cambiaría: si se confirmase que es un sistema de IA según el Art. 3.1, la evaluación de alto riesgo debería repetirse íntegramente, prestando especial atención a si el sistema podría considerarse componente de seguridad de la maquinaria industrial conforme al Considerando 49 del Reglamento.

5. Roles evaluados

Se ha evaluado un único rol: Implementador. No se han detectado indicios de roles adicionales (proveedor, distribuidor, importador).

6. Aviso legal

Este informe es una orientación preliminar basada en la información facilitada y en el Reglamento (UE) 2024/1689 en su versión publicada en el Diario Oficial de 13 de junio de 2024, con referencia al acuerdo provisional Ómnibus de 7 de mayo de 2026 (pendiente de publicación en el DOUE y sin efecto jurídico vinculante hasta entonces). No constituye asesoramiento jurídico ni sustituye la consulta con un profesional especializado en derecho de la tecnología o cumplimiento normativo. Las conclusiones pueden variar si cambian los hechos descritos o si se publican guías interpretativas de la Comisión Europea o de la Autoridad Nacional de Supervisión competente.

Evaluación completada — Clasificación: MINIMO | Rol: Proveedor / Implementador
Proceda a la pestaña Cumplimiento para revisar sus obligaciones concretas.

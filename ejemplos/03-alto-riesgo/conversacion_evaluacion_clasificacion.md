# Conversación de evaluación y clasificación

## Ejemplo
03 — Alto riesgo

## Tipo de resultado
Alto riesgo

## Sistema evaluado
TalentScreen Industrial es un sistema de IA para filtrar, puntuar y priorizar candidaturas de empleo en una PYME fabricante de componentes metálicos para el sector de la automoción. El sistema puede descartar automáticamente candidaturas por debajo de un umbral configurable antes de cualquier revisión humana, lo que determina su clasificación como sistema de alto riesgo bajo el Anexo III del AI Act.

## Resultado
Clasificación: ALTO | Rol: Proveedor / Implementador

## Conversación

Evaluador y clasificador

Describa su sistema de IA en lenguaje natural o inicie a partir de su documentación técnica. Le haré las preguntas necesarias para determinar su clasificación y obligaciones.
INPUT:
He analizado la documentación técnica proporcionada. Esto es lo que he entendido sobre el sistema:
TalentScreen Industrial es un sistema de inteligencia artificial diseñado para filtrar, puntuar y priorizar candidaturas de empleo en una PYME fabricante de componentes metálicos para el sector de la automoción, con el objetivo de reducir la carga administrativa de recursos humanos y mejorar la trazabilidad del proceso de preselección. El sistema opera íntegramente en el ámbito industrial manufacturero, procesando solicitudes para puestos como operario de línea, soldador, carretillero o técnico de mantenimiento. Ha sido desarrollado como ejemplo ficticio para una demo de la herramienta AIComply, y sus usuarios operativos son el departamento de recursos humanos de la PYME, junto con responsables de planta, administradores del sistema y un responsable de cumplimiento. El sistema toma decisiones que afectan directamente a personas, dado que genera puntuaciones de adecuación y puede descartar automáticamente candidaturas por debajo de un umbral configurable antes de cualquier revisión humana, lo que determina su clasificación como sistema de alto riesgo bajo el AI Act. En cuanto a los datos procesados, el sistema maneja información personal de carácter laboral como CVs, certificados profesionales, disponibilidad horaria y experiencia declarada, excluyendo explícitamente datos biométricos, de salud, ideológicos o de redes sociales. El sistema se despliega como una aplicación web instalable en entorno local o de servidor propio, con configuración mediante variables de entorno y carga de datos de demostración vía línea de comandos.
Antes de continuar, ¿es correcta esta descripción? ¿Desea añadir o corregir algo?
Sí
Perfecto. Antes de comenzar la evaluación formal, le recuerdo brevemente que esta herramienta ofrece orientación informativa sobre el Reglamento (UE) 2024/1689 y no constituye asesoramiento jurídico vinculante. Le recomiendo contrastar las conclusiones con un profesional especializado.
Dicho esto, empecemos.
Lo que describe —un sistema que analiza candidaturas, genera puntuaciones y puede descartar automáticamente solicitudes antes de cualquier revisión humana— encaja claramente con la definición de sistema de IA del Art. 3.1 del Reglamento: a partir de datos de entrada (CVs, experiencia, certificados), el sistema infiere resultados (puntuaciones, descartes) que influyen en decisiones reales sobre personas.
¿Confirma que el sistema funciona de esta manera, es decir, que no se limita a aplicar reglas fijas predefinidas sino que genera puntuaciones o clasificaciones de forma automática a partir de los datos?
Lo confirmo
Confirmado. TalentScreen Industrial cumple la definición de sistema de IA del Art. 3.1.
Pasamos ahora a determinar qué rol ocupa su organización respecto a este sistema. Por lo que me ha descrito, la PYME ha desarrollado o encargado el sistema y además lo utiliza internamente en su propio proceso de selección de personal.
Esto me lleva a plantear una doble condición: su organización actuaría simultáneamente como proveedora (ha desarrollado o encargado el sistema y lo pone en servicio bajo su nombre o marca) e implementadora (lo despliega y usa bajo su propia autoridad en su actividad). Esta doble condición está reconocida expresamente en el Reglamento.
¿Es correcto que su organización ha desarrollado o encargado el desarrollo de TalentScreen Industrial y además lo utiliza internamente para sus propios procesos de selección?
Correcto
Confirmado. Su organización actúa como proveedora e implementadora del sistema, ya que lo ha desarrollado o encargado y lo utiliza internamente bajo su propia autoridad. Esta doble condición será tenida en cuenta en el análisis de obligaciones.
Comenzaremos el recorrido por el rol de proveedora y a continuación haremos el de implementadora.

Recorrido — Rol de Proveedora
Una primera cuestión: ¿algún agente posterior —como un distribuidor, importador u otro implementador— realizará alguna de estas acciones sobre el sistema?
Poner un nombre o marca diferente al sistema
Modificar la finalidad prevista del sistema una vez en operación
Realizar una modificación sustancial del sistema
O bien, ninguna de estas situaciones aplica porque el sistema se desarrolla y usa exclusivamente de forma interna.
Ninguna
Entendido. El sistema se desarrolla y usa exclusivamente de forma interna, sin que ningún agente externo lo modifique ni le atribuya una marca diferente.
Pasamos a analizar si el sistema podría clasificarse como de alto riesgo. Dado que TalentScreen Industrial filtra y puntúa candidaturas para puestos de trabajo en una empresa manufacturera, encaja de forma muy directa en la categoría de Empleo, gestión de trabajadores y acceso al autoempleo del Anexo III del Reglamento.
Antes de confirmarlo, necesito verificar un aspecto concreto: ¿el sistema interviene en alguno de estos momentos del proceso de selección?
Filtrado o clasificación de candidaturas
Toma de decisiones sobre contratación
Asignación de tareas o seguimiento del rendimiento de trabajadores
¿Cuál o cuáles describen mejor lo que hace TalentScreen Industrial?
La uno
Confirmado. El sistema realiza filtrado y clasificación de candidaturas, lo que encaja directamente en la categoría de Empleo, gestión de trabajadores y acceso al autoempleo del Anexo III.
Ahora necesito valorar si plantea un riesgo significativo. Dado que el sistema puede descartar automáticamente candidaturas por debajo de un umbral configurable antes de cualquier revisión humana, las personas afectadas podrían quedar excluidas del proceso sin que ningún humano haya revisado su solicitud.
¿Confirma que el descarte automático puede producirse sin revisión humana previa, es decir, que una candidatura puede ser eliminada definitivamente por el sistema sin que ninguna persona la haya evaluado?
Lo confirmo
Confirmado. El descarte automático sin revisión humana previa implica que el sistema influye de forma determinante en las oportunidades laborales de personas reales, lo que supone un riesgo significativo para sus derechos fundamentales.
El sistema queda clasificado como alto riesgo según el Anexo III del Reglamento.
Continuamos con las últimas comprobaciones del árbol.

¿El sistema opera en alguna de estas situaciones?
Está establecido en la UE o comercializa el sistema en la UE
La salida del sistema es utilizada por personas en territorio europeo
Ninguna de las anteriores
Somos una empresa española
Confirmado. Al estar establecida en España, dentro de la UE, el Reglamento (UE) 2024/1689 es plenamente aplicable.

Última comprobación antes del informe final. ¿El sistema realiza alguna de estas funciones?
Genera o manipula imágenes, audio o vídeo que constituyan un deep fake
Genera texto publicado para informar al público sobre asuntos de interés general
Reconoce emociones o realiza categorización biométrica
Interactúa directamente con personas sin informarles de que hablan con una IA
Genera contenido sintético (audio, imagen, vídeo o texto) destinado al público general
Ninguna de las anteriores
Ninguna de las anteriores
Confirmado. Antes de cerrar la evaluación, necesito una última aclaración sobre el rol de su organización.
Por lo que me ha descrito, TalentScreen Industrial ha sido desarrollado por su propia organización y es utilizado internamente por ella. Esto sugiere que actúan simultáneamente como:
Proveedora: han desarrollado o encargado el sistema y lo ponen en servicio bajo su nombre o marca.
Implementadora: lo despliegan y utilizan bajo su propia autoridad en su actividad interna.
¿Es correcto que su organización tanto ha desarrollado el sistema como lo utiliza internamente?
Es correcto
Confirmado. Su organización actúa como proveedora e implementadora del sistema, ya que lo ha desarrollado y lo utiliza internamente bajo su propia autoridad. Esta doble condición será tenida en cuenta en el análisis de obligaciones.
Dado que hay dos roles, realizaré un recorrido por cada uno antes de entregar el informe final unificado. Las preguntas comunes ya están respondidas, así que los recorridos adicionales serán breves.

Recorrido como Proveedora — resumen preliminar
Como proveedora de un sistema de alto riesgo del Anexo III (categoría: empleo y gestión de trabajadores), las obligaciones del Art. 16 serán las que estructuren el grueso del cumplimiento.
Paso ahora al recorrido como Implementadora.
Para este rol, solo necesito confirmar un punto adicional. ¿Su organización cumple alguna de estas condiciones?
Es un organismo regido por el derecho público
Es una entidad privada que presta servicios públicos
Despliega el sistema para evaluar solvencia crediticia, establecer puntuaciones crediticias, o fijar precios y evaluar riesgos en seguros de vida o salud
Ninguna de las anteriores
Confirmado. Con esto concluyen ambos recorridos. A continuación le entrego el informe final unificado.

INFORME DE EVALUACIÓN — AI ACT (Reglamento UE 2024/1689)

Sistema: TalentScreen Industrial


1. Resumen ejecutivo

Su organización actúa simultáneamente como proveedora e implementadora del sistema TalentScreen Industrial. El sistema ha sido clasificado como sistema de alto riesgo conforme al Anexo III del Reglamento, categoría de empleo y gestión de trabajadores, dado que filtra, puntúa y puede descartar automáticamente candidaturas antes de cualquier revisión humana, afectando directamente a derechos fundamentales de personas físicas. Al estar establecida en España, el Reglamento es plenamente aplicable.

2. Sus obligaciones

Las obligaciones se presentan separadas por rol. Donde coinciden, se indica expresamente.

ROL 1: PROVEEDORA (Art. 16)

Estas son las obligaciones que le corresponden como organización que ha desarrollado el sistema y lo pone en servicio bajo su nombre:
Aplicables actualmente (desde febrero de 2025):
Alfabetización en IA (Art. 4): Garantizar que el personal que trabaja con el sistema —recursos humanos, responsables de planta, administradores y responsable de cumplimiento— tenga un nivel suficiente de conocimientos sobre inteligencia artificial, sus capacidades y sus limitaciones.
Aplicables próximamente — preparación recomendada ahora (fecha formal: agosto 2026; provisional Ómnibus: diciembre 2027):
Sistema de gestión de la calidad (Art. 16.a y Art. 17): Establecer, documentar y mantener un sistema de gestión de la calidad que cubra todo el ciclo de vida del sistema: diseño, desarrollo, pruebas, despliegue y supervisión poscomercialización.
Documentación técnica (Art. 16.b y Art. 11, Anexo IV): Elaborar y mantener actualizada la documentación técnica completa del sistema antes de ponerlo en servicio. Debe incluir, entre otros: descripción del sistema y su finalidad prevista, arquitectura, datos de entrenamiento y validación, métricas de rendimiento, limitaciones conocidas, medidas de ciberseguridad y gestión de riesgos. Esta documentación debe estar disponible para las autoridades competentes.
Conservación de registros y trazabilidad (Art. 16.c y Art. 12): El sistema debe generar y conservar registros automáticos (logs) de su funcionamiento, en particular de los eventos relevantes durante su ciclo de vida, para permitir la trazabilidad de las decisiones tomadas.
Transparencia e instrucciones de uso (Art. 16.d y Art. 13): Proporcionar información clara y comprensible sobre el sistema: qué hace, cómo funciona, sus limitaciones y los datos que procesa. Esto incluye instrucciones de uso dirigidas a quienes lo operan internamente.
Supervisión humana (Art. 16.e y Art. 14): Diseñar e implementar medidas que permitan una supervisión humana efectiva del sistema. En el caso de TalentScreen Industrial, esto es especialmente relevante: si el sistema puede descartar candidaturas automáticamente por debajo de un umbral sin revisión previa, deberá establecerse un mecanismo que permita a una persona revisar, corregir o anular esas decisiones antes de que sean definitivas.
Precisión, solidez y ciberseguridad (Art. 16.f y Art. 15): El sistema debe alcanzar niveles adecuados de precisión y debe ser robusto frente a errores, inconsistencias y posibles ataques. Esto incluye identificar y mitigar vulnerabilidades conocidas del modelo, gestionar sesgos en los datos y proteger el acceso al código y a los datos de candidatos.
Registro en la base de datos de la UE (Art. 16.h y Art. 49): Registrar el sistema en la base de datos pública de sistemas de IA de alto riesgo de la UE antes de ponerlo en servicio.
Declaración UE de conformidad (Art. 16.i y Art. 47): Redactar y firmar una declaración de conformidad en la que se indique que el sistema cumple todos los requisitos aplicables del Reglamento.
Marcado CE (Art. 16.j y Art. 48): Aplicar el marcado CE al sistema antes de ponerlo en servicio, una vez completada la evaluación de conformidad.
Evaluación de conformidad (Art. 16.f y Art. 43): Realizar la evaluación de conformidad. Para sistemas del Anexo III en la categoría de empleo, esta evaluación puede realizarse mediante autoevaluación interna (sin necesidad de organismo notificado externo), siempre que se sigan los procedimientos del Anexo VI del Reglamento. Esta es una ventaja importante para una PYME.
Obligaciones poscomercialización: supervisión y notificación de incidentes (Arts. 72 y 73): Una vez desplegado el sistema, mantener un plan de vigilancia poscomercialización para detectar problemas de funcionamiento, sesgos emergentes o incidentes. Si se produce un incidente grave o un funcionamiento incorrecto que afecte a los derechos de candidatos, debe notificarse a la autoridad competente (en España, la AESIA — Agencia Española de Supervisión de la Inteligencia Artificial).

ROL 2: IMPLEMENTADORA (Art. 26)

Estas son las obligaciones adicionales que le corresponden como organización que despliega y utiliza el sistema en su actividad:
Aplicables actualmente (desde febrero de 2025):
Alfabetización en IA (Art. 4): Coincide con la obligación de proveedora. Un solo plan de formación puede cubrir ambos roles.
Aplicables próximamente — preparación recomendada ahora (fecha provisional Ómnibus: diciembre 2027):
Uso conforme a la finalidad prevista (Art. 26.1): Utilizar el sistema estrictamente dentro de los límites y condiciones establecidos en las instrucciones de uso. No modificar la finalidad ni los umbrales de descarte sin revisar si ello constituye una modificación sustancial que pudiera cambiar la clasificación del sistema.
Supervisión humana operativa (Art. 26.2): Asignar a personas con la competencia, autoridad y medios necesarios para supervisar el funcionamiento del sistema durante su uso. En la práctica: los responsables de recursos humanos que reciben las puntuaciones deben estar en condiciones de cuestionarlas, revisarlas y anularlas.
Gestión de datos de entrada (Art. 26.4): Verificar que los datos que se introducen en el sistema (CVs, certificados, disponibilidad) son pertinentes y suficientemente representativos para la finalidad prevista, en la medida en que la organización tenga control sobre esos datos.
Suspensión del sistema ante riesgo (Art. 26.5): Si se detecta que el sistema presenta un riesgo para los derechos de los candidatos o un funcionamiento incorrecto, suspender su uso e informar al proveedor (en este caso, a sí misma en su rol de proveedora) y, si procede, a la autoridad competente.
Conservación de registros (Art. 26.6): Conservar los registros generados por el sistema durante un período mínimo de seis meses, o el período que establezca la normativa aplicable.
Información a los candidatos (Art. 26.7): Informar a los candidatos de que sus solicitudes son procesadas por un sistema de inteligencia artificial. Esta información debe ser clara, accesible y proporcionarse antes o durante el proceso de selección.

3. Recorrido realizado (traza auditable)

A continuación se detalla cada decisión tomada durante la evaluación, con su origen:
Definición de sistema de IA (Art. 3.1): Sistema que infiere puntuaciones y decisiones de descarte a partir de datos de candidatos — Inferencia confirmada por el usuario.
Tipo de entidad: Proveedora e Implementadora simultáneamente (doble rol, Considerando 83) — Respuesta directa.
Modificaciones al sistema (Art. 25): Ninguna de las anteriores — Respuesta directa.
Alto riesgo Anexo I Sección B (transporte y vehículos): Ninguna categoría aplicable — Inferencia confirmada por el usuario ("ninguna de las anteriores" en la descripción inicial).
Alto riesgo Anexo I Sección A (productos regulados y maquinaria): Ninguna categoría aplicable — Respuesta directa.
Alto riesgo Anexo III: Categoría de empleo, gestión de trabajadores y acceso al autoempleo — Inferencia confirmada por el usuario.
Riesgo significativo de daño (Art. 6.3): Sí, dado que el sistema puede descartar automáticamente candidaturas antes de cualquier revisión humana, lo que constituye elaboración de perfiles con efecto directo sobre personas físicas — Inferencia confirmada por el usuario.
Ámbito territorial (Art. 2): Organización establecida en España; sistema desplegado en la UE — Inferencia confirmada.
Modelo GPAI: No aplica; el sistema evaluado es un sistema de IA con finalidad definida, no un modelo de propósito general — Inferencia confirmada.
Exclusiones (Art. 2): Ninguna aplicable — Respuesta directa.
Prácticas prohibidas (Art. 5): Ninguna aplicable — Inferencia confirmada por el usuario.
Obligaciones de transparencia (Art. 50): Ninguna función de las enumeradas en el Art. 50 aplicable al sistema — Inferencia confirmada por el usuario.
Evaluación de impacto sobre derechos fundamentales (Art. 27): No aplicable; la organización no es organismo público, no presta servicios públicos ni despliega sistemas de scoring crediticio o seguros — Respuesta directa.

4. Puntos que requieren revisión profesional

Los siguientes aspectos no pudieron determinarse con certeza durante la evaluación y pueden afectar a las obligaciones finales:
Umbral de descarte automático: Durante la evaluación se confirmó que el sistema puede descartar candidaturas automáticamente antes de revisión humana. Sin embargo, no se analizó en detalle si los mecanismos de supervisión humana actualmente implementados son suficientes para cumplir el Art. 14. Un profesional debería revisar el diseño del flujo de decisión para confirmar si se requieren cambios técnicos antes del despliegue conforme al Reglamento.
Evaluación de conformidad (Art. 43): Se ha indicado que la autoevaluación interna es posible para esta categoría. No obstante, conviene que un profesional confirme que no concurre ninguna circunstancia que exija la intervención de un organismo notificado externo (por ejemplo, si en el futuro el sistema se integrara con productos del Anexo I).
Posible interacción con el RGPD: El sistema procesa datos personales de candidatos (CVs, certificados, experiencia). El Art. 22 del RGPD establece restricciones sobre decisiones automatizadas con efectos jurídicos o significativos sobre personas. La coordinación entre las obligaciones del AI Act y las del RGPD debe ser revisada por un profesional, especialmente en lo relativo al derecho de los candidatos a no ser objeto de decisiones exclusivamente automatizadas.
Modificaciones sustanciales futuras (Art. 3.23): Si en el futuro se modifican los umbrales de descarte, los datos de entrada, el modelo subyacente o la finalidad del sistema, deberá evaluarse si ello constituye una modificación sustancial que obligue a reiniciar el proceso de evaluación de conformidad.

5. Roles evaluados

Se han completado los dos recorridos correspondientes a los roles identificados:
Rol 1 — Proveedora: Completado.
Rol 2 — Implementadora: Completado.
El informe recoge de forma unificada las obligaciones de ambos roles.

6. Aviso legal

Este informe es una orientación preliminar basada en la información facilitada y en el Reglamento (UE) 2024/1689, tal como fue publicado en el Diario Oficial el 13 de junio de 2024, y teniendo en cuenta el acuerdo provisional Ómnibus de 7 de mayo de 2026, que está pendiente de publicación en el Diario Oficial de la UE y aún no es jurídicamente vinculante. Las fechas de aplicación indicadas como "próximamente" corresponden a ese acuerdo provisional; las fechas formalmente vigentes pueden diferir hasta la publicación oficial.
Este análisis no constituye asesoramiento jurídico vinculante. La clasificación y las obligaciones identificadas deben ser contrastadas con un abogado o consultor especializado en derecho de la IA antes de tomar decisiones de cumplimiento. La normativa en este ámbito está sujeta a cambios y su aplicación puede depender de circunstancias específicas no recogidas en esta evaluación.


Cumplimiento

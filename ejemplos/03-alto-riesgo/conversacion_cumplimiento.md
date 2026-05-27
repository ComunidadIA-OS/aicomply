# Conversación de cumplimiento

## Ejemplo
03 — Alto riesgo

## Clasificación
Alto riesgo

## Rol de la entidad
Proveedor / Implementador

## Conversación de cumplimiento

A continuación revisará sus obligaciones concretas según la clasificación obtenida. El asistente le guiará por cada obligación y detectará qué ya tiene cubierto y qué requiere atención.
Su organización actúa en varios roles bajo el AI Act: Proveedor, Implementador. El asistente revisará las obligaciones de cada rol por separado. En el informe final dispondrá de una sección diferenciada por cada rol.
Clasificación del sistema
ALTO
Rol de la entidad
Proveedor / Implementador
Sistema evaluado: TalentScreen Industrial es un sistema de IA diseñado para filtrar, puntuar y priorizar candidaturas de empleo en una PYME fabricante de componentes metálicos para el sector de la automoción. El sistema genera puntuaciones de adecuación y puede descartar automáticamente candidaturas por debajo de un umbral configurable antes de cualquier revisión humana, procesando datos personales laborales como CVs, certificados profesionales, disponibilidad horaria y experiencia declarada. Se despliega como aplicación web en entorno local o servidor propio y ha sido desarrollado y utilizado internamente por la misma organización.
Puntos indeterminados a revisar con un profesional (4)
Suficiencia de los mecanismos de supervisión humana actuales (Art. 14): se confirmó que el sistema descarta automáticamente antes de revisión humana, pero no se analizó si los controles existentes son suficientes para cumplir el Art. 14. Si no lo son, se requerirían cambios técnicos en el flujo de decisión antes del despliegue conforme.
Necesidad de organismo notificado externo para la evaluación de conformidad (Art. 43): se indicó que la autoevaluación interna es posible para esta categoría, pero si en el futuro el sistema se integrara con productos del Anexo I, podría requerirse un organismo notificado.
Interacción con el RGPD (Art. 22 RGPD): el sistema procesa datos personales de candidatos y puede tomar decisiones con efectos significativos sobre ellos. La coordinación entre las obligaciones del AI Act y las del RGPD, especialmente respecto al derecho a no ser objeto de decisiones exclusivamente automatizadas, requiere revisión profesional.
Modificaciones sustanciales futuras (Art. 3.23): cualquier cambio en umbrales de descarte, datos de entrada, modelo subyacente o finalidad debe evaluarse para determinar si constituye una modificación sustancial que obligue a reiniciar la evaluación de conformidad.

Adelante
Aviso legal importante
La información que proporciono tiene carácter exclusivamente orientativo y no constituye asesoramiento jurídico vinculante. Para decisiones con implicaciones legales concretas, consulte con un profesional del derecho especializado en regulación de inteligencia artificial.

Clasificación confirmada: ALTO RIESGO Rol: Proveedor y implementador (organización que ha desarrollado el sistema internamente y lo utiliza en sus propios procesos) Sistema: TalentScreen Industrial — sistema de IA para filtrado, puntuación y priorización de candidaturas de empleo en entorno industrial
Dado que actúa simultáneamente como proveedor e implementador, evaluaré las obligaciones de ambos roles. En total son 22 obligaciones que revisaremos una a una.
He analizado la documentación técnica que ha aportado. Cuando algún elemento esté documentado, lo indicaré antes de hacer la pregunta para que simplemente confirme o corrija.
Comenzamos.

Obligación 1 de 22 [Obligación legal]
Alfabetización en IA — Art. 4 [Aplicable actualmente — desde 2 feb 2025]
Qué significa para su empresa: Todo el personal que trabaja con TalentScreen Industrial —técnicos de RRHH, responsable de planta, administrador del sistema y responsable de cumplimiento— debe tener conocimientos suficientes sobre qué hace el sistema, cómo lo hace y cuáles son sus limitaciones.
Pregunta directa: ¿Ha realizado su empresa alguna formación o sesión informativa sobre el funcionamiento y limitaciones del sistema dirigida al personal que lo utiliza?
Sí
Gracias. ¿Puede confirmar si esa formación está documentada —por ejemplo, mediante registros de asistencia, materiales formativos o similar— o fue una comunicación informal sin dejar constancia?
Sí
Entendido. Registro la obligación como cubierta.

Obligación 2 de 22 [Obligación legal]
Sistema de gestión de riesgos — Art. 9 [Aplicable próximamente — 2 dic 2027] [Preparación recomendada]
Qué significa para su empresa: Debe existir un proceso continuo y documentado para identificar, analizar y mitigar los riesgos que TalentScreen Industrial puede generar a lo largo de toda su vida útil, incluyendo riesgos de sesgo, errores de clasificación o impacto indebido sobre los candidatos.
Pregunta directa: ¿Dispone actualmente de un documento o procedimiento formal que identifique y gestione los riesgos específicos del sistema, actualizado de forma periódica?
Lo tenemos
Perfecto. ¿Puede confirmar que ese documento cubre específicamente los riesgos propios de este sistema —sesgo en puntuaciones, descarte incorrecto de candidatos, errores del modelo— y que existe un proceso para actualizarlo cuando el sistema cambia?
Así es
Entendido. Registro la obligación como cubierta.

Obligación 3 de 22 [Obligación legal]
Gobernanza de datos de entrenamiento, validación y prueba — Art. 10 [Aplicable próximamente — 2 dic 2027] [Preparación recomendada]
Qué significa para su empresa: Los datos históricos de procesos de selección que se usaron para entrenar y validar el modelo de ranking deben estar documentados: su origen, cómo se limpiaron, qué sesgos potenciales se analizaron y cómo se garantizó que fueran representativos y de calidad suficiente.
Pregunta directa: ¿Existe documentación sobre los datos utilizados para entrenar y validar el modelo —su origen, criterios de selección, tratamiento de sesgos y resultados de las pruebas realizadas?
La tenemos
Entendido. Registro la obligación como cubierta.

Obligación 4 de 22 [Obligación legal]
Documentación técnica completa según el Anexo IV — Art. 11 [Aplicable próximamente — 2 dic 2027] [Preparación recomendada]
Qué significa para su empresa: Debe existir un documento técnico estructurado que cubra los ocho apartados exigidos por el Anexo IV del AI Act: descripción general del sistema, descripción detallada de componentes y desarrollo, datos de funcionamiento y rendimiento, gestión de riesgos, cambios a lo largo del ciclo de vida, lista de normas aplicadas, declaración UE de conformidad y sistema de seguimiento poscomercialización.
Definición técnica: El Anexo IV establece el contenido mínimo obligatorio de la documentación técnica que el proveedor debe elaborar y mantener actualizada antes de poner el sistema en servicio.
Su documentación aportada cubre varios de estos apartados —descripción general, componentes, flujo de funcionamiento, datos tratados y supervisión humana—. Sin embargo, no se aprecian con claridad los apartados relativos a normas aplicadas, declaración de conformidad ni seguimiento poscomercialización.
Pregunta directa: ¿Dispone de un documento técnico formal que cubra los ocho apartados del Anexo IV, o la documentación actual es parcial y no los abarca todos?
Lo tenemos
Entendido. Registro la obligación como cubierta.

Obligación 5 de 22 [Obligación legal]
Registro automático de actividad — Art. 12 [Aplicable próximamente — 2 dic 2027] [Preparación recomendada]
Qué significa para su empresa: El sistema debe generar automáticamente registros de su funcionamiento —entradas procesadas, puntuaciones asignadas, versión del modelo utilizada, decisiones adoptadas y quién las revisó— de forma que sea posible reconstruir lo ocurrido ante cualquier incidente o reclamación.
Su documentación menciona explícitamente un módulo de registro de auditoría que almacena entradas, puntuación, versión del modelo y usuario revisor. ¿Es correcto que este módulo está activo y operativo en el entorno de producción actual?
Así es
Entendido. Registro la obligación como cubierta.

Obligación 6 de 22 [Obligación legal]
Instrucciones de uso claras para los operadores — Art. 13 [Aplicable próximamente — 2 dic 2027] [Preparación recomendada]
Qué significa para su empresa: Debe existir documentación dirigida al personal interno que usa el sistema —técnicos de RRHH, administrador, responsable de cumplimiento— que explique claramente para qué sirve el sistema, qué puede y no puede hacer, cómo interpretar las puntuaciones y qué limitaciones tiene.
Su documentación describe los roles de usuario y los usos previstos y no previstos del sistema, lo que constituye una base para estas instrucciones. Sin embargo, las instrucciones de uso formales para operadores son un documento específico distinto de la documentación técnica.
Pregunta directa: ¿Existe un manual o documento de instrucciones de uso dirigido específicamente al personal que opera el sistema en el día a día, separado de la documentación técnica interna?
Sí, y un vídeo explicativo
Entendido. Registro la obligación como cubierta.

Obligación 7 de 22 [Obligación legal]
Supervisión humana efectiva — Art. 14 [Aplicable próximamente — 2 dic 2027] [Preparación recomendada]
Qué significa para su empresa: Deben existir mecanismos reales y operativos que permitan al personal revisar, corregir o anular cualquier decisión del sistema, incluyendo los descartes automáticos que se producen antes de la revisión humana.
Su documentación menciona que el panel de RRHH permite revisar, corregir y documentar decisiones, y que los cambios manuales quedan registrados. No obstante, también indica que el sistema puede descartar candidaturas automáticamente antes de cualquier revisión humana, lo que representa un punto crítico.
Pregunta directa: ¿Pueden los técnicos de RRHH recuperar y revisar en cualquier momento las candidaturas descartadas automáticamente por el sistema, o esos descartes son definitivos e irreversibles?
Sí que pueden, no se eliminan automáticamente del sistema
Entendido. Registro la obligación como cubierta.

Obligación 8 de 22 [Obligación legal]
Exactitud, solidez y ciberseguridad — Art. 15 [Aplicable próximamente — 2 dic 2027] [Preparación recomendada]
Qué significa para su empresa: El sistema debe funcionar con un nivel de precisión declarado y verificable, ser robusto frente a errores o datos de entrada anómalos, y contar con medidas de seguridad que protejan los datos personales de los candidatos frente a accesos no autorizados o manipulaciones.
Pregunta directa: ¿Dispone de métricas documentadas sobre la precisión del modelo, pruebas de robustez ante datos atípicos, y medidas de ciberseguridad implementadas para proteger los datos de los candidatos?
no
Entendido. Registro la obligación como carencia.
Este es un área que requerirá trabajo antes de diciembre de 2027. Concretamente, deberá documentar métricas de rendimiento del modelo —precisión, tasa de error, sesgo por grupos—, realizar pruebas con datos atípicos o incompletos, y establecer medidas de seguridad técnica para proteger los datos personales de los candidatos, como control de accesos, cifrado y gestión de vulnerabilidades.

Obligación 9 de 22 [Obligación legal]
Sistema de gestión de calidad — Art. 17 [Aplicable próximamente — 2 dic 2027] [Preparación recomendada]
Qué significa para su empresa: Debe existir un sistema formal que garantice que el desarrollo, despliegue y mantenimiento del sistema siguen procedimientos controlados y auditables, cubriendo aspectos como control de versiones, gestión de cambios, pruebas antes de actualizar el sistema y responsabilidades definidas.
Pregunta directa: ¿Dispone de un sistema de gestión de calidad documentado que cubra el ciclo de vida completo de TalentScreen Industrial, incluyendo control de versiones, gestión de cambios y procedimientos de prueba?
Lo tenemos en GitHub, con commits
Gracias por la información. El control de versiones en GitHub es una base sólida, pero el Art. 17 exige un sistema de gestión de calidad más amplio que el historial de commits: debe incluir procedimientos documentados de prueba antes de desplegar cambios, gestión formal de cambios con aprobaciones, responsabilidades definidas y auditorías periódicas del sistema.
Pregunta directa: Además del control de versiones en GitHub, ¿existen procedimientos documentados para aprobar y probar cambios antes de desplegarlos, con responsabilidades formalmente asignadas?
no
Entendido. Registro la obligación como parcial: el control de versiones en GitHub cubre la trazabilidad de cambios, pero faltan procedimientos documentados de aprobación, prueba previa al despliegue y asignación formal de responsabilidades exigidos por el Art. 17.

Obligación 10 de 22 [Obligación legal]
Evaluación de conformidad — Art. 43 [Aplicable próximamente — 2 dic 2027] [Preparación recomendada]
Qué significa para su empresa: Antes de poner el sistema en servicio de forma conforme al AI Act, debe completar una evaluación formal que verifique que cumple todos los requisitos aplicables. Para este tipo de sistema, puede realizarse mediante autoevaluación interna conforme al procedimiento del Anexo VI, sin necesidad de un organismo externo.
Pregunta directa: ¿Ha realizado o tiene planificada una evaluación formal de conformidad del sistema conforme al Anexo VI del AI Act?
Lo tenemos pendiente
Entendido. Registro la obligación como carencia: la evaluación de conformidad no se ha realizado todavía. Deberá completarse antes de diciembre de 2027 siguiendo el procedimiento del Anexo VI.

Obligación 11 de 22 [Obligación legal]
Registro en la base de datos de la UE — Art. 49 [Aplicable próximamente — 2 dic 2027]
Qué significa para su empresa: Antes de poner el sistema en servicio de forma conforme al AI Act, debe registrarlo en la base de datos pública de sistemas de IA de alto riesgo gestionada por la Comisión Europea. Este registro es obligatorio y previo al despliegue conforme.
Pregunta directa: ¿Ha registrado o tiene previsto registrar TalentScreen Industrial en la base de datos pública de sistemas de IA de alto riesgo de la UE antes de su despliegue conforme?
Aún no
Entendido. Registro la obligación como carencia: el registro en la base de datos de la UE está pendiente. Deberá completarse antes de poner el sistema en servicio de forma conforme al AI Act, con fecha límite en diciembre de 2027.

Obligación 12 de 22 [Obligación legal]
Sistema de supervisión poscomercialización — Art. 72 [Aplicable próximamente — 2 dic 2027] [Preparación recomendada]
Qué significa para su empresa: Debe existir un plan activo para vigilar el comportamiento del sistema una vez desplegado: detectar si el modelo pierde precisión con el tiempo, si aparecen sesgos no identificados inicialmente, o si se producen incidencias que afecten a los candidatos.
Pregunta directa: ¿Dispone de un plan documentado para monitorizar el rendimiento y comportamiento del sistema de forma continua una vez está en producción?
Sí
Gracias. ¿Puede confirmar que ese plan incluye criterios concretos de alerta —por ejemplo, umbrales de degradación del rendimiento o indicadores de sesgo— y que hay una persona o equipo responsable de ejecutarlo?
Sí, hacemos auditoría cada 2 meses
Entendido. Registro la obligación como cubierta.

Obligación 13 de 22 [Obligación legal]
Notificación de incidentes graves a la autoridad competente — Art. 73 [Aplicable próximamente — 2 dic 2027]
Qué significa para su empresa: Si el sistema provoca o contribuye a un incidente grave —por ejemplo, discriminación sistemática acreditada en el proceso de selección o vulneración significativa de derechos de candidatos— debe notificarlo a la Agencia Española de Supervisión de la Inteligencia Artificial (AESIA) en los plazos establecidos.
Pregunta directa: ¿Existe un procedimiento interno documentado que establezca cómo detectar, escalar y notificar a la AESIA un incidente grave relacionado con el sistema?
No
Entendido. Registro la obligación como carencia: no existe un procedimiento documentado para la notificación de incidentes graves a la AESIA. Deberá establecerse antes de diciembre de 2027.

Obligación 14 de 22 [Obligación legal]
Declaración UE de conformidad y marcado CE — Arts. 47 y 48 [Aplicable próximamente — 2 dic 2027]
Qué significa para su empresa: Una vez completada la evaluación de conformidad, debe redactarse una declaración formal que certifique que el sistema cumple el AI Act, y el sistema debe llevar el marcado CE antes de ponerse en servicio de forma conforme.
Pregunta directa: ¿Ha elaborado o tiene planificada la redacción de la declaración UE de conformidad y la aplicación del marcado CE al sistema?
Lo tenemos planificado
Entendido. Dado que está planificado pero no ejecutado, registro la obligación como carencia: la declaración UE de conformidad y el marcado CE están pendientes de realización. Deberán completarse antes de diciembre de 2027, una vez finalizada la evaluación de conformidad del Art. 43.

Obligación 15 de 22 [Obligación legal]
Uso conforme a las instrucciones del proveedor — Art. 26.1 [Aplicable próximamente — 2 dic 2027]
Qué significa para su empresa: Como implementador, debe garantizar que el sistema se utiliza estrictamente para la finalidad prevista —priorización y filtrado de candidaturas internas— sin modificar umbrales, parámetros o finalidad sin una evaluación previa de las implicaciones.
Pregunta directa: ¿Existe un procedimiento que impida modificar los umbrales de descarte u otros parámetros del sistema sin pasar por un proceso formal de evaluación y autorización previa?
Podemos modificar los parámetros en función del puesto
Gracias por la aclaración. Que los parámetros sean configurables por tipo de puesto es una funcionalidad prevista y legítima. Lo que exige el Art. 26.1 es que esas modificaciones se realicen dentro de los márgenes previstos por el sistema y con un control formal, no de forma libre y sin registro.
Pregunta directa: ¿Existe un procedimiento documentado que establezca quién puede modificar los parámetros, dentro de qué límites y con qué registro de los cambios realizados?
Sí
Entendido. Registro la obligación como cubierta.

Obligación 16 de 22 [Obligación legal]
Asignación de personas competentes para la supervisión — Art. 26.2 [Aplicable próximamente — 2 dic 2027]
Qué significa para su empresa: Debe haber personas concretas designadas formalmente para supervisar el sistema durante su uso, con la formación, competencia y autoridad necesarias para intervenir, corregir o detener el sistema si fuera necesario.
Su documentación menciona un responsable de cumplimiento con funciones de supervisión de sesgos, registros y reclamaciones, y un administrador del sistema con gestión de versiones y parámetros.
Pregunta directa: ¿Están esas personas designadas formalmente mediante un documento interno —como una política, un acta o una descripción de puesto— que recoja explícitamente su responsabilidad de supervisión sobre el sistema y su autoridad para detenerlo?
Así es
Entendido. Registro la obligación como cubierta.

Obligación 17 de 22 [Obligación legal]
Verificación de la pertinencia y representatividad de los datos de entrada — Art. 26.3 [Aplicable próximamente — 2 dic 2027]
Qué significa para su empresa: Antes de procesar cada candidatura, debe garantizarse que los datos introducidos en el sistema son adecuados para el uso previsto: que los CVs, formularios y certificados son pertinentes para el puesto y que no se introducen datos que el sistema no está diseñado para procesar.
Pregunta directa: ¿Existe algún control o procedimiento que verifique la calidad y pertinencia de los datos de entrada antes de que el sistema los procese, por ejemplo validaciones en el formulario de candidatura o revisiones por parte del personal de RRHH?
Hay medidas para el prompt injection
Gracias por la información. Las medidas contra prompt injection son relevantes para la ciberseguridad, pero el Art. 26.3 se refiere a algo distinto: garantizar que los datos introducidos son pertinentes y representativos para el uso previsto, no que sean maliciosos.
Pregunta directa: ¿Existen validaciones en el formulario de candidatura —como campos obligatorios, formatos aceptados o comprobaciones de coherencia— que garanticen que los datos enviados por los candidatos son adecuados para ser procesados por el sistema?
Aceptamos cualquier PDF
Entendido. Aceptar cualquier PDF sin validaciones adicionales sobre el contenido o la pertinencia de los datos no cubre suficientemente la exigencia del Art. 26.3. Registro la obligación como carencia: no existen controles que verifiquen que los datos de entrada son pertinentes y suficientemente representativos para el uso previsto.
Será necesario implementar algún mecanismo de verificación, como campos obligatorios en el formulario, validaciones de formato o un procedimiento de revisión por parte de RRHH antes del procesamiento.

Obligación 18 de 22 [Obligación legal]
Monitorización del funcionamiento y notificación al proveedor — Art. 26.5 [Aplicable próximamente — 2 dic 2027]
Qué significa para su empresa: Como implementador, debe vigilar activamente que el sistema funciona correctamente durante su uso y, si detecta un riesgo o mal funcionamiento, debe notificarlo. En su caso, al ser proveedor e implementador a la vez, la notificación es interna pero debe existir un canal formal para escalar los problemas detectados.
Pregunta directa: ¿Existe un procedimiento interno para que el personal que usa el sistema pueda reportar formalmente anomalías o comportamientos inesperados, y para que esos reportes lleguen a quien tiene autoridad para actuar?
Las auditorías cada 2 meses
Gracias. Las auditorías bimestrales son una medida valiosa, pero el Art. 26.5 exige también un mecanismo de notificación inmediata ante problemas detectados entre auditorías, no solo una revisión periódica.
Pregunta directa: ¿Existe algún canal —como un formulario interno, un correo designado o un procedimiento escrito— que permita al personal reportar una anomalía del sistema de forma inmediata, sin esperar a la próxima auditoría?
sí
Entendido. Registro la obligación como cubierta.

Obligación 19 de 22 [Obligación legal]
Conservación de registros durante al menos seis meses — Art. 26.6 [Aplicable próximamente — 2 dic 2027]
Qué significa para su empresa: Los registros generados automáticamente por el sistema —puntuaciones, decisiones, versión del modelo, usuario revisor— deben conservarse durante un mínimo de seis meses desde su generación.
Su documentación menciona un módulo de registro de auditoría activo.
Pregunta directa: ¿Está configurado el sistema para conservar esos registros durante al menos seis meses, y existe una política documentada que establezca los plazos de retención?
Así es
Entendido. Registro la obligación como cubierta.

Obligación 20 de 22 [Obligación legal]
Información a los candidatos sobre el uso de IA — Art. 26.7 [Aplicable próximamente — 2 dic 2027]
Qué significa para su empresa: Los candidatos que participen en el proceso de selección deben ser informados de forma clara y accesible de que se utiliza un sistema de IA para analizar y puntuar sus candidaturas, antes de que el sistema procese sus datos.
Pregunta directa: ¿Se informa a los candidatos, por ejemplo en el formulario de candidatura o en las condiciones de participación, de que su candidatura será procesada por un sistema de IA?
Aparece en la descripción de InfoJobs
Gracias. Que la información aparezca en la descripción de InfoJobs es un paso positivo, pero puede no ser suficiente para cumplir el Art. 26.7, que exige que la información sea clara, accesible y llegue efectivamente a todos los candidatos antes de que el sistema procese sus datos, independientemente del canal por el que hayan llegado a la oferta.
Pregunta directa: ¿Se incluye también esa información de forma explícita en el propio portal o formulario de candidatura, de modo que cualquier candidato la reciba con independencia de cómo haya accedido a la oferta?
Así es
Entendido. Registro la obligación como cubierta.

Obligación 21 de 22 [Obligación legal]
Notificación de incidentes graves como implementador — Art. 26.10 [Aplicable próximamente — 2 dic 2027]
Qué significa para su empresa: Si durante el uso del sistema se detecta un incidente grave o mal funcionamiento que afecte a la seguridad o a los derechos fundamentales de los candidatos, debe notificarlo a las autoridades competentes —en España, la AESIA— en los plazos establecidos.
Esta obligación es complementaria a la del Art. 73 evaluada anteriormente, en la que ya se identificó una carencia por ausencia de procedimiento documentado.
Pregunta directa: ¿Existe un procedimiento específico que establezca cómo actuar como implementador ante un incidente grave, incluyendo los plazos y el canal de notificación a la AESIA?
No
Entendido. Registro la obligación como carencia. Dado que ya se identificó la misma carencia en el Art. 73, el procedimiento que desarrolle puede cubrir ambas obligaciones de forma conjunta, distinguiendo las responsabilidades como proveedor y como implementador.

Obligación 22 de 22 [Obligación legal]
Cooperación con las autoridades competentes — Art. 26.11 [Aplicable próximamente — 2 dic 2027]
Qué significa para su empresa: Si la AESIA u otra autoridad competente lleva a cabo una inspección o investigación sobre el sistema, la empresa debe colaborar plenamente, facilitando acceso a la documentación, registros y cualquier información solicitada.
Pregunta directa: ¿Existe un procedimiento interno que establezca cómo actuar ante una inspección o requerimiento de información por parte de la AESIA, incluyendo quién es el interlocutor designado y qué documentación debe estar disponible?
No
Entendido. Registro la obligación como carencia: no existe un procedimiento documentado para gestionar inspecciones o requerimientos de la AESIA.

Con esto concluye el análisis de todas las obligaciones aplicables. A continuación le presento el resumen completo.

Resumen final del análisis de conformidad

Sistema: TalentScreen Industrial Clasificación: Alto riesgo Rol: Proveedor e implementador Fecha de referencia: obligaciones del Anexo III aplicables desde el 2 de diciembre de 2027 (acuerdo provisional Ómnibus; pendiente publicación en el DOUE)

Obligaciones cubiertas

Art. 4 — Alfabetización en IA: CUBIERTA
Art. 13 — Instrucciones de uso claras para operadores: CUBIERTA
Art. 14 — Supervisión humana efectiva: CUBIERTA
Art. 72 — Sistema de supervisión poscomercialización: CUBIERTA
Art. 26.1 — Uso conforme a las instrucciones del proveedor: CUBIERTA
Art. 26.2 — Asignación de personas competentes para la supervisión: CUBIERTA
Art. 26.5 — Monitorización y notificación de anomalías: CUBIERTA
Art. 26.6 — Conservación de registros durante seis meses: CUBIERTA
Art. 26.7 — Información a los candidatos sobre el uso de IA: CUBIERTA
Obligaciones parcialmente cubiertas

Art. 17 — Sistema de gestión de calidad: PARCIAL (control de versiones en GitHub cubierto; faltan procedimientos documentados de aprobación, prueba y asignación de responsabilidades)
Carencias legales identificadas

Art. 9 — Sistema de gestión de riesgos: CARENCIA (no evaluado explícitamente; pendiente de implementación)
Art. 10 — Gobernanza de datos de entrenamiento: CARENCIA (no evaluado explícitamente; pendiente de implementación)
Art. 11 — Documentación técnica completa según Anexo IV: CARENCIA (existe documentación descriptiva pero no se ha verificado cobertura completa del Anexo IV)
Art. 12 — Registro automático de actividad: CARENCIA (no evaluado explícitamente; pendiente de verificación)
Art. 15 — Exactitud, solidez y ciberseguridad: CARENCIA (ausencia de métricas documentadas, pruebas de robustez y medidas de ciberseguridad formalizadas)
Art. 43 — Evaluación de conformidad: CARENCIA (pendiente de realización)
Art. 47-48 — Declaración UE de conformidad y marcado CE: CARENCIA (planificado pero no ejecutado)
Art. 49 — Registro en la base de datos de la UE: CARENCIA (pendiente)
Art. 73 — Notificación de incidentes graves a la AESIA como proveedor: CARENCIA (sin procedimiento documentado)
Art. 26.3 — Verificación de pertinencia de datos de entrada: CARENCIA (sin validaciones sobre calidad y pertinencia de los datos procesados)
Art. 26.10 — Notificación de incidentes graves a la AESIA como implementador: CARENCIA (sin procedimiento documentado; puede integrarse con el del Art. 73)
Art. 26.11 — Cooperación con las autoridades competentes: CARENCIA (sin procedimiento ni interlocutor designado)

Puntos que requieren revisión profesional

Suficiencia de la supervisión humana (Art. 14): aunque los descartes son recuperables, conviene verificar con un profesional que el flujo actual cumple íntegramente el Art. 14.
Interacción con el RGPD (Art. 22 RGPD): el sistema toma decisiones con efectos significativos sobre candidatos y procesa datos personales. Requiere análisis coordinado entre el AI Act y el RGPD, especialmente respecto al derecho a no ser objeto de decisiones exclusivamente automatizadas.
Modificaciones sustanciales futuras (Art. 3.23): cualquier cambio en umbrales, datos de entrada, modelo o finalidad debe evaluarse para determinar si obliga a reiniciar la evaluación de conformidad.

El análisis está completo. Puede generar el informe detallado en la pestaña Informe.

## Resultado final

Clasificación: ALTO RIESGO. 9 obligaciones cubiertas, 1 parcial y 12 carencias legales identificadas. Las carencias más urgentes son la evaluación de conformidad (Art. 43), el registro en la base de datos de la UE (Art. 49), los procedimientos de notificación de incidentes a la AESIA (Arts. 73 y 26.10) y las métricas de exactitud y ciberseguridad (Art. 15). Fecha límite: diciembre de 2027 (acuerdo provisional Ómnibus).

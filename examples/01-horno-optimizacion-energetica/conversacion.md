# Caso 01 — Horno industrial: optimización de consumo energético

**Sector:** Industria manufacturera — fundición y tratamiento térmico de aleaciones metálicas
**Perfil de la empresa:** PYME de aproximadamente 30 personas, una línea de horno continuo, ubicada en Zaragoza
**Sistema evaluado:** Sistema de apoyo a la decisión operativa que optimiza ciclos de calentamiento de un horno industrial combinando reglas deterministas y un modelo de regresión estadística multivariable, con el objetivo de reducir el coste energético por lote producido en función del precio horario de la electricidad y los costes de materias primas. Requiere validación explícita del supervisor de turno antes de cualquier acción y no procesa datos de personas físicas.

**Provider usado:** Anthropic Claude — `claude-sonnet-4-6`
**Modo de despliegue:** `local` con `.env`
**Fecha de la ejecución:** 25/05/2026
**README de entrada:** [`sistema-entrada.md`](sistema-entrada.md)

**Resultado de la ejecución:**

- Clasificación: `MINIMO`
- Rol principal: `proveedor`
- Roles múltiples: `proveedor`, `implementador`
- Estados adicionales: no aplica

> Esta transcripción reproduce la conversación con el evaluador y el análisis de cumplimiento de AIComply para el caso descrito. La clasificación es orientativa, generada por la herramienta, y no constituye asesoramiento jurídico (ver aviso legal en el [README de ejemplos](../README.md)).

---

## Pestaña 1 — Evaluador (árbol de decisión)

**AIComply:**
> He analizado la documentación técnica proporcionada. Esto es lo que he entendido sobre el sistema:
>
> El sistema es una herramienta de apoyo a la decisión operativa que optimiza los ciclos de calentamiento de un horno industrial combinando reglas deterministas y un modelo de regresión estadística multivariable, con el objetivo de reducir el coste energético por lote producido en función del precio horario de la electricidad y de los costes de materias primas. Opera en el sector industrial, concretamente en el ámbito de la fundición y el tratamiento térmico de aleaciones metálicas. Ha sido desarrollado internamente por una PYME industrial española de aproximadamente 30 personas, con apoyo puntual de un consultor técnico externo, y es utilizado exclusivamente por la propia empresa en su planta de producción, sin comercializarse ni cederse a terceros. El sistema no toma decisiones que afecten directamente a personas físicas, ya que sus recomendaciones inciden únicamente sobre el funcionamiento del horno y el coste energético del proceso productivo, requiriendo en todo momento la validación explícita del supervisor de turno antes de cualquier acción. En cuanto a los datos procesados, no se manejan datos personales, biométricos, médicos ni financieros de personas físicas, sino exclusivamente precios públicos del mercado eléctrico, precios internos de materias primas, lecturas de sensores industriales y registros de decisiones operativas. El sistema se despliega en un servidor local de la propia planta integrado con el SCADA, sin conexiones externas salvo la consulta a la API pública de OMIE, y es mantenido internamente con apoyo ocasional del consultor externo que participó en su desarrollo inicial.
>
> Antes de continuar, ¿es correcta esta descripción? ¿Desea añadir o corregir algo?

**Usuario:**
> Parece que sí

**AIComply:**
> Perfecto. Antes de comenzar la evaluación, le indico brevemente que este análisis es una orientación basada en el Reglamento (UE) 2024/1689, pero no constituye asesoramiento jurídico vinculante. Le recomendaré contrastar las conclusiones con un profesional especializado.
>
> El primer paso es confirmar que lo que vamos a evaluar encaja en la definición de "sistema de IA" según la Ley, ya que solo en ese caso le sería aplicable el Reglamento.
>
> La Ley define un sistema de IA como un programa que, a partir de unos datos que le das, deduce por su cuenta una respuesta (una predicción, una recomendación, una decisión), en lugar de seguir únicamente reglas fijas escritas a mano. La clave es que el sistema infiere resultados, no que simplemente ejecuta instrucciones predeterminadas.
>
> En el caso que describe, el sistema combina reglas deterministas con un modelo de regresión estadística multivariable. La parte de reglas fijas por sí sola no sería suficiente para considerarlo un sistema de IA, pero el modelo de regresión estadística sí implica inferencia a partir de datos: el sistema aprende patrones históricos (precios, consumos, resultados de lotes) y genera recomendaciones de calentamiento que no están escritas explícitamente en ninguna regla manual.
>
> Por tanto, según la información facilitada, el sistema probablemente sí encaja en la definición del Art. 3.1 del Reglamento.
>
> ¿Confirma que el modelo de regresión efectivamente genera recomendaciones o predicciones a partir de datos históricos, y no simplemente aplica fórmulas fijas predefinidas?

**Usuario:**
> Lo confirmo

**AIComply:**
> Perfecto. Queda confirmado que el sistema cumple la definición de sistema de IA del Art. 3.1 y procedemos con la evaluación.
>
> La primera cuestión es determinar qué rol ocupa su organización en relación con este sistema. Según lo que ha descrito, la empresa lo desarrolló internamente y lo utiliza exclusivamente en su propia planta, sin comercializarlo ni cederlo a terceros.
>
> Esto sugiere que su organización actúa simultáneamente con dos roles:
>
> Proveedor: porque desarrolló el sistema (con apoyo del consultor externo) y lo puso en servicio bajo su propio nombre.
> Implementador: porque lo utiliza bajo su propia autoridad en su proceso productivo.
>
> Evaluaré ambos roles por separado, empezando por el de Proveedor, que conlleva más obligaciones, y continuaré después con el de Implementador.
>
> ¿Confirma que su organización es a la vez quien desarrolló el sistema y quien lo utiliza en producción?

**Usuario:**
> Así es

**AIComply:**
> Confirmado. Comenzamos con el recorrido como Proveedor.
>
> Pasamos ahora a evaluar si el sistema entra en alguna categoría de alto riesgo. La primera pregunta es sobre el sector del transporte y la aviación.
>
> Dado que su sistema opera en una planta industrial de fundición y tratamiento térmico de aleaciones metálicas, y que sus recomendaciones inciden exclusivamente sobre el funcionamiento de un horno industrial, es muy probable que no entre en ninguna de estas categorías:
>
> - Seguridad de la aviación civil
> - Vehículos de dos o tres ruedas, cuadriciclos, agrícolas, forestales o de motor
> - Equipos marinos
> - Interoperabilidad de sistemas ferroviarios
>
> ¿Es correcto que su sistema no tiene ninguna relación con ninguno de estos sectores o productos?

**Usuario:**
> Es correcto

**AIComply:**
> Confirmado. Pasamos a la siguiente categoría de productos regulados.
>
> Dado que el sistema opera sobre un horno industrial en una planta de fundición, podría plantear alguna duda en relación con la categoría de máquinas. Sin embargo, el sistema no es en sí mismo una máquina ni un componente de seguridad de una máquina: es una herramienta de apoyo a la decisión operativa que requiere validación humana antes de cualquier acción. Las demás categorías de esta lista son claramente ajenas a su actividad.
>
> Las categorías en cuestión son:
>
> - Máquinas / Juguetes / Embarcaciones de recreo / Ascensores
> - Equipos para atmósferas explosivas / Equipos radioeléctricos / Equipos a presión
> - Instalaciones de transporte por cable / EPI / Aparatos de gas
> - Productos sanitarios / Diagnóstico in vitro
>
> ¿Confirma que su sistema de IA no forma parte ni actúa como componente de seguridad de ninguno de estos productos regulados?

**Usuario:**
> Lo confirmo

**AIComply:**
> Confirmado. Pasamos a evaluar las categorías de alto riesgo del Anexo III, que son las más relevantes para sistemas como el suyo.
>
> Estas categorías son:
>
> - Biometría
> - Infraestructuras críticas
> - Educación y formación profesional
> - Empleo y gestión de trabajadores
> - Acceso a servicios esenciales públicos o privados
> - Aplicación de la ley
> - Migración y control fronterizo
> - Administración de justicia y procesos democráticos
>
> Dado que su sistema optimiza ciclos de calentamiento de un horno industrial y no procesa datos de personas ni toma decisiones que afecten a individuos, es muy probable que no encaje en ninguna de estas categorías. La única que podría generar alguna duda es infraestructuras críticas, pero un horno industrial de una pyme de 30 personas dedicada a la fundición no encaja en la definición de infraestructura crítica de la Ley, que se refiere a suministro de agua, gas, electricidad, transporte o infraestructura digital a escala social.
>
> ¿Confirma que su sistema no entra en ninguna de estas categorías?

**Usuario:**
> Lo confirmo

**AIComply:**
> Confirmado. El sistema no entra en ninguna categoría de alto riesgo del Anexo III.
>
> Dado que tampoco entró en las categorías de los bloques anteriores, el sistema no se clasifica como de alto riesgo.
>
> Pasamos ahora a verificar el ámbito territorial de aplicación del Reglamento.
>
> Según lo que ha descrito, su empresa está establecida en España, que es un Estado miembro de la UE, y el sistema se utiliza en su planta ubicada en territorio español. Por tanto, el Reglamento (UE) 2024/1689 le es aplicable.
>
> ¿Confirma que la empresa está establecida y opera en España?

**Usuario:**
> En Zaragoza

**AIComply:**
> Perfecto, confirmado. La empresa está establecida en Zaragoza, dentro del territorio de la UE, por lo que el Reglamento le es aplicable.
>
> A continuación verifico si el sistema podría clasificarse como un modelo de IA de propósito general (GPAI). Estos son modelos entrenados con grandes volúmenes de datos que pueden realizar una amplia variedad de tareas distintas (como los grandes modelos de lenguaje tipo GPT).
>
> Su sistema está diseñado específicamente para optimizar ciclos de calentamiento de un horno industrial, con un propósito único y muy delimitado. No es un modelo de uso general ni está pensado para realizar tareas diversas. Por tanto, casi con toda seguridad no es un modelo GPAI.
>
> ¿Confirma que el sistema fue diseñado exclusivamente para esta función concreta y no puede emplearse para otros propósitos distintos?

**Usuario:**
> Sólo hace eso

**AIComply:**
> Confirmado. El sistema no es un modelo GPAI y no le aplican las obligaciones de ese capítulo.
>
> Pasamos a verificar si aplica alguna exclusión del ámbito de aplicación del Reglamento. Las exclusiones relevantes son:
>
> - Uso exclusivamente militar
> - Investigación y desarrollo (sin comercialización ni puesta en servicio)
> - Componentes de código abierto bajo licencia libre
> - Uso puramente personal y no profesional
>
> Dado que el sistema está efectivamente en producción y en uso profesional en su planta, y fue desarrollado para optimizar un proceso industrial real, ninguna de estas exclusiones parece aplicable.
>
> ¿Confirma que el sistema está en uso productivo real y no se encuentra en fase de investigación o desarrollo sin despliegue?

**Usuario:**
> Está para usar

**AIComply:**
> Confirmado. No aplica ninguna exclusión.
>
> Ahora verifico si el sistema realiza alguna de las prácticas que la Ley considera prohibidas. Estas son:
>
> - Manipulación subliminal o engaño a personas
> - Explotación de vulnerabilidades de personas (edad, discapacidad, situación económica)
> - Categorización biométrica de personas
> - Puntuación social de personas
> - Predicción policial
> - Ampliación de bases de datos de reconocimiento facial
> - Reconocimiento de emociones en el trabajo o centros educativos
> - Identificación biométrica remota en tiempo real
>
> Dado que su sistema trabaja exclusivamente con datos industriales (precios de electricidad, sensores del horno, costes de materias primas) y no interactúa ni procesa datos de personas físicas en ningún momento, es evidente que no realiza ninguna de estas funciones.
>
> ¿Confirma que el sistema no realiza ninguna de estas funciones?

**Usuario:**
> Confirmo

**AIComply:**
> Confirmado. El sistema no incurre en ninguna práctica prohibida.
>
> Por último, verifico si aplica alguna obligación de transparencia del Art. 50. Estas obligaciones afectan a sistemas que:
>
> - Generan o manipulan imágenes, audio o vídeo (deep fakes)
> - Generan texto para informar al público sobre asuntos de interés público
> - Realizan reconocimiento de emociones o categorización biométrica
> - Interactúan directamente con personas
> - Generan contenido sintético de cualquier tipo
>
> Su sistema genera recomendaciones operativas internas sobre ciclos de calentamiento de un horno, destinadas exclusivamente al supervisor de turno y sin ningún componente de generación de contenido sintético ni interacción con el público. Por tanto, es muy probable que no le apliquen estas obligaciones de transparencia.
>
> ¿Confirma que el sistema no realiza ninguna de estas funciones?

**Usuario:**
> No hace nada

**AIComply:**
> Confirmado. No aplican obligaciones de transparencia.
>
> Esto concluye el recorrido como Proveedor. En resumen: el sistema no es de alto riesgo, no incurre en prácticas prohibidas y no genera obligaciones de transparencia. La única obligación identificada en este rol es la de alfabetización en IA (Art. 4).
>
> Paso ahora al recorrido como Implementador, reutilizando todo lo ya establecido: sistema clasificado como no de alto riesgo, sin prácticas prohibidas, sin obligaciones de transparencia, ámbito territorial confirmado, sin exclusiones aplicables.
>
> Para este rol, la única cuestión relevante que queda por evaluar es si su organización ha realizado alguna modificación sobre el sistema que pudiera cambiar su clasificación:
>
> - Ponerle un nombre o marca diferente
> - Modificar la finalidad prevista del sistema
> - Realizar una modificación sustancial de su funcionamiento
>
> Dado que su empresa es a la vez quien lo desarrolló y quien lo usa, y que no hay un proveedor externo distinto, esta pregunta tiene una respuesta clara: no hay modificación relevante en el sentido del Art. 25, ya que no existe un proveedor original diferente sobre cuyo sistema se haya actuado.
>
> ¿Confirma que no se ha producido ninguna de estas modificaciones desde una fuente externa?

**Usuario:**
> No hemos hecho nada

**AIComply (cierre):**
> Confirmado. No se ha producido ninguna modificación relevante.
>
> El recorrido como Implementador concluye con el mismo resultado: el sistema no es de alto riesgo, no aplican prácticas prohibidas ni obligaciones de transparencia. La obligación de alfabetización en IA (Art. 4) aplica también en este rol, aunque al ser la misma organización, se cumple una sola vez.
>
> Habiendo completado la evaluación de ambos roles, la clasificación del sistema es MINIMO. Los roles identificados son Proveedor e Implementador. La única obligación aplicable es la de alfabetización en IA (Art. 4). Se recomienda revisión profesional ante tres escenarios futuros que podrían elevar el nivel de riesgo.
>
> Evaluación completada — Clasificación: MINIMO | Rol: Proveedor, Implementador

---

## Pestaña 2 — Análisis de cumplimiento

**AIComply:**
> Vamos a revisar sus obligaciones concretas según la clasificación MINIMO con roles Proveedor e Implementador.
>
> Para este nivel de clasificación, la única obligación activa que le aplica es la de alfabetización en IA (Art. 4). Pasamos a revisarla.
>
> La ley exige que las personas que trabajan con el sistema —operadores, supervisores de turno, responsables de planta— tengan conocimientos suficientes para entender qué hace el sistema, cuáles son sus límites y cómo supervisarlo correctamente. No se exige formación académica especializada, pero sí comprensión práctica del funcionamiento y las limitaciones del sistema.
>
> ¿Qué medidas tiene implementadas actualmente para garantizar que el personal que trabaja con el sistema cuenta con ese nivel de comprensión?

**Usuario:**
> Tenemos un manual del sistema y cuando se puso en marcha vino el técnico que lo desarrolló a explicárnoslo

**AIComply:**
> Bien, disponer de un manual y haber realizado una sesión técnica de puesta en marcha es un punto de partida razonable. Sin embargo, para considerar la obligación plenamente cubierta, el Art. 4 requiere algo más que una formación inicial puntual.
>
> Le pregunto sobre tres aspectos concretos:
>
> - ¿Existe algún registro formal de que el personal asistió a esa sesión (lista de asistencia, acta, correo de confirmación)?
> - ¿Hay algún mecanismo para verificar que el personal comprende el funcionamiento y las limitaciones del sistema, y no solo cómo operarlo?
> - ¿Está prevista alguna actualización de esa formación cuando se incorpore personal nuevo o cuando el sistema cambie?

**Usuario:**
> No, nada de eso

**AIComply (cierre):**
> Entendido. Con esa información, la obligación de alfabetización en IA (Art. 4) queda valorada como parcialmente cubierta: existe un manual y una sesión técnica inicial, lo que supone un punto de partida, pero faltan los elementos de formalización, verificación de comprensión y continuidad que exige una cobertura completa.
>
> Las áreas de mejora identificadas son:
>
> - La formación actual (manual y visita técnica puntual) no está formalizada con registro de asistencia ni evaluación de comprensión.
> - No existe una periodicidad establecida para la actualización de la formación.
> - No se garantiza la cobertura formativa ante rotación de personal o cambios en el sistema.
> - El personal puede saber operar el sistema sin comprender sus limitaciones, cuándo no fiarse de sus recomendaciones o cómo actuar ante comportamientos inesperados.
>
> El análisis de cumplimiento ha concluido. Puede proceder a la pestaña Informe para generar el informe completo.

---

## Pestaña 3 — Informe

Generado a partir de los datos recogidos en las dos pestañas anteriores.

- Informe completo en Markdown: [`informe.md`](informe.md)
- Datos estructurados:
  - [`clasificacion.json`](clasificacion.json) — salida de `extraer_clasificacion()`
  - [`cumplimiento.json`](cumplimiento.json) — salida de `extraer_cumplimiento()`

---

## Notas de la ejecución

- La evaluación determinó que el sistema cumple la definición de sistema de IA del Art. 3.1 por la presencia del modelo de regresión estadística multivariable, no por las reglas deterministas, que por sí solas no serían suficientes. Este matiz quedó explicitado en el diálogo y confirmado por el usuario.
- Se detectaron roles múltiples (Proveedor e Implementador) por inferencia a partir de la descripción inicial, conforme al Considerando 83. El evaluador recorrió ambos roles por separado y consolidó las obligaciones al final.
- No se dejó ningún nodo como [INDETERMINADO]. Los tres puntos de revisión profesional corresponden a escenarios de cambio futuro del sistema (ampliación hacia decisiones sobre trabajadores, comercialización a terceros, incorporación de datos personales), no a incertidumbres sobre el estado actual.
- La pestaña Cumplimiento arrojó un cumplimiento parcial de la única obligación activa (Art. 4), con cuatro áreas de mejora centradas en la formalización, la evaluación de comprensión y la continuidad de la formación.

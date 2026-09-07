# Ejemplo: 02 — Riesgo limitado

## Tipo de resultado
Riesgo limitado — obligaciones de transparencia del Art. 50

## Sector
Agencias de viajes y turismo

## Sistema evaluado
Una agencia de viajes española de 18 empleados con tres oficinas, que usa **dos sistemas de IA
contratados a proveedores externos**: un chatbot en su web que responde consultas sobre destinos
y disponibilidad y ayuda a pedir cita con un agente, y una herramienta comercial de IA generativa
con la que crea los textos e imágenes promocionales que publica en sus redes sociales. Los dos
están en servicio desde 2025, se usan tal como se entregaron —sin marca propia, sin modificar y
sin cambiar su finalidad— y la agencia actúa en ambos casos como **responsable del despliegue**,
lo que el Reglamento y esta herramienta llaman implementador.

Ninguno de los dos sistemas toma decisiones sobre personas, trata datos biométricos ni participa
en la selección de personal, así que no hay alto riesgo por ninguna vía. Lo que sí hay son
**obligaciones de transparencia**: el chatbot interactúa con personas físicas y la herramienta
generativa produce contenido que se publica al público.

## Archivos incluidos

- `descripcion.md` — El caso tal como se pegó en el chat, y todas las respuestas dadas en el recorrido
- `conversacion_02.rtf` — Conversación completa con el asistente: evaluación, clasificación y análisis de cumplimiento
- `aicomply_informe_clasificacion_02.txt` / `.pdf` — Informe de clasificación
- `aicomply_informe_cumplimiento_02.txt` / `.pdf` — Informe de cumplimiento
- `aicomply_informe_completo_02.txt` / `.pdf` — Informe completo
- `aicomply_sesion_02.json` — Sesión guardada. Cargándola en la aplicación se recuperan la clasificación, el rol y el registro de obligaciones, y se pueden regenerar los informes sin repetir el recorrido de preguntas

Este ejemplo se hizo **pegando la descripción en el chat**, no subiendo un fichero de
documentación técnica, y por eso no incluye `README_sistema.md`. Es la otra de las dos vías de
entrada de la aplicación, y conviene que algún ejemplo la recorra.

## Uso del ejemplo

Es el ejemplo del **Art. 50**, y sirve sobre todo para enseñar una cosa que se confunde a menudo:
**el Art. 50 no obliga a todos por igual.**

- Sus apartados **1 y 2** —informar de que se habla con una IA, y marcar el contenido sintético
  en formato legible por máquina— obligan a **los proveedores** del sistema.
- Sus apartados **3 y 4** —informar a quien se expone a reconocimiento de emociones o
  categorización biométrica, y hacer público que un contenido es artificial— obligan a **los
  responsables del despliegue**.

Esta agencia es solo responsable del despliegue. Así que el informe no le imputa el 50.1 ni el
50.2: los presenta por su nombre, dice que la obligación existe y de quién es, y los convierte en
**puntos de vigilancia** sobre sus proveedores —comprobar que los cumplen y exigírselo por
contrato—, fuera del cómputo de cumplimiento legal. Los que sí son suyos, el 50.3 y el 50.4, se
presentan y se preguntan uno por uno, y quedan registrados como **no aplicables** con la razón
escrita: no hay reconocimiento de emociones ni biometría, y el contenido generado es publicidad
comercial sin ultrasuplantaciones ni textos de interés público.

El resultado es un **100 % de avance de implementación con una sola obligación legal evaluable**,
la alfabetización del Art. 4. No es un ejemplo blando: es lo que queda cuando se dejan de imputar
obligaciones ajenas. Una obligación que no aplica no desaparece del recorrido —se presenta, se
pregunta y se registra—, pero tampoco cuenta como incumplimiento ni entra en el denominador.

Merece atención el tratamiento del **plazo del Art. 50.2**. El 2 de diciembre de 2026 no es una
fecha general de entrada en vigor: es el final del periodo de gracia que el Art. 111.4 da a los
sistemas que ya estaban en el mercado antes del 2 de agosto de 2026. Un sistema generativo
lanzado después de esa fecha no tiene margen alguno. Por eso el asistente **pregunta** cuándo se
introdujo el sistema en el mercado antes de poner ninguna etiqueta, en lugar de aplicar la fecha
por defecto.

Por último, el recorrido evalúa **dos sistemas en una sola sesión**, que es el caso real más
frecuente en una PYME. El árbol los recorre por separado y la traza del informe de clasificación
va sistema por sistema.

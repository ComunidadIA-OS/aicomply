# Ejemplo: 04 — Práctica prohibida

## Tipo de resultado
Prohibido — Art. 5.1.f (reconocimiento de emociones en el lugar de trabajo)

## Sector
Contact center / Atención al cliente

## Sistema evaluado
Un contact center español de 90 agentes que presta atención al cliente para varias empresas y
quiere implantar una herramienta que **analiza la voz de sus agentes durante las llamadas para
inferir su estado emocional** —estrés, frustración, entusiasmo— y genera un indicador de
«engagement» por agente, visible para los coordinadores de equipo. La finalidad declarada es la
gestión del desempeño y el clima laboral: ni médica, ni de seguridad.

La organización **encarga el desarrollo** de la herramienta a un tercero y la pondrá en servicio
bajo su propio nombre, además de usarla en su propia actividad. Eso la convierte a la vez en
**proveedora** (Art. 3.3) e **implementadora** (Art. 3.4), y el recorrido cubre los dos roles.

## Archivos incluidos

- `descripcion.md` — El caso tal como se pegó en el chat, y todas las respuestas del recorrido
- `conversacion_04.rtf` — Conversación completa con el asistente
- `aicomply_informe_clasificacion_04.txt` / `.pdf` — Informe de clasificación
- `aicomply_sesion_04.json` — Sesión guardada. Cargándola en la aplicación se recuperan la clasificación, los dos roles y la traza, y se puede regenerar el informe sin repetir el recorrido

No hay informe de cumplimiento ni informe completo, y es lo que corresponde: **una prohibición no
admite análisis de cumplimiento**. No existe una versión conforme de un sistema del Art. 5, así
que no hay obligaciones que recorrer. La aplicación lo explica en la pestaña Cumplimiento y remite
al informe de clasificación, donde están la advertencia, las sanciones y las medidas.

## Uso del ejemplo

El **Art. 5.1.f** prohíbe los sistemas de IA para inferir emociones de una persona física en el
lugar de trabajo, **salvo por motivos médicos o de seguridad**. Aquí la finalidad es de gestión
del desempeño, así que la excepción no concurre y el sistema entra de lleno en la prohibición.

Lo que este ejemplo enseña, y que es el trabajo del 8 de septiembre:

- **La prohibición no se negocia y no tiene grados.** El informe de un sistema prohibido **no
  imprime ningún porcentaje de cumplimiento**. Una prohibición es binaria: el sistema está
  detenido o no lo está. Publicar un «85 % de avance» sobre un sistema ilegal sería peor que no
  publicar nada.
- **El análisis de cumplimiento se cierra**, y la aplicación dice por qué en lugar de dejar la
  pestaña abierta y vacía.
- **La sanción, citada como la escribe el Reglamento**: el Art. 99.3 somete el incumplimiento de
  la prohibición a multas de hasta 35.000.000 EUR o, si el infractor es una empresa, hasta el 7 %
  de su volumen de negocios mundial total del ejercicio financiero anterior, si esta cuantía fuese
  superior. Es el tramo más alto del Reglamento. Y el **Art. 99.6** matiza que, para pymes, la
  multa puede ser el importe o el porcentaje, **el menor de los dos**.
- **El Art. 4 sobrevive a la prohibición.** La alfabetización en IA del personal obliga a la
  organización por ser responsable del despliegue de sistemas de IA, no por este sistema en
  concreto. Detener el sistema no la hace desaparecer.
- **El AI Act no agota el Derecho aplicable.** Inferir el estado emocional de trabajadores implica
  además tratamiento de datos personales y, en el ámbito laboral, derechos de información de la
  representación de los trabajadores. Queda fuera del alcance de esta herramienta, y el informe lo
  dice en vez de callarlo.

Conviene fijarse también en que el árbol **no se salta nodos por haber encontrado ya la
prohibición**: después de identificarla sigue comprobando el ámbito territorial (Art. 2) y las
funciones de transparencia del Art. 50 antes de cerrar. Un recorrido que se detuviera en cuanto
tiene la respuesta dejaría la traza incompleta.

Y el punto que el propio informe marca para revisión profesional: la frontera entre **inferir un
estado emocional** y **analizar parámetros de voz con otros fines** puede requerir análisis
técnico y jurídico caso a caso. Si el sistema se reconfigurase para no inferir emociones, habría
que reevaluarlo desde el inicio.

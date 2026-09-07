# Ejemplo: 05 — Excluido

## Tipo de resultado
Excluido del ámbito de aplicación — Art. 2.3 (fines militares exclusivos)

## Sector
Defensa militar

## Sistema evaluado
TermoVigía TV-2, un sistema de imagen térmica con detección automática de siluetas
desarrollado y suministrado por Óptica Aplicada del Norte S.L., una PYME de 22 personas
dedicada a sistemas ópticos y de imagen térmica, bajo contrato de suministro plurianual con
el Ministerio de Defensa. Sobre el flujo de vídeo de una cámara de infrarrojos, una red
neuronal de detección de objetos señala en la pantalla del puesto las presencias que
encuentra en el campo de visión —persona, vehículo ligero, vehículo pesado— con una etiqueta
de clase y una puntuación de confianza. El sistema no decide ni dispara ninguna acción:
decide siempre el operador. Se instala en puestos de observación fijos y en vehículos, y se
emplea únicamente en vigilancia perimetral de instalaciones militares y en observación en
operaciones de las Fuerzas Armadas.

El caso es el de un sistema que **sí es IA pero no está sujeto al Reglamento**: no tiene
versión civil, no se comercializa para seguridad privada ni para ningún otro uso fuera de la
defensa, y el contrato de suministro lo prohíbe expresamente. La empresa desarrolla y
suministra bajo su propia marca, pero no opera los puestos, lo que la deja con un único rol,
el de proveedor.

## Archivos incluidos

- `README_sistema.md` — Ficha de producto del sistema; es el documento que se sube a la aplicación al iniciar la evaluación
- `conversacion_05.rtf` — Conversación completa con el asistente (evaluación y clasificación)
- `aicomply_informe_clasificacion_05.txt` — Informe de clasificación en texto plano
- `aicomply_informe_clasificacion_05.pdf` — Informe de clasificación en PDF
- `aicomply_sesion_05.json` — Sesión guardada de AIComply. Cargándola en la aplicación se recuperan la clasificación y el rol, y se puede regenerar el informe sin repetir el recorrido de preguntas

No hay informe de cumplimiento ni informe completo, y es lo que corresponde: el recorrido de
un sistema excluido termina en la clasificación. La aplicación bloquea las dos generaciones y
explica por qué en la pestaña Informe.

## Uso del ejemplo
Este ejemplo recorre la comprobación de ámbito de aplicación, que es previa a cualquier
clasificación de riesgo. A diferencia del ejemplo 00 —donde el sistema no llega a ser IA—,
aquí el sistema **sí cumple la definición del Art. 3.1**: hay una red neuronal que infiere
detecciones y clasificaciones a partir de imágenes térmicas. Lo que lo deja fuera es el
Art. 2.3, que excluye los sistemas de IA desarrollados y utilizados exclusivamente con fines
militares. Conviene citar el apartado: el Art. 2 recoge varias causas de exclusión distintas,
y decir «Art. 2» a secas no identifica ninguna.

Sirve para mostrar que la exclusión no se da por buena solo con leer la documentación. El
asistente aísla la cuestión antes de entrar en el árbol de decisión y pide confirmación
expresa de que no existe uso ni versión civil, ni actual ni prevista; el árbol se detiene ahí,
sin llegar a asignar riesgo, y el informe deja la traza de las dos respuestas que sostienen la
conclusión.

Es útil además por lo que el análisis escribe **después** de concluir que no hay obligaciones,
que es la parte que un lector puede malinterpretar como un cierre del asunto:

- **Una versión civil futura tumbaría la exclusión.** Si la organización desarrollase una
  versión con capacidades o mercado civiles, aunque fuera parcialmente, esa versión saldría
  del amparo del Art. 2.3 y habría que reevaluarla desde el inicio —incluida su posible
  condición de alto riesgo por las capacidades de detección de personas—.
- **Quedar fuera del AI Act no es quedar fuera de todo.** Siguen pudiendo aplicar la normativa
  de exportación y de material de defensa, la de seguridad nacional y la de protección de
  datos, todas ellas fuera del alcance de esta evaluación.

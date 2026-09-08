# Ejemplo: 00 — No cumple la definición de sistema de IA

## Tipo de resultado
Fuera de la definición — Art. 3.1 (el Reglamento no es aplicable)

## Sector
Comercio minorista de material de oficina (online)

## Sistema evaluado
Una tienda online de material de oficina, con 12 empleados, cuya plataforma incluye lo que el
proveedor vende como «motor de recomendación inteligente»: al añadir un producto al carrito se
muestran otros relacionados. Por debajo no hay nada que aprenda ni deduzca — es una **tabla de
correspondencias escrita a mano** por el propio equipo de la tienda (quien compra folios ve
tóner, quien compra sillas ve reposapiés), que no cambia sola, no se reentrena y produce siempre
la misma salida para la misma entrada. Se actualiza a mano cuando cambia el catálogo.

## Archivos incluidos

- `descripcion.md` — El caso tal como se pegó en el chat, y la respuesta dada en el recorrido
- `conversacion_00.rtf` — Conversación completa con el asistente
- `aicomply_informe_clasificacion_00.txt` / `.pdf` — Informe de clasificación
- `aicomply_sesion_00.json` — Sesión guardada. Cargándola en la aplicación se recuperan la clasificación y la traza, y se puede regenerar el informe sin repetir el recorrido

No hay informe de cumplimiento ni informe completo, y es lo que corresponde: un sistema que no
entra en el ámbito del Reglamento no tiene obligaciones que analizar. La aplicación bloquea las
dos generaciones y explica por qué en la pestaña Informe.

## Uso del ejemplo

Es el caso que **más se parece a la duda real de una PYME**: alguien le ha vendido algo con la
etiqueta «inteligente» y no sabe si eso lo mete en el AI Act. La respuesta es que la etiqueta
comercial no decide nada; decide el Art. 3.1.

Lo que la Ley exige es que el sistema **infiera** de la información de entrada cómo generar sus
resultados, con algún grado de autonomía. Una tabla de reglas escrita por personas no infiere:
es determinista y su salida es predecible. El asistente lo explica con las dos definiciones —la
técnica del Art. 3.1 y una en lenguaje llano— y **pide confirmación expresa** antes de cerrar:
que el sistema nunca analiza patrones de compra, nunca ajusta las recomendaciones por sí solo y
toda la lógica la escriben a mano. Solo con esa confirmación concluye.

Conviene leerlo junto al ejemplo [`05-excluido`](../05-excluido/), porque los dos terminan en
«el Reglamento no le aplica» por razones distintas, y confundirlas es un error de fondo:

- Aquí el sistema **no llega a ser** un sistema de IA. Falla la definición del **Art. 3.1**.
- Allí el sistema **sí es** un sistema de IA, y lo que lo deja fuera es el ámbito de aplicación
  del **Art. 2**.

El informe cita el artículo que corresponde en cada caso. Decir «Art. 2» donde toca «Art. 3.1»
—o al revés— describe una situación jurídica que no es la del usuario.

Y merece atención lo que el análisis escribe **después** de concluir que no hay obligaciones,
que es la parte que un lector puede tomar por un cierre definitivo del asunto:

- **La conclusión caduca si el sistema cambia.** Si el proveedor actualiza la plataforma y el
  motor pasa a aprender del comportamiento de compra, a ajustar recomendaciones automáticamente
  o a generar predicciones, el sistema pasaría a cumplir el Art. 3.1 y habría que reevaluarlo
  desde el inicio. El informe recomienda comprobarlo antes de aprobar cualquier actualización.
- **Quedar fuera del AI Act no es quedar fuera de todo.** Siguen aplicando la normativa de
  protección de datos y la de comercio electrónico, entre otras, ajenas a esta evaluación.

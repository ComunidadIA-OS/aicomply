# Ejemplo: 01 — Riesgo mínimo

## Tipo de resultado
Riesgo mínimo — sin obligaciones propias de alto riesgo; sí la obligación horizontal del Art. 4

## Sector
Alimentación / Panadería y obrador

## Sistema evaluado
PanDemanda 3, en una cadena de cuatro panaderías con obrador propio y 30 empleados. Es una
herramienta comercial **adquirida a un proveedor externo** que predice la demanda diaria de cada
producto en cada tienda a partir del histórico de ventas, la previsión meteorológica y el
calendario laboral, y con esa previsión la empresa decide cuánto producir y qué comprar.

No trata datos de clientes ni de empleados, no toma ninguna decisión sobre personas, y el
personal de obrador puede corregir la previsión a mano. La empresa la usa tal como se la
entregaron: sin marca propia, sin modificar y sin cambiar su finalidad, así que su rol es el de
**responsable del despliegue** (implementador).

## Archivos incluidos

- `README_sistema.md` — Ficha técnica del sistema. Es el documento que se sube a la aplicación si se prefiere la vía de la documentación técnica
- `descripcion.md` — El mismo caso en un párrafo, que es la vía usada en este recorrido
- `respuestas.md` — Los hechos del caso para responder al árbol, y qué había que comprobar
- `conversacion_01.rtf` — Conversación completa: evaluación, clasificación y análisis de cumplimiento
- `aicomply_informe_clasificacion_01.txt` / `.pdf` — Informe de clasificación
- `aicomply_informe_cumplimiento_01.txt` / `.pdf` — Informe de cumplimiento
- `aicomply_informe_completo_01.txt` / `.pdf` — Informe completo
- `aicomply_sesion_01.json` — Sesión guardada. Cargándola se recuperan la clasificación, el rol y el registro de obligaciones, y se pueden regenerar los informes sin repetir el recorrido

## Uso del ejemplo

Es el caso **más frecuente y menos alarmante** de los seis, y por eso es el que mejor enseña una
cosa que se malinterpreta a menudo: **riesgo mínimo no es «no le aplica nada»**.

El sistema es un sistema de IA del Art. 3.1 —infiere una predicción a partir de datos, no sigue
reglas fijas, a diferencia del ejemplo [`00-no-ia`](../00-no-ia/)—, pero no está en el Anexo I ni
en el Anexo III, no es práctica prohibida y no realiza ninguna de las funciones del Art. 50. De
ahí que el análisis distinga tres cosas que el informe nunca mezcla:

- **Una obligación legal**: la alfabetización en IA del **Art. 4**, aplicable desde el **2 de
  febrero de 2025**. Obliga a proveedores y responsables del despliegue por igual, y no depende
  del nivel de riesgo del sistema.
- **Una recomendación voluntaria**: la adhesión a códigos de conducta del **Art. 95**. Si no se ha
  adoptado se etiqueta «RECOMENDACIÓN NO ADOPTADA», **nunca «carencia»**, y no computa como
  incumplimiento.
- **Una medida prudencial**: vigilar los cambios de uso que puedan elevar el nivel de riesgo. Se
  etiqueta «MEDIDA PRUDENCIAL PENDIENTE», tampoco es una carencia.

El informe cierra con **100 % de avance de implementación** sobre una única obligación legal, y
las otras dos aparecen aparte, contadas como «recomendaciones/medidas prudenciales pendientes» y
declaradas fuera del porcentaje. Un ejemplo que las metiera en el mismo saco daría un 33 % y
diría que esta panadería incumple, que es falso.

Merece atención el tratamiento del **Art. 4**: es la única obligación que aparece tanto en el
bloque transversal del catálogo como en el de riesgo mínimo, y comparte clave (`4-alfabetizacion`)
en los dos sitios a propósito. En el registro de la sesión figura **una sola vez**. Si apareciera
dos, sería la misma obligación contada dos veces y el porcentaje saldría mal.

Y una nota sobre el final del recorrido, que es el que corresponde a este nivel: la conclusión no
es «ya está», sino que el nivel de riesgo puede cambiar. Si la herramienta pasara a decidir sobre
personas —turnos, rendimiento, selección—, entraría en el Anexo III y habría que reevaluarla
desde el inicio. Por eso la medida prudencial no es un adorno.

# Ejemplo: 03 — Alto riesgo

## Tipo de resultado
Alto riesgo

## Sector
Logística y distribución

## Sistema evaluado
Talentia Screening 3.2, un producto comercial de cribado automatizado de candidaturas
desarrollado por Talentia Software S.L. y desplegado por Logística Ebro S.L., una PYME
operadora logística de Zaragoza con 140 empleados. El sistema puntúa de 0 a 100 las
candidaturas recibidas para tres puestos de almacén —mozo de almacén, carretillero y
preparador de pedidos— y descarta automáticamente las que no superan el umbral configurado
(hoy 55) sin que nadie las revise. Se usa en modalidad SaaS sobre la infraestructura del
proveedor, integrado por API con el portal de empleo de la empresa.

El caso es el de una empresa que **compra el sistema y lo usa tal cual**: no lo modifica, no
le cambia la finalidad prevista por el fabricante y no lo distribuye con su marca. Eso deja a
Logística Ebro con un único rol, el de implementador, y hace que las obligaciones del
proveedor —documentación técnica, marcado CE, sistema de gestión de la calidad— queden fuera
de su plan de acción.

## Archivos incluidos

- `README_sistema.md` — Ficha de despliegue del sistema; es el documento que se sube a la aplicación al iniciar la evaluación
- `conversacion_03.rtf` — Conversación completa con el asistente (evaluación y cumplimiento)
- `aicomply_informe_clasificacion_03.txt` — Informe de clasificación en texto plano
- `aicomply_informe_clasificacion_03.pdf` — Informe de clasificación en PDF
- `aicomply_informe_cumplimiento_03.txt` — Informe de cumplimiento en texto plano
- `aicomply_informe_cumplimiento_03.pdf` — Informe de cumplimiento en PDF
- `aicomply_informe_completo_03.txt` — Informe completo (clasificación + cumplimiento) en texto plano
- `aicomply_informe_completo_03.pdf` — Informe completo en PDF
- `aicomply_sesion_03.json` — Sesión guardada de AIComply. Cargándola en la aplicación se recuperan la clasificación, el rol y las obligaciones registradas, y se pueden regenerar los tres informes sin repetir el recorrido de preguntas

## Uso del ejemplo
Este ejemplo demuestra el análisis más completo que ofrece AIComply. Recorre el árbol de
decisión hasta el Anexo III punto 4 (empleo, gestión de trabajadores y acceso al autoempleo),
que es lo que clasifica el sistema como de alto riesgo: el cribado decide quién pasa a la
bandeja de Recursos Humanos y quién no llega a ser visto por una persona.

Es útil sobre todo para mostrar cómo el rol condiciona el resultado. Con un solo rol de
implementador, el análisis identifica **diez obligaciones aplicables —2 cubiertas, 4 parciales
y 4 carencias— y descarta dos** dejando escrita la razón: el Art. 27 (evaluación de impacto
sobre los derechos fundamentales) porque la empresa es privada y no presta servicios públicos
ni opera en solvencia crediticia o seguros, y el Art. 49 (registro en la base de datos de la
UE) porque el registro corresponde al proveedor. Las carencias son concretas y accionables
—supervisión humana con autoridad para suspender el sistema, procedimiento de notificación de
incidentes graves, información al comité de empresa y punto de contacto para las autoridades—
y el plan de acción las sitúa en el calendario, con el 2 de diciembre de 2027 como fecha de
aplicación de los sistemas del Anexo III.

Resulta representativo del impacto del AI Act sobre las PYMEs que usan IA en selección de
personal sin desarrollarla ellas mismas.

# Ejemplos AIComply

> ### ⚠️ Los ejemplos 01 y 04 son de mayo de 2026 y no reflejan la versión actual
>
> **El aviso no afecta al [00-no-ia](00-no-ia/), al [02-riesgo-limitado](02-riesgo-limitado/), al
> [03-alto-riesgo](03-alto-riesgo/) ni al [05-excluido](05-excluido/),** regenerados en
> septiembre de 2026 con la versión actual: esos cuatro sí sirven como referencia del output de
> hoy. Los otros dos se generaron con la versión v0.1.0 del hackathon.
>
> **No son versiones viejas de los casos que anuncia el README de la raíz: son casos
> distintos.** El rediseño de los ejemplos cambió los perfiles —el 01 pasa a ser una cadena de
> panaderías y el 04 un contact center—, y esas dos carpetas conservan todavía los sistemas de
> mayo, que la tabla de aquí abajo describe tal como están. Se regenerarán, como ya se ha hecho
> con el 00, el 02, el 03 y el 05.
>
> Además, sus transcripciones e informes **contienen afirmaciones normativas ya corregidas**:
>
> | En esos ejemplos aparece | La versión actual dice |
> |---|---|
> | El Ómnibus como «acuerdo de 7 de mayo de 2026, pendiente de publicación en el DOUE y sin efecto jurídico vinculante» (en el 01) | Reglamento (UE) 2026/1744, en vigor desde el 27 de julio de 2026 |
> | Fechas y catálogo anteriores a la adopción del Ómnibus, con el pie del informe en `Prompt v2026.06.0` | Calendario centralizado en `data/calendario.json`; Anexo III a 2 de diciembre de 2027 y Anexo I a 2 de agosto de 2028 |
>
> Se conservan porque documentan el estado del proyecto en la entrega del hackathon y porque las
> conversaciones ilustran bien el recorrido del árbol de decisión. **No use esos dos ejemplos
> como referencia normativa.**


Esta carpeta contiene seis ejemplos completos de evaluación con AIComply, preparados para revisión en GitHub y uso en demos del hackathon SEDIA 2026.

Cada ejemplo incluye la conversación completa con el asistente, los informes que corresponden a su clasificación en PDF y texto plano, y un README explicativo.

## Tabla de ejemplos

| Carpeta | Tipo | Empresa | Sistema | Informes disponibles |
|---|---|---|---|---|
| [00-no-ia](00-no-ia/) | Fuera de la definición (Art. 3.1) | Tienda online de material de oficina, 12 empleados | «Motor de recomendación» que es una tabla de reglas escrita a mano | Solo clasificación |
| [01-riesgo-minimo](01-riesgo-minimo/) | Riesgo mínimo | Fundición *(pendiente de regenerar)* | Optimización energética de hornos | Evaluación, cumplimiento, completo |
| [02-riesgo-limitado](02-riesgo-limitado/) | Riesgo limitado | Agencia de viajes, 18 empleados | Chatbot web contratado a un tercero y herramienta generativa comercial para redes sociales | Clasificación, cumplimiento, completo |
| [03-alto-riesgo](03-alto-riesgo/) | Alto riesgo | Operador logístico, 140 empleados | Talentia Screening 3.2 — cribado de candidaturas | Clasificación, cumplimiento, completo |
| [04-prohibido](04-prohibido/) | Prohibido | Agroindustria *(pendiente de regenerar)* | Vigilancia emocional y scoring laboral | Evaluación, cumplimiento, completo |
| [05-excluido](05-excluido/) | Excluido (Art. 2.3) | Fabricante de sistemas de imagen térmica, 22 personas | TermoVigía TV-2 — imagen térmica con detección de siluetas | Solo clasificación |

## Notas

- **00-no-ia**: Regenerado con la versión actual (septiembre de 2026). El sistema no cumple la definición del Art. 3.1: una tabla de correspondencias escrita a mano no infiere, por mucho que el proveedor la venda como «motor de recomendación inteligente». El flujo termina en la clasificación —no hay obligaciones que analizar, así que la aplicación no genera informe de cumplimiento ni completo—, y la carpeta incluye la sesión guardada en JSON. Se recorrió **pegando la descripción en el chat**, así que no lleva `README_sistema.md` y sí `descripcion.md`.
- **02-riesgo-limitado**: Regenerado con la versión actual (septiembre de 2026). Es el ejemplo del Art. 50, y el otro que se recorrió pegando la descripción en el chat en vez de subir un fichero de documentación técnica. La agencia es responsable del despliegue de los dos sistemas evaluados, así que el informe no le imputa el Art. 50.1 ni el Art. 50.2 —que obligan al proveedor— sino que los presenta como puntos de vigilancia sobre sus proveedores. La carpeta incluye la sesión guardada en JSON.
- **03-alto-riesgo**: Regenerado con la versión actual (septiembre de 2026). La entidad tiene un solo rol —implementador— y la carpeta incluye además la sesión guardada en JSON, que permite recargar el caso en la aplicación y regenerar los informes sin repetir el recorrido.
- **04-prohibido**: Aunque el sistema es una práctica prohibida (Art. 5), el ejemplo incluye análisis de cumplimiento para documentar las medidas de cese, retirada, rediseño y remediación requeridas.
- **05-excluido**: Regenerado con la versión actual (septiembre de 2026). El sistema SÍ es IA (cumple el Art. 3.1), pero queda fuera del Reglamento por la exclusión del Art. 2.3 para los sistemas desarrollados y utilizados exclusivamente con fines militares. La entidad es proveedora. El flujo termina en la clasificación —no se inicia análisis de cumplimiento bajo el AI Act—, y la carpeta incluye la sesión guardada en JSON, que permite recargar el caso en la aplicación y regenerar el informe sin repetir el recorrido.
- **El 00 y el 05 son las dos formas distintas de quedar fuera**, y conviene leerlos juntos: en el 00 el sistema no llega a ser un sistema de IA (falla la definición del Art. 3.1); en el 05 sí lo es, y lo que lo deja fuera es el ámbito de aplicación (Art. 2). El informe cita el artículo que corresponde en cada caso.
- Los informes PDF y TXT son los generados directamente por AIComply durante la evaluación del ejemplo.
- Todos los sistemas y empresas son ficticios, creados como casos de uso representativos de PYMEs.

## Uso en demos

Cada subcarpeta es autosuficiente: puede presentarse de forma independiente en una demo. La secuencia recomendada para una presentación completa es seguir el orden 00 → 04, de menor a mayor complejidad regulatoria. El 00 y el 05 pueden usarse juntos, y de forma independiente del resto, para ilustrar la distinción entre quedar fuera por la definición (Art. 3.1) y quedar fuera por el ámbito (Art. 2); y el 02, para mostrar que el Art. 50 reparte sus apartados entre el proveedor y el responsable del despliegue, y que la herramienta no imputa a uno las obligaciones del otro.

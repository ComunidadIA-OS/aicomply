# Ejemplos AIComply

> ### ⚠️ Estos ejemplos son de mayo de 2026 y no reflejan la versión actual
>
> Se generaron con la versión v0.1.0 del hackathon. Desde entonces se han corregido varios
> defectos que **siguen presentes en estas transcripciones e informes**:
>
> | En los ejemplos aparece | La versión actual dice |
> |---|---|
> | El Ómnibus como «acuerdo provisional pendiente de publicación en el DOUE» | Reglamento (UE) 2026/1744, en vigor desde el 27 de julio de 2026 |
> | Art. 50.1, 50.3 y 50.4 aplicables «desde el 2 de agosto de 2025» | Desde el 2 de agosto de 2026 |
> | Art. 50.2 con fecha única de 2 de diciembre de 2026 | Condicional: periodo de gracia solo para sistemas ya en el mercado antes del 2 de agosto de 2026 |
> | Planes de acción que piden a un implementador documentación técnica del Anexo IV, sistema de gestión de calidad y marcado CE | Plan construido según el rol de la entidad |
> | Art. 49 como carencia legal de un implementador privado | Se pregunta por el carácter público antes de etiquetarlo; para una entidad privada, no aplica |
>
> Se conservan porque documentan el estado del proyecto en la entrega del hackathon y porque
> las conversaciones ilustran bien el recorrido del árbol de decisión. **No los use como
> referencia normativa.** Se regenerarán con la versión actual.


Esta carpeta contiene seis ejemplos completos de evaluación con AIComply, preparados para revisión en GitHub y uso en demos del hackathon SEDIA 2026.

Cada ejemplo incluye la conversación completa con el asistente, los informes generados en PDF y texto plano, y un README explicativo.

## Tabla de ejemplos

| Carpeta | Tipo | Sector | Sistema | Informes disponibles |
|---|---|---|---|---|
| [00-no-ia](00-no-ia/) | Fuera de alcance | Metalmecánica | Hoja Excel con reglas deterministas de stock | Solo evaluación |
| [01-riesgo-minimo](01-riesgo-minimo/) | Riesgo mínimo | Fundición | Optimización energética de hornos industriales | Evaluación, cumplimiento, completo |
| [02-riesgo-limitado](02-riesgo-limitado/) | Riesgo limitado | Cartón/Embalaje | CartonAssist B2B — chatbot comercial | Evaluación, cumplimiento, completo |
| [03-alto-riesgo](03-alto-riesgo/) | Alto riesgo | Automoción | TalentScreen Industrial — filtrado de CVs | Evaluación, cumplimiento, completo |
| [04-prohibido](04-prohibido/) | Prohibido | Agroindustria | Vigilancia emocional y scoring laboral | Evaluación, cumplimiento, completo |
| [05-excluido](05-excluido/) | Excluido (Art. 2) | Defensa | Visión artificial para control de calidad de drones militares | Solo evaluación |

## Notas

- **00-no-ia**: El sistema no cumple la definición de sistema de IA del Art. 3.1 del AI Act. El flujo termina tras la evaluación de clasificación; no se inicia análisis de cumplimiento.
- **04-prohibido**: Aunque el sistema es una práctica prohibida (Art. 5), el ejemplo incluye análisis de cumplimiento para documentar las medidas de cese, retirada, rediseño y remediación requeridas.
- **05-excluido**: El sistema SÍ es IA (cumple el Art. 3.1), pero queda fuera del Reglamento por la exclusión explícita del Art. 2 para uso militar. El flujo termina tras la evaluación; no se inicia análisis de cumplimiento bajo el AI Act.
- Los informes PDF y TXT son los generados directamente por AIComply durante la evaluación del ejemplo.
- Todos los sistemas son ficticios, creados como casos de uso representativos de PYMEs industriales españolas.

## Uso en demos

Cada subcarpeta es autosuficiente: puede presentarse de forma independiente en una demo. La secuencia recomendada para una presentación completa es seguir el orden 00 → 04, de menor a mayor complejidad regulatoria. El ejemplo 05 puede usarse de forma independiente para ilustrar la distinción entre exclusiones por definición (Art. 3.1) y exclusiones por ámbito (Art. 2).

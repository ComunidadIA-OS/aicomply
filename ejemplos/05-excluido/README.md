# Ejemplo: 05 — Sistema excluido del ámbito del AI Act (uso militar exclusivo)

## Tipo de resultado
Excluido — Art. 2 (uso militar exclusivo)

## Sector
Fabricación de componentes electrónicos para defensa

## Sistema evaluado
Sistema de IA de visión artificial que analiza imágenes de placas electrónicas y carcasas de drones militares para detectar grietas, daños térmicos, corrosión o defectos de montaje. La PYME lo ha desarrollado internamente y lo opera bajo contrato con el Ministerio de Defensa español. El sistema utiliza una red neuronal entrenada con imágenes históricas y clasifica cada componente como "apta", "requiere revisión" o "rechazada". Su uso es estrictamente militar; no se comercializa ni se utiliza en líneas de producción civiles.

## Resultado esperado
El sistema queda excluido del ámbito de aplicación del Reglamento (UE) 2024/1689 por uso militar exclusivo (Art. 2). El Reglamento no impone ninguna obligación. Rol identificado: Proveedor / Implementador.

## Archivos incluidos

- `conversacion_original.txt` — Conversación completa exportada del asistente AIComply
- `conversacion_evaluacion_clasificacion.md` — Conversación de evaluación y clasificación (archivo completo; no existe fase de cumplimiento)
- `conversacion_cumplimiento.md` — Nota de inaplicabilidad (sin análisis de cumplimiento)
- `informe_evaluacion.txt` — Informe de evaluación/clasificación en texto plano generado por AIComply
- `informe_evaluacion.pdf` — Informe de evaluación/clasificación en PDF

## Uso del ejemplo
Este ejemplo ilustra el segundo punto de exclusión del árbol de evaluación del AI Act: la comprobación del ámbito de aplicación (Art. 2). A diferencia del ejemplo 00 (donde el sistema no es IA), aquí el sistema SÍ cumple la definición técnica de sistema de IA del Art. 3.1 — tiene red neuronal, aprende de datos históricos y generaliza. Sin embargo, queda fuera del Reglamento porque la exclusión del Art. 2 para uso militar es explícita e independiente de las características técnicas del sistema.

Es especialmente útil para demostrar que el AI Act no regula todos los sistemas de IA, y para mostrar cómo AIComply distingue entre "no es IA" y "es IA pero está excluida del Reglamento". La distinción es relevante: las obligaciones que sí pueden aplicar son las de otras normativas sectoriales (normativa de defensa, contratos con el Ministerio, legislación OTAN, exportación de material de defensa), no el AI Act.

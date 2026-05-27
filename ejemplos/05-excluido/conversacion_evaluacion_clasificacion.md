# Conversación de evaluación y clasificación

## Ejemplo
05 — Sistema excluido del ámbito del AI Act (uso militar exclusivo)

## Tipo de resultado
Excluido — Art. 2 (uso militar exclusivo)

## Sector
Fabricación de componentes electrónicos para defensa

## Sistema evaluado
Una PYME industrial española fabrica componentes electrónicos para drones de uso exclusivamente militar bajo contrato con el Ministerio de Defensa. La empresa ha desarrollado un sistema de IA de visión artificial que analiza imágenes de placas electrónicas y carcasas de drones militares para detectar grietas, daños térmicos, corrosión o defectos de montaje. El sistema utiliza una red neuronal entrenada con imágenes históricas y genera una clasificación automática de cada pieza como "apta", "requiere revisión" o "rechazada".

## Resultado
El sistema queda excluido del ámbito de aplicación del Reglamento (UE) 2024/1689 por uso militar exclusivo (Art. 2). El Reglamento no impone obligación alguna. Rol: Proveedor / Implementador.

## Conversación

**Evaluador y clasificador**

> Describa su sistema de IA en lenguaje natural o inicie a partir de su documentación técnica. Le haré las preguntas necesarias para determinar su clasificación y obligaciones.

**Usuario:** Una PYME industrial española fabrica componentes electrónicos para drones de uso exclusivamente militar bajo contrato con el Ministerio de Defensa. La empresa ha desarrollado un sistema de IA de visión artificial que analiza imágenes de placas electrónicas y carcasas de drones militares para detectar grietas, daños térmicos, corrosión o defectos de montaje. El sistema utiliza una red neuronal entrenada con imágenes históricas de componentes militares inspeccionados previamente. Genera una clasificación automática de cada pieza como "apta", "requiere revisión" o "rechazada", y propone al técnico de calidad qué componentes deben retirarse del lote. El sistema se usa únicamente dentro de una línea de fabricación destinada a material militar. No se comercializa para usos civiles, no se utiliza en productos industriales ordinarios y no se pone a disposición de clientes privados. Su finalidad exclusiva es apoyar el control de calidad de componentes destinados a drones militares.

**AIComply:** Antes de comenzar, un aviso breve: este análisis es una orientación preliminar basada en el Reglamento (UE) 2024/1689. No constituye asesoramiento jurídico vinculante. Le recomiendo contrastar las conclusiones con un profesional especializado en derecho tecnológico o cumplimiento normativo.

Dicho esto, la descripción que ha facilitado permite llegar a una conclusión con bastante claridad, sin necesidad de recorrer todo el árbol de decisión.

El elemento determinante en este caso es el ámbito de aplicación del Reglamento. El artículo 2 del Reglamento (UE) 2024/1689 excluye expresamente de su ámbito los sistemas de IA utilizados exclusivamente con fines militares o de defensa, con independencia de quién los desarrolle o dónde se usen.

En su caso:
- El sistema analiza componentes destinados únicamente a drones militares bajo contrato con el Ministerio de Defensa.
- No se comercializa para usos civiles ni se pone a disposición de terceros privados.
- Su finalidad es estrictamente el control de calidad dentro de una línea de fabricación de material militar.

Esto encaja con precisión en la exclusión por uso militar. No obstante, permítame confirmar un punto antes de cerrar el análisis:

¿El sistema se utiliza o se utilizará en algún momento también en líneas de producción de componentes electrónicos de uso civil o dual, aunque sea de forma puntual o experimental?

**Usuario:** No

**AIComply:** Perfecto. Con esa confirmación, el análisis está completo.

---

### Informe final

**1. Resumen ejecutivo**

La organización ha desarrollado y opera internamente un sistema de IA de visión artificial para el control de calidad de componentes electrónicos destinados exclusivamente a drones militares. Tras analizar la descripción facilitada y confirmar que el sistema no tiene ningún uso civil ni dual, se concluye que el sistema queda excluido del ámbito de aplicación del Reglamento (UE) 2024/1689. El Reglamento no impone obligación alguna sobre este sistema en su configuración actual.

**2. Obligaciones identificadas**

Ninguna obligación bajo el Reglamento (UE) 2024/1689 en la configuración actual del sistema.

El artículo 2 del Reglamento excluye expresamente los sistemas de IA desarrollados y utilizados exclusivamente con fines militares. Esta exclusión es sensible al uso real del sistema: si en el futuro el sistema se reutiliza en líneas de producción civiles o duales, o se comercializa a terceros, la exclusión dejaría de ser válida.

**3. Recorrido realizado (traza auditable)**

| Nodo | Criterio | Resultado |
|---|---|---|
| Art. 3.1 — Definición de sistema de IA | Red neuronal con capacidad de inferencia | Cumple la definición |
| Tipo de entidad | Desarrolla y opera internamente | Proveedor / Implementador |
| Ámbito territorial | Establecida en España (UE) | Dentro del ámbito territorial |
| Art. 2 — Exclusión por uso militar | Uso exclusivo en fabricación de material militar, sin uso civil ni dual | **EXCLUIDO** |

**4. Puntos que requieren revisión profesional**

No existen nodos indeterminados. La exclusión es clara con la información facilitada. Se recomienda revisión profesional ante:
- Cualquier ampliación del uso a componentes civiles o de uso dual.
- Cambios en el marco normativo de la Comisión Europea sobre exclusiones del AI Act.
- Otras normativas sectoriales aplicables (normativa OTAN, legislación de exportación de material de defensa).

---

**Evaluación completada — Clasificación: EXCLUIDO | Rol: Proveedor / Implementador**

# Corpus normativo AIComply

Conjunto curado de fuentes oficiales sobre la Ley de Inteligencia
Artificial de la UE (Reglamento (UE) 2024/1689), procesado en formato
JSON estructurado para uso en pipelines de RAG, búsqueda semántica,
o análisis legal asistido por IA.

## Contenido

- `ai_act/ai_act_articles.json` — 25 artículos clave del AI Act
  procesados con: título, capítulo, nivel de riesgo asociado, texto
  oficial, requisitos clave, ámbito de aplicación y palabras clave.
  Incluye también las 8 categorías del Anexo III (alto riesgo).

- `docs/*.json` — 27 documentos complementarios (273 fragmentos
  totales): el texto consolidado del AI Act, 16 guías de la AESIA,
  borradores de directrices de la Comisión Europea sobre clasificación
  de alto riesgo (mayo 2026), opinión EDPB 28/2024 sobre modelos de
  IA, orientaciones sobre IA agéntica, y el Anteproyecto de Ley
  español de Buen Uso y Gobernanza de la IA.

## Estructura de cada fichero

Cada fichero en `docs/` sigue este esquema:

```json
{
  "titulo": "Guía de gestión de riesgos",
  "fuente": "AESIA",
  "tipo": "guia_oficial",
  "fecha": "2024-01-01",
  "url": "https://www.aesia.es",
  "total_fragmentos": 12,
  "documentos": [
    {
      "id": "aesia-gestion-riesgos-s3",
      "titulo": "Sección 3.1 — Identificación de riesgos",
      "capitulo": "3. Gestión de riesgos",
      "fuente": "AESIA",
      "texto": "..."
    }
  ]
}
```

Los valores admitidos para `tipo` son: `reglamento_ue`, `ley_nacional`,
`guia_oficial`, `directriz`, `documento_legal`.

## Cómo reutilizarlo

Ejemplo mínimo (sin dependencias de AIComply):

```python
import json
from pathlib import Path

for fichero in Path("data/docs").glob("*.json"):
    d = json.load(open(fichero))
    for frag in d.get("documentos", []):
        print(frag["titulo"], "—", frag["texto"][:100])
```

Para usar el corpus en un pipeline RAG propio basta con leer los
fragmentos, construir los embeddings con la librería de tu elección
(sentence-transformers, OpenAI embeddings, etc.) e indexarlos en el
vectorstore que prefieras.

## Licencia

Los datos curados (la estructura JSON, el etiquetado, los resúmenes y
el procesamiento) se publican bajo la misma licencia Apache 2.0 del
proyecto. El TEXTO OFICIAL de los documentos pertenece a sus fuentes
originales:

- Reglamento (UE) 2024/1689 → EUR-Lex, CELEX:32024R1689
- Guías AESIA → Agencia Española de Supervisión de la IA, dominio público
- Borradores de directrices → Comisión Europea, dominio público
- Anteproyecto de Ley español → Ministerio para la Transformación Digital

## Cómo contribuir

¿Has detectado un error de procesamiento, un fragmento mal asignado o
quieres añadir una nueva guía oficial? Abre un issue o un PR siguiendo
las normas de [`CONTRIBUTING.md`](../CONTRIBUTING.md).

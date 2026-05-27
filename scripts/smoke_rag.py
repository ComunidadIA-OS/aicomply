# Copyright 2026 AIComply Contributors
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""
smoke_rag.py — SOLO LECTURA
Foto del comportamiento del retriever TF-IDF ANTES de re-fragmentar el corpus.
Ejecuta 5 consultas representativas e imprime los fragmentos recuperados
con su origen y longitud en caracteres.
"""

import sys
from pathlib import Path

# Asegurar que el root del proyecto está en el path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.rag.retriever import buscar_articulos

CONSULTAS = [
    "obligaciones de transparencia de un chatbot",
    "documentación técnica Anexo IV",
    "gestión de riesgos alto riesgo",
    "categorización biométrica prohibida",
    "evaluación de impacto derechos fundamentales",
]


def main():
    total_chars = 0
    fragmentos_grandes = 0

    for i, consulta in enumerate(CONSULTAS, 1):
        print(f"\n{'='*70}")
        print(f"[{i}] Consulta: «{consulta}»")
        print("=" * 70)

        resultados = buscar_articulos(consulta, top_k=3)

        if not resultados:
            print("  (sin resultados)")
            continue

        for j, doc in enumerate(resultados, 1):
            meta   = doc.get("metadata", {})
            titulo = meta.get("titulo") or meta.get("articulo") or "—"
            fuente = meta.get("fichero") or meta.get("fuente") or "ai_act_articles.json"
            chars  = len(doc.get("texto", ""))
            total_chars += chars
            if chars > 8_000:
                fragmentos_grandes += 1
            alerta = "  ⚠ GRANDE" if chars > 8_000 else ""
            print(f"  [{j}] {titulo}")
            print(f"       fichero: {fuente}")
            print(f"       longitud: {chars:,} chars{alerta}")

    print(f"\n{'='*70}")
    print(f"RESUMEN — {len(CONSULTAS)} consultas, top_k=3")
    print(f"  Fragmentos recuperados totales : {len(CONSULTAS) * 3}")
    print(f"  Fragmentos > 8.000 chars       : {fragmentos_grandes}")
    print(f"  Caracteres totales inyectados  : {total_chars:,}")
    print(f"  Media por fragmento            : {total_chars // (len(CONSULTAS)*3):,} chars")
    print("=" * 70)
    print()


if __name__ == "__main__":
    main()

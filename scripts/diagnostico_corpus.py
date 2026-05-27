"""
diagnostico_corpus.py — SOLO LECTURA
Recorre data/docs/*.json y data/ai_act/ai_act_articles.json e imprime
estadísticas de fragmentación sin modificar ningún fichero.
"""

import json
import sys
from pathlib import Path

ROOT = Path(__file__).parent.parent
DOCS_DIR  = ROOT / "data" / "docs"
AI_ACT    = ROOT / "data" / "ai_act" / "ai_act_articles.json"

UMBRAL_ALERTA = 8_000  # caracteres


def analizar_docs_json(path: Path) -> tuple[int, int, int]:
    """Devuelve (num_fragmentos, max_chars, total_chars) para un fichero data/docs."""
    with open(path, encoding="utf-8") as f:
        datos = json.load(f)

    fragmentos = datos.get("documentos", [])
    if not fragmentos:
        return 0, 0, 0

    longitudes = [len(fr.get("texto", "")) for fr in fragmentos]
    return len(longitudes), max(longitudes), sum(longitudes)


def analizar_ai_act(path: Path) -> tuple[int, int, int]:
    """Devuelve (num_fragmentos, max_chars, total_chars) para ai_act_articles.json."""
    with open(path, encoding="utf-8") as f:
        datos = json.load(f)

    textos = []
    for contenido in datos.get("articulos", {}).values():
        partes = [
            contenido.get("texto_oficial", ""),
            "; ".join(contenido.get("requisitos_clave", [])),
            contenido.get("aplica_a", ""),
            " ".join(contenido.get("palabras_clave", [])),
        ]
        textos.append("\n".join(p for p in partes if p))

    for info in datos.get("categorias_alto_riesgo", {}).values():
        textos.append(info.get("descripcion", ""))

    if not textos:
        return 0, 0, 0

    longitudes = [len(t) for t in textos]
    return len(longitudes), max(longitudes), sum(longitudes)


def main():
    filas = []

    # --- data/docs/*.json ---
    for path in sorted(DOCS_DIR.glob("*.json")):
        try:
            n, mx, total = analizar_docs_json(path)
        except Exception as e:
            print(f"[ERROR] {path.name}: {e}", file=sys.stderr)
            continue
        filas.append((path.name, n, mx, total))

    # --- ai_act_articles.json ---
    try:
        n, mx, total = analizar_ai_act(AI_ACT)
        filas.append((AI_ACT.name, n, mx, total))
    except Exception as e:
        print(f"[ERROR] {AI_ACT.name}: {e}", file=sys.stderr)

    # --- Tabla ---
    col_w = [max(len(f[0]) for f in filas) + 2, 12, 14, 14]
    sep = "+" + "+".join("-" * w for w in col_w) + "+"
    hdr = "| {:<{}} | {:>{}} | {:>{}} | {:>{}} |".format(
        "Fichero", col_w[0]-2,
        "Fragmentos", col_w[1]-2,
        "Max (chars)", col_w[2]-2,
        "Total (chars)", col_w[3]-2,
    )

    print("\n" + sep)
    print(hdr)
    print(sep)
    for nombre, n, mx, total in filas:
        alerta = " !" if mx > UMBRAL_ALERTA else "  "
        print("| {:<{}} | {:>{}} | {:>{}} | {:>{}} |{}".format(
            nombre, col_w[0]-2,
            n, col_w[1]-2,
            f"{mx:,}", col_w[2]-2,
            f"{total:,}", col_w[3]-2,
            alerta,
        ))
    print(sep)

    # --- Ficheros problemáticos ---
    grandes = [(n, mx, total) for n, mx, total in
               [(f[0], f[2], f[3]) for f in filas] if mx > UMBRAL_ALERTA]

    print(f"\nFicheros con fragmento más largo > {UMBRAL_ALERTA:,} chars ({len([f for f in filas if f[2] > UMBRAL_ALERTA])}):")
    for nombre, mx, total in [(f[0], f[2], f[3]) for f in filas if f[2] > UMBRAL_ALERTA]:
        print(f"  - {nombre}  (max={mx:,}, total={total:,})")

    print()


if __name__ == "__main__":
    main()

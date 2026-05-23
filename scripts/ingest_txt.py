#!/usr/bin/env python3
# Copyright 2025 AIComply Contributors
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0

"""
Convierte documentos legales .txt en JSON para el RAG de AIComply.

Uso básico:
    python scripts/ingest_txt.py ruta/al/documento.txt \
        --titulo "Anteproyecto de Ley de IA" \
        --fuente "Ministerio de Transformación Digital" \
        --tipo ley_nacional

El JSON resultante se guarda en data/docs/<nombre_fichero>.json y es
cargado automáticamente por el vectorstore en el próximo arranque.
"""

import argparse
import json
import re
import sys
from pathlib import Path

# Patrones para detectar límites de artículos en textos legales españoles.
# Capturan: "Artículo 1.", "Artículo 1 bis.", "ARTÍCULO 1.", etc.
_RE_ARTICULO = re.compile(
    r"^(?:Art[ií]culo|ARTÍCULO|ARTICULO)\s+(\d+\s*(?:bis|ter|quáter)?)\s*[.\-–]?\s*(.*)$",
    re.MULTILINE,
)

# Captura cabeceras de capítulo para enriquecer la metadata de cada artículo.
_RE_CAPITULO = re.compile(
    r"^(?:CAP[ÍI]TULO|Capítulo)\s+[IVXLCDM\d]+\s*[:\-–]?\s*(.*)$",
    re.MULTILINE,
)

# Captura disposiciones adicionales, finales y anexos.
_RE_DISPOSICION = re.compile(
    r"^(Disposici[oó]n\s+(?:adicional|final|transitoria|derogatoria)\s+\w+(?:\s+\w+)?|ANEXO\s*[IVXLCDM\d]*)\s*[.\-–]?\s*(.*)$",
    re.MULTILINE,
)

DATA_DOCS = Path(__file__).parent.parent / "data" / "docs"


def _limpiar(texto: str) -> str:
    """Elimina líneas vacías múltiples y espacios sobrantes."""
    texto = re.sub(r"\n{3,}", "\n\n", texto)
    return texto.strip()


def _extraer_capitulo_activo(texto: str, hasta_pos: int) -> str:
    """Devuelve el último capítulo encontrado antes de la posición dada."""
    capitulo = ""
    for m in _RE_CAPITULO.finditer(texto):
        if m.start() >= hasta_pos:
            break
        capitulo = m.group(1).strip()
    return capitulo


def trocear_por_articulo(texto: str, titulo_doc: str, fuente: str) -> list[dict]:
    """
    Divide un texto legal en fragmentos por artículo.
    Los bloques previos al primer artículo (exposición de motivos, preámbulo)
    se conservan como un fragmento único de introducción.
    Las disposiciones y anexos al final también se capturan.
    """
    fragmentos = []

    # Recoger todos los puntos de corte: artículos + disposiciones
    cortes: list[tuple[int, str, str]] = []  # (pos, tipo, encabezado)
    for m in _RE_ARTICULO.finditer(texto):
        num = m.group(1).strip()
        titulo_art = m.group(2).strip()
        cortes.append((m.start(), f"Art. {num}", titulo_art))
    for m in _RE_DISPOSICION.finditer(texto):
        tipo_disp = m.group(1).strip()
        titulo_disp = m.group(2).strip()
        cortes.append((m.start(), tipo_disp, titulo_disp))

    cortes.sort(key=lambda x: x[0])

    if not cortes:
        # Sin artículos: tratar el documento completo como un fragmento
        fragmentos.append({
            "id": f"{_slug(fuente)}-completo",
            "titulo": titulo_doc,
            "texto": _limpiar(texto),
            "capitulo": "",
            "fuente": fuente,
        })
        return fragmentos

    # Bloque previo al primer artículo (preámbulo / exposición de motivos)
    preambulo = texto[: cortes[0][0]].strip()
    if preambulo:
        fragmentos.append({
            "id": f"{_slug(fuente)}-preambulo",
            "titulo": f"Preámbulo — {titulo_doc}",
            "texto": _limpiar(preambulo),
            "capitulo": "Preámbulo",
            "fuente": fuente,
        })

    # Artículos y disposiciones
    for i, (pos, ref, titulo_art) in enumerate(cortes):
        fin = cortes[i + 1][0] if i + 1 < len(cortes) else len(texto)
        cuerpo = texto[pos:fin].strip()
        capitulo = _extraer_capitulo_activo(texto, pos)

        titulo_completo = f"{ref}: {titulo_art}" if titulo_art else ref

        fragmentos.append({
            "id": f"{_slug(fuente)}-{_slug(ref)}",
            "titulo": titulo_completo,
            "texto": _limpiar(cuerpo),
            "capitulo": capitulo,
            "fuente": fuente,
        })

    return fragmentos


def _slug(texto: str) -> str:
    """Genera un identificador seguro para ficheros y IDs."""
    texto = texto.lower()
    texto = re.sub(r"[áàä]", "a", texto)
    texto = re.sub(r"[éèë]", "e", texto)
    texto = re.sub(r"[íìï]", "i", texto)
    texto = re.sub(r"[óòö]", "o", texto)
    texto = re.sub(r"[úùü]", "u", texto)
    texto = re.sub(r"[ñ]", "n", texto)
    texto = re.sub(r"[^a-z0-9]+", "-", texto)
    return texto.strip("-")[:60]


def ingestar(
    ruta_txt: Path,
    titulo: str,
    fuente: str,
    tipo: str,
    fecha: str,
    url: str,
    salida: Path | None = None,
) -> Path:
    texto = ruta_txt.read_text(encoding="utf-8", errors="replace")
    fragmentos = trocear_por_articulo(texto, titulo, fuente)

    resultado = {
        "titulo": titulo,
        "fuente": fuente,
        "tipo": tipo,
        "fecha": fecha,
        "url": url,
        "total_fragmentos": len(fragmentos),
        "documentos": fragmentos,
    }

    if salida is None:
        DATA_DOCS.mkdir(parents=True, exist_ok=True)
        salida = DATA_DOCS / f"{ruta_txt.stem}.json"

    salida.write_text(json.dumps(resultado, ensure_ascii=False, indent=2), encoding="utf-8")
    return salida


def main() -> None:
    parser = argparse.ArgumentParser(description="Ingesta un .txt legal en el RAG de AIComply")
    parser.add_argument("fichero", type=Path, help="Ruta al fichero .txt")
    parser.add_argument("--titulo", required=True, help="Título del documento")
    parser.add_argument("--fuente", required=True, help="Organismo emisor")
    parser.add_argument(
        "--tipo",
        default="documento_legal",
        choices=["ley_nacional", "reglamento_ue", "guia_oficial", "directriz", "documento_legal"],
        help="Tipo de documento",
    )
    parser.add_argument("--fecha", default="", help="Fecha de publicación (YYYY-MM-DD)")
    parser.add_argument("--url", default="", help="URL del documento original")
    parser.add_argument("--salida", type=Path, default=None, help="Ruta de salida del JSON")
    args = parser.parse_args()

    if not args.fichero.exists():
        print(f"Error: no se encuentra el fichero '{args.fichero}'", file=sys.stderr)
        sys.exit(1)

    ruta_json = ingestar(
        ruta_txt=args.fichero,
        titulo=args.titulo,
        fuente=args.fuente,
        tipo=args.tipo,
        fecha=args.fecha,
        url=args.url,
        salida=args.salida,
    )

    datos = json.loads(ruta_json.read_text(encoding="utf-8"))
    print(f"✓ {datos['total_fragmentos']} fragmentos → {ruta_json}")


if __name__ == "__main__":
    main()

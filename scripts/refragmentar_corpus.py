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
refragmentar_corpus.py — Re-fragmenta data/docs/*.json en chunks de 1500-4000 chars.

Reglas:
- Backup intacto en data/docs/_backup_prefragmentacion/ antes de tocar nada.
- División por límites naturales: \\f > párrafos dobles > líneas simples.
- Overlap de ~150 chars entre chunks contiguos.
- NO reescribe texto: solo trocea. Aserción de integridad incluida.
- IDs deterministas: <id_original>-c01, -c02, ...
- Ficheros excluidos (ya fragmentados): ver EXCLUIR.
"""

import json
import re
import shutil
import sys
from pathlib import Path

ROOT     = Path(__file__).parent.parent
DOCS_DIR = ROOT / "data" / "docs"
BACKUP   = DOCS_DIR / "_backup_prefragmentacion"

TARGET_MIN = 1_500
TARGET_MAX = 4_000
OVERLAP    = 150
UMBRAL     = 8_000   # solo se procesa un fragmento si supera este tamaño

# Ficheros con fragmentación ya adecuada — no tocar
EXCLUIR = {
    "AIAct.json",
    "Omnibus.json",
    "06-guia-vigilancia-humana.json",
    "Anteproyecto de Ley.json",
    "requisitos-auditorias-tratamientos-incluyan-ia.json",
}

# Patrón de encabezado de sección al inicio de una línea
_RE_SECCION = re.compile(r"^(?:\d+(?:\.\d+)*\.?\s+\S.{0,79})", re.MULTILINE)


# ── Utilidades ────────────────────────────────────────────────────────────────

def _encontrar_rangos(texto: str, target_min: int, target_max: int) -> list[tuple[int, int]]:
    """
    Devuelve lista de (start, end) sin overlap que cubre texto[0:len(texto)].
    Garantía: rangos[i][1] == rangos[i+1][0] y ''.join(texto[s:e]) == texto.
    """
    n = len(texto)
    if n == 0:
        return []

    # Recopilar posiciones de corte, con prioridad implícita por orden de inserción
    pos_set: set[int] = {0, n}

    for m in re.finditer(r"\f", texto):           # form feeds
        pos_set.add(m.end())
    for m in re.finditer(r"(?m)^(?:\d+\.)+\s*\d*\.?\s+\S", texto):  # secciones
        pos_set.add(m.start())
    for m in re.finditer(r"\n{2,}", texto):       # dobles saltos
        pos_set.add(m.end())
    for m in re.finditer(r"\n", texto):           # saltos simples (fallback)
        pos_set.add(m.end())

    posiciones = sorted(pos_set)

    rangos: list[tuple[int, int]] = []
    inicio = 0

    for pos in posiciones:
        if pos <= inicio:
            continue
        tam = pos - inicio
        if tam >= target_max or tam >= target_min:
            rangos.append((inicio, pos))
            inicio = pos

    # Cola: texto restante
    if inicio < n:
        if rangos and (n - inicio) < TARGET_MIN // 3:
            s, _ = rangos[-1]
            rangos[-1] = (s, n)
        else:
            rangos.append((inicio, n))

    # Aserción de cobertura total y contigüidad
    assert rangos, "No se generaron rangos"
    assert rangos[0][0] == 0, "El primer rango no empieza en 0"
    assert rangos[-1][1] == n, f"El último rango no termina en {n}: termina en {rangos[-1][1]}"
    for i in range(len(rangos) - 1):
        assert rangos[i][1] == rangos[i + 1][0], (
            f"Hueco entre rango {i} ({rangos[i]}) y {i+1} ({rangos[i+1]})"
        )

    return rangos


def _titulo_desde_chunk(texto_chunk: str, titulo_padre: str) -> str:
    """Intenta extraer un encabezado de sección del inicio del chunk."""
    candidato = texto_chunk.lstrip("\f\n\r ")
    for linea in candidato.split("\n")[:6]:
        linea = linea.strip()
        if len(linea) < 4:
            continue
        if re.match(r"^\d+(?:\.\d+)*\.?\s+\S", linea):
            seccion = linea[:80].rstrip(".")
            return f"{titulo_padre} — {seccion}"
        if len(linea) >= 8 and linea.isupper() and not re.search(r"\d{6,}", linea):
            return f"{titulo_padre} — {linea[:60]}"
    return titulo_padre


def _fragmentar_texto(
    frag_original: dict,
    target_min: int = TARGET_MIN,
    target_max: int = TARGET_MAX,
    overlap: int = OVERLAP,
) -> list[dict]:
    """
    Divide un fragmento grande en sub-fragmentos respetando límites naturales.
    Si el texto es <= UMBRAL lo devuelve intacto.
    """
    texto = frag_original.get("texto", "")
    if len(texto) <= UMBRAL:
        return [frag_original]

    id_orig   = frag_original.get("id", "frag")
    tit_orig  = frag_original.get("titulo", "")
    cap_orig  = frag_original.get("capitulo", "")
    fue_orig  = frag_original.get("fuente", "")

    rangos = _encontrar_rangos(texto, target_min, target_max)

    # Aserción de integridad: la concatenación de las porciones únicas == texto original
    assert "".join(texto[s:e] for s, e in rangos) == texto, (
        f"[{id_orig}] La concatenación de rangos no reproduce el texto original"
    )

    sub_fragmentos = []
    for i, (s, e) in enumerate(rangos):
        num = f"c{i+1:02d}"
        overlap_s = max(0, s - overlap)
        texto_chunk = texto[overlap_s:e]

        titulo_chunk = _titulo_desde_chunk(texto[s:e], tit_orig)

        sub_fragmentos.append({
            "id":       f"{id_orig}-{num}",
            "titulo":   titulo_chunk,
            "texto":    texto_chunk,
            "capitulo": cap_orig,
            "fuente":   fue_orig,
        })

    return sub_fragmentos


# ── Lógica principal ──────────────────────────────────────────────────────────

def procesar_fichero(path: Path, dry_run: bool = False) -> tuple[int, int]:
    """
    Procesa un fichero JSON: re-fragmenta los fragmentos grandes.
    Devuelve (fragmentos_originales, fragmentos_nuevos).
    """
    with open(path, encoding="utf-8") as f:
        datos = json.load(f)

    frags_orig = datos.get("documentos", [])
    max_len = max((len(fr.get("texto", "")) for fr in frags_orig), default=0)

    if max_len <= UMBRAL:
        return len(frags_orig), len(frags_orig)

    # Backup
    BACKUP.mkdir(parents=True, exist_ok=True)
    dest_backup = BACKUP / path.name
    if not dest_backup.exists():
        shutil.copy2(path, dest_backup)

    nuevos_docs: list[dict] = []
    for frag in frags_orig:
        nuevos_docs.extend(_fragmentar_texto(frag))

    datos["documentos"]      = nuevos_docs
    datos["total_fragmentos"] = len(nuevos_docs)

    if not dry_run:
        with open(path, "w", encoding="utf-8") as f:
            json.dump(datos, f, ensure_ascii=False, indent=2)

    return len(frags_orig), len(nuevos_docs)


def main(dry_run: bool = False) -> None:
    ficheros = sorted(DOCS_DIR.glob("*.json"))
    print(f"\nModo: {'DRY-RUN' if dry_run else 'ESCRITURA'}")
    print(f"Directorio: {DOCS_DIR}")
    print(f"Backup:     {BACKUP}\n")

    total_orig = 0
    total_nuevo = 0
    procesados = 0
    omitidos = 0

    for path in ficheros:
        nombre = path.name

        if nombre in EXCLUIR:
            print(f"  [OMITIDO]  {nombre}")
            omitidos += 1
            continue

        n_orig, n_nuevo = procesar_fichero(path, dry_run=dry_run)
        total_orig  += n_orig
        total_nuevo += n_nuevo

        if n_nuevo > n_orig:
            procesados += 1
            print(f"  [OK]  {nombre:<70}  {n_orig:>3} → {n_nuevo:>4} fragmentos")
        else:
            print(f"  [---] {nombre:<70}  {n_orig:>3} fragmentos (sin cambio)")

    print(f"\nResumen:")
    print(f"  Ficheros procesados  : {procesados}")
    print(f"  Ficheros omitidos    : {omitidos}")
    print(f"  Fragmentos originales: {total_orig}")
    print(f"  Fragmentos nuevos    : {total_nuevo}")
    print(f"  Incremento           : +{total_nuevo - total_orig} ({(total_nuevo/max(total_orig,1)-1)*100:.0f}%)")
    if not dry_run:
        print(f"\n  Backup en: {BACKUP}")
    print()


if __name__ == "__main__":
    dry = "--dry-run" in sys.argv or "-n" in sys.argv
    main(dry_run=dry)

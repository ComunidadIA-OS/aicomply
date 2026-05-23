# Copyright 2025 AIComply Contributors
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

import json
from pathlib import Path

import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


DATA_DIR = Path(__file__).parent.parent.parent / "data" / "ai_act"
ARTICLES_FILE = DATA_DIR / "ai_act_articles.json"
DATA_DOCS_DIR = Path(__file__).parent.parent.parent / "data" / "docs"


def cargar_articulos_como_documentos() -> list[dict]:
    """Carga los artículos del AI Act como documentos para el vectorstore."""
    with open(ARTICLES_FILE, "r", encoding="utf-8") as f:
        datos = json.load(f)

    documentos = []

    for num_art, contenido in datos.get("articulos", {}).items():
        titulo = contenido.get("titulo", "")
        texto_oficial = contenido.get("texto_oficial", "")
        palabras_clave = contenido.get("palabras_clave", [])

        requisitos = contenido.get("requisitos_clave", [])
        aplica_a = contenido.get("aplica_a", "")

        texto_completo = f"Artículo {num_art}: {titulo}\n{texto_oficial}"
        if requisitos:
            texto_completo += "\nRequisitos clave: " + "; ".join(requisitos)
        if aplica_a:
            texto_completo += f"\nAplica a: {aplica_a}"
        if palabras_clave:
            texto_completo += "\nPalabras clave: " + " ".join(palabras_clave)

        documentos.append(
            {
                "texto": texto_completo,
                "metadata": {
                    "articulo": f"Art. {num_art}",
                    "titulo": titulo,
                    "numero": int(num_art),
                    "nivel_riesgo": contenido.get("nivel_riesgo", ""),
                },
            }
        )

    for categoria, info in datos.get("categorias_alto_riesgo", {}).items():
        ejemplos = info.get("ejemplos", [])
        texto = (
            f"Categoría de alto riesgo — {categoria}: {info.get('descripcion', '')} "
            f"({info.get('articulo', '')})"
        )
        if ejemplos:
            texto += " Ejemplos: " + "; ".join(ejemplos)

        documentos.append(
            {
                "texto": texto,
                "metadata": {
                    "articulo": info.get("articulo", "Anexo III"),
                    "titulo": f"Categoría alto riesgo: {categoria}",
                    "categoria": categoria,
                    "nivel_riesgo": "alto",
                },
            }
        )

    return documentos


def cargar_documentos_adicionales() -> list[dict]:
    """Carga fragmentos de documentos legales adicionales desde data/docs/*.json."""
    documentos = []
    if not DATA_DOCS_DIR.exists():
        return documentos

    for fichero in sorted(DATA_DOCS_DIR.glob("*.json")):
        try:
            with open(fichero, encoding="utf-8") as f:
                datos = json.load(f)
        except Exception:
            continue

        fuente = datos.get("fuente", fichero.stem)
        tipo = datos.get("tipo", "documento_legal")
        titulo_doc = datos.get("titulo", fichero.stem)

        for fragmento in datos.get("documentos", []):
            texto = fragmento.get("texto", "").strip()
            if not texto:
                continue

            titulo_frag = fragmento.get("titulo", "")
            capitulo = fragmento.get("capitulo", "")

            # Enriquecer el texto con contexto para que TF-IDF lo indexe bien
            texto_completo = f"{titulo_doc}\n{titulo_frag}\n{texto}"
            if capitulo:
                texto_completo = f"{capitulo}\n{texto_completo}"

            documentos.append({
                "texto": texto_completo,
                "metadata": {
                    "articulo": titulo_frag,
                    "titulo": titulo_frag,
                    "fuente": fuente,
                    "tipo": tipo,
                    "capitulo": capitulo,
                    "fichero": fichero.name,
                },
            })

    return documentos


class VectorstoreSimple:
    """Vectorstore TF-IDF sin dependencias externas de bases de datos vectoriales."""

    def __init__(self):
        self.documentos: list[dict] = []
        self.vectorizer = TfidfVectorizer(
            analyzer="word",
            ngram_range=(1, 2),
            min_df=1,
            sublinear_tf=True,
        )
        self.matriz_tfidf = None
        self._construir()

    def _construir(self) -> None:
        self.documentos = cargar_articulos_como_documentos() + cargar_documentos_adicionales()
        corpus = [doc["texto"] for doc in self.documentos]
        if corpus:
            self.matriz_tfidf = self.vectorizer.fit_transform(corpus)

    def buscar(self, consulta: str, top_k: int = 3) -> list[dict]:
        if self.matriz_tfidf is None or not consulta.strip():
            return self.documentos[:top_k]

        vector_consulta = self.vectorizer.transform([consulta])
        similitudes = cosine_similarity(vector_consulta, self.matriz_tfidf).flatten()
        indices_top = np.argsort(similitudes)[::-1][:top_k]

        resultados = []
        for idx in indices_top:
            if similitudes[idx] > 0:
                doc = self.documentos[idx].copy()
                doc["score"] = float(similitudes[idx])
                resultados.append(doc)

        return resultados if resultados else self.documentos[:top_k]


_instancia_cache: VectorstoreSimple | None = None


def obtener_vectorstore() -> VectorstoreSimple:
    global _instancia_cache
    if _instancia_cache is None:
        _instancia_cache = VectorstoreSimple()
    return _instancia_cache

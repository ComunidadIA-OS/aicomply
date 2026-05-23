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

import pytest

from src.rag.vectorstore import VectorstoreSimple, cargar_articulos_como_documentos


class TestCargarArticulos:
    def test_devuelve_lista_no_vacia(self):
        docs = cargar_articulos_como_documentos()
        assert len(docs) > 0

    def test_cada_documento_tiene_texto_y_metadata(self):
        docs = cargar_articulos_como_documentos()
        for doc in docs[:10]:
            assert "texto" in doc, f"Documento sin campo 'texto': {doc}"
            assert "metadata" in doc, f"Documento sin campo 'metadata': {doc}"

    def test_texto_no_vacio(self):
        docs = cargar_articulos_como_documentos()
        for doc in docs[:10]:
            assert isinstance(doc["texto"], str)
            assert len(doc["texto"]) > 0

    def test_metadata_tiene_articulo_y_titulo(self):
        docs = cargar_articulos_como_documentos()
        for doc in docs[:10]:
            meta = doc["metadata"]
            assert "articulo" in meta
            assert "titulo" in meta

    def test_contiene_articulos_del_ai_act(self):
        docs = cargar_articulos_como_documentos()
        textos = " ".join(d["texto"] for d in docs)
        assert "Artículo" in textos or "articulo" in textos.lower()


class TestVectorstoreSimple:
    @pytest.fixture(scope="class")
    def vs(self):
        return VectorstoreSimple()

    def test_carga_documentos(self, vs):
        assert len(vs.documentos) > 0

    def test_matriz_tfidf_construida(self, vs):
        assert vs.matriz_tfidf is not None

    def test_buscar_devuelve_lista(self, vs):
        resultados = vs.buscar("sistema de alto riesgo reconocimiento facial", top_k=3)
        assert isinstance(resultados, list)
        assert len(resultados) > 0

    def test_buscar_respeta_top_k(self, vs):
        resultados = vs.buscar("obligaciones del proveedor", top_k=2)
        assert len(resultados) <= 2

    def test_resultados_tienen_estructura_correcta(self, vs):
        resultados = vs.buscar("obligaciones Art. 9 gestión de riesgos", top_k=3)
        for r in resultados:
            assert "texto" in r
            assert "metadata" in r
            assert "score" in r
            assert isinstance(r["score"], float)
            assert 0.0 <= r["score"] <= 1.0

    def test_consulta_vacia_devuelve_fallback(self, vs):
        resultados = vs.buscar("", top_k=3)
        assert isinstance(resultados, list)

    def test_buscar_relevancia_alta_riesgo(self, vs):
        resultados = vs.buscar("proveedor alto riesgo documentación técnica Anexo IV", top_k=5)
        assert len(resultados) > 0
        # El resultado más relevante debe tener score > 0
        assert resultados[0]["score"] > 0

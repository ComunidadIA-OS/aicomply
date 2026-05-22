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

from .vectorstore import obtener_vectorstore


def buscar_articulos(consulta: str, top_k: int = 3) -> list[dict]:
    """Busca artículos relevantes del AI Act para una consulta dada."""
    vectorstore = obtener_vectorstore()
    return vectorstore.buscar(consulta, top_k)


def formatear_contexto_rag(consulta: str, top_k: int = 3) -> str:
    """Formatea los artículos más relevantes como contexto para el prompt de Claude."""
    documentos = buscar_articulos(consulta, top_k)
    if not documentos:
        return ""

    partes = ["Artículos relevantes del AI Act (Reglamento UE 2024/1689) para el contexto:"]
    for doc in documentos:
        meta = doc.get("metadata", {})
        articulo = meta.get("articulo", "")
        titulo = meta.get("titulo", "")
        partes.append(f"\n--- {articulo}: {titulo} ---\n{doc['texto']}")

    return "\n".join(partes)

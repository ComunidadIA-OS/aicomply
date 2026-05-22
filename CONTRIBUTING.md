# Guía de contribución a AIComply

Gracias por su interés en contribuir a AIComply. Este documento describe cómo colaborar en el proyecto de forma efectiva.

## Aviso legal

Al contribuir, acepta que sus contribuciones se publicarán bajo la [Licencia Apache 2.0](LICENSE).

## Formas de contribuir

- Reportar errores o problemas
- Proponer nuevas funcionalidades
- Añadir nuevos providers de LLM
- Mejorar la documentación
- Actualizar los artículos del AI Act
- Traducir a otros idiomas

---

## Configuración del entorno de desarrollo

```bash
git clone https://github.com/tu-usuario/aicomply.git
cd aicomply
python -m venv .venv
source .venv/bin/activate   # Linux/macOS
pip install -r requirements.txt
cp .env.example .env        # Configure su provider preferido
```

## Proceso de contribución

### 1. Crear una rama

```bash
git checkout -b feat/nombre-funcionalidad
# o
git checkout -b fix/descripcion-error
# o
git checkout -b provider/nombre-nuevo-provider
```

### 2. Cabecera obligatoria en ficheros `.py` nuevos

```python
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
```

### 3. Estilo de código

- Python 3.10+ con type hints
- Comentarios en español
- Sin emojis en la interfaz de usuario
- Lenguaje profesional y claro

### 4. Verificar que la aplicación funciona

```bash
streamlit run app.py
```

### 5. Enviar el pull request

```bash
git add .
git commit -m "feat: descripción concisa del cambio"
git push origin feat/nombre-funcionalidad
```

---

## Cómo añadir un nuevo provider de LLM

La arquitectura de AIComply hace que añadir soporte para un nuevo proveedor de LLM sea sencillo.

### Paso 1: Crear el fichero del provider

Cree `src/llm/mi_provider.py` implementando la clase abstracta `LLMProvider`:

```python
# Copyright 2025 AIComply Contributors
# [cabecera Apache 2.0 completa]

from typing import Generator
from .provider import LLMProvider


class MiNuevoProvider(LLMProvider):
    """Provider para MiServicio LLM."""

    def __init__(self, api_key: str, model: str = "mi-modelo-default"):
        # Inicialice el cliente del servicio aquí
        self._model = model

    @property
    def nombre_modelo(self) -> str:
        return self._model

    @property
    def nombre_provider(self) -> str:
        return "mi_provider"   # identificador único en minúsculas

    def chat(self, messages: list[dict], system_prompt: str = "") -> str:
        """
        messages: lista de {"role": "user"|"assistant", "content": "..."}
        system_prompt: string con el system prompt (puede estar vacío)
        Devuelve: string con la respuesta completa
        """
        # Implemente la llamada a la API aquí
        raise NotImplementedError

    def chat_stream(
        self, messages: list[dict], system_prompt: str = ""
    ) -> Generator[str, None, None]:
        """
        Produce fragmentos de texto (streaming).
        Si el servicio no soporta streaming, puede simular con:
          yield self.chat(messages, system_prompt)
        """
        raise NotImplementedError
```

### Paso 2: Registrar el provider en la fábrica

En `src/llm/factory.py`, añada la importación y el caso correspondiente:

```python
from .mi_provider import MiNuevoProvider

def crear_provider(config: dict) -> LLMProvider:
    tipo = config.get("provider", "anthropic")
    ...
    if tipo == "mi_provider":
        return MiNuevoProvider(
            api_key=config["api_key"],
            model=config.get("model", "mi-modelo-default"),
        )
    ...

def crear_provider_desde_env() -> LLMProvider | None:
    ...
    if provider_type == "mi_provider":
        return MiNuevoProvider(
            api_key=os.getenv("MI_PROVIDER_API_KEY", ""),
            model=os.getenv("MI_PROVIDER_MODEL", "mi-modelo-default"),
        )
    ...
```

### Paso 3: Añadir el aviso de privacidad en `app.py`

En el diccionario `_AVISOS` al inicio de `app.py`:

```python
_AVISOS = {
    ...
    "mi_provider": (
        "warning",   # "success" | "info" | "warning" | "error"
        "Descripción clara de las condiciones de privacidad de este provider.",
    ),
}
```

Y añada la opción en la función `mostrar_selector_provider()`.

### Paso 4: Añadir variables de entorno en `.env.example`

```bash
# ── Mi Nuevo Provider ──────────────────────────────────────────────────────────
MI_PROVIDER_API_KEY=your_key_here
MI_PROVIDER_MODEL=mi-modelo-default
```

### Paso 5: Actualizar `requirements.txt` si se necesita un nuevo paquete

```
mi-paquete-sdk>=1.0.0
```

### Paso 6: Documentar en README.md

Añada su provider a la tabla comparativa de privacidad y a la sección de ejemplos de configuración.

---

## Actualización de artículos del AI Act

El AI Act es una normativa viva. Si detecta que algún artículo en `data/ai_act/ai_act_articles.json` está desactualizado:

1. Consulte el texto oficial en [EUR-Lex](https://eur-lex.europa.eu/legal-content/ES/TXT/?uri=CELEX:32024R1689)
2. Actualice el JSON manteniendo la estructura existente
3. Indique en el PR el número de artículo y la referencia oficial

---

## Reportar errores

Abra un issue en GitHub con:
- Descripción clara del problema
- Pasos para reproducirlo
- Provider y modelo utilizados
- Versión de Python y sistema operativo

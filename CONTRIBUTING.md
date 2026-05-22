# Guía de contribución a AIComply

Gracias por su interés en contribuir a AIComply. Este documento describe cómo puede colaborar en el proyecto de forma efectiva.

## Aviso legal

Al contribuir a este proyecto, acepta que sus contribuciones se publicarán bajo la [Licencia Apache 2.0](LICENSE).

## Formas de contribuir

- Reportar errores o problemas
- Proponer nuevas funcionalidades
- Mejorar la documentación
- Actualizar los artículos del AI Act (cuando la normativa evolucione)
- Traducir a otros idiomas
- Enviar pull requests con correcciones o mejoras

## Proceso de contribución

### 1. Preparar el entorno

```bash
git clone https://github.com/tu-usuario/aicomply.git
cd aicomply
python -m venv .venv
source .venv/bin/activate   # Linux/macOS
pip install -r requirements.txt
cp .env.example .env        # Añada su ANTHROPIC_API_KEY
```

### 2. Crear una rama para su cambio

```bash
git checkout -b feat/nombre-de-la-funcionalidad
# o
git checkout -b fix/descripcion-del-error
```

Convención de nombres de rama:
- `feat/` — nueva funcionalidad
- `fix/` — corrección de errores
- `docs/` — cambios en documentación
- `data/` — actualizaciones de artículos del AI Act

### 3. Realizar los cambios

**Estilo de código:**
- Python 3.10+ con type hints
- Comentarios en español
- Cabecera de licencia Apache 2.0 en todos los ficheros `.py` nuevos
- Sin emojis en la interfaz de usuario ni en los mensajes del asistente
- Lenguaje profesional y claro

**Cabecera obligatoria para ficheros `.py` nuevos:**

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

### 4. Verificar que la aplicación funciona

```bash
streamlit run app.py
```

Compruebe que:
- El chatbot responde correctamente
- El análisis documental funciona con un README de prueba
- El informe se genera y descarga correctamente
- No hay mensajes de error en la consola

### 5. Enviar el pull request

```bash
git add .
git commit -m "feat: descripción concisa del cambio"
git push origin feat/nombre-de-la-funcionalidad
```

Abra un pull request en GitHub con:
- **Título:** descripción concisa del cambio
- **Descripción:** qué cambia, por qué y cómo probarlo
- **Tipo de cambio:** feat / fix / docs / data

## Actualización de artículos del AI Act

El AI Act es una normativa viva. Si detecta que algún artículo en `data/ai_act/ai_act_articles.json` está desactualizado o incompleto:

1. Consulte el texto oficial en [EUR-Lex](https://eur-lex.europa.eu/legal-content/ES/TXT/?uri=CELEX:32024R1689)
2. Actualice el JSON manteniendo la estructura existente
3. Indique en el pull request el número de artículo, la sección modificada y la referencia oficial
4. No modifique los números de artículo sin consultar previamente, ya que el AI Act tuvo varias numeraciones durante su tramitación

## Reportar errores

Abra un issue en GitHub con:
- Descripción clara del problema
- Pasos para reproducirlo
- Comportamiento esperado vs. comportamiento observado
- Versión de Python y sistema operativo

## Código de conducta

Este proyecto sigue un entorno de colaboración respetuoso y profesional. Se esperan interacciones constructivas y orientadas a mejorar la herramienta para las PYMEs que necesitan orientación sobre el AI Act.

## Preguntas

Si tiene preguntas sobre el proceso de contribución, abra un issue con la etiqueta `question`.

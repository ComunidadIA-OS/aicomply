# CartonAssist B2B - Chatbot comercial para PYME industrial

> **Estado:** ejemplo ficticio para hackathon / demo de AIComply  
> **Tipo de sistema:** asistente conversacional basado en IA  
> **Clasificación esperada AIComply:** riesgo limitado / transparencia (Art. 50) + alfabetización en IA (Art. 4)  
> **Sector:** fabricación de embalajes de cartón para clientes B2B

## 1. Resumen

CartonAssist B2B es un asistente conversacional para una PYME fabricante de cajas de cartón ondulado. El sistema responde preguntas frecuentes de clientes profesionales sobre productos, cantidades mínimas, plazos de fabricación, fichas técnicas, estado de pedidos y preparación inicial de solicitudes de presupuesto.

El sistema no aprueba contratos, no fija precios finales, no resuelve reclamaciones legales y no toma decisiones vinculantes. Cuando la consulta tiene impacto comercial, contractual o legal, deriva la conversación a una persona del equipo comercial.

## 2. Descripción no técnica

El cliente entra en la web de la empresa y abre un chat. Antes de empezar, el sistema muestra un aviso claro: "Estás interactuando con un asistente de IA". El cliente puede hacer preguntas como:

- "Necesito cajas para botellas de vidrio, ¿qué formato recomendáis?"
- "¿Cuál es el pedido mínimo para cajas personalizadas?"
- "¿Podéis preparar un presupuesto para 2.000 unidades?"
- "¿Cuál es el estado de mi pedido?"

El asistente busca información en documentos internos aprobados, como fichas de producto, condiciones comerciales generales, preguntas frecuentes y datos de pedidos autorizados. Si no está seguro, lo indica y ofrece contactar con una persona.

## 3. Descripción técnica

CartonAssist B2B combina un modelo de lenguaje con recuperación aumentada por búsqueda documental (RAG). El sistema no entrena un modelo propio con conversaciones de clientes. Usa una base documental indexada y genera respuestas condicionadas a fragmentos recuperados.

### 3.1 Componentes

- **Frontend web:** widget de chat integrado en la página corporativa.
- **API backend:** servicio REST que recibe mensajes, aplica controles y devuelve respuestas.
- **Retriever:** búsqueda semántica e híbrida sobre documentos internos aprobados.
- **Vector store:** índice de embeddings de fichas técnicas, FAQs y políticas comerciales.
- **LLM:** modelo de lenguaje usado para redactar respuestas a partir del contexto recuperado.
- **Conectores:** integración limitada con ERP/CRM para consultar estado de pedido cuando el usuario se autentica.
- **Módulo de escalado:** deriva a un agente humano cuando detecta intención sensible.
- **Logging:** registro de conversación, fuentes usadas y eventos de escalado.

### 3.2 Flujo de funcionamiento

1. El cliente abre el chat y recibe aviso de interacción con IA.
2. El sistema clasifica la intención de la consulta.
3. Si la consulta requiere datos de pedido, solicita autenticación.
4. El retriever recupera fragmentos relevantes de documentos aprobados.
5. El LLM genera una respuesta limitada al contexto recuperado.
6. El sistema comprueba reglas de seguridad y coherencia.
7. Si hay baja confianza o impacto contractual, se deriva a una persona.

## 4. Uso previsto

El sistema está diseñado para:

- responder preguntas comerciales frecuentes;
- explicar características de productos de embalaje;
- orientar sobre cantidades mínimas y plazos estimados;
- preparar solicitudes preliminares de presupuesto;
- consultar estado de pedidos autenticados;
- reducir carga repetitiva del equipo comercial.

## 5. Usos no previstos

El sistema no debe utilizarse para:

- aprobar contratos o pedidos vinculantes;
- fijar precios finales;
- resolver reclamaciones jurídicas;
- negociar condiciones especiales;
- aceptar pedidos con efectos contractuales automáticos;
- responder a consumidores vulnerables o menores;
- tratar datos sensibles no necesarios para la consulta.

## 6. Usuarios y roles

- **Cliente B2B:** persona externa que interactúa con el chatbot.
- **Equipo comercial:** revisa solicitudes escaladas.
- **Administrador:** actualiza documentos aprobados y reglas de escalado.
- **Responsable de cumplimiento:** revisa transparencia, logs y avisos.

## 7. Datos tratados

### 7.1 Entradas

- Mensajes escritos por el cliente.
- Identificador de cliente cuando se consulta estado de pedido.
- Datos básicos del pedido si la consulta está autenticada.

### 7.2 Fuentes documentales

- Catálogo de productos.
- Fichas técnicas.
- FAQs comerciales.
- Políticas de plazos y cantidades mínimas.
- Plantillas de solicitud de presupuesto.

### 7.3 Salidas

- Respuestas conversacionales.
- Enlaces a fichas o documentos.
- Solicitudes preliminares de presupuesto.
- Tickets de escalado a equipo humano.

## 8. Arquitectura orientativa

```text
Usuario web
   |
Widget de chat
   |
API backend ---- Módulo de autenticación opcional
   |
Clasificador de intención
   |
Retriever RAG ---- Vector store ---- Documentos aprobados
   |
LLM generador
   |
Filtros de seguridad y reglas de escalado
   |
Respuesta / derivación humana
```

## 9. Transparencia y aviso al usuario

El sistema muestra al inicio del chat:

> "Estás interactuando con un asistente de inteligencia artificial. Sus respuestas son orientativas. Para presupuestos finales, contratos, reclamaciones o condiciones especiales, te atenderá una persona del equipo comercial."

El icono del chat identifica visualmente que se trata de un asistente de IA.

## 10. Controles de riesgo

- Aviso visible de IA antes de la primera interacción.
- Derivación obligatoria para precios finales y condiciones contractuales.
- Respuestas basadas en documentos aprobados.
- Registro de fuentes usadas en cada respuesta.
- Desactivación de respuesta cuando no se encuentran fuentes suficientes.
- Revisión mensual de conversaciones escaladas.
- Formación básica del personal comercial sobre límites del sistema.

## 11. Clasificación AI Act esperada

### Resultado preliminar

- **Categoría:** riesgo limitado / transparencia.
- **Motivo:** el sistema interactúa directamente con personas externas.
- **Obligación principal:** informar al usuario de que interactúa con un sistema de IA.
- **Obligación horizontal:** alfabetización en IA del personal que opera o supervisa el sistema.

### Por qué no es alto riesgo en este ejemplo

- No decide sobre empleo, educación, crédito, servicios esenciales o aplicación de la ley.
- No realiza identificación biométrica.
- No produce efectos jurídicos vinculantes.
- No aprueba ni rechaza contratos automáticamente.

## 12. Instalación para demo

```bash
git clone https://example.local/cartonassist-b2b.git
cd cartonassist-b2b
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
python manage.py ingest_docs data/docs/
python manage.py runserver
```

## 13. Variables de entorno

```env
LLM_PROVIDER=local
MODEL_NAME=llama-3.1-8b-instruct
VECTOR_DB=chroma
ENABLE_ORDER_STATUS=true
ENABLE_HUMAN_HANDOFF=true
LOG_RETENTION_DAYS=180
SHOW_AI_NOTICE=true
```

## 14. Pruebas mínimas

```bash
pytest tests/test_transparency_notice.py
pytest tests/test_handoff_rules.py
pytest tests/test_rag_citations.py
pytest tests/test_no_final_price_approval.py
```

## 15. Limitaciones conocidas

- Puede responder de forma incompleta si la documentación está desactualizada.
- Puede no detectar todos los casos que requieren escalado humano.
- No sustituye al equipo comercial ni a asesoramiento legal.
- Requiere revisión periódica de fuentes y prompts.

## 16. Mantenimiento

- Revisión mensual de documentos indexados.
- Revisión trimestral del aviso de transparencia.
- Auditoría de conversaciones escaladas.
- Formación anual del equipo comercial y administradores.

## 17. Licencia

Ejemplo ficticio para uso interno en hackathon. No usar en producción sin revisión jurídica, técnica y de protección de datos.

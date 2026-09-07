# 02 · Riesgo limitado — descripción del caso

Este recorrido se hizo por la **vía del texto pegado**, no subiendo un fichero de documentación
técnica. Es la otra de las dos entradas de la aplicación, y conviene que algún ejemplo la
ejercite: por esta vía el árbol arranca directamente, sin el paso previo en el que la aplicación
extrae una descripción del documento y pide confirmarla.

Esto es lo que se pegó en el chat del evaluador:

---

Somos una agencia de viajes española con tres oficinas y 18 empleados. Tenemos un chatbot en
nuestra web, contratado a un proveedor externo y en servicio desde 2025, que responde consultas
sobre destinos y disponibilidad y ayuda a pedir cita con un agente. Además usamos una herramienta
comercial de IA generativa para crear textos e imágenes promocionales que publicamos en nuestras
redes sociales. No tomamos decisiones automáticas sobre personas, no tratamos datos biométricos y
no hacemos selección de personal con IA.

---

## Respuestas dadas en el recorrido

**Evaluador**

| Pregunta | Respuesta |
|---|---|
| ¿El chatbot infiere o son respuestas predefinidas? | `Así es` (infiere) |
| Rol para el chatbot | `Correcto` (implementador, sin modificar ni marcar) |
| ¿La herramienta generativa infiere? | `Así es` |
| Rol para la herramienta generativa | `Correcto` (implementador) |
| ¿Ultrasuplantaciones en las imágenes? | `Las imágenes promocionales son contenido generado o manipulado y se publican al público. Pero no son de personas y si aparecen, son anónimas y no en primer plano.` |
| ¿Texto para informar al público sobre asuntos de interés público? | `Es contenido promocional y publicitario` |

**Cumplimiento**

| Obligación | Respuesta |
|---|---|
| Art. 4 — alfabetización | `Así es` → `Ambos` (los dos sistemas, capacidades y limitaciones) |
| Art. 50.3 — emociones y biometría | `No` |
| Art. 50.4 — divulgación de contenido artificial | `No` |
| Art. 50.1 — vigilancia sobre el proveedor del chatbot | `Hay un mensaje al inicio` → `Que se está interactuando con una IA` |
| Art. 50.2 — ¿estaba en el mercado antes del 2 ago 2026? | `Fue lanzada en 2025` |
| Art. 50.2 — vigilancia sobre el marcado | `No` |

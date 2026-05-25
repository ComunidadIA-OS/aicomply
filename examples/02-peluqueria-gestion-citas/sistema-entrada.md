# Sistema de gestión de citas para peluquería

Sistema conversacional que interpreta descripciones en lenguaje natural de los clientes, identifica los tratamientos de peluquería y estética solicitados, estima su duración y recomienda los huecos horarios disponibles compatibles con la agenda del profesional. El sistema interactúa directamente con los clientes a través de una interfaz conversacional. Ha sido desarrollado por la misma entidad que lo opera en su propio local.

---

## Contexto operativo

- **Sector:** Servicios de peluquería y estética.
- **Entidad usuaria:** Pequeño negocio de peluquería, autónomo o microempresa, con un único local.
- **Rol técnico:** La entidad ha desarrollado el sistema por su cuenta y lo opera en su propio establecimiento. No lo comercializa ni lo cede a terceros.
- **Régimen de uso:** Atención directa al cliente. El sistema funciona como interfaz de reservas para los clientes del local.

## Qué hace el sistema

1. Recibe una descripción en lenguaje natural del cliente describiendo el servicio que desea (por ejemplo: "quiero cortarme el pelo y hacerme mechas").
2. Analiza la descripción e identifica los tratamientos concretos que ofrece el local que corresponden a la solicitud.
3. Estima la duración total del servicio combinado a partir de los tratamientos identificados.
4. Consulta la agenda del profesional y recomienda los huecos horarios disponibles y compatibles con la duración estimada.
5. El cliente selecciona el hueco de su preferencia y se confirma la cita.

## Datos procesados

- Texto libre introducido por el cliente describiendo el servicio deseado.
- Catálogo de servicios y duraciones del local.
- Agenda de disponibilidad del profesional.
- **No se procesan datos biométricos, médicos, financieros ni datos personales sensibles.**
- **El sistema no toma decisiones sobre personas físicas más allá de la gestión de reservas.**

## Componente algorítmico

- Modelo de lenguaje o componente de procesamiento de lenguaje natural para interpretar la descripción del cliente e identificar tratamientos.
- Lógica de estimación de duración a partir del catálogo de servicios.
- Motor de disponibilidad que cruza la duración estimada con la agenda del profesional.

## Interfaz

- Interfaz conversacional directa con el cliente (chatbot o similar).
- Al inicio de cada conversación se muestra un aviso explícito de que el cliente está interactuando con un sistema de inteligencia artificial (recuadro visible).

## Supervisión humana

- La recomendación de huecos horarios es definitiva si el cliente la acepta; no hay una validación manual intermedia por parte del profesional para cada reserva.
- El profesional gestiona el catálogo de servicios, la agenda y la configuración del sistema.

## Estado actual y motivo de la evaluación

La entidad desarrolló el sistema y lo lleva usando en su local. La dirección quiere determinar:

- Si el sistema entra dentro del concepto de "sistema de IA" del Art. 3.1 del Reglamento (UE) 2024/1689.
- Qué nivel de riesgo le aplica bajo el AI Act europeo.
- Qué obligaciones concretas debe cumplir como entidad que desarrolla y opera el sistema.

# PanDemanda 3 — ficha del sistema

Documento interno de Panadería La Espiga de Castilla, S.L. Describe una herramienta de un
proveedor externo que la empresa tiene en uso.

*Sistema y empresa ficticios, creados como caso de ejemplo.*

## La organización

Cadena de cuatro panaderías con obrador propio, 30 empleados, en Valladolid y provincia. Tres
tiendas de calle y una en un centro comercial. El obrador produce de madrugada para las cuatro.

## Qué es el sistema

PanDemanda 3 es una herramienta de previsión de demanda que contratamos a Datacereal S.L. en
modalidad de suscripción. Se conecta a nuestro TPV y cada tarde estima, para cada tienda y cada
referencia del catálogo, cuántas unidades se venderán al día siguiente.

Lo usamos tal cual nos lo entrega el proveedor. No lo hemos modificado, no le hemos puesto
nuestra marca y no lo revendemos ni lo cedemos a nadie.

## Para qué se usa

Para decidir **cuánto producir en el obrador y qué materia prima comprar**. La previsión llega
como una hoja con las cantidades sugeridas por tienda y producto; el encargado de obrador la
revisa y la corrige a mano cuando lo ve necesario —fiestas locales, pedidos de encargo, una obra
en la calle— y sobre esa hoja corregida se lanza la producción.

El objetivo es reducir el excedente del cierre y las roturas de las primeras horas.

## Cómo funciona

Un modelo entrenado con el histórico de ventas de nuestras cuatro tiendas, la previsión
meteorológica de la zona y el calendario laboral y festivo. Aprende del histórico: la previsión
para un mismo producto cambia según la temporada, el día de la semana y el tiempo que se espera,
y se reentrena con las ventas de cada mes.

No es una tabla de cantidades fijas: el proveedor no escribe a mano ninguna regla del tipo «los
sábados, 200 barras». La salida es una estimación numérica con un margen.

## Datos que trata

Ventas agregadas por producto, tienda, día y franja horaria. Meteorología y calendario, que son
datos públicos.

**No trata datos de clientes**: no tenemos programa de fidelización, no identificamos a quien
compra y los tickets no llevan datos personales. **No trata datos de empleados**: no mide el
rendimiento de nadie, no reparte turnos y no entra en la gestión de personal.

## Qué decide y qué no

No toma ninguna decisión sobre personas. No selecciona, evalúa, puntúa ni clasifica a clientes ni
a trabajadores. Lo único que produce es una cantidad sugerida de producto, que una persona revisa
antes de que tenga efecto.

Tampoco interactúa con clientes ni con el público: no hay chat, no hay asistente, no genera
textos ni imágenes. Solo la ven las cuatro personas del equipo de obrador y compras.

## Nuestro papel

Somos usuarios de una herramienta comercial de terceros. No la desarrollamos, no la
comercializamos, no la distribuimos y no la hemos modificado. La responsabilidad del producto es
del proveedor; nosotros decidimos cómo la usamos dentro de la empresa.

## Estado

En uso desde marzo de 2025 en las cuatro tiendas. Contrato anual con Datacereal S.L., renovado en
marzo de 2026.

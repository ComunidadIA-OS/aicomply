# Talentia Screening 3.2 — ficha de despliegue

Documento interno de LogÍstica Ebro S.L. Describe cómo está implantada en la empresa la
herramienta de cribado de candidaturas contratada a Talentia Software S.L.

*Sistema y empresa ficticios, creados como caso de ejemplo.*

## La organización

Operador logístico español con sede en Zaragoza y dos plataformas de almacenaje. 140
empleados. Servicio de almacenaje y distribución para empresas de alimentación y comercio
electrónico. La rotación en los puestos de almacén es alta: se abren entre 15 y 25 procesos de
selección al año, con 200-400 candidaturas cada uno.

## Qué es el sistema

Talentia Screening es un producto comercial de cribado de candidaturas. Lo hemos **adquirido a
Talentia Software**, que es quien lo desarrolla y lo mantiene. Nosotros lo usamos como viene:
no hemos modificado el producto, no le hemos cambiado la finalidad prevista por el fabricante y
no lo distribuimos con nuestra marca. En la interfaz y en la documentación sigue siendo
Talentia Screening.

Versión desplegada: 3.2. En servicio desde marzo de 2024.

## Para qué lo usamos

Filtrado y ordenación de candidaturas en los procesos de selección de tres puestos:

- Mozo de almacén
- Carretillero
- Preparador de pedidos

No se usa para puestos de oficina, ni para promociones internas, ni para evaluar el desempeño
de personas ya contratadas.

## Cómo funciona

El sistema recibe el currículum en PDF y los datos que el candidato rellena en el formulario del
portal de empleo. De ahí extrae experiencia declarada, formación, disponibilidad horaria y
certificados (carné de carretillero, manipulador de alimentos).

Con esa información **genera una puntuación de adecuación de 0 a 100** para cada candidatura,
comparándola con el perfil del puesto. La puntuación no procede de un baremo fijo que hayamos
escrito nosotros: el proveedor entrena el modelo con datos históricos de procesos de selección y
la puntuación varía según lo que el modelo aprende.

**Las candidaturas por debajo del umbral se descartan automáticamente** y no llegan a la bandeja
de Recursos Humanos. El umbral lo fijamos nosotros desde el panel de configuración del producto
—hoy está en 55— y es una opción que el propio producto ofrece. Nadie revisa las candidaturas
descartadas.

Las que superan el umbral se presentan ordenadas por puntuación al equipo de Recursos Humanos,
que decide a quién entrevistar.

## Datos que trata

- Datos identificativos y de contacto del candidato
- Experiencia laboral y formación declaradas
- Certificados y carnés profesionales
- Disponibilidad horaria y geográfica

No trata datos biométricos, ni de salud, ni categorías especiales del Art. 9 del RGPD. No graba
ni analiza vídeo ni voz.

## Despliegue

Servicio en la nube del proveedor (SaaS). Integrado con nuestro portal de empleo mediante API.
Los registros de funcionamiento los genera y los almacena el proveedor en su infraestructura;
nosotros accedemos a ellos desde el panel, pero no tenemos copia propia ni control sobre su
periodo de conservación.

## Quién lo opera

El departamento de Recursos Humanos: la responsable del área y dos técnicos de selección. Los
coordinadores de almacén participan en las entrevistas, pero no usan la herramienta.

## Situación actual

- Contrato de servicio en vigor con Talentia Software.
- Manual de uso del proveedor disponible en la intranet.
- El equipo de Recursos Humanos recibió formación del proveedor sobre el manejo del producto.
- No hay un procedimiento escrito de seguimiento del funcionamiento del sistema.
- No se ha informado al comité de empresa del uso de la herramienta en los procesos de
  selección.
- Los candidatos no reciben información específica sobre la existencia de un cribado
  automatizado.

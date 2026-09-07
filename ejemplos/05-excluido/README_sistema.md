# TermoVigía TV-2 — ficha de producto

Documento interno de Óptica Aplicada del Norte S.L. Describe el sistema que la empresa
desarrolla y suministra.

*Sistema y empresa ficticios, creados como caso de ejemplo.*

## La organización

PYME española de 22 personas dedicada al diseño y fabricación de sistemas ópticos y de imagen
térmica. Cliente único: el Ministerio de Defensa, a través de un contrato de suministro
plurianual. No vendemos a clientes civiles ni tenemos línea de producto comercial.

## Qué es el sistema

TermoVigía TV-2 es un sistema de imagen térmica con detección automática de siluetas. Integra
una cámara de infrarrojos y un modelo de visión artificial que, sobre el flujo de vídeo,
detecta y clasifica presencias en el campo de visión —persona, vehículo ligero, vehículo
pesado— y las señala al operador en la pantalla del puesto.

Se instala en puestos de observación fijos y en vehículos.

## Para qué se usa

**Exclusivamente para vigilancia perimetral de instalaciones militares y para observación en
operaciones de las Fuerzas Armadas.** El sistema se desarrolla bajo especificación del
Ministerio de Defensa, se suministra únicamente a las Fuerzas Armadas y se emplea solo en ese
ámbito.

No tiene versión civil. No se comercializa para seguridad privada, control de accesos,
vigilancia de instalaciones industriales ni ningún otro uso fuera del ámbito de la defensa. El
contrato de suministro lo prohíbe expresamente.

## Cómo funciona

Red neuronal de detección de objetos entrenada con imágenes térmicas etiquetadas. Entrada:
fotograma de infrarrojos. Salida: cajas de detección con una etiqueta de clase y una
puntuación de confianza, superpuestas sobre la imagen que ve el operador.

**El sistema no toma ninguna decisión ni dispara ninguna acción.** Señala; decide siempre la
persona que está en el puesto.

## Datos que trata

Imágenes térmicas del campo de visión. La imagen de infrarrojos no permite identificar a una
persona concreta: no hay reconocimiento facial, ni biometría, ni comparación contra ninguna
base de datos de personas. No se almacenan las secuencias salvo cuando el operador marca un
evento, y en ese caso la custodia es del cliente.

## Nuestro papel

Somos quienes lo desarrollan y lo suministran, bajo nuestra propia marca, al Ministerio de
Defensa. No lo operamos nosotros: los puestos los manejan las Fuerzas Armadas.

## Estado

En servicio desde 2023. Versión TV-2 desplegada desde 2025. Mantenimiento y actualizaciones a
nuestro cargo dentro del contrato.

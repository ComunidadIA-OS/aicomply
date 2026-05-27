## Tipo de cambio

Marque las casillas que apliquen:

- [ ] Corrección de bug (cambio que arregla un problema sin romper compatibilidad)
- [ ] Nueva funcionalidad (cambio que añade comportamiento sin romper compatibilidad)
- [ ] Cambio que rompe compatibilidad (corrección o funcionalidad que provoca que el comportamiento existente cambie)
- [ ] Documentación (cambios solo en README, CONTRIBUTING, docs, etc.)
- [ ] Actualización del corpus normativo (cambios en `data/`)
- [ ] Refactorización (cambios internos sin alterar funcionalidad observable)
- [ ] Tests (añadir o mejorar tests sin cambiar el código de producción)
- [ ] CI / herramientas de desarrollo (cambios en `.github/`, `pyproject.toml`, scripts...)

## Descripción del cambio

Describa de forma clara y concisa qué cambia y por qué.

## Issue relacionado

Closes #(número de issue)

(O indique "No relacionado con un issue concreto" si aplica.)

## Cómo se ha probado

Describa los pasos que ha seguido para verificar que el cambio funciona como
se espera. Indique el provider LLM con el que se ha probado, si aplica.

## Checklist

- [ ] He leído [`CONTRIBUTING.md`](CONTRIBUTING.md)
- [ ] Mi código sigue el estilo del proyecto (`ruff check` pasa sin errores)
- [ ] He añadido tests que cubren los cambios (o he justificado por qué no aplica)
- [ ] Los tests existentes siguen pasando (`pytest` en local)
- [ ] He actualizado `CHANGELOG.md` con una entrada en la versión correspondiente
- [ ] He actualizado el `README.md` si los cambios afectan a uso, instalación o capacidades
- [ ] Cualquier dependencia nueva es compatible con licencia Apache 2.0 del proyecto
- [ ] No he incluido claves API, secretos ni datos personales en el código ni en los tests
- [ ] Los ficheros .py nuevos incluyen el header de copyright Apache 2.0 (ver ficheros existentes)

## Capturas (si aplica)

Si el cambio afecta a la interfaz Streamlit, incluya capturas antes/después.

## Compatibilidad de licencias

Si este PR introduce nuevas dependencias, liste cada una con su licencia y
confirme que es compatible con Apache 2.0:

| Dependencia | Versión | Licencia | Compatible Apache 2.0 |
|-------------|---------|----------|-----------------------|
|             |         |          |                       |

(Si no se añaden dependencias, indique "No aplica".)

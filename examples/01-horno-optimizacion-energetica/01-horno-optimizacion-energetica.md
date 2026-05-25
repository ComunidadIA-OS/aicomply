# Sistema de optimización de consumo energético de horno industrial

Sistema de control que ajusta automáticamente los ciclos de calentamiento de un horno industrial en función del precio horario de la electricidad y de los costes previstos de materias primas, con el objetivo de reducir el coste energético por lote producido. El sistema combina reglas deterministas configuradas por el equipo de producción con un componente de previsión basado en datos históricos de la planta y del mercado.

---

## Contexto operativo

- **Sector:** industria — fundición / tratamiento térmico de aleaciones metálicas.
- **Entidad usuaria:** PYME industrial española de aproximadamente 30 personas, una línea de horno continuo.
- **Rol técnico:** la PYME ha desarrollado el sistema internamente con apoyo de un consultor técnico externo, lo opera en su propia planta y no lo comercializa ni lo cede a terceros.
- **Régimen de uso:** producción 24/5. El sistema funciona de forma continua y emite recomendaciones de ajuste al supervisor del turno.

## Qué hace el sistema

1. Lee cada 15 minutos:
   - El precio horario de la electricidad del mercado mayorista (fuente: API pública de OMIE).
   - El precio actual y previsto de las materias primas (chatarra metálica, aleantes) desde una hoja interna actualizada manualmente por compras.
   - El estado térmico del horno (temperatura, energía consumida en el ciclo en curso) desde el SCADA de la planta.
2. Calcula una recomendación de "ciclo intensivo" o "ciclo de mantenimiento" para las próximas 4 horas, según:
   - Reglas deterministas configuradas por el equipo de producción (umbrales fijos de precio €/MWh y de margen objetivo).
   - Una estimación del coste-beneficio esperado del ciclo, calculada a partir de un modelo estadístico simple ajustado sobre 18 meses de datos históricos de la propia planta.
3. Muestra la recomendación en el panel del supervisor del turno, junto con la justificación numérica (precio actual, precio previsto, coste estimado del ciclo).
4. **No actúa directamente sobre el horno.** El supervisor humano decide si aplicar la recomendación, modificarla o ignorarla, y ejecuta el cambio manualmente desde el panel de control del horno.
5. Registra todas las recomendaciones, la decisión final del supervisor y el consumo real para análisis posterior.

## Datos procesados

- Precios de mercado eléctrico (datos públicos del operador del sistema).
- Precios internos de materias primas (datos comerciales de la empresa).
- Lecturas de sensores del horno (temperatura, consumo eléctrico).
- Registro temporal de decisiones del supervisor.
- **No se procesan datos personales, biométricos, médicos ni financieros de personas físicas.**
- **El sistema no toma decisiones sobre personas físicas.** Sus recomendaciones afectan exclusivamente al funcionamiento del horno y al coste energético del lote.

## Componente algorítmico

- Reglas deterministas: lógica condicional configurada por el equipo de producción, con umbrales ajustables.
- Modelo estadístico de previsión: regresión multivariable ajustada sobre 18 meses de datos históricos. Salida: estimación numérica del coste por kWh efectivo para el siguiente ciclo.
- El modelo se reajusta una vez al trimestre con los datos más recientes. No hay aprendizaje continuo en producción.
- No se utilizan redes neuronales, modelos de lenguaje ni componentes generativos.

## Despliegue y operación

- El sistema se ejecuta en un servidor de la propia planta, integrado con el SCADA.
- No hay conexión saliente fuera de la consulta del precio eléctrico al API público de OMIE.
- Mantenimiento realizado internamente por el responsable de producción con apoyo puntual del consultor externo que ayudó al desarrollo inicial.

## Supervisión humana actual

- La recomendación nunca se aplica de forma autónoma: requiere validación explícita del supervisor del turno.
- El supervisor puede ajustar manualmente cualquier parámetro o ignorar la recomendación.
- Se registra cada decisión (aplicar / modificar / ignorar) para revisión posterior.

## Estado actual del sistema y motivo de la evaluación

El sistema lleva 8 meses en uso. La dirección de la PYME quiere determinar:

- Si el sistema entra dentro del concepto de "sistema de IA" del Art. 3.1 del Reglamento (UE) 2024/1689 o si, por estar basado mayoritariamente en reglas deterministas y un modelo estadístico simple, queda fuera de esa definición.
- Si entra dentro del ámbito del Reglamento, qué nivel de riesgo le aplica.
- Qué documentación o procedimientos debe formalizar como organización.

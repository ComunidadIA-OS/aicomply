# TalentScreen Industrial - IA de filtrado de CVs para PYME industrial

> **Estado:** ejemplo ficticio para hackathon / demo de AIComply  
> **Tipo de sistema:** sistema de IA para priorización y filtrado de candidaturas  
> **Clasificación esperada AIComply:** alto riesgo por empleo y contratación  
> **Sector:** fabricación de componentes metálicos para automoción

## 1. Resumen

TalentScreen Industrial es un sistema de IA utilizado por una PYME fabricante de componentes metálicos para automoción. Su finalidad es ayudar al departamento de recursos humanos a filtrar candidaturas para puestos de operario de línea, técnico de mantenimiento, carretillero, soldador y responsable de turno.

El sistema analiza CVs, formularios de candidatura, certificados profesionales y respuestas a preguntas estructuradas. A partir de esos datos genera una puntuación de adecuación y propone una lista priorizada de candidatos. En la configuración inicial del ejemplo, el sistema descarta automáticamente candidaturas por debajo de un umbral antes de la revisión humana, lo que refuerza la clasificación como alto riesgo.

## 2. Descripción no técnica

Cuando una persona solicita empleo en la fábrica, sube su CV y responde a un formulario. El sistema extrae información relevante, como experiencia en turnos, formación en prevención de riesgos laborales, manejo de maquinaria, certificados y disponibilidad.

Después, compara esa información con los requisitos del puesto y genera una puntuación. Recursos Humanos recibe una lista ordenada. Las candidaturas por debajo de cierto umbral quedan marcadas como "no prioritarias" o son descartadas si la configuración automática está activada.

## 3. Descripción técnica

TalentScreen Industrial utiliza procesamiento de lenguaje natural para extraer información de CVs y formularios. Combina reglas de elegibilidad, embeddings semánticos y un modelo supervisado de ranking entrenado con datos históricos de procesos de selección.

### 3.1 Componentes

- **Portal de candidatura:** formulario web para candidatos.
- **Parser de CV:** extracción de texto, entidades y certificaciones.
- **Normalizador:** convierte experiencia, formación y disponibilidad a variables estructuradas.
- **Motor de reglas:** valida requisitos mínimos explícitos del puesto.
- **Modelo de ranking:** estima ajuste entre candidatura y puesto.
- **Módulo de explicabilidad:** muestra factores principales de la puntuación.
- **Panel de RRHH:** permite revisar, corregir y documentar decisiones.
- **Registro de auditoría:** almacena entradas, puntuación, versión del modelo y usuario revisor.

### 3.2 Flujo de funcionamiento

1. El candidato completa el formulario y sube su CV.
2. El sistema extrae texto y normaliza datos relevantes.
3. Se aplican reglas de requisitos mínimos.
4. El modelo calcula una puntuación de adecuación.
5. El sistema genera una explicación breve de factores principales.
6. RRHH revisa la lista y decide a quién entrevistar.
7. Las decisiones y cambios manuales quedan registrados.

## 4. Uso previsto

El sistema está diseñado para ayudar en procesos de selección internos de una PYME industrial, especialmente para:

- ordenar candidaturas recibidas para puestos de fábrica;
- detectar requisitos mínimos documentados;
- reducir carga administrativa de RRHH;
- mejorar trazabilidad del proceso de preselección;
- facilitar revisión humana de candidaturas.

## 5. Usos no previstos

El sistema no debe utilizarse para:

- tomar decisiones finales de contratación sin revisión humana;
- inferir personalidad, salud, ideología, afiliación sindical u otros atributos sensibles;
- analizar redes sociales de candidatos;
- usar fotografías para inferir características personales;
- descartar candidatos por edad, sexo, origen, discapacidad u otros factores protegidos;
- reutilizar datos de candidatos para fines disciplinarios o comerciales.

## 6. Usuarios y roles

- **Candidato:** persona que solicita empleo.
- **Técnico de RRHH:** revisa resultados y toma decisiones documentadas.
- **Responsable de planta:** define requisitos técnicos del puesto, sin modificar el modelo.
- **Administrador del sistema:** gestiona usuarios, versiones y parámetros autorizados.
- **Responsable de cumplimiento:** supervisa sesgos, registros y reclamaciones.

## 7. Datos tratados

### 7.1 Entradas

- CV y carta de presentación.
- Formulario de candidatura.
- Certificados profesionales aportados voluntariamente.
- Disponibilidad horaria y experiencia declarada.
- Puesto solicitado.

### 7.2 Variables calculadas

- Años de experiencia relevante.
- Coincidencia con requisitos obligatorios.
- Coincidencia semántica con descripción del puesto.
- Puntuación de adecuación.
- Factores explicativos principales.

### 7.3 Datos excluidos

- Fotografías.
- Datos biométricos.
- Datos de salud no necesarios.
- Datos sobre ideología, religión o afiliación sindical.
- Información de redes sociales.

## 8. Arquitectura orientativa

```text
Candidato
   |
Portal de candidatura
   |
Parser de CV ---- Almacenamiento seguro de documentos
   |
Normalizador de variables
   |
Motor de reglas ---- Requisitos del puesto
   |
Modelo de ranking
   |
Módulo de explicabilidad
   |
Panel de RRHH ---- Revisión humana ---- Registro de auditoría
```

## 9. Modelo y criterios de decisión

### 9.1 Enfoque de modelado

- Extracción NLP para CVs y documentos.
- Reglas explícitas para requisitos obligatorios.
- Modelo supervisado de ranking para priorización.
- Umbrales configurables por tipo de puesto.

### 9.2 Salida del sistema

```json
{
  "candidate_id": "CAND-2026-00125",
  "job_id": "JOB-MANT-042",
  "score": 0.82,
  "recommendation": "priorizar entrevista",
  "main_factors": [
    "certificado PRL vigente",
    "4 años de experiencia en mantenimiento industrial",
    "disponibilidad para turnos rotativos"
  ],
  "model_version": "ranker-0.9.3"
}
```

## 10. Supervisión humana

El sistema debe configurarse para que ninguna decisión final se adopte sin revisión humana. La revisión humana debe incluir:

- posibilidad real de cambiar la recomendación;
- acceso a factores explicativos;
- revisión de candidaturas descartadas por umbral;
- registro del motivo de aceptación o rechazo;
- canal para reclamaciones o solicitudes de revisión.

## 11. Controles de riesgo

- Prohibición de usar atributos sensibles.
- Evaluación periódica de sesgos.
- Revisión humana obligatoria.
- Logs de versiones, puntuaciones y cambios manuales.
- Política de conservación limitada de datos.
- Información clara a candidatos sobre uso de IA.
- Pruebas antes de cada cambio de modelo o umbral.
- Documentación de finalidad prevista y límites de uso.

## 12. Clasificación AI Act esperada

### Resultado preliminar

- **Categoría:** alto riesgo.
- **Motivo:** sistema usado para selección, priorización o filtrado de candidatos a empleo.
- **Rol probable de la PYME:** implementador si compra el sistema a un tercero; proveedor si lo desarrolla internamente, lo pone en servicio bajo su nombre o lo modifica sustancialmente.

### Obligaciones que AIComply debería analizar

Para un implementador de un sistema de alto riesgo, el informe debería revisar, entre otros puntos:

- uso conforme a instrucciones del proveedor;
- supervisión humana efectiva;
- pertinencia de datos de entrada bajo control del implementador;
- conservación de logs cuando estén bajo su control;
- información a personas afectadas cuando corresponda;
- cooperación con autoridades;
- alfabetización en IA del personal;
- protección de datos y documentación del proceso.

## 13. Instalación para demo

```bash
git clone https://example.local/talentscreen-industrial.git
cd talentscreen-industrial
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
python manage.py migrate
python manage.py load_demo_jobs data/demo_jobs.csv
python manage.py runserver
```

## 14. Variables de entorno

```env
MODEL_VERSION=ranker-0.9.3
ENABLE_AUTO_REJECTION=false
MIN_HUMAN_REVIEW=true
LOG_RETENTION_DAYS=365
EXPLAINABILITY_ENABLED=true
SENSITIVE_ATTRIBUTE_FILTER=true
BIAS_AUDIT_ENABLED=true
```

## 15. Pruebas mínimas

```bash
pytest tests/test_no_sensitive_attributes.py
pytest tests/test_human_review_required.py
pytest tests/test_audit_log.py
pytest tests/test_threshold_changes_are_logged.py
pytest tests/test_explanations_available.py
```

## 16. Limitaciones conocidas

- El modelo puede reproducir sesgos presentes en datos históricos.
- CVs incompletos o formatos no estándar pueden degradar la extracción.
- La puntuación no debe interpretarse como verdad objetiva sobre la persona.
- Cambios de umbral pueden alterar significativamente resultados.
- Requiere revisión jurídica, laboral y de protección de datos antes de producción.

## 17. Mantenimiento

- Auditoría de sesgos antes de cada campaña de contratación relevante.
- Revisión de requisitos de puesto por RRHH y responsable de planta.
- Revisión de logs y decisiones revertidas.
- Control de versiones de modelo, datos y umbrales.
- Formación periódica de usuarios de RRHH.

## 18. Licencia

Ejemplo ficticio para uso interno en hackathon. No usar en producción sin evaluación de conformidad, revisión laboral, revisión RGPD y validación técnica.

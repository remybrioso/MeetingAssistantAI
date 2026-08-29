# M4 - AI Pipeline

## Versión

v0.9.0-alpha.1

## Estado

✅ Completado

## Objetivo

Convertir `transcript.json` en artefactos útiles, verificables y
entregables al usuario.

## Principios

- La IA trabaja sobre `transcript.json`, nunca sobre archivos WAV.
- Los audios originales no se modifican.
- Cada resultado derivado es un artefacto independiente.
- El procesamiento debe poder funcionar offline.
- No se requieren APIs de pago.
- La IA no habla directamente con la GUI.
- El formato final lo controla la aplicación, no el modelo.
- La evidencia se reconstruye determinísticamente desde el transcript.
- Las proyecciones de salida no realizan nuevas llamadas al LLM.

## Arquitectura productiva

```text
Transcript
    |
    v
Staged Chunk Knowledge
    |
    v
MeetingKnowledge
    |
    v
Staged Global Consolidation
    |
    v
MeetingReport
    |
    v
MeetingArtifactDeliveryService
```

## Estrategia de inteligencia

### Extracción por chunks

Cada chunk usa un contrato flat para clasificar:

- decision
- action
- risk
- pending
- topic

La evidencia se representa mediante referencias a segmentos y se
reconstruye determinísticamente.

Las acciones pueden recibir un segundo paso batch para:

- owner
- due_date
- status

### Consolidación global

La consolidación global trabaja con referencias compactas a las
fuentes y no obliga al modelo a copiar timestamps, evidencia ni
metadata confiable.

Una segunda etapa narrativa genera:

- título
- objetivo cuando existe evidencia suficiente
- resumen ejecutivo
- puntos clave

El ensamblado final vuelve a ser determinista.

## Artefacto maestro

`MeetingReport` es la fuente confiable para todas las salidas
derivadas.

## Artefactos productivos

```text
.mai/
├── meeting_report.json
├── action_items.json
└── decisions.json

Documentos/
├── Meeting Report.md
├── minutes.docx
└── meeting.pdf
```

`action_items.json` y `decisions.json` son proyecciones
deterministas del MeetingReport.

DOCX y PDF también se generan directamente desde MeetingReport;
no se utiliza un LLM adicional para formatearlos.

## Validación de cierre

Al cierre de TASK-058:

- 820 tests passed.
- 3 tests skipped.
- 0 failures.
- E2E productivo autosuficiente: 1 passed.
- Los seis artefactos de entrega fueron verificados en el pipeline
  productivo.

## Resultado

M4 deja a MAI preparado para entrar al milestone M5:
Beta / Release Engineering y construcción de la versión instalable.

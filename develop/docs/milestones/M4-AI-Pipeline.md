# M4 - AI Pipeline

## Versión

v0.9.0-alpha.1

## Objetivo

Convertir `transcript.json` en artefactos útiles para el usuario.

## Principios

- La IA trabaja sobre `transcript.json`, nunca sobre archivos WAV.
- Los audios originales no se modifican.
- Cada resultado de IA será un artefacto independiente.
- Todo debe funcionar offline.
- No se usarán APIs de pago.
- La IA no hablará directamente con la GUI.
- El formato final será controlado por la aplicación, no por el modelo.

## Artefactos objetivo

- summary.md
- action_items.json
- decisions.json
- minutes.docx
- meeting.pdf

## Arquitectura propuesta

```text
RecordingSession
    |
    v
transcript.json
    |
    v
AI Provider
    |
    v
Domain Artifact
    |
    v
Artifact Storage
    |
    v
artifacts/
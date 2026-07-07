# QA-001 - Meeting Pipeline Validation

## Versión

v0.8.0-alpha.1

## Objetivo

Validar el flujo completo de reunión antes de cerrar la release.

---

## Escenario 1 - Reunión corta

Duración: 10-20 segundos

Resultado esperado:

- mic.wav
- system.wav
- transcript.json
- processing_metrics.json

Estado: Aprobado

---

## Escenario 2 - Reunión media

Duración: 2 minutos

Resultado esperado:

- UI responsiva
- transcript.json generado
- métricas generadas

Estado: Aprobado

---

## Escenario 3 - Dos reuniones consecutivas

Resultado esperado:

- Carpetas distintas
- Archivos sin sobrescribir

Estado: Aprobado

---

## Escenario 4 - Reunión sin audio

Resultado esperado:

- La app no se cae
- Se registra resultado de Whisper

Estado: Pendiente

---

## Resultado general

Aprobado
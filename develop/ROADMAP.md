# Meeting Assistant AI

## Versión actual

v0.9.0-alpha.1

---

# Milestones

## M1 - Arquitectura Base

Estado: ✅ Completado

## M2 - Transcript Pipeline

Estado: ✅ Completado

## M3 - Meeting Pipeline

Versión objetivo: v0.8.0-alpha.1

Estado: ✅ Completado

Resultado principal:

- Flujo completo de reunión desde la GUI.
- Captura dual de audio.
- Transcripción automática.
- Persistencia de `transcript.json`.
- Procesamiento fuera del hilo principal de la interfaz.
- Soporte para reuniones grabadas e importadas.

## M4 - AI Pipeline

Versión objetivo: v0.9.0-alpha.1

Estado: ✅ Completado

Resultado principal:

- Extracción de conocimiento staged por chunks.
- Consolidación global staged.
- `MeetingReport` validado y grounded.
- Proyecciones deterministas de acciones y decisiones.
- Entrega automática de artefactos JSON, Markdown, DOCX y PDF.
- Pipeline productivo validado con E2E autosuficiente.

Artefactos productivos:

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

## M5 - Beta / Release Engineering

Estado: 🚧 En preparación

Objetivo:

Convertir MAI en una aplicación de escritorio instalable y
reproducible para Windows, manteniendo el funcionamiento offline
y guiando al usuario en la validación de dependencias externas.

Frentes previstos:

1. Alinear versionado, documentación y deuda técnica.
2. Preparar el runtime para ejecución empaquetada.
3. Crear un ejecutable reproducible de Windows.
4. Crear el instalador.
5. Validar instalación y primera ejecución en una máquina limpia.
6. Documentar instalación, requisitos y recuperación.

---

# Próxima tarea

TASK-059 - Product / Technical Debt Alignment

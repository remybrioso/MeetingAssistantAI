# Meeting Assistant AI

## Versión actual

v0.9.0-alpha.3

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

Artefactos productivos principales:

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

## M5 - Alpha Release Engineering

Versión objetivo: v0.9.0-alpha.2

Estado: ✅ Completado

Resultado principal:

- Runtime productivo empaquetado con PyInstaller.
- Aplicación GUI sin consola.
- Instalador de Windows mediante Inno Setup.
- Instalación por usuario sin requerir privilegios administrativos.
- Setup Wizard de primera ejecución.
- Descarga asistida del modelo de transcripción.
- Onboarding de Ollama.
- Descarga y verificación de `qwen2.5:3b`.
- Configuración asistida de audio de Windows.
- Validación clean-machine / isolated-runtime.
- Documentación de instalación y release.
- Baseline de regresión: 941 passed, 2 skipped.

## M5.1 - Corporate Acceptance Hardening

Versión objetivo: v0.9.0-alpha.3

Estado: 🟡 Hardening completado; release en preparación

Resultado principal:

- Corporate Acceptance completado en la estación corporativa TSS.
- Compatibilidad de salida estructurada con Ollama endurecida.
- Integridad temporal de Faster-Whisper corregida para reuniones largas.
- Cobertura semántica y procedencia narrativa preservadas determinísticamente.
- Reuniones importadas dirigidas a la ruta canónica de Meetings.
- Resultado de evidencia insuficiente tratado como condición de dominio esperada.
- Runtime congelado validado para CAT-001 y CAT-002.
- Baseline de regresión: 1018 collected, 1016 passed, 2 skipped, 0 failed.

## M6 - Beta Feedback & Product Hardening

Estado: ⏳ Pendiente

Objetivo:

Validar MAI con usuarios reales y convertir el feedback de la alpha
en mejoras de usabilidad, observabilidad, recuperación y estabilidad.

Frentes previstos:

1. Telemetría local y diagnósticos orientados a soporte.
2. Refinamiento de UX del flujo de reunión.
3. Manejo de errores y recuperación de sesiones.
4. Rendimiento en reuniones largas.
5. Compatibilidad ampliada de dispositivos de audio.
6. Preparación de una beta distribuible.

---

# Próximo objetivo

Preparar, validar y publicar `v0.9.0-alpha.3` como GitHub Release. Después de
cerrar esa prerelease podrá abrirse el ciclo de feedback previo a M6.

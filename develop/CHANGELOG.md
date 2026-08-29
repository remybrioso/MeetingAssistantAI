# Changelog

## v0.9.0-alpha.1

### Added

- Meeting Intelligence staged por chunks.
- Consolidación global staged de conocimiento.
- `MeetingReport` como artefacto principal de dominio.
- Proyección determinista de acciones y decisiones.
- Persistencia de:
  - `.mai/meeting_report.json`
  - `.mai/action_items.json`
  - `.mai/decisions.json`
- Exportación de:
  - `Documentos/Meeting Report.md`
  - `Documentos/minutes.docx`
  - `Documentos/meeting.pdf`
- `MeetingArtifactDeliveryService`.
- Generación formal de DOCX mediante `python-docx`.
- Generación formal de PDF mediante `reportlab`.
- E2E productivo autosuficiente del Meeting Pipeline.

### Changed

- El `MeetingPipelineService` delega la entrega de artefactos a
  `MeetingArtifactDeliveryService`.
- La consolidación global legacy fue reemplazada en producción por
  el flujo staged.
- El contrato productivo de MeetingReport es
  `meeting_report_global_staged_v1`.

### Quality

- Regresión global al cierre de TASK-058:
  - 820 tests passed.
  - 3 tests skipped.
  - 0 failures.
- E2E productivo de entrega completa:
  - 1 test passed.

---

## v0.8.0-alpha.1

### Added

- Flujo completo de reunión desde la GUI.
- Orquestación de finalización de reuniones.
- Generación automática de transcripción.
- Persistencia automática de `transcript.json`.
- Procesamiento desacoplado de la interfaz gráfica.
- Soporte de reuniones importadas.
- Setup Wizard y evaluación de capacidades funcionales.

### Architecture

- Separación entre controladores, servicios y estado de aplicación.
- Consolidación del Meeting Pipeline como capa de orquestación.
- Integración del contenedor de dependencias.

---

## v0.7.0-alpha.1

### Added

- Arquitectura desacoplada.
- Captura dual de audio.
- Faster-Whisper integrado.
- Transcript Pipeline.
- Persistencia de `transcript.json`.
- Arquitectura Builder.
- Arquitectura Provider.
- Transcript Storage.

### Fixed

- Correcciones de captura WASAPI.
- Correcciones de RecordingSession.
- Correcciones del EventBus.
- Correcciones del Timer.

### Architecture

- Primera auditoría completa.
- Arquitectura validada.
- Inicio del versionado del desarrollo.

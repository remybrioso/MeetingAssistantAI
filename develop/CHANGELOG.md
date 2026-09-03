# Changelog

## v0.9.0-alpha.3

### Fixed

- Se mejoró la compatibilidad de las respuestas estructuradas con la versión local de Ollama utilizada por MAI.
- Se corrigieron discontinuidades temporales de Faster-Whisper que podían invalidar reuniones largas con pistas de audio superpuestas.
- La consolidación global preserva determinísticamente todo el conocimiento extraído de la reunión sin inventar procedencia.
- Las referencias narrativas representan únicamente los elementos que realmente fundamentan cada texto.
- Las reuniones importadas se guardan en la ruta canónica de Meetings dentro de Documents, incluida su redirección corporativa a OneDrive.
- Las reuniones sin evidencia suficiente conservan audio, transcripción y métricas, y muestran un aviso comprensible sin habilitar exportación ni presentar un falso éxito.

### Release Engineering

- Se eliminó una colisión de nombres durante la colección global de pytest.
- Se añadieron contratos y pruebas de regresión para integridad temporal, cobertura semántica, procedencia narrativa, almacenamiento de importaciones y resultados de evidencia insuficiente.
- Se actualizó la documentación persistente de continuidad de ingeniería después del cierre de Corporate Acceptance.

### Quality

Regresión global posterior a esta actualización de metadata:

- 1018 tests collected.
- 1016 tests passed.
- 2 tests skipped.
- 0 failures.

También se validó:

- Meeting Pipeline con la reunión corporativa real de TSS;
- runtime congelado para el enrutamiento canónico de reuniones importadas;
- runtime congelado para la experiencia de evidencia estructural insuficiente.

---

## v0.9.0-alpha.2

### Added

- Ejecutable productivo de Windows mediante PyInstaller en modo one-folder.
- Instalador de Windows mediante Inno Setup.
- Setup Wizard de primera ejecución con acciones reparables.
- Descarga explícita del modelo de transcripción mediante Faster-Whisper.
- Onboarding de Ollama desde su página oficial.
- Descarga explícita y verificación del modelo `qwen2.5:3b`.
- Apertura asistida de la configuración de sonido de Windows.
- Documentación de instalación, first-run y release.

### Changed

- El runtime productivo ya no depende de Python ni de `.venv` en el equipo del usuario.
- El Setup Wizard distingue entre reparaciones internas y acciones externas que requieren intervención del usuario.
- El audio del sistema puede permanecer en estado degradado sin bloquear la aplicación cuando el micrófono sigue siendo utilizable.
- La versión de publicación se promueve de `v0.9.0-alpha.1` a `v0.9.0-alpha.2` para mantener trazabilidad entre código y artefactos binarios.

### Release Engineering

- Build productivo GUI sin consola.
- Instalación por usuario sin requerir privilegios administrativos.
- Desinstalación validada preservando datos de reuniones del usuario.
- Runtime congelado validado fuera del repositorio y de `.venv`.
- First-run validado desde instalación real.
- Onboarding validado con dependencias deliberadamente ausentes.
- Contratos de PyInstaller e Inno Setup cubiertos por tests.

### Quality

Baseline previo a publicación:

- 941 tests passed.
- 2 tests skipped.
- 0 failures.

E2E de release validados:

- runtime congelado desde directorio ajeno al repositorio;
- instalación limpia;
- modelo de transcripción ausente → descarga → disponible;
- Ollama ausente → acción requerida → disponible;
- `qwen2.5:3b` ausente → descarga → disponible;
- audio disponible o degradado sin bloquear la continuación.

---

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

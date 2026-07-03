## MAI-017 - Cambio hacia Transcript Pipeline

Se cambia la estrategia de procesamiento.

Antes:
- Mezclar mic.wav + system.wav -> meeting.wav -> Whisper.

Ahora:
- Transcribir mic.wav.
- Transcribir system.wav.
- Fusionar transcripciones por timestamps.

Decisión:
`meeting.wav` deja de ser requisito para Whisper y pasa a ser un artefacto opcional.
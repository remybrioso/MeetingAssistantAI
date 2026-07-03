## Cambio de arquitectura - MAI-017

Se decide no usar `meeting.wav` como entrada principal para Whisper.

Nueva estrategia:

```text
mic.wav       -> Whisper -> mic_transcript.json
system.wav    -> Whisper -> system_transcript.json

mic_transcript.json
system_transcript.json
        |
        v
TranscriptMerger
        |
        v
transcript.json
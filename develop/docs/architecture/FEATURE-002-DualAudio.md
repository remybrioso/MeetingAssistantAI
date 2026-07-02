# FEATURE-002 - Captura Dual de Audio

## Objetivo

Implementar captura simultánea de:

- Micrófono del usuario.
- Audio del sistema.
- Mezcla final en un único archivo `meeting.wav`.

Este archivo será usado posteriormente por Whisper para la transcripción.

---

## Arquitectura propuesta

```text
AudioCaptureService
    |
    |-- MicrophoneRecorder
    |-- SystemAudioRecorder
    |-- AudioMixer
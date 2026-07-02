## MAI-005 - Diseño de Captura Dual de Audio

Se define la arquitectura de FEATURE-002.

Decisiones:

- AudioCaptureService coordinará la captura.
- Micrófono y audio del sistema se capturarán por separado.
- La mezcla se realizará después de finalizar la grabación.
- Se priorizará WASAPI Loopback.
- Stereo Mix será alternativa.
- El archivo final será output/meeting.wav.

Próximo objetivo:
Implementar SystemAudioRecorder.